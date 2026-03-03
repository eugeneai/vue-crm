# Makefile for Web-IS-Vue CRM System
# ====================================

# Variables
PYTHON = python3
PIP = pip3
PSERVE = pserve
PYTEST = pytest
ALEMBIC = alembic
NPM = npm
DOCKER_COMPOSE = docker-compose

# Directories
BACKEND_DIR = backend
FRONTEND_DIR = frontend
DATABASE_DIR = database

# Configuration files
DEV_CONFIG = $(BACKEND_DIR)/development.ini
PROD_CONFIG = $(BACKEND_DIR)/production.ini

# Default target
.PHONY: help
help:
	@echo "Web-IS-Vue CRM System - Makefile Commands"
	@echo "=========================================="
	@echo ""
	@echo "Backend Development:"
	@echo "  make dev-server     - Start Pyramid development server with auto-reload"
	@echo "  make dev            - Alias for dev-server"
	@echo "  make simple-server  - Start server without auto-reload (Python 3.14 compatible)"
	@echo "  make test           - Run backend tests"
	@echo "  make test-verbose   - Run backend tests with verbose output"
	@echo "  make lint           - Run Python linting and formatting checks"
	@echo "  make format         - Format Python code"
	@echo "  make type-check     - Run Python type checking"
	@echo ""
	@echo "Database:"
	@echo "  make db-init        - Initialize database (create if not exists)"
	@echo "  make db-migrate     - Create new migration"
	@echo "  make db-upgrade     - Apply migrations"
	@echo "  make db-downgrade   - Rollback last migration"
	@echo ""
	@echo "Frontend Development:"
	@echo "  make frontend-dev   - Start Vue.js development server"
	@echo "  make frontend-build - Build frontend for production"
	@echo "  make frontend-lint  - Run frontend linting"
	@echo "  make frontend-test  - Run frontend tests"
	@echo ""
	@echo "Full Stack:"
	@echo "  make all            - Start both backend and frontend in development"
	@echo "  make docker-up      - Start all services with Docker Compose"
	@echo "  make docker-down    - Stop all Docker services"
	@echo ""
	@echo "Installation:"
	@echo "  make install        - Install all dependencies (backend + frontend)"
	@echo "  make install-backend - Install backend dependencies"
	@echo "  make install-frontend - Install frontend dependencies"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean          - Clean temporary files"
	@echo "  make reset-db       - Reset database (WARNING: deletes all data!)"

# Backend Development
.PHONY: dev-server dev
dev-server dev:
	@echo "Starting Pyramid development server on http://localhost:6543"
	@echo "Auto-reload enabled - server will restart on code changes"
	@echo "Press Ctrl+C to stop"
	@echo ""
	@echo "Note: If auto-reload fails due to Python 3.14 compatibility issues,"
	@echo "      use 'make simple-server' instead."
	@echo ""
	$(PYTHON) start_server.py

.PHONY: simple-server
simple-server:
	@echo "Starting Pyramid server on http://localhost:6543"
	@echo "Simple mode (no auto-reload) for Python 3.14 compatibility"
	@echo "Press Ctrl+C to stop"
	@echo ""
	$(PYTHON) start_simple.py

.PHONY: test
test:
	@echo "Running backend tests..."
	cd $(BACKEND_DIR) && $(PYTEST)

.PHONY: test-verbose
test-verbose:
	@echo "Running backend tests with verbose output..."
	cd $(BACKEND_DIR) && $(PYTEST) -v

.PHONY: lint
lint:
	@echo "Running Python linting checks..."
	@echo "Checking code formatting with black..."
	black $(BACKEND_DIR) --check
	@echo "Checking import sorting with isort..."
	isort $(BACKEND_DIR) --check-only
	@echo "Checking code style with flake8..."
	flake8 $(BACKEND_DIR)

.PHONY: format
format:
	@echo "Formatting Python code..."
	black $(BACKEND_DIR)
	isort $(BACKEND_DIR)

.PHONY: type-check
type-check:
	@echo "Running Python type checking..."
	mypy $(BACKEND_DIR)

