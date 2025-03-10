# Snake Game Agent - Usage Guide

This document provides detailed instructions on how to use the Snake Game Agent.

## Setup

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- For Windows: [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or another X server (see [Windows Setup](WINDOWS_SETUP.md))

## Using the Makefile (Recommended)

The project includes a Makefile for common tasks:

### Playing the Game

```bash
make play
```

Then open your browser to http://localhost:3000 and use the arrow keys to control the snake.

### Watching the Agent Play

```bash
make agent
```

### Training the Agent

```bash
# Standard training
make train

# Fast training (optimized for Apple Silicon)
make fast-train
```

### Visual Training with Real-time Feedback

```bash
# Using the visual training script directly
./bin/run-docker-visual-train.sh
```

Then open your browser to http://localhost:3000 to access the training dashboard.

### Cleaning Up

```bash
make clean
```

This kills all related processes and removes temporary files.

## Using Scripts Directly (For Advanced Options)

For more control and custom options, you can call the scripts directly:

### Playing the Game (Human Mode)

```bash
# On Linux/macOS
./bin/run-docker-web.sh [options]

# On Windows
./bin/run-docker-windows.ps1 [python src/main_web.py [options]]
```

### Watching the Agent Play

```bash
# On Linux/macOS
./bin/run-docker-web.sh --mode=agent --model=models/snake_dqn.h5

# On Windows
./bin/run-docker-windows.ps1 python src/main_web.py --mode=agent --model=models/snake_dqn.h5
```

### Training the Agent

```bash
# On Linux/macOS
./bin/run-docker-train.sh --episodes=1000 --batch-size=64 --max-steps=2000

# On Windows
./bin/run-docker-windows.ps1 python src/main_train.py --episodes=1000 --batch-size=64 --max-steps=2000
```

### Fast Training (For Apple Silicon)

```bash
./bin/run-docker-fast-train.sh --episodes=100 --batch-size=32 --max-steps=500
```

### Visual Training

```bash
./bin/run-docker-visual-train.sh --episodes=50 --model=models/visual_model.h5
```

This script starts the training process with a real-time web-based dashboard.

## Visual Training Dashboard Features

The visual training dashboard provides an interactive interface to monitor and control the training process:

### Main Features

- **Game Visualization**: Watch the snake learn in real-time
- **Training Statistics**: Monitor metrics like score, episodes, and epsilon
- **Interactive Controls**:
  - Pause/Resume training
  - Adjust training speed (faster/slower)
  - Clear the console log
- **Real-time Charts**: Track scores and epsilon over episodes
- **Console Logging**: Detailed feedback on training events including:
  - Episode start/end notifications
  - Food collection events
  - Collision and timeout reports
  - Model saving checkpoints
- **Connection Status**: Clearly see if the dashboard is connected to the training process
- **Progress Bar**: Visual indication of training completion percentage

### Dashboard Sections

- **Control Panel**: Contains buttons to control the training process and status indicators
- **Game View**: Shows the current state of the snake game
- **Console**: Displays detailed logs about the training process
- **Training Progress**: Shows statistics and a progress bar
- **Training Metrics Chart**: Visual representation of scores and epsilon values

## Incremental Training

All training scripts support continuing from a previously saved model:

```bash
# Continue from the default model path
./bin/run-docker-fast-train.sh --continue

# Continue from a specific model
./bin/run-docker-visual-train.sh --continue --model=models/my_custom_model.h5

# Start fresh, ignoring any existing model
./bin/run-docker-train.sh --fresh
```

By default, training will continue from an existing model if one exists at the specified path.

## Utility Scripts

### Killing Game Processes

If you need to kill all processes related to the Snake Game:

```bash
# Interactive mode (asks for confirmation)
./bin/kill-snake-servers.sh

# Non-interactive mode (automatically kills all processes)
./bin/force-kill-snake-servers.sh
```

## Command Line Options

### Web Interface

```
--mode=human|agent   # Game mode (default: human)
--model=path         # Path to model file (for agent mode)
--port=number        # Port to run web server (default: 3000)
```

### Training

```
--episodes=number    # Number of episodes to train
--model=path         # Path to save the model
--render-freq=number # Frequency to render during training
--save-freq=number   # Frequency to save checkpoints
--batch-size=number  # Batch size for neural network training
--max-steps=number   # Maximum steps per episode
--continue           # Continue training from existing model (default)
--fresh              # Start with a fresh model
```

### Visual Training

```
--episodes=number    # Number of episodes to train (default: 50)
--model=path         # Path to save/load the model (default: models/visual_model.h5)
--port=number        # Web server port (default: 3000)
--timeout=number     # Timeout multiplier (default: 40)
--save-freq=number   # Checkpoint saving frequency (default: 5)
--continue           # Continue training from existing model (default)
--fresh              # Start with a fresh model
```

## Troubleshooting

### Docker Daemon Not Running

If you get an error about the Docker daemon not running:

```
ERROR: Docker daemon is not running.
Please start Docker Desktop or the Docker service before running this script.
```

Start Docker Desktop (or the Docker service) and try again.

### Port Already in Use

The game automatically runs on port 3000. If another process is already using this port, the script will automatically:

1. Detect the process using the port
2. Terminate that process
3. Start the game on port 3000

If needed, you can manually specify a different port:

```bash
# On Linux/macOS
./bin/run-docker-web.sh --port=8080

# On Windows
./bin/run-docker-windows.ps1 python src/main_web.py --port=8080
```

### Common UI Issues

If you see "Cannot set properties of null" errors in the console:
- The application has built-in error handling to prevent these issues
- The interface will automatically try to reconnect if the connection is lost
- Status indicators will show the current connection state

### Windows X Server Issues

If you're having trouble with the X server on Windows, see [Windows Setup](WINDOWS_SETUP.md) for detailed instructions.

### ALSA Sound Issues

You can safely ignore ALSA errors about sound devices during Docker execution:

```
ALSA lib confmisc.c:1334:(snd_func_refer) error evaluating name
ALSA lib conf.c:5180:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
```

These don't affect functionality. 