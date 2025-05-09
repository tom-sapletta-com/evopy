# Run script for Evopy Assistant on Windows (PowerShell)

$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$VENV_DIR = Join-Path $SCRIPT_DIR ".venv"

# Activate virtual environment
if (Test-Path (Join-Path $VENV_DIR "Scripts\Activate.ps1")) {
    & (Join-Path $VENV_DIR "Scripts\Activate.ps1")
    $PYTHON_CMD = "python"
} else {
    # Choose available Python command
    try {
        Get-Command python -ErrorAction Stop
        $PYTHON_CMD = "python"
    } catch {
        try {
            Get-Command python3 -ErrorAction Stop
            $PYTHON_CMD = "python3"
        } catch {
            Write-Host "Python not found. Please install Python 3.8 or newer."
            exit 1
        }
    }
}

# Run assistant
& $PYTHON_CMD (Join-Path $SCRIPT_DIR "evo.py") $args
