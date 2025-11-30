FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Generate gRPC code
RUN python -m grpc_tools.protoc \
    -I app/grpc_server \
    --python_out=app/grpc_server \
    --grpc_python_out=app/grpc_server \
    app/grpc_server/mlops.proto

# Create directories
RUN mkdir -p /app/models /app/data

# Set environment variables for paths
ENV MODELS_DIR=/app/models
ENV DATASETS_DIR=/app/data

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

