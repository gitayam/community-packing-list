# Makefile for Community Packing List
# Simplifies Docker and development commands

.PHONY: help
help: ## Show this help message
	@echo "Community Packing List - Development Commands"
	@echo "============================================="
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development Commands
.PHONY: dev
dev: ## Start development environment with Docker
	docker-compose -f docker-compose.local.yml up

.PHONY: dev-build
dev-build: ## Build and start development environment
	docker-compose -f docker-compose.local.yml up --build

.PHONY: dev-down
dev-down: ## Stop development environment
	docker-compose -f docker-compose.local.yml down

.PHONY: dev-logs
dev-logs: ## Show development logs
	docker-compose -f docker-compose.local.yml logs -f

.PHONY: dev-shell
dev-shell: ## Open Django shell in development container
	docker-compose -f docker-compose.local.yml exec web python manage.py shell

.PHONY: dev-bash
dev-bash: ## Open bash shell in development container
	docker-compose -f docker-compose.local.yml exec web bash

# Production Commands
.PHONY: prod
prod: ## Start production environment with Docker
	docker-compose -f docker-compose.prod.yml up -d

.PHONY: prod-build
prod-build: ## Build and start production environment
	docker-compose -f docker-compose.prod.yml up -d --build

.PHONY: prod-down
prod-down: ## Stop production environment
	docker-compose -f docker-compose.prod.yml down

.PHONY: prod-logs
prod-logs: ## Show production logs
	docker-compose -f docker-compose.prod.yml logs -f

.PHONY: prod-restart
prod-restart: ## Restart production services
	docker-compose -f docker-compose.prod.yml restart

# Database Commands
.PHONY: migrate
migrate: ## Run Django migrations
	docker-compose -f docker-compose.local.yml exec web python manage.py migrate

.PHONY: makemigrations
makemigrations: ## Create Django migrations
	docker-compose -f docker-compose.local.yml exec web python manage.py makemigrations

.PHONY: createsuperuser
createsuperuser: ## Create Django superuser
	docker-compose -f docker-compose.local.yml exec web python manage.py createsuperuser

.PHONY: db-shell
db-shell: ## Open PostgreSQL shell
	docker-compose -f docker-compose.local.yml exec db psql -U packinglist_user -d packinglist_dev

.PHONY: db-backup
db-backup: ## Backup database to file
	docker-compose -f docker-compose.local.yml exec db pg_dump -U packinglist_user packinglist_dev > backup_$$(date +%Y%m%d_%H%M%S).sql

.PHONY: db-restore
db-restore: ## Restore database from backup (usage: make db-restore FILE=backup.sql)
	docker-compose -f docker-compose.local.yml exec -T db psql -U packinglist_user packinglist_dev < $(FILE)

# Testing Commands
.PHONY: test
test: ## Run Django tests
	docker-compose -f docker-compose.local.yml exec web python manage.py test

.PHONY: test-coverage
test-coverage: ## Run tests with coverage
	docker-compose -f docker-compose.local.yml exec web coverage run --source='.' manage.py test
	docker-compose -f docker-compose.local.yml exec web coverage report

.PHONY: test-js
test-js: ## Run JavaScript tests
	npm test

.PHONY: lint
lint: ## Run linters
	docker-compose -f docker-compose.local.yml exec web flake8 .
	npm run lint

# Static Files Commands
.PHONY: collectstatic
collectstatic: ## Collect static files
	docker-compose -f docker-compose.local.yml exec web python manage.py collectstatic --noinput

.PHONY: build-js
build-js: ## Build JavaScript files
	npm run build

.PHONY: build-css
build-css: ## Build CSS files
	npm run css:build

.PHONY: watch-js
watch-js: ## Watch and rebuild JavaScript files
	npm run dev

.PHONY: watch-css
watch-css: ## Watch and rebuild CSS files
	npm run css:dev

# Utility Commands
.PHONY: clean
clean: ## Clean up generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf staticfiles/
	rm -rf .coverage
	rm -rf htmlcov/
	npm run clean

.PHONY: reset
reset: dev-down ## Reset development environment (removes volumes)
	docker-compose -f docker-compose.local.yml down -v
	docker volume prune -f

.PHONY: install
install: ## Install all dependencies
	pip install -r requirements.txt
	npm install

.PHONY: install-dev
install-dev: ## Install development dependencies
	pip install -r requirements.txt -r requirements-dev.txt
	npm install

.PHONY: format
format: ## Format code
	black .
	isort .
	npm run format

.PHONY: security-check
security-check: ## Run security checks
	pip-audit
	npm audit
	docker-compose -f docker-compose.local.yml exec web python manage.py check --deploy

# Docker Commands
.PHONY: docker-prune
docker-prune: ## Clean up Docker resources
	docker system prune -af --volumes

.PHONY: docker-stats
docker-stats: ## Show Docker container stats
	docker stats

# Quick Start Commands
.PHONY: setup
setup: ## Initial project setup
	cp .env.example .env.local
	cp .env.example .env
	npm install
	@echo "Setup complete! Edit .env.local and .env files, then run 'make dev'"

.PHONY: quick-start
quick-start: setup dev-build migrate createsuperuser ## Quick start for new developers
	@echo "Development environment is ready!"
	@echo "Access the application at http://localhost:8000"
	@echo "Access the admin at http://localhost:8000/admin"
	@echo "Access Mailhog at http://localhost:8025"

# Default target
.DEFAULT_GOAL := help