# Database Operations
.PHONY: db-init
db-init:
	@echo "Initializing database..."
	@mkdir -p $(DATABASE_DIR)
	@if [ ! -f "$(DATABASE_DIR)/contacts.db" ]; then \
		echo "Creating database file..."; \
		touch "$(DATABASE_DIR)/contacts.db"; \
		echo "Database created at $(DATABASE_DIR)/contacts.db"; \
	else \
		echo "Database already exists at $(DATABASE_DIR)/contacts.db"; \
	fi

.PHONY: db-migrate
db-migrate:
	@echo "Creating new database migration..."
	@read -p "Enter migration description: " desc; \
	$(ALEMBIC) revision --autogenerate -m "$$desc"

.PHONY: db-upgrade
db-upgrade:
	@echo "Applying database migrations..."
	$(ALEMBIC) upgrade head

.PHONY: db-downgrade
db-downgrade:
	@echo "Rolling back last migration..."
	$(ALEMBIC) downgrade -1

# Frontend Development
.PHONY: frontend-dev
frontend-dev:
	@echo "Starting Vue.js development server..."
	@echo "Server will be available at http://localhost:5173"
	@echo "Press Ctrl+C to stop"
	@echo ""
	cd $(FRONTEND_DIR) && $(NPM) run dev

.PHONY: frontend-build
frontend-build:
	@echo "Building frontend for production..."
	cd $(FRONTEND_DIR) && $(NPM) run build

.PHONY: frontend-lint
frontend-lint:
	@echo "Running frontend linting..."
	cd $(FRONTEND_DIR) && $(NPM) run lint

.PHONY: frontend-test
frontend-test:
	@echo "Running frontend tests..."
	cd $(FRONTEND_DIR) && $(NPM) test

# Full Stack Development
.PHONY: all
all:
	@echo "Starting full stack development..."
	@echo "Backend: http://localhost:6543"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@echo "Use separate terminals for:"
	@echo "  make dev-server    - for backend"
	@echo "  make frontend-dev  - for frontend"
	@echo ""
	@echo "Or use Docker Compose: make docker-up"

.PHONY: docker-up
docker-up:
	@echo "Starting all services with Docker Compose..."
	$(DOCKER_COMPOSE) up -d
	@echo ""
	@echo "Services started:"
	@echo "  Backend API: http://localhost:6543"
	@echo "  Frontend:    http://localhost:5173"
	@echo "  Database:    localhost:5432"
	@echo ""
	@echo "View logs: docker-compose logs -f"
	@echo "Stop services: make docker-down"

.PHONY: docker-down
docker-down:
	@echo "Stopping Docker services..."
	$(DOCKER_COMPOSE) down

# Installation
.PHONY: install
install: install-backend install-frontend
	@echo "All dependencies installed successfully!"

.PHONY: install-backend
install-backend:
	@echo "Installing backend dependencies..."
	$(PIP) install -r $(BACKEND_DIR)/requirements.txt
	@echo "Backend dependencies installed."

.PHONY: install-frontend
install-frontend:
	@echo "Installing frontend dependencies..."
	cd $(FRONTEND_DIR) && $(NPM) install
	@echo "Frontend dependencies installed."

# Utilities
.PHONY: clean
clean:
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete."

.PHONY: reset-db
reset-db:
	@echo "WARNING: This will delete all database data!"
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		echo "Resetting database..."; \
		rm -f $(DATABASE_DIR)/contacts.db; \
		make db-init; \
		echo "Database reset complete."; \
	else \
		echo "Database reset cancelled."; \
	fi

# CLI Client (from crm.py)
.PHONY: cli
cli:
	@echo "Running CRM CLI client..."
	@echo "Usage: python crm.py [command]"
	@echo ""
	@echo "Available commands:"
	@echo "  python crm.py contacts list"
	@echo "  python crm.py contacts get <id>"
	@echo "  python crm.py contacts create"
	@echo "  python crm.py contacts update <id>"
	@echo "  python crm.py contacts delete <id>"
	@echo ""
	@echo "For more details, see CLI_GUIDE.md"
	@echo ""
	@if [ -f "crm.py" ]; then \
		python crm.py --help; \
	else \
		echo "Error: crm.py not found"; \
	fi

.PHONY: cli-test
cli-test:
	@echo "Running CLI client tests..."
	python test_cli.py

# Default target
.DEFAULT_GOAL := help