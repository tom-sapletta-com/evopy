# Evopy Sandbox CLI for Windows
# This PowerShell script runs the cross-platform sandbox CLI on Windows with enhanced features

# Set error action preference
$ErrorActionPreference = "Stop"

# Get the directory of this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Test-Dependencies {
    # Check for Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "Using $pythonVersion" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
        return $false
    }
    
    # Check for Docker
    try {
        $dockerVersion = docker --version 2>&1
        Write-Host "Using $dockerVersion" -ForegroundColor Cyan
    }
    catch {
        Write-Host "Docker is not installed or not in PATH." -ForegroundColor Red
        Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        return $false
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
    }
    catch {
        Write-Host "Docker is not running." -ForegroundColor Red
        Write-Host "Please start Docker Desktop." -ForegroundColor Yellow
        return $false
    }
    
    return $true
}

function Run-Sandbox {
    param (
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    
    # Check dependencies
    if (-not (Test-Dependencies)) {
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    # Check if virtual environment exists
    if (Test-Path "$ScriptDir\.venv") {
        # Activate virtual environment
        & "$ScriptDir\.venv\Scripts\Activate.ps1"
    }
    
    # Run the Python script with all arguments
    $pythonScript = Join-Path $ScriptDir "sandbox_cli.py"
    
    try {
        if ($Arguments.Count -gt 0) {
            & python $pythonScript $Arguments
        }
        else {
            # Show help if no arguments provided
            & python $pythonScript --help
        }
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "An error occurred while running the sandbox." -ForegroundColor Red
            Read-Host "Press Enter to continue"
        }
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Read-Host "Press Enter to continue"
    }
}

# Run the sandbox with all arguments
Run-Sandbox $args
