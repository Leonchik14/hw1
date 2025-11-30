"""gRPC client for testing ML model service."""

import json
import grpc
from app.grpc_server import mlops_pb2, mlops_pb2_grpc


def test_grpc_service(server_address: str = "localhost:50051"):
    """
    Test the gRPC service.
    
    Args:
        server_address: Address of the gRPC server
    """
    print(f"Connecting to gRPC server at {server_address}...")
    
    with grpc.insecure_channel(server_address) as channel:
        stub = mlops_pb2_grpc.MLModelServiceStub(channel)
        
        # Test health check
        print("\n1. Testing Health Check...")
        try:
            response = stub.HealthCheck(mlops_pb2.HealthRequest())
            print(f"   Status: {response.status}")
            print(f"   Version: {response.version}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test get available models
        print("\n2. Testing Get Available Models...")
        try:
            response = stub.GetAvailableModels(mlops_pb2.Empty())
            print(f"   Available model classes: {list(response.model_classes)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test list datasets
        print("\n3. Testing List Datasets...")
        try:
            response = stub.ListDatasets(mlops_pb2.Empty())
            print(f"   Found {len(response.datasets)} datasets:")
            for dataset in response.datasets:
                print(f"     - {dataset.name} ({dataset.size} bytes)")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test list models
        print("\n4. Testing List Models...")
        try:
            response = stub.ListModels(mlops_pb2.Empty())
            print(f"   Found {len(response.models)} models:")
            for model in response.models:
                print(f"     - {model.model_id} (trained: {model.is_trained})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test train model (if dataset exists)
        print("\n5. Testing Train Model...")
        try:
            # Example hyperparameters for Random Forest
            hyperparameters = {
                "n_estimators": 10,
                "max_depth": 5,
                "task_type": "classification"
            }
            
            request = mlops_pb2.TrainRequest(
                model_class="random_forest",
                hyperparameters_json=json.dumps(hyperparameters),
                dataset_name="test_dataset.csv"  # Change to actual dataset name
            )
            
            response = stub.TrainModel(request)
            if response.model_id:
                print(f"   Model trained successfully!")
                print(f"   Model ID: {response.model_id}")
                print(f"   Metrics: {response.metrics_json}")
            else:
                print("   Training failed (check server logs)")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test predict (if model exists)
        print("\n6. Testing Predict...")
        try:
            # Example features
            features = [
                mlops_pb2.FeatureVector(values=[1.0, 2.0, 3.0, 4.0])
            ]
            
            request = mlops_pb2.PredictRequest(
                model_id="test_model_id",  # Change to actual model ID
                features=features
            )
            
            response = stub.Predict(request)
            print(f"   Predictions: {list(response.predictions)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n=== gRPC Client Test Complete ===")


if __name__ == "__main__":
    import sys
    server_address = sys.argv[1] if len(sys.argv) > 1 else "localhost:50051"
    test_grpc_service(server_address)




