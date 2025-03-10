#!/bin/bash
# Helper script to run the snake game in Docker with a web interface
# This allows you to play the game in your browser!
# 
# The game will always run on port 3000 by default.
# If another process is using this port, it will be terminated to allow the game to run.

# Set the default designated port
DEFAULT_PORT=3000

# Parse command line arguments
MODE="human"
MODEL="models/snake_dqn.h5"
PORT="$DEFAULT_PORT"

# Process arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    --model=*)
      MODEL="${1#*=}"
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--mode=human|agent] [--model=path/to/model] [--port=3000]"
      exit 1
      ;;
  esac
done

echo "Running Snake Game with Web Interface"
echo "-----------------------------------------------------"
echo "Mode: $MODE"
echo "Port: $PORT"
if [ "$MODE" == "agent" ]; then
  echo "Model: $MODEL"
fi

# Verify the model file exists if in agent mode
if [ "$MODE" == "agent" ]; then
    if [ ! -f "$MODEL" ]; then
        echo "Error: Model file '$MODEL' does not exist!"
        echo "Please specify a valid model file with --model=PATH"
        exit 1
    else
        echo "Model file found: $MODEL"
        echo "Full path: $(realpath $MODEL)"
    fi
fi

# Check if Docker daemon is running
function check_docker_running() {
  if ! docker info &>/dev/null; then
    echo "ERROR: Docker daemon is not running."
    echo "Please start Docker Desktop or the Docker service before running this script."
    echo "If Docker is installed, you can start it with one of these commands:"
    echo "  - On macOS: open -a Docker"
    echo "  - On Linux: sudo systemctl start docker"
    echo "  - On Windows: Start Docker Desktop from the Start menu"
    return 1
  fi
  return 0
}

# Check if the port is already in use and kill the process if needed
function check_and_clear_port() {
  local port=$1
  
  # Check if the port is in use
  if lsof -i:"$port" &>/dev/null; then
    echo "Port $port is already in use. Terminating the process..."
    
    # Get the PID of the process using the port
    local pid=$(lsof -ti:"$port")
    
    if [ -n "$pid" ]; then
      echo "Killing process $pid that's using port $port"
      kill -9 "$pid"
      sleep 1
    fi
  else
    echo "Port $port is available"
  fi
}

# First, check if Docker is running
if ! check_docker_running; then
  exit 1
fi

# Then clear the designated port before running
check_and_clear_port "$PORT"

# Build the image if needed
echo "Building Docker image..."
if ! docker-compose -f $(dirname $0)/../config/docker-compose.yml build snake-game; then
  echo "ERROR: Failed to build Docker image."
  echo "Check the Docker configuration or try rebuilding with 'docker-compose build --no-cache snake-game'"
  exit 1
fi

# Create directories if they don't exist
mkdir -p models
mkdir -p data

# Construct command
CMD="python src/main_web.py --port $PORT --mode $MODE"
if [ "$MODE" == "agent" ] && [ ! -z "$MODEL" ]; then
  CMD="$CMD --model $MODEL"
fi

# Run the container with web server
echo "Running Docker container with web interface..."
echo "Command: $CMD"
if ! docker-compose -f $(dirname $0)/../config/docker-compose.yml run --rm \
    -p $PORT:$PORT \
    -v "$(pwd)/models:/app/models" \
    -v "$(pwd)/data:/app/data" \
    snake-game bash -c "$CMD"; then
  echo "Error running container. There was a problem with port $PORT."
  echo "You can try manually specifying a different port with --port=<number>"
  exit 1
else
  echo "Container execution completed"
  echo "To play the game, visit: http://localhost:$PORT in your browser"
fi 