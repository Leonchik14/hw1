# Примеры использования API

## REST API Примеры

### 1. Проверка здоровья сервиса

```bash
curl http://localhost:8000/api/v1/health
```

Ответ:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Получение списка доступных моделей

```bash
curl http://localhost:8000/api/v1/models/available
```

Ответ:
```json
{
  "model_classes": ["random_forest", "logistic_regression"]
}
```

### 3. Загрузка датасета

```bash
curl -X POST http://localhost:8000/api/v1/datasets/upload \
  -F "file=@data/example_dataset.csv"
```

Ответ:
```json
{
  "message": "Dataset uploaded successfully",
  "dataset_name": "example_dataset.csv"
}
```

### 4. Обучение модели

```bash
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Content-Type: application/json" \
  -d '{
    "model_class": "random_forest",
    "hyperparameters": {
      "n_estimators": 100,
      "max_depth": 10,
      "min_samples_split": 2,
      "task_type": "classification"
    },
    "dataset_name": "example_dataset.csv"
  }'
```

Ответ:
```json
{
  "model_id": "123e4567-e89b-12d3-a456-426614174000",
  "metrics": {
    "accuracy": 0.95
  },
  "message": "Model trained successfully"
}
```

### 5. Получение предсказаний

```bash
curl -X POST http://localhost:8000/api/v1/models/{model_id}/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[1.0, 2.0, 3.0, 4.0], [5.0, 6.0, 7.0, 8.0]]
  }'
```

Ответ:
```json
{
  "predictions": [0, 1]
}
```

### 6. Список обученных моделей

```bash
curl http://localhost:8000/api/v1/models
```

Ответ:
```json
{
  "models": [
    {
      "model_id": "123e4567-e89b-12d3-a456-426614174000",
      "is_trained": true,
      "hyperparameters": {
        "n_estimators": 100,
        "max_depth": 10,
        "task_type": "classification"
      }
    }
  ]
}
```

### 7. Переобучение модели

```bash
curl -X POST http://localhost:8000/api/v1/models/{model_id}/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_name": "example_dataset.csv",
    "hyperparameters": {
      "n_estimators": 200
    }
  }'
```

### 8. Удаление модели

```bash
curl -X DELETE http://localhost:8000/api/v1/models/{model_id}
```

## gRPC Примеры

### Python клиент

```python
import grpc
import json
from app.grpc_server import mlops_pb2, mlops_pb2_grpc

# Подключение
channel = grpc.insecure_channel('localhost:50051')
stub = mlops_pb2_grpc.MLModelServiceStub(channel)

# Health check
response = stub.HealthCheck(mlops_pb2.HealthRequest())
print(f"Status: {response.status}")

# Обучение модели
hyperparameters = {
    "n_estimators": 100,
    "max_depth": 10,
    "task_type": "classification"
}

request = mlops_pb2.TrainRequest(
    model_class="random_forest",
    hyperparameters_json=json.dumps(hyperparameters),
    dataset_name="example_dataset.csv"
)

response = stub.TrainModel(request)
print(f"Model ID: {response.model_id}")
print(f"Metrics: {response.metrics_json}")

# Предсказания
features = [
    mlops_pb2.FeatureVector(values=[1.0, 2.0, 3.0, 4.0])
]

request = mlops_pb2.PredictRequest(
    model_id=response.model_id,
    features=features
)

response = stub.Predict(request)
print(f"Predictions: {list(response.predictions)}")
```

## Python SDK примеры

```python
import requests

API_BASE = "http://localhost:8000/api/v1"

# Обучение модели
response = requests.post(
    f"{API_BASE}/models/train",
    json={
        "model_class": "random_forest",
        "hyperparameters": {
            "n_estimators": 100,
            "max_depth": 10,
            "task_type": "classification"
        },
        "dataset_name": "example_dataset.csv"
    }
)

model_id = response.json()["model_id"]

# Предсказания
response = requests.post(
    f"{API_BASE}/models/{model_id}/predict",
    json={
        "features": [[1.0, 2.0, 3.0, 4.0]]
    }
)

predictions = response.json()["predictions"]
print(predictions)
```




