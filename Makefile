.PHONY: play train fast-train visual-train test-train clean help venv check lint lint-fix lint-python lint-frontend lint-frontend-fix format isort flake8 pylint eslint eslint-fix stylelint stylelint-fix htmlhint

# Default target
help:
	@echo "Snake Game Agent Makefile"
	@echo "------------------------"
	@echo "Available targets:"
	@echo "  play          - Run the game in human mode"
	@echo "  agent         - Run the game with the AI agent playing"
	@echo "  train         - Train the AI agent"
	@echo "  fast-train    - Train the AI agent with optimized settings for Apple Silicon"
	@echo "  visual-train  - Train the AI agent with browser-based visualization"
	@echo "  test-train    - Quickly test the AI agent with minimal episodes"
	@echo "  venv          - Create a Python virtual environment and install all dependencies"
	@echo "  check         - Verify that your development environment is correctly set up"
	@echo "  lint          - Run all linting checks (Python and frontend)"
	@echo "  lint-fix      - Automatically fix linting issues where possible"
	@echo "  lint-python   - Run Python linting only (black, flake8, pylint, isort)"
	@echo "  lint-frontend - Run frontend linting only (ESLint, Stylelint, HTMLHint)"
	@echo "  lint-frontend-fix - Fix frontend linting issues only"
	@echo "  format        - Format Python code with Black"
	@echo "  isort         - Sort Python imports with isort"
	@echo "  flake8        - Run Flake8 Python linter"
	@echo "  pylint        - Run pylint"
	@echo "  eslint        - Run ESLint for JavaScript"
	@echo "  eslint-fix    - Run ESLint with auto-fix"
	@echo "  stylelint     - Run Stylelint for CSS"
	@echo "  stylelint-fix - Run Stylelint with auto-fix"
	@echo "  htmlhint      - Run HTMLHint for HTML"
	@echo "  clean         - Kill all server processes and clean temporary files"
	@echo "  help          - Display this help message"

# Run the game in human mode
play:
	./bin/run-docker-web.sh

# Run the game with the AI agent
agent:
	./bin/run-docker-web.sh --mode=agent --model=models/snake_dqn.h5

# Train the AI agent
train:
	./bin/run-docker-train.sh

# Fast train on Apple Silicon
fast-train:
	./bin/run-docker-fast-train.sh

# Visual training with browser visualization
visual-train:
	./bin/run-docker-visual-train.sh

# Test training with minimal episodes
test-train:
	./bin/run-docker-test-train.sh

# Setup development environment
venv:
	@echo "Setting up Python virtual environment..."
	python -m venv venv
	@echo "Activating virtual environment and installing Python dependencies..."
	@if [ "$(shell uname)" = "Windows_NT" ]; then \
		echo "Windows detected, use: venv\\Scripts\\activate"; \
		./venv/Scripts/python -m pip install --upgrade pip; \
		./venv/Scripts/pip install -r requirements.txt; \
	else \
		echo "Unix-like OS detected"; \
		./venv/bin/python -m pip install --upgrade pip; \
		./venv/bin/pip install -r requirements.txt; \
	fi
	@echo "Installing Node.js dependencies for frontend tools..."
	npm install
	@echo "Setting up pre-commit hooks..."
	npx husky install || echo "Husky installation failed. You may need to run 'npx husky install' manually."
	@echo ""
	@echo "Virtual environment setup complete!"
	@echo "To activate the virtual environment:"
	@echo "  Windows: venv\\Scripts\\activate"
	@echo "  Unix/macOS: source venv/bin/activate"
	@echo ""
	@echo "Run './bin/lint-all.sh' to ensure everything is properly formatted."

# Check development environment
check:
	./bin/check-dev-setup.sh

# Run all linting tools
lint:
	./bin/lint-all.sh

# Auto-fix linting issues where possible
lint-fix:
	./bin/lint-all.sh --fix

# Run Python linting only
lint-python:
	./bin/lint.sh

# Run frontend linting only
lint-frontend:
	./bin/lint-frontend.sh

# Fix frontend linting issues
lint-frontend-fix:
	./bin/lint-frontend.sh --fix

# Format Python code with Black
format:
	python -m black src

# Sort Python imports with isort
isort:
	python -m isort src

# Run Flake8 Python linter
flake8:
	python -m flake8 src

# Run pylint
pylint:
	python -m pylint src

# Run ESLint for JavaScript
eslint:
	npm run lint:js

# Run ESLint with auto-fix
eslint-fix:
	npm run lint:js:fix

# Run Stylelint for CSS
stylelint:
	npm run lint:css

# Run Stylelint with auto-fix
stylelint-fix:
	npm run lint:css:fix

# Run HTMLHint for HTML
htmlhint:
	npm run lint:html

# Clean up
clean:
	./bin/force-kill-snake-servers.sh
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} + 