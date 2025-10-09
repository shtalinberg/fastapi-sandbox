.PHONY: help install install-dev lint format test test-cov clean docker-build docker-up docker-down migrate

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: ## Install production dependencies
	pip install -r requirements/base.pip

install-dev: ## Install development dependencies
	pip install -r requirements/local.pip
	pip install -r requirements/code-checks.pip

# Code quality
lint: ## Run linting (flake8, mypy)
	flake8 sc_backend/
	mypy sc_backend/

format: ## Format code (black, isort)
	black sc_backend/
	isort sc_backend/

format-check: ## Check code formatting
	black --check sc_backend/
	isort --check-only sc_backend/

# Testing
test: ## Run tests
	pytest sc_backend/tests/

test-cov: ## Run tests with coverage
	pytest sc_backend/tests/ --cov=sc_backend --cov-report=html --cov-report=term

# Database migrations
migrate: ## Run database migrations
	cd sc_backend/faproject && alembic upgrade head

migrate-create: ## Create new migration (usage: make migrate-create MESSAGE="migration description")
	cd sc_backend/faproject && alembic revision --autogenerate -m "$(MESSAGE)"

# Environment setup
env-setup: ## Copy .env.example to .env (for first setup)
	cp .env.example .env
	@echo "Created .env file. Please edit it with your configuration."

# Docker
docker-build: ## Build Docker image
	docker-compose -f docker/docker-compose.yml --env-file .env build

docker-up: ## Start services with Docker
	docker-compose -f docker/docker-compose.yml --env-file .env up -d

docker-down: ## Stop Docker services
	docker-compose -f docker/docker-compose.yml --env-file .env down

docker-logs: ## Show Docker logs
	docker-compose -f docker/docker-compose.yml --env-file .env logs -f

docker-restart: ## Restart all Docker services
	docker-compose -f docker/docker-compose.yml --env-file .env restart

docker-clean: ## Remove all containers, networks, and volumes
	docker-compose -f docker/docker-compose.yml --env-file .env down -v --remove-orphans
	docker system prune -f

# Production Docker
docker-prod-build: ## Build production Docker image
	docker-compose -f docker/docker-compose.prod.yml build

docker-prod-up: ## Start production services
	docker-compose -f docker/docker-compose.prod.yml up -d

docker-prod-down: ## Stop production services
	docker-compose -f docker/docker-compose.prod.yml down

# Development server
dev: ## Run development server
	cd sc_backend/faproject && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Celery monitoring (optional)
flower: ## Run Celery Flower monitoring (requires flower to be installed)
	cd sc_backend/faproject && celery -A core.celery_app flower --port=5555

# Cleanup
clean: ## Clean up cache files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage