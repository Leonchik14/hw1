"""Service for managing ML models."""

import os
import uuid
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from app.models import MODEL_REGISTRY, BaseModel
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelService:
    """Service for managing ML models."""
    
    def __init__(self):
        """Initialize the model service."""
        self.models: Dict[str, BaseModel] = {}
        self.models_dir = settings.models_dir
        os.makedirs(self.models_dir, exist_ok=True)
        logger.info(f"ModelService initialized with models_dir: {self.models_dir}")
    
    def get_available_model_classes(self) -> List[str]:
        """
        Get list of available model classes.
        
        Returns:
            List of available model class names
        """
        classes = list(MODEL_REGISTRY.keys())
        logger.info(f"Available model classes: {classes}")
        return classes
    
    def create_model(
        self,
        model_class: str,
        hyperparameters: Dict[str, Any]
    ) -> str:
        """
        Create a new model instance.
        
        Args:
            model_class: Name of the model class
            hyperparameters: Model hyperparameters
            
        Returns:
            Model ID
        """
        if model_class not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model class: {model_class}")
        
        model_id = str(uuid.uuid4())
        model_cls = MODEL_REGISTRY[model_class]
        model = model_cls(model_id, hyperparameters)
        self.models[model_id] = model
        
        logger.info(f"Created model {model_id} of class {model_class}")
        return model_id
    
    def train_model(
        self,
        model_id: str,
        dataset_path: str
    ) -> Dict[str, Any]:
        """
        Train a model on a dataset.
        
        Args:
            model_id: ID of the model to train
            dataset_path: Path to the training dataset
            
        Returns:
            Training metrics
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        
        # Load dataset
        logger.info(f"Loading dataset from {dataset_path}")
        
        if dataset_path.endswith('.csv'):
            df = pd.read_csv(dataset_path)
        elif dataset_path.endswith('.json'):
            df = pd.read_json(dataset_path)
        else:
            raise ValueError(f"Unsupported file format. Only CSV and JSON are supported.")
        
        # Assume last column is target
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        
        # Train model
        metrics = model.train(X, y)
        
        # Save model
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        model.save(model_path)
        
        logger.info(f"Model {model_id} trained successfully. Metrics: {metrics}")
        return metrics
    
    def predict(
        self,
        model_id: str,
        features: List[List[float]]
    ) -> List[Any]:
        """
        Make predictions using a model.
        
        Args:
            model_id: ID of the model
            features: List of feature vectors
            
        Returns:
            List of predictions
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        model = self.models[model_id]
        X = np.array(features)
        predictions = model.predict(X)
        
        logger.info(f"Made predictions with model {model_id}")
        return predictions
    
    def get_model(self, model_id: str) -> Optional[BaseModel]:
        """
        Get a model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model instance or None
        """
        return self.models.get(model_id)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """
        List all trained models.
        
        Returns:
            List of model information dictionaries
        """
        models_info = []
        for model_id, model in self.models.items():
            models_info.append({
                'model_id': model_id,
                'is_trained': model.is_trained,
                'hyperparameters': model.get_hyperparameters()
            })
        
        logger.info(f"Listed {len(models_info)} models")
        return models_info
    
    def delete_model(self, model_id: str) -> None:
        """
        Delete a model.
        
        Args:
            model_id: ID of the model to delete
        """
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")
        
        # Remove from memory
        del self.models[model_id]
        
        # Remove from disk
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        if os.path.exists(model_path):
            os.remove(model_path)
        
        logger.info(f"Deleted model {model_id}")
    
    def load_model(self, model_id: str, model_class: str) -> None:
        """
        Load a model from disk.
        
        Args:
            model_id: Model ID
            model_class: Model class name
        """
        if model_class not in MODEL_REGISTRY:
            raise ValueError(f"Unknown model class: {model_class}")
        
        model_path = os.path.join(self.models_dir, f"{model_id}.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        model_cls = MODEL_REGISTRY[model_class]
        model = model_cls(model_id, {})
        model.load(model_path)
        self.models[model_id] = model
        
        logger.info(f"Loaded model {model_id} from disk")

