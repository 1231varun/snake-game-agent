# PowerShell script for running snake-game in Docker on Windows
# This script handles both regular Windows and WSL2 installations

Write-Host "Windows Docker helper script for snake-game" -ForegroundColor Cyan
Write-Host "----------------------------------------------" -ForegroundColor Cyan

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop first!" -ForegroundColor Red
    exit 1
}

# Test Docker functionality with a simple container
Write-Host "Testing Docker with a simple container..." -ForegroundColor Cyan
try {
    docker run --rm hello-world | Out-Null
    Write-Host "✓ Docker test container ran successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker test failed. There might be an issue with your Docker installation." -ForegroundColor Red
    Write-Host "  Error: $_" -ForegroundColor Red
    $continueAnyway = Read-Host "Continue anyway? (y/n)"
    if ($continueAnyway -ne "y") {
        exit 1
    }
}

# Determine if using WSL2 or regular Windows
$usingWSL = $false
try {
    $dockerInfo = docker info
    if ($dockerInfo -match "WSL2") {
        
        $usingWSL = $true
        Write-Host "Detected Docker running with WSL2 backend" -ForegroundColor Yellow
    } else {
        Write-Host "Detected Docker running with standard Windows backend" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not determine Docker backend. Assuming standard Windows." -ForegroundColor Yellow
}

# Check if an X server is running
$xServerRunning = $false
$vcxsrvProc = Get-Process -Name vcxsrv -ErrorAction SilentlyContinue
$xmingProc = Get-Process -Name Xming -ErrorAction SilentlyContinue
if ($vcxsrvProc -or $xmingProc) {
    $xServerRunning = $true
    Write-Host "✓ X server is running" -ForegroundColor Green
} else {
    Write-Host "! No X server detected" -ForegroundColor Yellow
    Write-Host "Installing or launching an X server (VcXsrv recommended):" -ForegroundColor Cyan
    Write-Host "  1. Download and install VcXsrv: https://sourceforge.net/projects/vcxsrv/" -ForegroundColor White
    Write-Host "  2. Launch XLaunch and configure:" -ForegroundColor White
    Write-Host "     - Multiple windows: Display number = 0" -ForegroundColor White
    Write-Host "     - Start no client" -ForegroundColor White
    Write-Host "     - Check 'Disable access control'" -ForegroundColor White
    Write-Host "     - Finish" -ForegroundColor White
    
    $installChoice = Read-Host "Would you like to continue anyway? (y/n)"
    if ($installChoice -ne "y") {
        exit 0
    }
}

# Get IP address - different approach depending on if using WSL2 or not
$displayIP = "host.docker.internal"
if ($usingWSL) {
    # For WSL2, we need the WSL2 VM's IP
    Write-Host "Setting up for WSL2..." -ForegroundColor Cyan
    Write-Host "For WSL2, run these commands in your WSL2 terminal before running Docker:" -ForegroundColor Yellow
    Write-Host "  export DISPLAY=`$(grep -m 1 nameserver /etc/resolv.conf | awk '{print `$2}'):0" -ForegroundColor White
    $prompt = Read-Host "Press Enter to continue once you've configured WSL2, or type 'skip' to skip this step"
    
    if ($prompt -ne "skip") {
        # We're going to continue with the assumption that WSL2 is set up properly
        Write-Host "Continuing with WSL2 setup..." -ForegroundColor Green
    }
} else {
    # For regular Windows, use host.docker.internal
    Write-Host "Using $displayIP as display address" -ForegroundColor Cyan
}

# Set the path to the config directory and docker-compose.yml
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$configDir = Join-Path (Split-Path -Parent $scriptDir) "config"
$composeFile = Join-Path $configDir "docker-compose.yml"

# Build the image
Write-Host "Building Docker image..." -ForegroundColor Cyan
docker-compose -f $composeFile build snake-game

# Run the container with appropriate display settings
$displayArgs = "-e DISPLAY=$($displayIP):0"
Write-Host "Running Docker container..." -ForegroundColor Cyan
Write-Host "docker-compose -f $composeFile run --rm $displayArgs snake-game $args" -ForegroundColor Yellow

# Execute the command
docker-compose -f $composeFile run --rm $displayArgs snake-game $args

Write-Host "Container execution completed" -ForegroundColor Green 