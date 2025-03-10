#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine if we should fix issues
FIX=""
if [ "$1" == "--fix" ]; then
  FIX="--fix"
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running all linting checks${NC}"
echo -e "${BLUE}========================================${NC}"

# Run Python linting
echo -e "${YELLOW}Running Python linting...${NC}"
bin/lint.sh

# Run Frontend linting
echo -e "${YELLOW}Running Frontend linting...${NC}"
bin/lint-frontend.sh $FIX

echo -e "${GREEN}All linting tasks completed!${NC}"
echo -e "${BLUE}========================================${NC}" 