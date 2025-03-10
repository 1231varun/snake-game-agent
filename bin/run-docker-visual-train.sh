#!/bin/bash
set -e

# Default values for visual training
EPISODES=50
MODEL=models/visual_model.h5
RENDER_FREQ=1  # Render every episode
SAVE_FREQ=5
BATCH_SIZE=32
MAX_STEPS=250  # Balanced for visualization
TIMEOUT=40    # Higher timeout to show learning process
PORT=3000     # Web server port
CONTINUE=true # Continue training from existing model by default

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
        --port=*)
            PORT="${1#*=}"
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
            exit 1
            ;;
    esac
done

echo "Visual Training Snake Game RL Agent"
echo "-----------------------------------------------------"
echo "Episodes: $EPISODES (balanced for visualization)"
echo "Model: $MODEL"
echo "Render Frequency: $RENDER_FREQ (frequent updates for visualization)"
echo "Save Frequency: $SAVE_FREQ"
echo "Batch Size: $BATCH_SIZE (optimized for performance)"
echo "Max Steps: $MAX_STEPS (balanced for visualization)"
echo "Timeout Multiplier: $TIMEOUT (higher to show exploration)"
echo "Web Port: $PORT (view at http://localhost:$PORT)"
echo "Continue Training: $CONTINUE (use --fresh to start with a new model)"

# Check port and clear if necessary
check_and_clear_port() {
    local port=$1
    
    # Check if port is in use
    if lsof -i :$port -sTCP:LISTEN >/dev/null 2>&1; then
        echo "Port $port is in use. Attempting to clear..."
        
        # Get PID of process using the port
        local pid=$(lsof -i :$port -sTCP:LISTEN -t)
        
        # Kill the process
        if [ ! -z "$pid" ]; then
            echo "Killing process $pid using port $port"
            kill -9 $pid 2>/dev/null || true
            sleep 1
        fi
        
        # Check if port is still in use
        if lsof -i :$port -sTCP:LISTEN >/dev/null 2>&1; then
            echo "ERROR: Failed to clear port $port"
            return 1
        else
            echo "Port $port cleared successfully"
        fi
    else
        echo "Port $port is available"
    fi
    
    return 0
}

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

# Check and clear port
check_and_clear_port $PORT

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
ENV_VARS="$ENV_VARS -e SNAKE_GAME_WEB_PORT=$PORT"

# Add Apple Silicon specific optimizations
if [[ "$IS_APPLE_SILICON" == true ]]; then
    ENV_VARS="$ENV_VARS -e PYTORCH_ENABLE_MPS_FALLBACK=1"
    ENV_VARS="$ENV_VARS -e TF_METAL_DEVICE_FORCE_MEMORY_FORMAT=channel_last_then_first"
    ENV_VARS="$ENV_VARS -e PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0"
    ENV_VARS="$ENV_VARS -e TF_ENABLE_AUTO_MIXED_PRECISION=1"
fi

# Build command for visual training mode
CMD="python -O src/main_visual_train.py --episodes $EPISODES --model $MODEL --render-freq $RENDER_FREQ --save-freq $SAVE_FREQ --batch-size $BATCH_SIZE --max-steps $MAX_STEPS --timeout $TIMEOUT --port $PORT"

# Add continue/fresh flag to command
if [ "$CONTINUE" = true ]; then
    CMD="$CMD --continue"
else
    CMD="$CMD --fresh"
fi

echo "Running visual training..."
echo "Command: $CMD"
echo "Training visualization will be available at http://localhost:$PORT"

# Run the container with mounted volumes and port mapping
docker-compose -f "$(dirname "$0")/../config/docker-compose.yml" run --rm -p $PORT:$PORT $ENV_VARS \
    -v "$ABSOLUTE_MODEL_PATH:/app/models" \
    -v "$ABSOLUTE_DATA_PATH:/app/data" \
    snake-game bash -c "$CMD" || {
    echo "Error: Failed to run training container."
    echo "Check the logs above for specific error messages."
    exit 1
}

echo "Visual training completed"
echo "Model saved to: $MODEL"
echo "Training data saved to data directory" 