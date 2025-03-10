.PHONY: play train fast-train clean help

# Default target
help:
	@echo "Snake Game Agent Makefile"
	@echo "------------------------"
	@echo "Available targets:"
	@echo "  play        - Run the game in human mode"
	@echo "  agent       - Run the game with the AI agent playing"
	@echo "  train       - Train the AI agent"
	@echo "  fast-train  - Train the AI agent with optimized settings for Apple Silicon"
	@echo "  clean       - Kill all server processes and remove temporary files"
	@echo "  help        - Display this help message"

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