#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed. Please install Node.js and npm first.${NC}"
    exit 1
fi

# Determine if we should fix issues
FIX=false
if [ "$1" == "--fix" ]; then
  FIX=true
fi

# Run ESLint for JavaScript files
echo -e "${YELLOW}Running ESLint for JavaScript files...${NC}"
if [ "$FIX" = true ]; then
  npm run lint:js:fix
else
  npm run lint:js
fi

# Run Stylelint for CSS files
echo -e "${YELLOW}Running Stylelint for CSS files...${NC}"
if [ "$FIX" = true ]; then
  npm run lint:css:fix
else
  npm run lint:css
fi

# Run HTMLHint for HTML files
echo -e "${YELLOW}Running HTMLHint for HTML files...${NC}"
npm run lint:html

echo -e "${GREEN}Frontend linting completed!${NC}" 