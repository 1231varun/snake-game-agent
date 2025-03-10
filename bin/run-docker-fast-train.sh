#!/bin/bash
# Fast training script for Snake Game RL Agent
# Optimized for Apple Silicon (M1/M2/M3) processors

# Enable debug mode
set -x

# Default values optimized for faster training but still effective
EPISODES=100
MODEL=models/fast_model.h5
RENDER_FREQ=0
SAVE_FREQ=10
BATCH_SIZE=32
MAX_STEPS=1000   # Increased to allow more exploration per episode 
TIMEOUT=25       # Less aggressive timeout but still prevents infinite loops
CONTINUE=true    # Continue training from existing model by default

# Process command-line arguments
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
        --timeout=*)
            TIMEOUT="${1#*=}"
            shift
            ;;
        --fresh)
            CONTINUE=false
            shift
            ;;
        --continue)
            CONTINUE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--episodes=100] [--model=models/fast_model.h5] [--render-freq=0] [--save-freq=10] [--batch-size=32] [--max-steps=1000] [--timeout=25] [--fresh|--continue]"
            exit 1
            ;;
    esac
done

echo "Fast Training Snake Game RL Agent"
echo "-----------------------------------------------------"
echo "Episodes: $EPISODES (balanced for learning and speed)"
echo "Model: $MODEL"
echo "Render Frequency: $RENDER_FREQ"
echo "Save Frequency: $SAVE_FREQ"
echo "Batch Size: $BATCH_SIZE (optimized for performance)"
echo "Max Steps: $MAX_STEPS (increased to allow exploration)"
echo "Timeout Multiplier: $TIMEOUT (balanced to prevent infinite loops)"
echo "Continue Training: $CONTINUE (use --fresh to start with a new model)"

# Debug: Print current directory
echo "Current directory: $(pwd)"
echo "Script directory: $(dirname $0)"

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

# Check if we're running on Apple Silicon
IS_APPLE_SILICON=false
if [[ $(uname -m) == 'arm64' && $(uname -s) == 'Darwin' ]]; then
  IS_APPLE_SILICON=true
  echo "Detected Apple Silicon - enabling Metal performance optimizations"
fi

# First, check if Docker is running
if ! check_docker_running; then
  exit 1
fi

# Create directories for models and data
mkdir -p models
mkdir -p data

# Get absolute paths
ABSOLUTE_MODEL_PATH="$PWD/models"
ABSOLUTE_DATA_PATH="$PWD/data"
echo "Absolute model path: $ABSOLUTE_MODEL_PATH"
echo "Absolute data path: $ABSOLUTE_DATA_PATH"

# Debug: Show Docker Compose file
echo "Docker Compose file: $(dirname $0)/../config/docker-compose.yml"
ls -la $(dirname $0)/../config/

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

# Apple Silicon specific optimizations
if [[ "$IS_APPLE_SILICON" == true ]]; then
  # Enable Metal plugin for TensorFlow on Apple Silicon
  ENV_VARS="$ENV_VARS -e PYTORCH_ENABLE_MPS_FALLBACK=1"
  ENV_VARS="$ENV_VARS -e TF_METAL_DEVICE_FORCE_MEMORY_FORMAT=channel_last_then_first"
  ENV_VARS="$ENV_VARS -e PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0"
  
  # Lower precision for faster training
  ENV_VARS="$ENV_VARS -e TF_ENABLE_AUTO_MIXED_PRECISION=1"
  
  # Comment out problematic optimizations
  # ENV_VARS="$ENV_VARS -e TF_GPU_ALLOCATOR=cuda_malloc_async"
  # ENV_VARS="$ENV_VARS -e TF_GPU_THREAD_MODE=gpu_private"
fi

# Construct command with optimization flag
CMD="python -O src/main_train.py --episodes $EPISODES --model $MODEL --render-freq $RENDER_FREQ --save-freq $SAVE_FREQ --batch-size $BATCH_SIZE --max-steps $MAX_STEPS --timeout $TIMEOUT"

# Add continue/fresh flag to command
if [ "$CONTINUE" = true ]; then
    CMD="$CMD --continue"
else
    CMD="$CMD --fresh"
fi

# Debug: Print the full Docker command
echo "Full docker-compose command:"
echo "docker-compose -f $(dirname $0)/../config/docker-compose.yml run --rm $ENV_VARS -v \"$PWD/models:/app/models\" -v \"$PWD/data:/app/data\" snake-game bash -c \"$CMD\""

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