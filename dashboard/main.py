"""Streamlit dashboard for MLOps service."""

import streamlit as st
import requests
import json
import pandas as pd
from typing import Dict, Any, List

# Configuration
import os
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")

st.set_page_config(
    page_title="MLOps Dashboard",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 MLOps Model Management Dashboard")


def check_api_health() -> bool:
    """Check if API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def get_available_models() -> List[str]:
    """Get list of available model classes."""
    try:
        response = requests.get(f"{API_BASE_URL}/models/available", timeout=5)
        if response.status_code == 200:
            return response.json()["model_classes"]
        return []
    except:
        return []


def get_trained_models() -> List[Dict[str, Any]]:
    """Get list of trained models."""
    try:
        response = requests.get(f"{API_BASE_URL}/models", timeout=5)
        if response.status_code == 200:
            return response.json()["models"]
        return []
    except:
        return []


def get_datasets() -> List[Dict[str, Any]]:
    """Get list of datasets."""
    try:
        response = requests.get(f"{API_BASE_URL}/datasets", timeout=5)
        if response.status_code == 200:
            return response.json()["datasets"]
        return []
    except:
        return []


# Sidebar
st.sidebar.title("Navigation")
tab = st.sidebar.radio(
    "Select Tab",
    ["Datasets", "Training", "Inference"]
)

# Check API health
if not check_api_health():
    st.error("⚠️ API service is not available. Please make sure the API is running.")
    st.stop()

# Datasets Tab
if tab == "Datasets":
    st.header("📊 Dataset Management")
    
    # List datasets
    st.subheader("Available Datasets")
    datasets = get_datasets()
    
    if datasets:
        df = pd.DataFrame(datasets)
        st.dataframe(df[["name", "size"]], use_container_width=True)
        
        # Delete dataset
        st.subheader("Delete Dataset")
        dataset_names = [d["name"] for d in datasets]
        selected_dataset = st.selectbox("Select dataset to delete", dataset_names)
        
        if st.button("Delete Dataset"):
            try:
                # Note: Delete endpoint would need to be added to API
                st.warning("Delete functionality requires API endpoint")
            except Exception as e:
                st.error(f"Error deleting dataset: {e}")
    else:
        st.info("No datasets available")
    
    # Upload dataset
    st.subheader("Upload New Dataset")
    uploaded_file = st.file_uploader(
        "Choose a CSV or JSON file",
        type=["csv", "json"]
    )
    
    if uploaded_file is not None:
        if st.button("Upload Dataset"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(
                    f"{API_BASE_URL}/datasets/upload",
                    files=files,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Dataset uploaded: {result['dataset_name']}")
                    st.rerun()
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error uploading dataset: {e}")

# Training Tab
elif tab == "Training":
    st.header("🎓 Model Training")
    
    # Get available model classes
    model_classes = get_available_models()
    
    if not model_classes:
        st.error("No model classes available")
        st.stop()
    
    # Model selection
    model_class = st.selectbox("Select Model Class", model_classes)
    
    # Hyperparameters input
    st.subheader("Hyperparameters")
    hyperparameters_json = st.text_area(
        "Enter hyperparameters as JSON",
        height=200,
        value='{\n  "n_estimators": 100,\n  "max_depth": 10,\n  "task_type": "classification"\n}'
    )
    
    # Dataset selection
    datasets = get_datasets()
    if datasets:
        dataset_names = [d["name"] for d in datasets]
        dataset_name = st.selectbox("Select Dataset", dataset_names)
        
        # Train button
        if st.button("Train Model", type="primary"):
            try:
                hyperparameters = json.loads(hyperparameters_json)
                
                request_data = {
                    "model_class": model_class,
                    "hyperparameters": hyperparameters,
                    "dataset_name": dataset_name
                }
                
                with st.spinner("Training model..."):
                    response = requests.post(
                        f"{API_BASE_URL}/models/train",
                        json=request_data,
                        timeout=300
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Model trained successfully!")
                    st.json(result)
                else:
                    st.error(f"Error: {response.text}")
            except json.JSONDecodeError:
                st.error("Invalid JSON format for hyperparameters")
            except Exception as e:
                st.error(f"Error training model: {e}")
    else:
        st.warning("No datasets available. Please upload a dataset first.")
    
    # List trained models
    st.subheader("Trained Models")
    trained_models = get_trained_models()
    
    if trained_models:
        df = pd.DataFrame(trained_models)
        st.dataframe(df, use_container_width=True)
        
        # Retrain model
        st.subheader("Retrain Model")
        model_ids = [m["model_id"] for m in trained_models]
        selected_model_id = st.selectbox("Select model to retrain", model_ids)
        
        if datasets:
            retrain_dataset = st.selectbox(
                "Select dataset for retraining",
                [d["name"] for d in datasets]
            )
            
            new_hyperparameters_json = st.text_area(
                "Enter new hyperparameters (optional)",
                height=150,
                value="{}"
            )
            
            if st.button("Retrain Model"):
                try:
                    new_hyperparameters = json.loads(new_hyperparameters_json) if new_hyperparameters_json.strip() != "{}" else None
                    
                    request_data = {
                        "dataset_name": retrain_dataset
                    }
                    if new_hyperparameters:
                        request_data["hyperparameters"] = new_hyperparameters
                    
                    with st.spinner("Retraining model..."):
                        response = requests.post(
                            f"{API_BASE_URL}/models/{selected_model_id}/retrain",
                            json=request_data,
                            timeout=300
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ Model retrained successfully!")
                        st.json(result)
                    else:
                        st.error(f"Error: {response.text}")
                except json.JSONDecodeError:
                    st.error("Invalid JSON format for hyperparameters")
                except Exception as e:
                    st.error(f"Error retraining model: {e}")
    else:
        st.info("No trained models yet")

# Inference Tab
elif tab == "Inference":
    st.header("🔮 Model Inference")
    
    # Get trained models
    trained_models = get_trained_models()
    
    if not trained_models:
        st.warning("No trained models available. Please train a model first.")
        st.stop()
    
    # Model selection
    model_ids = [m["model_id"] for m in trained_models]
    selected_model_id = st.selectbox("Select Model", model_ids)
    
    # Get model info
    selected_model = next(m for m in trained_models if m["model_id"] == selected_model_id)
    st.json(selected_model)
    
    # Features input
    st.subheader("Input Features")
    
    # Option 1: Manual input
    input_method = st.radio("Input Method", ["Manual", "CSV Upload"])
    
    if input_method == "Manual":
        num_features = st.number_input("Number of features", min_value=1, max_value=100, value=4)
        
        features = []
        cols = st.columns(min(num_features, 5))
        
        for i in range(num_features):
            with cols[i % len(cols)]:
                feature_value = st.number_input(f"Feature {i+1}", key=f"feature_{i}", value=0.0)
                features.append(feature_value)
        
        if st.button("Predict", type="primary"):
            try:
                request_data = {
                    "features": [features]
                }
                
                response = requests.post(
                    f"{API_BASE_URL}/models/{selected_model_id}/predict",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Prediction successful!")
                    st.json(result)
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error making prediction: {e}")
    
    else:  # CSV Upload
        uploaded_file = st.file_uploader("Upload CSV with features", type=["csv"])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df, use_container_width=True)
            
            if st.button("Predict", type="primary"):
                try:
                    # Convert DataFrame to list of lists
                    features = df.values.tolist()
                    
                    request_data = {
                        "features": features
                    }
                    
                    with st.spinner("Making predictions..."):
                        response = requests.post(
                            f"{API_BASE_URL}/models/{selected_model_id}/predict",
                            json=request_data,
                            timeout=30
                        )
                    
                    if response.status_code == 200:
                        result = response.json()
                        predictions = result["predictions"]
                        
                        # Add predictions to dataframe
                        df["prediction"] = predictions
                        st.success("✅ Predictions successful!")
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error making predictions: {e}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**MLOps Homework 1**")
st.sidebar.markdown(f"API: {API_BASE_URL}")

