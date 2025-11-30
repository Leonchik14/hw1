"""REST API routes."""

from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import os
import json
from app.api.schemas import (
    HealthResponse,
    ModelClassResponse,
    TrainRequest,
    TrainResponse,
    PredictRequest,
    PredictResponse,
    RetrainRequest,
    ModelsListResponse,
    DatasetsListResponse,
    UploadDatasetResponse
)
from app.services import ModelService, DVCService, ClearMLService
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

# Initialize services
model_service = ModelService()
dvc_service = DVCService()
clearml_service = ClearMLService()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the service.
    
    Returns:
        Health status information
    """
    logger.info("Health check requested")
    return HealthResponse()


@router.get("/models/available", response_model=ModelClassResponse)
async def get_available_models():
    """
    Get list of available model classes for training.
    
    Returns:
        List of available model class names
    """
    logger.info("Requested available model classes")
    model_classes = model_service.get_available_model_classes()
    return ModelClassResponse(model_classes=model_classes)


@router.get("/models", response_model=ModelsListResponse)
async def list_models():
    """
    Get list of all trained models.
    
    Returns:
        List of model information
    """
    logger.info("Requested list of models")
    models = model_service.list_models()
    return ModelsListResponse(models=models)


@router.post("/models/train", response_model=TrainResponse)
async def train_model(request: TrainRequest):
    """
    Train a new model with specified hyperparameters.
    
    Args:
        request: Training request with model class, hyperparameters, and dataset
        
    Returns:
        Training results with model ID and metrics
    """
    logger.info(f"Training request: model_class={request.model_class}, dataset={request.dataset_name}")
    
    try:
        # Get dataset path
        dataset_path = dvc_service.get_dataset_path(request.dataset_name)
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_name} not found")
        
        # Create model
        model_id = model_service.create_model(
            request.model_class,
            request.hyperparameters
        )
        
        # Train model
        metrics = model_service.train_model(model_id, dataset_path)
        
        # Upload to ClearML
        model_path = os.path.join(settings.models_dir, f"{model_id}.pkl")
        if os.path.exists(model_path):
            clearml_service.upload_model(
                model_id,
                model_path,
                request.model_class,
                request.hyperparameters,
                metrics
            )
        
        return TrainResponse(
            model_id=model_id,
            metrics=metrics,
            message="Model trained successfully"
        )
    except ValueError as e:
        logger.error(f"Training error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/predict", response_model=PredictResponse)
async def predict(model_id: str, request: PredictRequest):
    """
    Get predictions from a trained model.
    
    Args:
        model_id: ID of the model to use
        request: Prediction request with features
        
    Returns:
        Predictions from the model
    """
    logger.info(f"Prediction request for model {model_id}")
    
    try:
        predictions = model_service.predict(model_id, request.features)
        return PredictResponse(predictions=predictions)
    except ValueError as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{model_id}/retrain", response_model=TrainResponse)
async def retrain_model(model_id: str, request: RetrainRequest):
    """
    Retrain an existing model.
    
    Args:
        model_id: ID of the model to retrain
        request: Retraining request with dataset and optional new hyperparameters
        
    Returns:
        Training results
    """
    logger.info(f"Retraining request for model {model_id}")
    
    try:
        model = model_service.get_model(model_id)
        if not model:
            raise HTTPException(status_code=404, detail=f"Model {model_id} not found")
        
        # Get dataset path
        dataset_path = dvc_service.get_dataset_path(request.dataset_name)
        if not os.path.exists(dataset_path):
            raise HTTPException(status_code=404, detail=f"Dataset {request.dataset_name} not found")
        
        # Update hyperparameters if provided
        if request.hyperparameters:
            model.hyperparameters.update(request.hyperparameters)
        
        # Train model
        metrics = model_service.train_model(model_id, dataset_path)
        
        # Upload to ClearML
        model_path = os.path.join(settings.models_dir, f"{model_id}.pkl")
        if os.path.exists(model_path):
            clearml_service.upload_model(
                model_id,
                model_path,
                type(model).__name__,
                model.get_hyperparameters(),
                metrics
            )
        
        return TrainResponse(
            model_id=model_id,
            metrics=metrics,
            message="Model retrained successfully"
        )
    except ValueError as e:
        logger.error(f"Retraining error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during retraining: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """
    Delete a trained model.
    
    Args:
        model_id: ID of the model to delete
        
    Returns:
        Success message
    """
    logger.info(f"Delete request for model {model_id}")
    
    try:
        model_service.delete_model(model_id)
        return {"message": f"Model {model_id} deleted successfully"}
    except ValueError as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during deletion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/datasets", response_model=DatasetsListResponse)
async def list_datasets():
    """
    Get list of available datasets.
    
    Returns:
        List of dataset information
    """
    logger.info("Requested list of datasets")
    datasets = dvc_service.list_datasets()
    return DatasetsListResponse(datasets=datasets)


@router.post("/datasets/upload", response_model=UploadDatasetResponse)
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload a new dataset (CSV or JSON format).
    
    Args:
        file: Dataset file to upload
        
    Returns:
        Upload confirmation
    """
    logger.info(f"Upload request for dataset: {file.filename}")
    
    try:
        # Validate file extension
        if not file.filename.endswith(('.csv', '.json')):
            raise HTTPException(
                status_code=400,
                detail="Only CSV and JSON files are supported"
            )
        
        # Save file
        file_path = os.path.join(settings.datasets_dir, file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Add to DVC
        dvc_service.add_dataset(file_path, file.filename)
        
        logger.info(f"Dataset {file.filename} uploaded successfully")
        return UploadDatasetResponse(
            message="Dataset uploaded successfully",
            dataset_name=file.filename
        )
    except Exception as e:
        logger.error(f"Error uploading dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))




