"""Random Forest model implementation."""

from typing import Dict, Any, List
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from app.models.base_model import BaseModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class RandomForestModel(BaseModel):
    """Random Forest model for classification and regression."""
    
    def __init__(self, model_id: str, hyperparameters: Dict[str, Any]):
        """
        Initialize Random Forest model.
        
        Args:
            model_id: Unique identifier for the model
            hyperparameters: Dictionary with keys:
                - n_estimators: Number of trees (default: 100)
                - max_depth: Maximum depth (default: None)
                - min_samples_split: Minimum samples to split (default: 2)
                - task_type: 'classification' or 'regression' (default: 'classification')
        """
        super().__init__(model_id, hyperparameters)
        self.task_type = hyperparameters.get('task_type', 'classification')
        self.n_estimators = hyperparameters.get('n_estimators', 100)
        self.max_depth = hyperparameters.get('max_depth', None)
        self.min_samples_split = hyperparameters.get('min_samples_split', 2)
        
        if self.task_type == 'classification':
            self.model = RandomForestClassifier(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=42
            )
        else:
            self.model = RandomForestRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                random_state=42
            )
        
        logger.info(f"Created RandomForest model {model_id} for {self.task_type}")
    
    def train(self, X, y) -> Dict[str, Any]:
        """
        Train the Random Forest model.
        
        Args:
            X: Training features
            y: Training labels
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training RandomForest model {self.model_id}")
        self.model.fit(X, y)
        self.is_trained = True
        
        # Calculate metrics
        y_pred = self.model.predict(X)
        if self.task_type == 'classification':
            accuracy = accuracy_score(y, y_pred)
            metrics = {'accuracy': float(accuracy)}
        else:
            mse = mean_squared_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            metrics = {'mse': float(mse), 'r2_score': float(r2)}
        
        logger.info(f"Model {self.model_id} trained. Metrics: {metrics}")
        return metrics
    
    def predict(self, X) -> List[Any]:
        """
        Make predictions.
        
        Args:
            X: Features for prediction
            
        Returns:
            List of predictions
        """
        if not self.is_trained:
            raise ValueError(f"Model {self.model_id} is not trained yet")
        
        predictions = self.model.predict(X)
        logger.info(f"Made {len(predictions)} predictions with model {self.model_id}")
        return predictions.tolist()
    
    def get_hyperparameters(self) -> Dict[str, Any]:
        """Get model hyperparameters."""
        return {
            'task_type': self.task_type,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'min_samples_split': self.min_samples_split
        }




