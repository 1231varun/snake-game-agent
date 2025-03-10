# This script activates the virtual environment for Windows users
# Usage: .\bin\Activate-Venv.ps1

# Get the directory where the script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Path to the virtual environment activation script
$VenvActivate = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"

# Check if the virtual environment exists
if (-not (Test-Path $VenvActivate)) {
    Write-Host "Virtual environment not found. Creating it..."
    
    # Navigate to project root and run make venv
    Push-Location $ProjectRoot
    python -m venv venv
    
    # Check if the venv was created successfully
    if (Test-Path "venv\Scripts\python.exe") {
        Write-Host "Installing dependencies..."
        & "venv\Scripts\python.exe" -m pip install --upgrade pip
        & "venv\Scripts\pip.exe" install -r requirements.txt
        
        # Install Node.js dependencies
        npm install
        
        # Set up pre-commit hooks
        npx husky install
    } else {
        Write-Host "Failed to create virtual environment. Please run 'python -m venv venv' manually."
    }
    
    Pop-Location
}

# Activate the virtual environment
& $VenvActivate

Write-Host "Virtual environment activated. Run 'deactivate' to exit." 