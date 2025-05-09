#!/bin/bash
# Debug monitor script for Evopy Assistant on Linux/macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Detect terminal colors support
if [ -t 1 ]; then
    BLUE='\033[0;34m'
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
else
    BLUE=''
    GREEN=''
    RED=''
    NC=''
fi

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
else
    echo -e "${BLUE}Virtual environment not found, using system Python...${NC}"
    # Choose available Python command
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d " " -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

echo -e "${BLUE}Using Python $PYTHON_VERSION${NC}"

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Error: Python 3.8 or newer is required. Found Python $PYTHON_VERSION${NC}"
    echo -e "${BLUE}Please run the install.sh script to set up the environment.${NC}"
    exit 1
fi

# Run debug monitor
echo -e "${GREEN}Starting Evopy Debug Monitor...${NC}"
$PYTHON_CMD "$SCRIPT_DIR/monitor.py" --script "$SCRIPT_DIR/evo.py" "$@"
