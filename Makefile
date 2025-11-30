.PHONY: help deploy undeploy build logs clean minikube-start minikube-stop

# Minikube configuration
MINIKUBE_DRIVER=docker
NAMESPACE=mlops

help:
	@echo "Available commands:"
	@echo "  make deploy          - Deploy all services to Minikube"
	@echo "  make undeploy        - Remove all services from Minikube"
	@echo "  make build           - Build Docker images"
	@echo "  make logs            - Show logs from services"
	@echo "  make clean           - Clean temporary files"
	@echo "  make minikube-start  - Start Minikube"
	@echo "  make minikube-stop   - Stop Minikube"

minikube-start:
	@echo "Starting Minikube..."
	minikube start --driver=$(MINIKUBE_DRIVER)
	minikube addons enable ingress
	minikube addons enable storage-provisioner

minikube-stop:
	@echo "Stopping Minikube..."
	minikube stop

deploy: minikube-start build
	@echo "Deploying to Minikube..."
	@# Create namespace
	kubectl create namespace $(NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	@# Deploy MinIO
	kubectl apply -f k8s/minio/ -n $(NAMESPACE)
	@# Wait for MinIO to be ready
	@echo "Waiting for MinIO to be ready..."
	kubectl wait --for=condition=ready pod -l app=minio -n $(NAMESPACE) --timeout=300s || true
	@# Deploy API service
	kubectl apply -f k8s/api/ -n $(NAMESPACE)
	@# Deploy Dashboard
	kubectl apply -f k8s/dashboard/ -n $(NAMESPACE)
	@# Wait for services
	@echo "Waiting for services to be ready..."
	kubectl wait --for=condition=ready pod -l app=mlops-api -n $(NAMESPACE) --timeout=300s || true
	kubectl wait --for=condition=ready pod -l app=mlops-dashboard -n $(NAMESPACE) --timeout=300s || true
	@echo "Deployment complete!"
	@echo "API URL: $$(minikube service mlops-api -n $(NAMESPACE) --url)"
	@echo "Dashboard URL: $$(minikube service mlops-dashboard -n $(NAMESPACE) --url)"

undeploy:
	@echo "Undeploying from Minikube..."
	kubectl delete -f k8s/ -n $(NAMESPACE) --ignore-not-found=true
	kubectl delete namespace $(NAMESPACE) --ignore-not-found=true
	@echo "Undeployment complete!"

build:
	@echo "Building Docker images..."
	docker build -t mlops-api:latest -f Dockerfile .
	docker build -t mlops-dashboard:latest -f Dockerfile.dashboard .
	@echo "Loading images into Minikube..."
	eval $$(minikube docker-env) && docker build -t mlops-api:latest -f Dockerfile .
	eval $$(minikube docker-env) && docker build -t mlops-dashboard:latest -f Dockerfile.dashboard .
	@echo "Images built and loaded successfully!"

proto:
	@echo "Generating gRPC code..."
	python -m grpc_tools.protoc -I app/grpc_server --python_out=app/grpc_server --grpc_python_out=app/grpc_server app/grpc_server/mlops.proto
	@echo "Proto files generated successfully!"

logs:
	@echo "Showing logs..."
	kubectl logs -f -l app=mlops-api -n $(NAMESPACE)
	kubectl logs -f -l app=mlops-dashboard -n $(NAMESPACE)

clean:
	@echo "Cleaning temporary files..."
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "Clean complete!"

