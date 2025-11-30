#!/bin/bash
# Script to initialize DVC with MinIO backend

# Initialize DVC if not already initialized
if [ ! -d ".dvc" ]; then
    dvc init
    echo "DVC initialized"
fi

# Remove existing remote if it exists
dvc remote remove minio 2>/dev/null || true

# Configure DVC remote (MinIO)
dvc remote add -d minio s3://dvc-data \
    --endpoint-url http://localhost:9000 \
    --access-key-id minioadmin \
    --secret-access-key minioadmin

echo "DVC configured with MinIO backend"
echo "Remote storage: s3://dvc-data"
echo "Endpoint: http://localhost:9000"

