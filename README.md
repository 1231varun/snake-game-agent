# Snake Game Agent

A reinforcement learning project that trains an agent to play a Python-based snake game.

## Project Overview

This project implements a classic Snake game using Pygame and develops an AI agent using reinforcement learning techniques to play the game autonomously. The agent learns to navigate the snake, collect food, and avoid collisions through training.

## Features

- **Classic Snake Game**: Arrow key controls, growing when eating food
- **Web-Based Interface**: Play directly in your browser 
- **Reinforcement Learning Agent**: Train an AI to learn the game
- **Visual Training**: Browser-based visualization of the training process in real-time
- **Incremental Learning**: Resume training from previously saved models
- **Enhanced Console Logging**: Real-time feedback on training progress and events
- **Robust UI**: Error-resistant interface with clear status indicators
- **Visualization Tools**: Training metrics and performance graphs
- **Docker Support**: Cross-platform play and training (Linux, macOS, and Windows) 
- **Code Quality Tools**: Integrated linting and formatting for Python, JavaScript, HTML, and CSS

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

### Visual Training with Real-time Feedback

```bash
./bin/run-docker-visual-train.sh
```

This opens a real-time dashboard in your browser showing training progress, game state, console logs, and performance metrics.

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
- **Incremental Learning**: Continue training from previously saved models

For more details, see [Architecture](docs/ARCHITECTURE.md).

## M3 Optimization Features

This project includes special optimizations for Apple Silicon (M1/M2/M3) processors:

1. **Metal Performance Optimizations**: Uses Metal-specific configurations to accelerate TensorFlow and PyTorch.

2. **Mixed Precision Training**: Automatically enables mixed precision on Apple Silicon for faster training.

3. **Fast Training Scripts**: Includes specialized scripts for both full training and rapid testing:
   - `bin/run-docker-fast-train.sh`: Optimized training with balanced parameters
   - `bin/run-docker-test-train.sh`: Super-fast testing for rapid development iterations
   - `bin/run-docker-visual-train.sh`: Train with real-time visualization in the browser

4. **Intelligent Agent Design**:
   - Targeted exploration strategy that biases toward food
   - Adaptive learning rates optimized for Apple Silicon
   - Smart food placement to improve initial learning
   - Faster epsilon decay pattern for quicker learning
   - Incremental learning from existing models

## Usage

### Training

For full training on Apple Silicon:

```bash
./bin/run-docker-fast-train.sh
```

For real-time visualization of training in your browser:

```bash
./bin/run-docker-visual-train.sh
```

For quick testing of changes:

```bash
./bin/run-docker-test-train.sh
```

All scripts accept the following parameters:
- `--episodes=N`: Number of training episodes
- `--model=path/to/model.h5`: Path to save the model
- `--max-steps=N`: Maximum steps per episode
- `--timeout=N`: Timeout multiplier (higher values give more time to find food)
- `--continue`: Continue training from an existing model (default)
- `--fresh`: Start with a fresh model, ignoring any existing one

Visual training also accepts:
- `--port=N`: Web port for the visualization (default: 3000)

### Incremental Training

By default, all training scripts will continue training from an existing model if one is found. This allows you to build on previous training sessions rather than starting from scratch each time.

To start with a fresh model instead:

```bash
./bin/run-docker-fast-train.sh --fresh
```

To explicitly continue from an existing model:

```bash
./bin/run-docker-fast-train.sh --continue --model=models/my_existing_model.h5
```

### Visualizing Training

The visual training script provides a real-time browser interface that allows you to:
- Watch the snake's learning progress in real-time
- View training metrics and charts
- Pause/resume training
- Adjust visualization speed
- Monitor connection status with clear indicators
- Read detailed console logs about training events (food collected, game overs, etc.)
- Track statistics like average score, epsilon value, and timeouts
- Auto-scrolling console that respects user interaction

Access the visualization by opening http://localhost:3000 in your browser while the training is running.

### Web Interface

Run the web interface to play the game or watch the trained agent:

```bash
./bin/run-docker-web.sh
```

This will start the web server on port 3000. Open your browser to `http://localhost:3000` to access the game.

## Troubleshooting

- **Port conflicts**: The scripts automatically detect and clear ports in use
- **Docker issues**: Make sure Docker is running before executing the scripts
- **Training timeouts**: If all episodes timeout, try increasing the `--timeout` parameter
- **UI errors**: The interface is designed to gracefully handle connection issues and DOM element errors

## License

See the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Code Quality Tools

The project includes several linting and formatting tools to maintain code quality:

### Python Linting and Formatting

We use the following Python tools:
- **Black**: Code formatter
- **Flake8**: PEP8 style guide enforcer
- **Pylint**: Static code analyzer
- **isort**: Import sorting

Run Python linting:
```bash
# Run all Python linting tools
make lint-python

# Format Python code with Black
make format

# Sort Python imports with isort
make isort

# Run Flake8 linter
make flake8

# Run Pylint static analyzer
make pylint
```

### JavaScript, HTML, and CSS Linting

We use the following frontend tools:
- **ESLint**: JavaScript linter (using StandardJS rules)
- **Stylelint**: CSS linter
- **HTMLHint**: HTML validator

Run frontend linting:
```bash
# Run all frontend linting tools
make lint-frontend

# Run ESLint for JavaScript
make eslint

# Run Stylelint for CSS
make stylelint

# Run HTMLHint for HTML
make htmlhint
```

To automatically fix issues where possible:
```bash
# Fix all frontend issues
make lint-frontend-fix

# Fix only JavaScript issues
make eslint-fix

# Fix only CSS issues
make stylelint-fix
```

### Run All Linting Checks

To run all linting tools at once:
```bash
make lint
```

With auto-fix for all fixable issues:
```bash
make lint-fix
```

### Setting Up Development Environment

The easiest way to set up your development environment is to use the `make venv` command:

```bash
make venv
```

This will:
1. Create a Python virtual environment in the `venv` directory
2. Install all Python dependencies from `requirements.txt`
3. Install all Node.js dependencies for frontend tools
4. Set up pre-commit hooks with Husky

After running `make venv`, you'll need to activate the virtual environment:

**On Unix/macOS**:
```bash
source venv/bin/activate
# Or use our helper script
source bin/activate_venv.sh
```

**On Windows**:
```powershell
.\venv\Scripts\activate
# Or use our helper script
.\bin\Activate-Venv.ps1
```

To deactivate the virtual environment, simply run:
```bash
deactivate
```

### Verifying Your Development Environment

To check if your development environment is correctly set up, run:

```bash
./bin/check-dev-setup.sh
```

This script will verify:
- Python virtual environment activation
- Required Python packages installation
- Node.js and npm installation
- Frontend dependency installation
- Git hooks setup

### Manual Setup

If you prefer to set up your environment manually:

1. Install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Set up pre-commit hooks:
```bash
npx husky install
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality before commits:

1. JavaScript, CSS, and HTML files are automatically linted and fixed (where possible) using lint-staged and Husky.
2. Python files are automatically formatted using Black and isort.

These hooks are automatically set up when you run `make venv` or you can set them up manually:

```bash
npm install
npx husky install
```

This will ensure that all code is properly formatted before being committed to the repository.
