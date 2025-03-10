# Windows Setup Guide for Snake Game Agent

This guide provides detailed instructions for setting up and running the Snake Game Agent in Docker on Windows systems.

## Prerequisites

1. **Docker Desktop for Windows**
   - Download and install from [Docker's website](https://www.docker.com/products/docker-desktop)
   - Ensure it's properly configured and running

2. **X Server for Windows**
   - VcXsrv (recommended): [Download VcXsrv](https://sourceforge.net/projects/vcxsrv/)
   - Alternative: [Xming](https://sourceforge.net/projects/xming/)

## Setup Instructions

### 1. Install Docker Desktop

1. Download and install Docker Desktop from [Docker's website](https://www.docker.com/products/docker-desktop)
2. Launch Docker Desktop and ensure it's running (check for the Docker icon in your system tray)
3. If prompted, complete the Docker tutorial

### 2. Install an X Server (VcXsrv recommended)

VcXsrv is needed to display the graphical interface of the Snake game running in Docker:

1. Download VcXsrv from [SourceForge](https://sourceforge.net/projects/vcxsrv/)
2. Install with default settings
3. Launch XLaunch from your Start menu
4. Configure XLaunch:
   - Display settings: Multiple Windows, Display number: 0
   - Client startup: Start no client
   - Extra settings: **✓ Disable access control** (important!)
   - Save configuration: Optionally save this configuration for future use
5. Click "Finish" to start the X server

### 3. Clone the Repository

Using Git Bash, Command Prompt, or PowerShell:

```bash
git clone https://github.com/1231varun/snake-game-agent.git
cd snake-game-agent
```

### 4. Running the Project

#### Option 1: Using PowerShell Script (Recommended)

We've provided a PowerShell script that automatically handles X server detection and configuration:

1. Right-click on `run-docker-windows.ps1` and select "Run with PowerShell"

   or

2. Open PowerShell and run:
   ```powershell
   .\run-docker-windows.ps1
   ```

3. For specific game modes:
   ```powershell
   .\run-docker-windows.ps1 --mode=train --episodes=500
   .\run-docker-windows.ps1 --mode=agent --model=models/best_model.h5
   ```

#### Option 2: Using Docker Compose Directly

If you prefer to use Docker Compose commands directly:

1. Make sure your X server is running
2. Open Command Prompt or PowerShell
3. Run:
   ```
   docker-compose build snake-game
   docker-compose run --rm -e DISPLAY=host.docker.internal:0 snake-game
   ```

## Windows Subsystem for Linux (WSL2) Instructions

If you're using Docker Desktop with WSL2 backend:

1. Install an X server as described above
2. In your WSL2 terminal, run:
   ```bash
   export DISPLAY=$(grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'):0
   ```
3. Then run the snake game:
   ```bash
   ./run-docker.sh
   ```

## Troubleshooting

### Common Issues

1. **No graphical window appears**
   - Make sure VcXsrv is running (look for the icon in your system tray)
   - Verify "Disable access control" was checked when starting VcXsrv
   - Try restarting VcXsrv and Docker Desktop

2. **"Cannot connect to X server" error**
   - Ensure your firewall isn't blocking VcXsrv
   - Add exceptions in Windows Defender or your antivirus for VcXsrv

3. **Black or frozen window**
   - Try running in the fallback mode which uses Xvfb in the container:
     ```
     docker-compose run --rm snake-game
     ```

4. **Performance issues**
   - If the game runs slowly, try adjusting Docker Desktop resource settings
   - Go to Docker Desktop > Settings > Resources > Advanced and increase memory/CPU allocation

## Additional Resources

- [Docker Desktop documentation](https://docs.docker.com/desktop/windows/)
- [VcXsrv documentation](https://sourceforge.net/projects/vcxsrv/) 