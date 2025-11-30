#!/bin/bash
# Script to generate gRPC Python code from proto file

python -m grpc_tools.protoc \
    -I app/grpc_server \
    --python_out=app/grpc_server \
    --grpc_python_out=app/grpc_server \
    app/grpc_server/mlops.proto

echo "Proto files generated successfully!"




