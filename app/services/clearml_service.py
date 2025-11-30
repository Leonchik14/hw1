"""Service for working with ClearML."""

import os
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

# Try to import ClearML, but don't fail if not available
try:
    from clearml import Task, Model, OutputModel
    CLEARML_AVAILABLE = True
except ImportError:
    CLEARML_AVAILABLE = False
    logger.warning("ClearML not available. Install with: pip install clearml")


class ClearMLService:
    """Service for managing experiments and models in ClearML."""
    
    def __init__(self):
        """Initialize the ClearML service."""
        self.initialized = False
        if CLEARML_AVAILABLE and settings.clearml_api_access_key:
            try:
                Task.set_credentials(
                    api_host=settings.clearml_api_host,
                    web_host=settings.clearml_web_host,
                    files_host=settings.clearml_web_host,
                    key=settings.clearml_api_access_key,
                    secret=settings.clearml_api_secret_key
                )
                self.initialized = True
                logger.info("ClearML service initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ClearML: {e}")
        else:
            logger.warning("ClearML not configured or not available")
    
    def create_experiment(
        self,
        model_id: str,
        model_class: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create a ClearML experiment for model training.
        
        Args:
            model_id: Model ID
            model_class: Model class name
            hyperparameters: Model hyperparameters
            metrics: Training metrics
            
        Returns:
            Task ID or None if ClearML is not available
        """
        if not self.initialized:
            logger.warning("ClearML not initialized, skipping experiment creation")
            return None
        
        try:
            task = Task.init(
                project_name="MLOps-Homework",
                task_name=f"train_{model_class}_{model_id}",
                task_type=Task.TaskTypes.training
            )
            
            # Log hyperparameters
            task.connect(hyperparameters)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                task.get_logger().report_scalar(
                    title="Training Metrics",
                    series=metric_name,
                    value=metric_value,
                    iteration=0
                )
            
            task.set_parameter("model_id", model_id)
            task.set_parameter("model_class", model_class)
            
            task_id = task.id
            logger.info(f"Created ClearML experiment {task_id} for model {model_id}")
            return task_id
        except Exception as e:
            logger.error(f"Error creating ClearML experiment: {e}")
            return None
    
    def upload_model(
        self,
        model_id: str,
        model_path: str,
        model_class: str,
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any]
    ) -> Optional[str]:
        """
        Upload a model to ClearML Model Registry.
        
        Args:
            model_id: Model ID
            model_path: Path to the model file
            model_class: Model class name
            hyperparameters: Model hyperparameters
            metrics: Training metrics
            
        Returns:
            Model ID in ClearML or None
        """
        if not self.initialized:
            logger.warning("ClearML not initialized, skipping model upload")
            return None
        
        try:
            # Create experiment first
            task_id = self.create_experiment(
                model_id, model_class, hyperparameters, metrics
            )
            
            # Create model
            model = Model(
                task=task_id,
                name=f"{model_class}_{model_id}",
                tags=[model_class, model_id]
            )
            
            # Upload model file
            model.update_weights(model_path)
            
            # Set metadata
            model.set_metadata("hyperparameters", hyperparameters)
            model.set_metadata("metrics", metrics)
            
            model_id_clearml = model.id
            logger.info(f"Uploaded model {model_id} to ClearML as {model_id_clearml}")
            return model_id_clearml
        except Exception as e:
            logger.error(f"Error uploading model to ClearML: {e}")
            return None
    
    def download_model(self, clearml_model_id: str, local_path: str) -> str:
        """
        Download a model from ClearML.
        
        Args:
            clearml_model_id: ClearML model ID
            local_path: Local path to save the model
            
        Returns:
            Path to downloaded model
        """
        if not self.initialized:
            raise RuntimeError("ClearML not initialized")
        
        try:
            model = Model(model_id=clearml_model_id)
            model_path = model.get_local_copy()
            
            # Copy to desired location
            import shutil
            shutil.copy2(model_path, local_path)
            
            logger.info(f"Downloaded model {clearml_model_id} to {local_path}")
            return local_path
        except Exception as e:
            logger.error(f"Error downloading model from ClearML: {e}")
            raise




