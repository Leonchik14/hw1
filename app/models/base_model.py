"""Base class for ML models."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pickle
import os
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseModel(ABC):
    """Base class for all ML models."""
    
    def __init__(self, model_id: str, hyperparameters: Dict[str, Any]):
        """
        Initialize the model.
        
        Args:
            model_id: Unique identifier for the model
            hyperparameters: Dictionary of hyperparameters
        """
        self.model_id = model_id
        self.hyperparameters = hyperparameters
        self.model = None
        self.is_trained = False
        logger.info(f"Initialized model {model_id} with hyperparameters: {hyperparameters}")
    
    @abstractmethod
    def train(self, X, y) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X: Training features
            y: Training labels
            
        Returns:
            Dictionary with training metrics
        """
        pass
    
    @abstractmethod
    def predict(self, X) -> List[Any]:
        """
        Make predictions.
        
        Args:
            X: Features for prediction
            
        Returns:
            List of predictions
        """
        pass
    
    @abstractmethod
    def get_hyperparameters(self) -> Dict[str, Any]:
        """
        Get model hyperparameters.
        
        Returns:
            Dictionary of hyperparameters
        """
        return self.hyperparameters
    
    def save(self, path: str) -> None:
        """
        Save the model to disk.
        
        Args:
            path: Path to save the model
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'hyperparameters': self.hyperparameters,
                'model_id': self.model_id,
                'is_trained': self.is_trained
            }, f)
        logger.info(f"Model {self.model_id} saved to {path}")
    
    def load(self, path: str) -> None:
        """
        Load the model from disk.
        
        Args:
            path: Path to load the model from
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.hyperparameters = data['hyperparameters']
            self.model_id = data['model_id']
            self.is_trained = data['is_trained']
        logger.info(f"Model {self.model_id} loaded from {path}")




