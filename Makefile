.PHONY: help build up down logs test clean

help:
	@echo "Available commands:"
	@echo "  make build         - Build all Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make test          - Run all tests"
	@echo "  make test-user     - Run user service tests"
	@echo "  make test-analytics - Run analytics service tests"
	@echo "  make clean         - Remove all containers and volumes"
	@echo "  make k8s-deploy    - Deploy to Kubernetes"
	@echo "  make k8s-delete    - Delete Kubernetes deployment"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "Frontend: http://localhost:3000"
	@echo "User Service: http://localhost:8000"
	@echo "Analytics Service: http://localhost:8001"
	@echo "Grafana: http://localhost:3001"
	@echo "Prometheus: http://localhost:9090"

down:
	docker-compose down

logs:
	docker-compose logs -f

test: test-user test-analytics

test-user:
	cd user-service && pytest -v

test-analytics:
	cd analytics-service && pytest -v

clean:
	docker-compose down -v
	docker system prune -f

k8s-deploy:
	kubectl apply -f kubernetes/namespace.yaml
	kubectl apply -k kubernetes/

k8s-delete:
	kubectl delete -k kubernetes/
	kubectl delete namespace microservices-analytics
