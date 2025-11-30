"""Pydantic schemas for API requests and responses."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"


class ModelClassResponse(BaseModel):
    """Response with available model classes."""
    model_classes: List[str]


class TrainRequest(BaseModel):
    """Request for training a model."""
    model_class: str = Field(..., description="Model class name")
    hyperparameters: Dict[str, Any] = Field(..., description="Model hyperparameters")
    dataset_name: str = Field(..., description="Name of the dataset to use")


class TrainResponse(BaseModel):
    """Response after training."""
    model_id: str
    metrics: Dict[str, float]
    message: str


class PredictRequest(BaseModel):
    """Request for prediction."""
    features: List[List[float]] = Field(..., description="List of feature vectors")


class PredictResponse(BaseModel):
    """Response with predictions."""
    predictions: List[Any]


class RetrainRequest(BaseModel):
    """Request for retraining a model."""
    dataset_name: str = Field(..., description="Name of the dataset to use")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="New hyperparameters (optional)")


class ModelInfo(BaseModel):
    """Model information."""
    model_id: str
    is_trained: bool
    hyperparameters: Dict[str, Any]


class ModelsListResponse(BaseModel):
    """Response with list of models."""
    models: List[ModelInfo]


class DatasetInfo(BaseModel):
    """Dataset information."""
    name: str
    path: str
    size: int


class DatasetsListResponse(BaseModel):
    """Response with list of datasets."""
    datasets: List[DatasetInfo]


class UploadDatasetResponse(BaseModel):
    """Response after uploading dataset."""
    message: str
    dataset_name: str




