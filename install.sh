#!/bin/bash
# install.sh - Cross-platform installation script for Evopy Assistant
# Author: Claude
# Date: 09.05.2025

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Banner
echo -e "${MAGENTA}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              EVOPY ASSISTANT - INSTALLATION                    ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
elif [[ "$OSTYPE" == "msys" ]]; then
    OS="windows"
elif [[ "$OSTYPE" == "win32" ]]; then
    OS="windows"
elif [[ -f "/proc/version" ]] && grep -q "Microsoft" "/proc/version"; then
    OS="wsl"
fi

echo -e "${BLUE}Detected operating system: ${YELLOW}${OS}${NC}"

# Check if running with appropriate permissions
if [[ "$OS" == "linux" || "$OS" == "wsl" ]] && [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Error: This script should not be run as root.${NC}"
    exit 1
fi

# Helper functions
check_command() {
    command -v $1 >/dev/null 2>&1
}

create_directory() {
    mkdir -p "$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Created directory: $1${NC}"
    else
        echo -e "${RED}✗ Failed to create directory: $1${NC}"
        exit 1
    fi
}

# Configuration and variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.evo-assistant"
LOG_DIR="$SCRIPT_DIR/logs"
VENV_DIR="$SCRIPT_DIR/.venv"
PYTHON_CMD=""

# Create necessary directories
echo -e "${BLUE}Creating necessary directories...${NC}"
create_directory "$INSTALL_DIR"
create_directory "$INSTALL_DIR/history"
create_directory "$INSTALL_DIR/projects"
create_directory "$INSTALL_DIR/sandbox"
create_directory "$INSTALL_DIR/code"
create_directory "$LOG_DIR"

# Determine Python command
echo -e "${BLUE}Checking for Python...${NC}"
if check_command python3; then
    PYTHON_CMD="python3"
elif check_command python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.8 or newer.${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        echo -e "${YELLOW}You can install Python on Linux with:${NC}"
        echo -e "  sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
    elif [[ "$OS" == "macos" ]]; then
        echo -e "${YELLOW}You can install Python on macOS with:${NC}"
        echo -e "  brew install python"
        echo -e "  or download from https://www.python.org/downloads/"
    elif [[ "$OS" == "windows" || "$OS" == "wsl" ]]; then
        echo -e "${YELLOW}You can install Python on Windows by:${NC}"
        echo -e "  Downloading from https://www.python.org/downloads/"
        echo -e "  or using Windows Store"
    fi
    
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "${GREEN}✓ Found Python $PYTHON_VERSION${NC}"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or newer is required. Found Python $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo -e "${BLUE}Setting up virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Installing venv package...${NC}"
        
        if [[ "$OS" == "linux" || "$OS" == "wsl" ]]; then
            sudo apt-get update && sudo apt-get install -y python3-venv
        elif [[ "$OS" == "macos" ]]; then
            pip3 install virtualenv
        fi
        
        $PYTHON_CMD -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo -e "${RED}Error: Failed to create virtual environment.${NC}"
            exit 1
        fi
    fi
    echo -e "${GREEN}✓ Created virtual environment${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment
if [[ "$OS" == "windows" ]]; then
    source "$VENV_DIR/Scripts/activate"
else
    source "$VENV_DIR/bin/activate"
fi

# Install dependencies
echo -e "${BLUE}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/requirements.txt"

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to install dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Installed Python dependencies${NC}"

# Install system dependencies for report generation
echo -e "${BLUE}Checking for report generation dependencies...${NC}"
if [[ "$OS" == "linux" || "$OS" == "wsl" ]]; then
    if ! check_command pandoc || ! check_command wkhtmltopdf; then
        echo -e "${YELLOW}Installing pandoc and wkhtmltopdf for report generation...${NC}"
        sudo apt-get update && sudo apt-get install -y pandoc wkhtmltopdf
        if [ $? -ne 0 ]; then
            echo -e "${YELLOW}⚠ Could not automatically install pandoc and wkhtmltopdf.${NC}"
            echo -e "${YELLOW}Please install them manually:${NC}"
            echo -e "  sudo apt-get install pandoc wkhtmltopdf${NC}"
        else
            echo -e "${GREEN}✓ Installed report generation dependencies${NC}"
        fi
    else
        echo -e "${GREEN}✓ Report generation dependencies already installed${NC}"
    fi
elif [[ "$OS" == "macos" ]]; then
    if ! check_command pandoc || ! check_command wkhtmltopdf; then
        echo -e "${YELLOW}To install report generation dependencies on macOS, run:${NC}"
        echo -e "  brew install pandoc wkhtmltopdf${NC}"
    else
        echo -e "${GREEN}✓ Report generation dependencies already installed${NC}"
    fi
elif [[ "$OS" == "windows" ]]; then
    echo -e "${YELLOW}For report generation on Windows, please install:${NC}"
    echo -e "  - Pandoc: https://pandoc.org/installing.html${NC}"
    echo -e "  - wkhtmltopdf: https://wkhtmltopdf.org/downloads.html${NC}"
fi

# Check for Docker
echo -e "${BLUE}Checking for Docker...${NC}"
if check_command docker; then
    echo -e "${GREEN}✓ Docker is installed${NC}"
    
    # Check if Docker is running
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Docker is running${NC}"
    else
        echo -e "${YELLOW}⚠ Docker is installed but not running${NC}"
        
        if [[ "$OS" == "linux" ]]; then
            echo -e "${YELLOW}You can start Docker with:${NC}"
            echo -e "  sudo systemctl start docker"
        elif [[ "$OS" == "macos" || "$OS" == "windows" ]]; then
            echo -e "${YELLOW}Please start Docker Desktop application${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠ Docker is not installed${NC}"
    echo -e "${YELLOW}Docker is recommended but not required for full functionality.${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        echo -e "${YELLOW}You can install Docker on Linux with:${NC}"
        echo -e "  curl -fsSL https://get.docker.com -o get-docker.sh"
        echo -e "  sudo sh get-docker.sh"
    elif [[ "$OS" == "macos" ]]; then
        echo -e "${YELLOW}You can install Docker on macOS by downloading Docker Desktop:${NC}"
        echo -e "  https://www.docker.com/products/docker-desktop"
    elif [[ "$OS" == "windows" || "$OS" == "wsl" ]]; then
        echo -e "${YELLOW}You can install Docker on Windows by downloading Docker Desktop:${NC}"
        echo -e "  https://www.docker.com/products/docker-desktop"
    fi
fi

# Check for Ollama
echo -e "${BLUE}Checking for Ollama...${NC}"
if check_command ollama; then
    echo -e "${GREEN}✓ Ollama is installed${NC}"
else
    echo -e "${YELLOW}⚠ Ollama is not installed${NC}"
    
    if [[ "$OS" == "linux" ]]; then
        echo -e "${YELLOW}You can install Ollama on Linux with:${NC}"
        echo -e "  curl -fsSL https://ollama.com/install.sh | sh"
    elif [[ "$OS" == "macos" ]]; then
        echo -e "${YELLOW}You can install Ollama on macOS by downloading:${NC}"
        echo -e "  https://ollama.com/download/Ollama-darwin.zip"
    elif [[ "$OS" == "windows" ]]; then
        echo -e "${YELLOW}You can install Ollama on Windows by downloading:${NC}"
        echo -e "  https://ollama.com/download/OllamaSetup.exe"
    fi
fi

# Create run scripts for different platforms
echo -e "${BLUE}Creating platform-specific run scripts...${NC}"

# Linux/macOS run script
cat > "$SCRIPT_DIR/run.sh" << 'EOFSH'
#!/bin/bash
# Run script for Evopy Assistant on Linux/macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
else
    # Choose available Python command
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Run assistant
$PYTHON_CMD "$SCRIPT_DIR/evo.py" "$@"
EOFSH

chmod +x "$SCRIPT_DIR/run.sh"
echo -e "${GREEN}✓ Created run.sh script${NC}"

# Windows run script
cat > "$SCRIPT_DIR/run.bat" << 'EOFBAT'
@echo off
:: Run script for Evopy Assistant on Windows

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv

:: Activate virtual environment
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    set PYTHON_CMD=python
) else (
    :: Choose available Python command
    where python > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_CMD=python
    ) else (
        where python3 > nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set PYTHON_CMD=python3
        ) else (
            echo Python not found. Please install Python 3.8 or newer.
            exit /b 1
        )
    )
)

