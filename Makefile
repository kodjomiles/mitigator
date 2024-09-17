# Makefile for setting up and running the mitigator application

# Variables
VENV_NAME=venv
PYTHON=python3
PIP=pip
UVICORN=uvicorn
ENV_FILE=.env

# Default target: help
.DEFAULT_GOAL := help

#Activate
activate:
	@echo "Activating virtual environment..."
	source $(VENV_NAME)/bin/activate

# Help command to list all available commands
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Set up the virtual environment
venv: ## Create a Python virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_NAME)
	@echo "Virtual environment created."

# Install dependencies
install: venv ## Install Python dependencies
	@echo "Installing dependencies..."
	$(VENV_NAME)/bin/$(PIP) install -r requirements.txt
	@echo "Dependencies installed."

# Load environment variables
load-env: ## Load environment variables from .env file
	@echo "Loading environment variables..."
	if [ ! -f $(ENV_FILE) ]; then \
		echo ".env file not found! Please create a .env file with the necessary environment variables."; \
		exit 1; \
	fi
	@echo "Environment variables loaded."

# Run the FastAPI server
run: ## Run the FastAPI application
	@echo "Starting FastAPI server..."
	$(VENV_NAME)/bin/$(UVICORN) main:app --reload

# Clean virtual environment
clean: ## Remove virtual environment and cached files
	@echo "Cleaning up..."
	rm -rf $(VENV_NAME)
	@echo "Virtual environment removed."

# Run the server after setup
start: install load-env run ## Set up and run the FastAPI application
