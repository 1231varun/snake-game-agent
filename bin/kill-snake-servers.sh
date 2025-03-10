#!/bin/bash
# Script to find and kill all Snake Game server processes

echo "Checking for Snake Game server processes..."

# List of common ports used by the application
PORTS=(3000 5000 8080 8000)

# Track if we found any processes
FOUND_PROCESSES=false

# Check each port
for PORT in "${PORTS[@]}"; do
  # Get PIDs using this port
  PIDS=$(lsof -ti:$PORT)
  
  if [ -n "$PIDS" ]; then
    FOUND_PROCESSES=true
    echo "Found process(es) using port $PORT: $PIDS"
    
    read -p "Kill process(es) on port $PORT? (y/n): " CONFIRM
    if [[ $CONFIRM == [yY] || $CONFIRM == [yY][eE][sS] ]]; then
      echo "Killing process(es) on port $PORT..."
      kill -9 $PIDS
      echo "Process(es) killed."
    else
      echo "Skipped killing process(es) on port $PORT."
    fi
  fi
done

# Option to search for Python processes related to the game
echo ""
echo "Checking for Python processes running Snake Game..."
PYTHON_PROCS=$(ps aux | grep "[p]ython" | grep -E "main_web|webserver" | awk '{print $2}')

if [ -n "$PYTHON_PROCS" ]; then
  FOUND_PROCESSES=true
  echo "Found Python processes that might be running Snake Game:"
  ps aux | grep "[p]ython" | grep -E "main_web|webserver"
  
  read -p "Kill these Python processes? (y/n): " CONFIRM
  if [[ $CONFIRM == [yY] || $CONFIRM == [yY][eE][sS] ]]; then
    echo "Killing Python processes..."
    kill -9 $PYTHON_PROCS
    echo "Python processes killed."
  else
    echo "Skipped killing Python processes."
  fi
fi

if [ "$FOUND_PROCESSES" = false ]; then
  echo "No Snake Game server processes found running on common ports."
fi

echo ""
echo "Process check complete." 