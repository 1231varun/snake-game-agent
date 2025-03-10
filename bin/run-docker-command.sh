#!/bin/bash

# Run a command in the snake-game Docker container
set -e

# Build the Docker image if needed
docker-compose -f ./config/docker-compose.yml build snake-game

# Run the command
docker-compose -f ./config/docker-compose.yml run --rm snake-game "$@" 