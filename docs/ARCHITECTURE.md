# Snake Game Agent - Architecture

This document describes the architecture of the Snake Game Agent project.

## Project Structure

```
snake-game-agent/
├── README.md                # Project overview
├── requirements.txt         # Python dependencies
├── Makefile                 # Convenient commands
├── bin/                     # Executable scripts
│   ├── kill-snake-servers.sh        # Utility to kill server processes
│   ├── force-kill-snake-servers.sh  # Force kill server processes
│   ├── run-docker-web.sh            # Run game in web mode
│   ├── run-docker-train.sh          # Train the agent
│   ├── run-docker-fast-train.sh     # Fast training for Apple Silicon
│   ├── run-docker-visual-train.sh   # Training with visual dashboard
│   └── run-docker-windows.ps1       # Windows support script
├── config/                  # Configuration files
│   ├── Dockerfile                   # Docker image definition
│   ├── docker-compose.yml           # Docker Compose configuration
│   └── docker-entrypoint.sh         # Docker container entry point
├── docs/                    # Documentation
│   ├── USAGE.md                     # Usage instructions
│   ├── ARCHITECTURE.md              # This file
│   └── WINDOWS_SETUP.md             # Windows setup guide
├── src/                     # Source code
│   ├── game/                # Snake game implementation
│   │   ├── snake.py         # Core snake game logic
│   │   └── webserver.py     # Web interface for the game
│   ├── agent/               # RL agent implementation
│   │   ├── dqn_agent.py     # Deep Q-Network agent
│   │   └── trainer.py       # Training functionality
│   ├── main_web.py          # Web interface entry point
│   ├── main_train.py        # Agent training entry point
│   ├── main_visual_train.py # Visual training dashboard
│   ├── static/              # Static assets for web interface
│   │   ├── css/             # Stylesheets
│   │   └── js/              # JavaScript files
│   └── templates/           # HTML templates
├── models/                  # Saved model weights
└── data/                    # Training data and logs
```

## Components

### Game Engine

The core Snake game engine is implemented in `src/game/snake.py`. This provides:
- Snake movement mechanics
- Collision detection
- Food placement
- Score tracking

### Web Interface

The web interface is implemented in `src/game/webserver.py` and `src/main_web.py`. This allows:
- Playing the game in a browser
- Watching the agent play
- Controlling the snake with keyboard input

### Visual Training Dashboard

The visual training dashboard is implemented in `src/main_visual_train.py` and related frontend files. It provides:
- Real-time visualization of the training process
- Interactive controls for pausing/resuming training
- Speed adjustment for visualization
- Training metrics and charts
- Console logging system for training events
- Connection status monitoring
- Robust error handling for UI elements

### Reinforcement Learning Agent

The reinforcement learning agent is implemented in `src/agent/dqn_agent.py` and uses:
- Deep Q-Network (DQN) architecture
- Experience replay
- ε-greedy exploration policy
- Incremental learning from saved models

### Training Infrastructure

The training infrastructure is in `src/agent/trainer.py` and `src/main_train.py` and provides:
- Environment setup
- Agent training loop
- Model saving/loading
- Performance metrics
- Incremental training capability

### Console Logging System

The console logging system includes:
- Server-side log message queue
- Client-side display and rendering
- Event-based logging (food collection, collisions, etc.)
- Automatic log rotation to prevent memory issues
- Status indicators for connection state

## Command Interfaces

The project provides two main interfaces for users:

### Makefile Interface

For convenience, a Makefile provides common commands:
- `make play`: Run the game in human mode
- `make agent`: Watch the AI play the game
- `make train`: Train the agent with standard settings
- `make fast-train`: Train with optimized settings for Apple Silicon
- `make clean`: Kill all processes and clean up temporary files

### Script Interface

For advanced options and more control, the executable scripts in `bin/` can be called directly:
- `bin/run-docker-web.sh`: Run the web interface with custom options
- `bin/run-docker-train.sh`: Train with custom parameters
- `bin/run-docker-fast-train.sh`: Use optimized training
- `bin/run-docker-visual-train.sh`: Train with visual dashboard

## Cross-Platform Support

The project is designed to run seamlessly on multiple platforms:

### Linux and macOS
- Uses shell scripts in `bin/` directory
- Docker containers handle rendering and dependencies

### Windows
- Uses PowerShell script (`bin/run-docker-windows.ps1`)
- Optional X server support for graphical rendering

## Utility Scripts

### Port Management
- `bin/kill-snake-servers.sh`: Interactive script to find and kill server processes
- `bin/force-kill-snake-servers.sh`: Non-interactive script to automatically kill all related processes

## Docker Configuration

The Docker environment is defined in:
- `config/Dockerfile`: Image definition with Python dependencies
- `config/docker-compose.yml`: Service configuration
- `config/docker-entrypoint.sh`: Container startup script

## Execution Flow

1. User invokes either a Makefile command or a script from the bin directory
2. Docker containers handle the environment setup
3. Python entry points (main_*.py) parse arguments and initialize components
4. Game and agent components interact during gameplay or training 