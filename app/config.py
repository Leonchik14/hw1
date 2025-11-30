"""Configuration settings for the application."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    grpc_port: int = 50051
    
    # ClearML Settings
    clearml_api_access_key: Optional[str] = os.getenv("CLEARML_API_ACCESS_KEY")
    clearml_api_secret_key: Optional[str] = os.getenv("CLEARML_API_SECRET_KEY")
    clearml_web_host: str = os.getenv("CLEARML_WEB_HOST", "http://localhost:8080")
    clearml_api_host: str = os.getenv("CLEARML_API_HOST", "http://localhost:8008")
    
    # MinIO/S3 Settings
    minio_endpoint: str = os.getenv("MINIO_ENDPOINT", "localhost:9000")
    minio_access_key: str = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    minio_secret_key: str = os.getenv("MINIO_SECRET_KEY", "minioadmin")
    minio_bucket: str = os.getenv("MINIO_BUCKET", "mlops")
    minio_use_ssl: bool = False
    
    # Model Storage
    models_dir: str = os.getenv("MODELS_DIR", "models")
    datasets_dir: str = os.getenv("DATASETS_DIR", "app/data")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


settings = Settings()

