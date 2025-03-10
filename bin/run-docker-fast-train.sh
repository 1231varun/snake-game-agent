#!/bin/bash
# Fast training script for Snake Game RL Agent
# Optimized for Apple Silicon (M1/M2/M3) processors

# Parse command line arguments with smaller defaults
EPISODES=10
MODEL="models/fast_model.h5"
RENDER_FREQ=0
SAVE_FREQ=5
BATCH_SIZE=32
MAX_STEPS=500

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
      echo "Usage: $0 [--episodes=10] [--model=models/fast_model.h5] [--render-freq=0] [--save-freq=5] [--batch-size=32] [--max-steps=500]"
      exit 1
      ;;
  esac
done

echo "Fast Training Snake Game RL Agent"
echo "-----------------------------------------------------"
echo "Episodes: $EPISODES (reduced for faster training)"
echo "Model: $MODEL"
echo "Render Frequency: $RENDER_FREQ"
echo "Save Frequency: $SAVE_FREQ"
echo "Batch Size: $BATCH_SIZE (optimized for performance)"
echo "Max Steps: $MAX_STEPS (reduced for faster episodes)"

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

# Set environment variables for TensorFlow performance optimization
ENV_VARS="-e TF_CPP_MIN_LOG_LEVEL=2"
ENV_VARS="$ENV_VARS -e TF_FORCE_GPU_ALLOW_GROWTH=true"
ENV_VARS="$ENV_VARS -e TF_ENABLE_ONEDNN_OPTS=1"

# For Apple Silicon M1/M2/M3, enable Metal plugin if available
if [[ $(uname -m) == 'arm64' ]]; then
  echo "Detected Apple Silicon - enabling Metal performance optimizations"
  ENV_VARS="$ENV_VARS -e PYTORCH_ENABLE_MPS_FALLBACK=1"
fi

# Construct command with optimization flag
CMD="python -O src/main_train.py --episodes $EPISODES --model $MODEL --render-freq $RENDER_FREQ --save-freq $SAVE_FREQ --batch-size $BATCH_SIZE --max-steps $MAX_STEPS"

# Run the container for training with optimized settings
echo "Running optimized Docker container for training..."
echo "Command: $CMD"
if ! docker-compose -f $(dirname $0)/../config/docker-compose.yml run --rm $ENV_VARS -v "$PWD/models:/app/models" -v "$PWD/data:/app/data" snake-game bash -c "$CMD"; then
  echo "Error running training container."
  echo "Check the logs above for specific error messages."
  exit 1
fi

echo "Fast training completed"
echo "Model saved to: $MODEL"
echo "Training data saved to data directory" 