"""ML model implementations."""

from app.models.base_model import BaseModel
from app.models.random_forest_model import RandomForestModel
from app.models.logistic_regression_model import LogisticRegressionModel

__all__ = [
    'BaseModel',
    'RandomForestModel',
    'LogisticRegressionModel'
]

# Model registry
MODEL_REGISTRY = {
    'random_forest': RandomForestModel,
    'logistic_regression': LogisticRegressionModel
}




