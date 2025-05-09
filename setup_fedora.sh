#!/bin/bash
#
# Evopy Fedora Setup Script
# =========================
# This script installs all dependencies required for Evopy on Fedora Linux
#

set -e  # Exit on error

# ANSI colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'  # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}This script needs to be run as root to install system packages.${NC}"
  echo -e "${YELLOW}Please run with: sudo $0${NC}"
  exit 1
fi

# Check if running on Fedora
if [ ! -f /etc/fedora-release ]; then
  echo -e "${RED}This script is intended for Fedora Linux only.${NC}"
  echo -e "${YELLOW}If you're using a different Linux distribution, please refer to the documentation.${NC}"
  exit 1
fi

# Print header
echo -e "${GREEN}${BOLD}=== Evopy Fedora Setup ===${NC}"
echo -e "${BLUE}Installing dependencies for Evopy on Fedora Linux...${NC}"
echo ""

# Update package list
echo -e "${CYAN}Updating package list...${NC}"
dnf update -y

# Install Python and development tools
echo -e "${CYAN}Installing Python and development tools...${NC}"
dnf install -y python3 python3-devel python3-pip python3-virtualenv

# Install Docker
echo -e "${CYAN}Installing Docker...${NC}"
dnf -y install dnf-plugins-core
dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
dnf install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start and enable Docker service
echo -e "${CYAN}Starting and enabling Docker service...${NC}"
systemctl start docker
systemctl enable docker

# Add current user to Docker group
echo -e "${CYAN}Adding current user to Docker group...${NC}"
usermod -aG docker $SUDO_USER

# Install pandoc for report generation
echo -e "${CYAN}Installing pandoc for report generation...${NC}"
dnf install -y pandoc

# Install wkhtmltopdf for PDF generation
echo -e "${CYAN}Installing wkhtmltopdf for PDF generation...${NC}"
dnf install -y wkhtmltopdf

# Install other dependencies
echo -e "${CYAN}Installing other dependencies...${NC}"
dnf install -y git curl wget

# Install Ollama (if not already installed)
if ! command -v ollama &> /dev/null; then
  echo -e "${CYAN}Installing Ollama...${NC}"
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo -e "${GREEN}Ollama is already installed.${NC}"
fi

# Create Python virtual environment
echo -e "${CYAN}Creating Python virtual environment...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

# Create venv as the original user, not as root
if [ -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}Virtual environment already exists at $VENV_DIR${NC}"
else
  echo -e "${CYAN}Creating virtual environment at $VENV_DIR${NC}"
  su - $SUDO_USER -c "python3 -m venv $VENV_DIR"
fi

# Install Python dependencies
echo -e "${CYAN}Installing Python dependencies...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
  su - $SUDO_USER -c "$VENV_DIR/bin/pip install -r $SCRIPT_DIR/requirements.txt"
else
  echo -e "${YELLOW}requirements.txt not found. Skipping dependency installation.${NC}"
fi

# Make scripts executable
echo -e "${CYAN}Making scripts executable...${NC}"
chmod +x "$SCRIPT_DIR/evopy.py"
chmod +x "$SCRIPT_DIR/sandbox_cli.py"
chmod +x "$SCRIPT_DIR/report.sh"
chmod +x "$SCRIPT_DIR/report_debug.sh"
chmod +x "$SCRIPT_DIR/test.sh"
chmod +x "$SCRIPT_DIR/cleanup.sh"

# Create necessary directories
echo -e "${CYAN}Creating necessary directories...${NC}"
mkdir -p "$SCRIPT_DIR/test_results"
mkdir -p "$SCRIPT_DIR/reports"
mkdir -p "$SCRIPT_DIR/generated_code"
mkdir -p "$SCRIPT_DIR/tests/performance/results"
mkdir -p "$SCRIPT_DIR/tests/correctness/results"

# Set proper ownership for all files
echo -e "${CYAN}Setting proper ownership...${NC}"
chown -R $SUDO_USER:$SUDO_USER "$SCRIPT_DIR"

# Print success message
echo ""
echo -e "${GREEN}${BOLD}=== Installation complete! ===${NC}"
echo -e "${BLUE}Evopy has been successfully set up on your Fedora system.${NC}"
echo ""
echo -e "${YELLOW}Important notes:${NC}"
echo -e "1. You may need to log out and log back in for Docker group changes to take effect."
echo -e "2. To activate the virtual environment, run: ${CYAN}source $VENV_DIR/bin/activate${NC}"
echo -e "3. To run Evopy, use: ${CYAN}./evopy.py${NC}"
echo ""
echo -e "${GREEN}Thank you for using Evopy!${NC}"
