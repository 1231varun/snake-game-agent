#!/bin/bash
set -e

# Ultra-fast testing values for rapid iteration
EPISODES=5
MODEL=models/test_model.h5
RENDER_FREQ=0
SAVE_FREQ=5
BATCH_SIZE=32
MAX_STEPS=100    # Shorter episodes for faster testing
TIMEOUT=50       # Higher timeout to allow exploration during testing

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
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "Testing Snake Game RL Agent - Super Fast Mode"
echo "-----------------------------------------------------"
echo "Episodes: $EPISODES (minimal for fast testing)"
echo "Model: $MODEL"
echo "Render Frequency: $RENDER_FREQ"
echo "Save Frequency: $SAVE_FREQ"
echo "Batch Size: $BATCH_SIZE (optimized for performance)"
echo "Max Steps: $MAX_STEPS (limited for fast testing)"
echo "Timeout Multiplier: $TIMEOUT (high to prevent timeouts during testing)"

# Check if Docker is running
check_docker_running() {
    docker info >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "Error: Docker is not running. Please start Docker and try again."
        echo "  - For macOS: Open Docker Desktop application"
        echo "  - For Linux: Run 'sudo systemctl start docker'"
        echo "  - For Windows: Start Docker Desktop from the system tray"
        exit 1
    fi
    return 0
}

# Check Docker
check_docker_running

# Detect Apple Silicon for optimizations
IS_APPLE_SILICON=false
if [[ $(uname -m) == "arm64" && $(uname -s) == "Darwin" ]]; then
    IS_APPLE_SILICON=true
    echo "Detected Apple Silicon - enabling Metal performance optimizations"
fi

# Create directories for models and data
mkdir -p models
mkdir -p data

ABSOLUTE_MODEL_PATH="$(pwd)/models"
ABSOLUTE_DATA_PATH="$(pwd)/data"

echo "Building Docker image..."
docker-compose -f "$(dirname "$0")/../config/docker-compose.yml" build snake-game || {
    echo "Error: Failed to build Docker image."
    exit 1
}

# Set environment variables for TensorFlow optimization
ENV_VARS="-e TF_CPP_MIN_LOG_LEVEL=2"
ENV_VARS="$ENV_VARS -e TF_FORCE_GPU_ALLOW_GROWTH=true"
ENV_VARS="$ENV_VARS -e TF_ENABLE_ONEDNN_OPTS=1"

# Add Apple Silicon specific optimizations
if [[ "$IS_APPLE_SILICON" == true ]]; then
    ENV_VARS="$ENV_VARS -e PYTORCH_ENABLE_MPS_FALLBACK=1"
    ENV_VARS="$ENV_VARS -e TF_METAL_DEVICE_FORCE_MEMORY_FORMAT=channel_last_then_first"
    ENV_VARS="$ENV_VARS -e PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0"
    ENV_VARS="$ENV_VARS -e TF_ENABLE_AUTO_MIXED_PRECISION=1"
fi

# Build command
CMD="python -O src/main_train.py --episodes $EPISODES --model $MODEL --render-freq $RENDER_FREQ --save-freq $SAVE_FREQ --batch-size $BATCH_SIZE --max-steps $MAX_STEPS --timeout $TIMEOUT"

echo "Running test training..."
echo "Command: $CMD"

# Run the container with mounted volumes
docker-compose -f "$(dirname "$0")/../config/docker-compose.yml" run --rm $ENV_VARS \
    -v "$ABSOLUTE_MODEL_PATH:/app/models" \
    -v "$ABSOLUTE_DATA_PATH:/app/data" \
    snake-game bash -c "$CMD" || {
    echo "Error: Failed to run training container."
    echo "Check the logs above for specific error messages."
    exit 1
}

echo "Test training completed"
echo "Model saved to: $MODEL"
echo "Training data saved to data directory" 