#!/bin/bash

# This script sources the virtual environment activation script
# Usage: source bin/activate_venv.sh

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Path to the virtual environment activation script
VENV_ACTIVATE="$PROJECT_ROOT/venv/bin/activate"

# Check if we're on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    VENV_ACTIVATE="$PROJECT_ROOT/venv/Scripts/activate"
fi

# Check if the virtual environment exists
if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "Virtual environment not found. Creating it..."
    make -C "$PROJECT_ROOT" venv
fi

# Source the activation script
source "$VENV_ACTIVATE"

echo "Virtual environment activated. Run 'deactivate' to exit." 