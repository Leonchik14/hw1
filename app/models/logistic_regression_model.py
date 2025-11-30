"""Logistic Regression model implementation."""

from typing import Dict, Any, List
import numpy as np
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
from app.models.base_model import BaseModel
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LogisticRegressionModel(BaseModel):
    """Logistic Regression / Ridge Regression model."""
    
    def __init__(self, model_id: str, hyperparameters: Dict[str, Any]):
        """
        Initialize Logistic/Ridge Regression model.
        
        Args:
            model_id: Unique identifier for the model
            hyperparameters: Dictionary with keys:
                - C: Regularization strength (default: 1.0)
                - max_iter: Maximum iterations (default: 1000)
                - task_type: 'classification' or 'regression' (default: 'classification')
        """
        super().__init__(model_id, hyperparameters)
        self.task_type = hyperparameters.get('task_type', 'classification')
        self.C = hyperparameters.get('C', 1.0)
        self.max_iter = hyperparameters.get('max_iter', 1000)
        
        if self.task_type == 'classification':
            self.model = LogisticRegression(
                C=self.C,
                max_iter=self.max_iter,
                random_state=42
            )
        else:
            self.model = Ridge(
                alpha=1.0 / self.C,
                max_iter=self.max_iter,
                random_state=42
            )
        
        logger.info(f"Created LogisticRegression model {model_id} for {self.task_type}")
    
    def train(self, X, y) -> Dict[str, Any]:
        """
        Train the Logistic/Ridge Regression model.
        
        Args:
            X: Training features
            y: Training labels
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training LogisticRegression model {self.model_id}")
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
            'C': self.C,
            'max_iter': self.max_iter
        }