:: Run assistant
%PYTHON_CMD% "%SCRIPT_DIR%evo.py" %*
EOFBAT

echo -e "${GREEN}✓ Created run.bat script${NC}"

# PowerShell run script
cat > "$SCRIPT_DIR/run.ps1" << 'EOFPS'
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
EOFPS

echo -e "${GREEN}✓ Created run.ps1 script${NC}"

# Set permissions
chmod +x "$SCRIPT_DIR/run.sh"
chmod +x "$SCRIPT_DIR/evo.py"

echo -e "${GREEN}${BOLD}Installation completed successfully!${NC}"
echo -e "${BLUE}You can now run Evopy Assistant using:${NC}"
echo -e "  ${GREEN}On Linux/macOS:${NC} ./run.sh"
echo -e "  ${GREEN}On Windows:${NC} run.bat or powershell -ExecutionPolicy Bypass -File run.ps1"
echo

# Ask to run the assistant
echo -e "${BLUE}Would you like to run Evopy Assistant now? (y/N)${NC}"
read -n 1 -r choice
echo

if [[ "$choice" == "y" ]] || [[ "$choice" == "Y" ]]; then
    echo -e "${BLUE}Starting Evopy Assistant...${NC}"
    if [[ "$OS" == "windows" ]]; then
        cmd.exe /c "$SCRIPT_DIR/run.bat"
    else
        "$SCRIPT_DIR/run.sh"
    fi
else
    echo -e "${BLUE}You can run Evopy Assistant later using the appropriate script for your platform.${NC}"
fi
