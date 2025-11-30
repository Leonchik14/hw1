"""Service for working with DVC."""

import os
import subprocess
import json
from typing import List, Dict, Any
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class DVCService:
    """Service for managing datasets with DVC."""
    
    def __init__(self):
        """Initialize the DVC service."""
        self.datasets_dir = settings.datasets_dir
        os.makedirs(self.datasets_dir, exist_ok=True)
        logger.info(f"DVCService initialized with datasets_dir: {self.datasets_dir}")
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all datasets tracked by DVC.
        
        Returns:
            List of dataset information dictionaries
        """
        try:
            # Run dvc list to get tracked files
            result = subprocess.run(
                ['dvc', 'list', '.', '--dvc-only'],
                capture_output=True,
                text=True,
                cwd=self.datasets_dir
            )
            
            datasets = []
            if result.returncode == 0:
                files = result.stdout.strip().split('\n')
                for file in files:
                    if file:
                        file_path = os.path.join(self.datasets_dir, file)
                        if os.path.exists(file_path):
                            size = os.path.getsize(file_path)
                            datasets.append({
                                'name': file,
                                'path': file_path,
                                'size': size
                            })
            
            logger.info(f"Listed {len(datasets)} datasets")
            return datasets
        except Exception as e:
            logger.error(f"Error listing datasets: {e}")
            # Fallback: list files in datasets directory
            datasets = []
            for file in os.listdir(self.datasets_dir):
                if file.endswith(('.csv', '.json')):
                    file_path = os.path.join(self.datasets_dir, file)
                    datasets.append({
                        'name': file,
                        'path': file_path,
                        'size': os.path.getsize(file_path)
                    })
            return datasets
    
    def add_dataset(self, file_path: str, dataset_name: str) -> str:
        """
        Add a dataset to DVC tracking.
        
        Args:
            file_path: Path to the dataset file
            dataset_name: Name for the dataset
            
        Returns:
            Path to the tracked dataset
        """
        try:
            target_path = os.path.join(self.datasets_dir, dataset_name)
            
            # Copy file to datasets directory
            import shutil
            shutil.copy2(file_path, target_path)
            
            # Add to DVC
            result = subprocess.run(
                ['dvc', 'add', target_path],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(self.datasets_dir)
            )
            
            if result.returncode == 0:
                logger.info(f"Added dataset {dataset_name} to DVC")
                return target_path
            else:
                logger.warning(f"DVC add failed: {result.stderr}")
                return target_path
        except Exception as e:
            logger.error(f"Error adding dataset: {e}")
            raise
    
    def remove_dataset(self, dataset_name: str) -> None:
        """
        Remove a dataset from DVC tracking.
        
        Args:
            dataset_name: Name of the dataset to remove
        """
        try:
            dataset_path = os.path.join(self.datasets_dir, dataset_name)
            
            # Remove from DVC
            subprocess.run(
                ['dvc', 'remove', dataset_path],
                capture_output=True,
                text=True
            )
            
            # Remove file
            if os.path.exists(dataset_path):
                os.remove(dataset_path)
            
            logger.info(f"Removed dataset {dataset_name}")
        except Exception as e:
            logger.error(f"Error removing dataset: {e}")
            raise
    
    def get_dataset_path(self, dataset_name: str) -> str:
        """
        Get the path to a dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Path to the dataset file
        """
        return os.path.join(self.datasets_dir, dataset_name)




