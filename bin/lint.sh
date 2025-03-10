#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running isort to sort imports...${NC}"
python -m isort src

echo -e "${YELLOW}Running black formatter...${NC}"
python -m black src

echo -e "${YELLOW}Running flake8 to check for PEP8 compliance...${NC}"
python -m flake8 src

echo -e "${YELLOW}Running pylint for code quality analysis...${NC}"
python -m pylint src

echo -e "${GREEN}Linting completed!${NC}" 