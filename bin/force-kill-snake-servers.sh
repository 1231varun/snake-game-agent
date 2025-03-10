#!/bin/bash
# Script to forcefully kill all Snake Game server processes without confirmation

echo "Forcefully killing all Snake Game server processes..."

# List of common ports used by the application
PORTS=(3000 5000 8080 8000)

# Track if we found any processes
FOUND_PROCESSES=false

# Kill all processes on specified ports
for PORT in "${PORTS[@]}"; do
  # Get PIDs using this port
  PIDS=$(lsof -ti:$PORT)
  
  if [ -n "$PIDS" ]; then
    FOUND_PROCESSES=true
    echo "Found process(es) using port $PORT: $PIDS"
    echo "Killing process(es) on port $PORT..."
    kill -9 $PIDS
    echo "Process(es) killed."
  fi
done

# Kill all Python processes related to the game
echo ""
echo "Checking for Python processes running Snake Game..."
PYTHON_PROCS=$(ps aux | grep "[p]ython" | grep -E "main_web|webserver" | awk '{print $2}')

if [ -n "$PYTHON_PROCS" ]; then
  FOUND_PROCESSES=true
  echo "Found Python processes that might be running Snake Game: $PYTHON_PROCS"
  echo "Killing Python processes..."
  kill -9 $PYTHON_PROCS
  echo "Python processes killed."
fi

# Check if any Docker containers are running the Snake game
DOCKER_CONTAINERS=$(docker ps --filter name=snake-game -q)
if [ -n "$DOCKER_CONTAINERS" ]; then
  FOUND_PROCESSES=true
  echo "Found Docker containers running Snake Game: $DOCKER_CONTAINERS"
  echo "Stopping Docker containers..."
  docker stop $DOCKER_CONTAINERS
  echo "Docker containers stopped."
fi

if [ "$FOUND_PROCESSES" = false ]; then
  echo "No Snake Game server processes found."
fi

echo ""
echo "All Snake Game server processes have been terminated." 