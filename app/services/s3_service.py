"""Service for working with S3/MinIO."""

import boto3
from botocore.client import Config
from typing import Optional
from app.config import settings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class S3Service:
    """Service for managing files in S3/MinIO."""
    
    def __init__(self):
        """Initialize the S3 service."""
        self.s3_client = None
        self.bucket_name = settings.minio_bucket
        
        try:
            self.s3_client = boto3.client(
                's3',
                endpoint_url=f"http://{settings.minio_endpoint}",
                aws_access_key_id=settings.minio_access_key,
                aws_secret_access_key=settings.minio_secret_key,
                config=Config(signature_version='s3v4'),
                use_ssl=settings.minio_use_ssl
            )
            
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
            except:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created bucket {self.bucket_name}")
            
            logger.info(f"S3Service initialized with bucket {self.bucket_name}")
        except Exception as e:
            logger.warning(f"Failed to initialize S3 service: {e}")
    
    def upload_file(self, local_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3.
        
        Args:
            local_path: Local file path
            s3_key: S3 object key
            
        Returns:
            True if successful
        """
        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return False
        
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
            logger.info(f"Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
            return True
        except Exception as e:
            logger.error(f"Error uploading file to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 object key
            local_path: Local file path
            
        Returns:
            True if successful
        """
        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return False
        
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
            logger.info(f"Downloaded s3://{self.bucket_name}/{s3_key} to {local_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file from S3: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> list:
        """
        List files in S3 bucket.
        
        Args:
            prefix: Prefix to filter files
            
        Returns:
            List of file keys
        """
        if not self.s3_client:
            logger.warning("S3 client not initialized")
            return []
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
        except Exception as e:
            logger.error(f"Error listing files in S3: {e}")
            return []




