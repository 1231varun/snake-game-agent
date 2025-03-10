#!/bin/bash
# Helper script to train the snake game agent in Docker

# Parse command line arguments
EPISODES=1000
MODEL="models/snake_dqn.h5"
RENDER_FREQ=0
SAVE_FREQ=100
BATCH_SIZE=64
MAX_STEPS=2000

# Process arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --episodes=*)
      EPISODES="${1#*=}"
      shift
      ;;
    --model=*)
      MODEL="${1#*=}"
      shift
      ;;
    --render-freq=*)
      RENDER_FREQ="${1#*=}"
      shift
      ;;
    --save-freq=*)
      SAVE_FREQ="${1#*=}"
      shift
      ;;
    --batch-size=*)
      BATCH_SIZE="${1#*=}"
      shift
      ;;
    --max-steps=*)
      MAX_STEPS="${1#*=}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--episodes=1000] [--model=models/snake_dqn.h5] [--render-freq=0] [--save-freq=100] [--batch-size=64] [--max-steps=2000]"
      exit 1
      ;;
  esac
done

echo "Training Snake Game RL Agent"
echo "-----------------------------------------------------"
echo "Episodes: $EPISODES"
echo "Model: $MODEL"
echo "Render Frequency: $RENDER_FREQ"
echo "Save Frequency: $SAVE_FREQ"
echo "Batch Size: $BATCH_SIZE"
echo "Max Steps: $MAX_STEPS"

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

# First, check if Docker is running
if ! check_docker_running; then
  exit 1
fi

# Create directories for models and data
mkdir -p models
mkdir -p data

# Build the image if needed
echo "Building Docker image..."
if ! docker-compose -f $(dirname $0)/../config/docker-compose.yml build snake-game; then
  echo "ERROR: Failed to build Docker image."
  echo "Check the Docker configuration or try rebuilding with 'docker-compose build --no-cache snake-game'"
  exit 1
fi

# Construct command
CMD="python src/main_train.py --episodes $EPISODES --model $MODEL --render-freq $RENDER_FREQ --save-freq $SAVE_FREQ --batch-size $BATCH_SIZE --max-steps $MAX_STEPS"

# Run the container for training
echo "Running Docker container for training..."
echo "Command: $CMD"
if ! docker-compose -f $(dirname $0)/../config/docker-compose.yml run --rm -v "$PWD/models:/app/models" -v "$PWD/data:/app/data" snake-game bash -c "$CMD"; then
  echo "Error running training container."
  echo "Check the logs above for specific error messages."
  exit 1
fi

echo "Training completed"
echo "Model saved to: $MODEL"
echo "Training data saved to data directory" 