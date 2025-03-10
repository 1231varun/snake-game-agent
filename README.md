# Snake Game Agent

A reinforcement learning project that trains an agent to play a Python-based snake game.

## Project Overview

This project implements a classic Snake game using Pygame and develops an AI agent using reinforcement learning techniques to play the game autonomously. The agent learns to navigate the snake, collect food, and avoid collisions through training.

## Features

- **Classic Snake Game**: Arrow key controls, growing when eating food
- **Web-Based Interface**: Play directly in your browser 
- **Reinforcement Learning Agent**: Train an AI to learn the game
- **Visualization Tools**: Training metrics and performance graphs
- **Docker Support**: Cross-platform play and training (Linux, macOS, and Windows) 

## Quick Start

The project uses a Makefile for common tasks:

### Playing the Game (Human Mode)

```bash
make play
```

Then open your browser to http://localhost:3000 and use the arrow keys to control the snake.

### Training the Agent

```bash
make train       # Standard training
make fast-train  # Optimized for Apple Silicon
```

### Watching the Agent Play

```bash
make agent
```

### Cleaning Up

```bash
make clean  # Kill all processes and clean temporary files
```

### Advanced Usage

For more advanced options, you can run the scripts directly:

```bash
# On Linux/macOS
./bin/run-docker-web.sh --port=8080 --mode=agent --model=models/custom_model.h5

# On Windows
./bin/run-docker-windows.ps1 python src/main_web.py --mode=agent --model=models/custom_model.h5
```

## Project Structure

```
snake-game-agent/
├── README.md                # This file
├── requirements.txt         # Project dependencies
├── Makefile                 # Convenient commands
├── bin/                     # Executable scripts
│   ├── kill-snake-servers.sh        # Utility to kill server processes
│   ├── force-kill-snake-servers.sh  # Force kill server processes
│   ├── run-docker-web.sh            # Run game in web mode
│   ├── run-docker-train.sh          # Train the agent
│   ├── run-docker-fast-train.sh     # Fast training for Apple Silicon
│   └── run-docker-windows.ps1       # Windows support script
├── config/                  # Configuration files
│   ├── Dockerfile                   # Docker image definition
│   ├── docker-compose.yml           # Docker Compose configuration
│   └── docker-entrypoint.sh         # Docker container entry point
├── docs/                    # Documentation
│   ├── USAGE.md                     # Usage instructions
│   ├── ARCHITECTURE.md              # Architecture details
│   └── WINDOWS_SETUP.md             # Windows setup guide
├── src/                     # Source code
│   ├── game/                # Snake game implementation
│   │   ├── snake.py         # Core snake game logic
│   │   └── webserver.py     # Web interface for the game
│   ├── agent/               # RL agent implementation
│   │   ├── dqn_agent.py     # Deep Q-Network agent
│   │   └── trainer.py       # Training functionality
│   ├── main_web.py          # Web interface entry point
│   └── main_train.py        # Agent training entry point
├── models/                  # Saved model weights
└── data/                    # Training data and logs
```

## Documentation

For detailed documentation:

- [Usage Guide](docs/USAGE.md) - Detailed instructions on using the application
- [Architecture](docs/ARCHITECTURE.md) - Overview of the project architecture
- [Windows Setup](docs/WINDOWS_SETUP.md) - Guide for Windows users

## Troubleshooting

### Docker Daemon Not Running

Before running any commands, ensure that Docker is running on your system. The scripts will automatically check if Docker daemon is running and provide instructions if it's not.

### Port Already in Use

The game automatically runs on port 3000. If another process is already using this port, the script will automatically clear the port.

### Killing All Game Processes

If you need to kill all processes related to the Snake Game:

```bash
./bin/kill-snake-servers.sh
```

For more troubleshooting information, see [Usage Guide](docs/USAGE.md).

## Environment Setup

The project runs in Docker for cross-platform compatibility. You only need Docker and Docker Compose installed.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Reinforcement Learning Approach

The agent uses a Deep Q-Network (DQN) with the following characteristics:

- **State Space**: Simplified representation of the game state
- **Action Space**: 3 possible actions (straight, right, left)
- **Reward System**: Rewards for eating food, penalties for collisions

For more details, see [Architecture](docs/ARCHITECTURE.md).

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
