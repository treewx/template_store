# SaaS Template Generator Makefile
# Provides convenient commands for generating and managing SaaS templates

.PHONY: help setup generate-rent generate-subscription generate-project generate-custom clean test examples

# Default target
help:
	@echo "🚀 SaaS Template Generator"
	@echo "======================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make setup              - Install dependencies and setup environment"
	@echo "  make interactive        - Interactive template configuration"
	@echo "  make generate-rent      - Generate rent tracking SaaS template"
	@echo "  make generate-sub       - Generate subscription management SaaS"  
	@echo "  make generate-project   - Generate project management SaaS"
	@echo "  make generate-custom    - Generate with custom configuration"
	@echo "  make examples           - Generate all example templates"
	@echo "  make clean              - Clean up generated templates"
	@echo "  make test               - Test template generation"
	@echo ""
	@echo "Examples:"
	@echo "  make generate-rent OUTPUT_DIR=my-rent-app"
	@echo "  make generate-sub OUTPUT_DIR=subscription-tracker"
	@echo "  make generate-project OUTPUT_DIR=project-hub"

# Setup environment
setup:
	@echo "⚙️ Setting up SaaS Template Generator..."
	@python -m pip install --upgrade pip
	@pip install -r backend/requirements.txt
	@echo "✅ Setup complete!"

# Interactive setup
interactive:
	@echo "🛠️ Starting interactive template setup..."
	@python setup_template.py

# Generate specific template types
OUTPUT_DIR ?= generated-saas

generate-rent:
	@echo "🏠 Generating rent tracking SaaS template..."
	@python generate.py rent $(OUTPUT_DIR)
	@echo "✅ Rent tracking SaaS generated in $(OUTPUT_DIR)/"

generate-sub:
	@echo "📊 Generating subscription management SaaS template..."
	@python generate.py subscription $(OUTPUT_DIR) 
	@echo "✅ Subscription SaaS generated in $(OUTPUT_DIR)/"

generate-project:
	@echo "📋 Generating project management SaaS template..."
	@python generate.py project $(OUTPUT_DIR)
	@echo "✅ Project management SaaS generated in $(OUTPUT_DIR)/"

# Custom generation with config file
CONFIG_FILE ?= config.json
generate-custom:
	@echo "⚙️ Generating custom SaaS template..."
	@if [ ! -f $(CONFIG_FILE) ]; then \
		echo "❌ Configuration file $(CONFIG_FILE) not found."; \
		echo "Run 'make interactive' to create one."; \
		exit 1; \
	fi
	@python template_generator.py custom $(OUTPUT_DIR) --config $(CONFIG_FILE)
	@echo "✅ Custom SaaS generated in $(OUTPUT_DIR)/"

# Generate all examples
examples:
	@echo "📦 Generating all example templates..."
	@make generate-rent OUTPUT_DIR=examples/rent-tracker
	@make generate-sub OUTPUT_DIR=examples/subscription-manager
	@make generate-project OUTPUT_DIR=examples/project-hub
	@echo "✅ All examples generated in examples/ directory"

# Clean up generated files
clean:
	@echo "🧹 Cleaning up generated templates..."
	@rm -rf examples/
	@rm -rf generated-saas/
	@rm -rf *-config.json
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@echo "✅ Cleanup complete!"

# Test template generation
test:
	@echo "🧪 Testing template generation..."
	@echo "Testing rent tracker template..."
	@python generate.py rent test-rent-app
	@cd test-rent-app && python backend/database_init.py
	@echo "✅ Rent tracker test passed"
	@echo ""
	@echo "Testing subscription template..."
	@python generate.py subscription test-sub-app
	@cd test-sub-app && python backend/database_init.py
	@echo "✅ Subscription template test passed"
	@echo ""
	@echo "Testing project template..."
	@python generate.py project test-project-app
	@cd test-project-app && python backend/database_init.py
	@echo "✅ Project template test passed"
	@echo ""
	@echo "Cleaning up test files..."
	@rm -rf test-rent-app test-sub-app test-project-app
	@echo "✅ All tests passed!"

# Quick start for different SaaS types
rent-saas:
	@echo "🏠 Quick start: Rent Tracking SaaS"
	@echo "================================"
	@make generate-rent OUTPUT_DIR=rent-tracker-saas
	@echo "🚀 Next steps:"
	@echo "   cd rent-tracker-saas"
	@echo "   python -m venv venv"
	@echo "   source venv/bin/activate"
	@echo "   pip install -r backend/requirements.txt"
	@echo "   cp .env.template .env"
	@echo "   cd backend && python database_init.py"
	@echo "   python app.py"

subscription-saas:
	@echo "📊 Quick start: Subscription Management SaaS"
	@echo "==========================================="
	@make generate-sub OUTPUT_DIR=subscription-saas
	@echo "🚀 Next steps:"
	@echo "   cd subscription-saas"
	@echo "   python -m venv venv"  
	@echo "   source venv/bin/activate"
	@echo "   pip install -r backend/requirements.txt"
	@echo "   cp .env.template .env"
	@echo "   cd backend && python database_init.py"
	@echo "   python app.py"

project-saas:
	@echo "📋 Quick start: Project Management SaaS"
	@echo "======================================"
	@make generate-project OUTPUT_DIR=project-management-saas
	@echo "🚀 Next steps:"
	@echo "   cd project-management-saas"
	@echo "   python -m venv venv"
	@echo "   source venv/bin/activate"
	@echo "   pip install -r backend/requirements.txt"
	@echo "   cp .env.template .env"
	@echo "   cd backend && python database_init.py"
	@echo "   python app.py"

# Development helpers
lint:
	@echo "🔍 Linting code..."
	@python -m flake8 --max-line-length=100 --ignore=E501,W503 *.py

format:
	@echo "🎨 Formatting code..."
	@python -m black *.py

check-deps:
	@echo "📦 Checking dependencies..."
	@python -c "import template_config, template_generator; print('✅ All imports working')"

# Show template structure
show-structure:
	@echo "📁 Template Structure:"
	@echo "====================="
	@tree -I '__pycache__|venv|*.pyc' -a