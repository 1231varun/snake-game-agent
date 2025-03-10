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

### Windows X Server Issues

If you're having trouble with the X server on Windows, see [Windows Setup](WINDOWS_SETUP.md) for detailed instructions.

### ALSA Sound Issues

You can safely ignore ALSA errors about sound devices during Docker execution:

```
ALSA lib confmisc.c:1334:(snd_func_refer) error evaluating name
ALSA lib conf.c:5180:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
```

These don't affect functionality. 