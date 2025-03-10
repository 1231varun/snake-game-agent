#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Checking development environment setup${NC}"
echo -e "${BLUE}========================================${NC}"

# Check if we're in a virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Not running in a Python virtual environment.${NC}"
    echo -e "${YELLOW}Please activate your virtual environment:${NC}"
    echo -e "  source venv/bin/activate  # Unix/macOS"
    echo -e "  source bin/activate_venv.sh  # Helper script"
    echo -e "  .\\venv\\Scripts\\activate  # Windows"
    echo -e "  .\\bin\\Activate-Venv.ps1  # Windows helper script"
    echo ""
else
    echo -e "${GREEN}✓ Virtual environment is activated.${NC}"
fi

# Check Python version
PYTHON_VERSION=$(python --version 2>&1)
echo -e "${GREEN}✓ Python version: ${PYTHON_VERSION}${NC}"

# Check Python packages
echo -e "${BLUE}Checking required Python packages...${NC}"
PACKAGES=("numpy" "tensorflow" "pygame" "flask" "black" "flake8" "pylint" "isort")
ALL_PACKAGES_INSTALLED=true

for package in "${PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓ $package is installed${NC}"
    else
        echo -e "${RED}✗ $package is NOT installed${NC}"
        ALL_PACKAGES_INSTALLED=false
    fi
done

if [ "$ALL_PACKAGES_INSTALLED" = false ]; then
    echo -e "${YELLOW}Some Python packages are missing. Run:${NC}"
    echo -e "  pip install -r requirements.txt"
    echo ""
fi

# Check Node.js
if command -v node &>/dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✓ Node.js version: ${NODE_VERSION}${NC}"
    
    # Check NPM
    if command -v npm &>/dev/null; then
        NPM_VERSION=$(npm --version)
        echo -e "${GREEN}✓ npm version: ${NPM_VERSION}${NC}"
        
        # Check if node_modules exists
        if [ -d "node_modules" ]; then
            echo -e "${GREEN}✓ node_modules directory exists${NC}"
        else
            echo -e "${RED}✗ node_modules directory NOT found${NC}"
            echo -e "${YELLOW}Run 'npm install' to install Node.js dependencies${NC}"
        fi
    else
        echo -e "${RED}✗ npm is NOT installed${NC}"
    fi
else
    echo -e "${RED}✗ Node.js is NOT installed${NC}"
    echo -e "${YELLOW}Node.js is required for frontend linting. Visit https://nodejs.org/ to install.${NC}"
fi

# Check Git hooks
echo -e "${BLUE}Checking Git hooks...${NC}"
if [ -d ".git/hooks" ]; then
    if [ -f ".git/hooks/pre-commit" ]; then
        echo -e "${GREEN}✓ pre-commit hook is installed${NC}"
    else
        echo -e "${RED}✗ pre-commit hook is NOT installed${NC}"
        echo -e "${YELLOW}Run 'npx husky install' to set up Git hooks${NC}"
    fi
else
    echo -e "${YELLOW}Not a Git repository or .git directory not found${NC}"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Environment check complete${NC}"
echo -e "${BLUE}========================================${NC}" 