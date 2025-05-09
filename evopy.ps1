# Evopy PowerShell Launcher
# This PowerShell script runs the cross-platform Evopy Python script on Windows with enhanced features

# Set error action preference
$ErrorActionPreference = "Stop"

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Using $pythonVersion" -ForegroundColor Cyan
        return $true
    }
    catch {
        return $false
    }
}

function Install-Dependencies {
    Write-Host "Installing required dependencies..." -ForegroundColor Yellow
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path "$ScriptDir\.venv")) {
        Write-Host "Creating virtual environment..." -ForegroundColor Cyan
        python -m venv "$ScriptDir\.venv"
    }
    
    # Activate virtual environment
    & "$ScriptDir\.venv\Scripts\Activate.ps1"
    
    # Install requirements
    if (Test-Path "$ScriptDir\requirements.txt") {
        Write-Host "Installing requirements from requirements.txt..." -ForegroundColor Cyan
        pip install -r "$ScriptDir\requirements.txt"
    }
}

function Run-Evopy {
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    
    # Check if Python is installed
    if (-not (Test-PythonInstalled)) {
        Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check if virtual environment exists
    if (Test-Path "$ScriptDir\.venv") {
        # Activate virtual environment
        & "$ScriptDir\.venv\Scripts\Activate.ps1"
    }
    
    # Run the Python script with all arguments
    $pythonScript = Join-Path $ScriptDir "evopy.py"
    
    try {
        if ($Arguments.Count -gt 0) {
            & python $pythonScript $Arguments
        }
        else {
            & python $pythonScript
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "An error occurred while running Evopy." -ForegroundColor Red
            Read-Host "Press Enter to continue"
        }
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Press Enter to continue"
    }
}

# Check if --install flag is provided
if ($args -contains "--install") {
    Install-Dependencies
    $args = $args | Where-Object { $_ -ne "--install" }
}

# Run Evopy with remaining arguments
Run-Evopy $args
