#!/usr/bin/env python3
"""
Evopy Cross-Platform Installer
==============================
This script installs Evopy and its dependencies on Linux, Windows, and macOS.
It detects the operating system and installs the appropriate dependencies.

Usage:
    python install.py [--no-venv] [--no-deps] [--force]

Options:
    --no-venv   Do not create a virtual environment
    --no-deps   Do not install dependencies
    --force     Force reinstallation of dependencies
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
from pathlib import Path

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_FEDORA = IS_LINUX and os.path.exists("/etc/fedora-release")
IS_MACOS = platform.system() == "Darwin"

# Directory setup
SCRIPT_DIR = Path(__file__).parent.absolute()
VENV_DIR = SCRIPT_DIR / ".venv"

# ANSI colors for terminal output (Windows-compatible)
if IS_WINDOWS:
    # Enable ANSI colors on Windows
    os.system("")

BLUE = '\033[0;34m' if not IS_WINDOWS or os.environ.get('TERM') else ''
GREEN = '\033[0;32m' if not IS_WINDOWS or os.environ.get('TERM') else ''
YELLOW = '\033[0;33m' if not IS_WINDOWS or os.environ.get('TERM') else ''
RED = '\033[0;31m' if not IS_WINDOWS or os.environ.get('TERM') else ''
CYAN = '\033[0;36m' if not IS_WINDOWS or os.environ.get('TERM') else ''
BOLD = '\033[1m' if not IS_WINDOWS or os.environ.get('TERM') else ''
NC = '\033[0m' if not IS_WINDOWS or os.environ.get('TERM') else ''  # No Color

def print_color(color: str, message: str, bold: bool = False) -> None:
    """Print colored text that works across platforms."""
    if bold:
        print(f"{BOLD}{color}{message}{NC}")
    else:
        print(f"{color}{message}{NC}")

def run_command(cmd, shell=False, cwd=None):
    """Run a command and return exit code, stdout, and stderr."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def check_python_version():
    """Check if Python version is compatible."""
    print_color(BLUE, "Checking Python version...")
    
    major, minor = sys.version_info.major, sys.version_info.minor
    if major < 3 or (major == 3 and minor < 8):
        print_color(RED, f"Python 3.8 or higher is required. You have {major}.{minor}.", bold=True)
        return False
    
    print_color(GREEN, f"Python version {major}.{minor} is compatible.")
    return True

def check_system_dependencies():
    """Check if system dependencies are installed."""
    print_color(BLUE, "Checking system dependencies...")
    
    if IS_LINUX:
        # Check for Docker
        code, stdout, stderr = run_command(["docker", "--version"])
        if code != 0:
            print_color(YELLOW, "Docker is not installed or not in PATH.")
            print_color(YELLOW, "Docker is required for the dependency auto-repair system.")
            
            if IS_FEDORA:
                print_color(CYAN, "To install Docker on Fedora, run:")
                print("sudo dnf -y install dnf-plugins-core")
                print("sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo")
                print("sudo dnf install docker-ce docker-ce-cli containerd.io")
                print("sudo systemctl start docker")
                print("sudo systemctl enable docker")
                print("sudo usermod -aG docker $USER")
            else:
                print_color(CYAN, "To install Docker on Ubuntu/Debian, run:")
                print("sudo apt-get update")
                print("sudo apt-get install docker.io")
                print("sudo systemctl start docker")
                print("sudo systemctl enable docker")
                print("sudo usermod -aG docker $USER")
        else:
            print_color(GREEN, f"Docker is installed: {stdout.strip()}")
        
        # Check for pandoc (for report generation)
        code, stdout, stderr = run_command(["pandoc", "--version"])
        if code != 0:
            print_color(YELLOW, "pandoc is not installed or not in PATH.")
            print_color(YELLOW, "pandoc is required for HTML and PDF report generation.")
            
            if IS_FEDORA:
                print_color(CYAN, "To install pandoc on Fedora, run:")
                print("sudo dnf install pandoc")
            else:
                print_color(CYAN, "To install pandoc on Ubuntu/Debian, run:")
                print("sudo apt-get install pandoc")
        else:
            print_color(GREEN, f"pandoc is installed: {stdout.splitlines()[0]}")
        
        # Check for wkhtmltopdf (for PDF generation)
        code, stdout, stderr = run_command(["wkhtmltopdf", "--version"])
        if code != 0:
            print_color(YELLOW, "wkhtmltopdf is not installed or not in PATH.")
            print_color(YELLOW, "wkhtmltopdf is required for PDF report generation.")
            
            if IS_FEDORA:
                print_color(CYAN, "To install wkhtmltopdf on Fedora, run:")
                print("sudo dnf install wkhtmltopdf")
            else:
                print_color(CYAN, "To install wkhtmltopdf on Ubuntu/Debian, run:")
                print("sudo apt-get install wkhtmltopdf")
        else:
            print_color(GREEN, f"wkhtmltopdf is installed: {stdout.strip()}")
    
    elif IS_WINDOWS:
        # Check for Docker Desktop
        docker_path = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Docker" / "Docker" / "Docker Desktop.exe"
        if not docker_path.exists():
            print_color(YELLOW, "Docker Desktop is not installed or not in the default location.")
            print_color(YELLOW, "Docker is required for the dependency auto-repair system.")
            print_color(CYAN, "To install Docker Desktop on Windows, download from:")
            print("https://www.docker.com/products/docker-desktop")
        else:
            print_color(GREEN, "Docker Desktop is installed.")
        
        # Check for pandoc
        code, stdout, stderr = run_command(["pandoc", "--version"], shell=True)
        if code != 0:
            print_color(YELLOW, "pandoc is not installed or not in PATH.")
            print_color(YELLOW, "pandoc is required for HTML and PDF report generation.")
            print_color(CYAN, "To install pandoc on Windows, download from:")
            print("https://pandoc.org/installing.html")
        else:
            print_color(GREEN, f"pandoc is installed: {stdout.splitlines()[0]}")
        
        # Check for wkhtmltopdf
        code, stdout, stderr = run_command(["wkhtmltopdf", "--version"], shell=True)
        if code != 0:
            print_color(YELLOW, "wkhtmltopdf is not installed or not in PATH.")
            print_color(YELLOW, "wkhtmltopdf is required for PDF report generation.")
            print_color(CYAN, "To install wkhtmltopdf on Windows, download from:")
            print("https://wkhtmltopdf.org/downloads.html")
        else:
            print_color(GREEN, f"wkhtmltopdf is installed: {stdout.strip()}")

def create_virtual_environment():
    """Create a virtual environment for Evopy."""
    print_color(BLUE, "Creating virtual environment...")
    
    # Check if virtual environment already exists
    if VENV_DIR.exists():
        print_color(YELLOW, f"Virtual environment already exists at {VENV_DIR}")
        return True
    
    # Create virtual environment
    if IS_WINDOWS:
        code, stdout, stderr = run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    else:
        code, stdout, stderr = run_command([sys.executable, "-m", "venv", str(VENV_DIR)])
    
    if code != 0:
        print_color(RED, f"Failed to create virtual environment: {stderr}")
        return False
    
    print_color(GREEN, f"Virtual environment created at {VENV_DIR}")
    return True

def install_dependencies():
    """Install Python dependencies."""
    print_color(BLUE, "Installing Python dependencies...")
    
    # Get pip command
    if IS_WINDOWS:
        pip_cmd = str(VENV_DIR / "Scripts" / "pip")
    else:
        pip_cmd = str(VENV_DIR / "bin" / "pip")
    
    # Upgrade pip
    code, stdout, stderr = run_command([pip_cmd, "install", "--upgrade", "pip"])
    if code != 0:
        print_color(RED, f"Failed to upgrade pip: {stderr}")
    
    # Install dependencies from requirements.txt
    requirements_file = SCRIPT_DIR / "requirements.txt"
    if requirements_file.exists():
        code, stdout, stderr = run_command([pip_cmd, "install", "-r", str(requirements_file)])
        if code != 0:
            print_color(RED, f"Failed to install dependencies: {stderr}")
            return False
        
        print_color(GREEN, "Dependencies installed successfully.")
    else:
        print_color(YELLOW, "requirements.txt not found. Skipping dependency installation.")
    
    return True

def check_ollama():
    """Check if Ollama is installed and running."""
    print_color(BLUE, "Checking Ollama installation...")
    
    ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"
    code, stdout, stderr = run_command([ollama_cmd, "list"])
    
    if code != 0:
        print_color(YELLOW, "Ollama is not installed or not running.")
        print_color(YELLOW, "Ollama is required for running language models locally.")
        
        if IS_LINUX:
            if IS_FEDORA:
                print_color(CYAN, "To install Ollama on Fedora, run:")
                print("curl -fsSL https://ollama.com/install.sh | sh")
            else:
                print_color(CYAN, "To install Ollama on Linux, run:")
                print("curl -fsSL https://ollama.com/install.sh | sh")
        elif IS_WINDOWS:
            print_color(CYAN, "To install Ollama on Windows, download from:")
            print("https://ollama.com/download/windows")
        elif IS_MACOS:
            print_color(CYAN, "To install Ollama on macOS, run:")
            print("curl -fsSL https://ollama.com/install.sh | sh")
        
        return False
    
    print_color(GREEN, "Ollama is installed and running.")
    print_color(BLUE, "Available models:")
    for line in stdout.splitlines()[1:]:  # Skip header
        if line.strip():
            print(f"  - {line.split()[0]}")
    
    return True

def make_scripts_executable():
    """Make scripts executable on Unix systems."""
    if not IS_WINDOWS:
        print_color(BLUE, "Making scripts executable...")
        
        scripts = [
            "evopy.py",
            "report.sh",
            "report_debug.sh",
            "test.sh",
            "cleanup.sh",
            "update_latest_report_link.sh"
        ]
        
        for script in scripts:
            script_path = SCRIPT_DIR / script
            if script_path.exists():
                os.chmod(script_path, 0o755)
                print(f"  - Made {script} executable")

def create_directories():
    """Create necessary directories."""
    print_color(BLUE, "Creating necessary directories...")
    
    directories = [
        SCRIPT_DIR / "test_results",
        SCRIPT_DIR / "reports",
        SCRIPT_DIR / "generated_code",
        SCRIPT_DIR / "tests" / "performance" / "results",
        SCRIPT_DIR / "tests" / "correctness" / "results"
    ]
    
    for directory in directories:
        directory.mkdir(exist_ok=True, parents=True)
        print(f"  - Created {directory}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Evopy Cross-Platform Installer")
    parser.add_argument("--no-venv", action="store_true", help="Do not create a virtual environment")
    parser.add_argument("--no-deps", action="store_true", help="Do not install dependencies")
    parser.add_argument("--force", action="store_true", help="Force reinstallation of dependencies")
    
    args = parser.parse_args()
    
    print_color(GREEN, "=== Evopy Cross-Platform Installer ===", bold=True)
    print_color(BLUE, f"Platform: {platform.system()} ({platform.platform()})")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Create directories
    create_directories()
    
    # Check system dependencies
    check_system_dependencies()
    
    # Create virtual environment
    if not args.no_venv:
        if not create_virtual_environment():
            return 1
    
    # Install dependencies
    if not args.no_deps:
        if not install_dependencies():
            return 1
    
    # Check Ollama
    check_ollama()
    
    # Make scripts executable
    make_scripts_executable()
    
    print_color(GREEN, "=== Installation complete ===", bold=True)
    print_color(BLUE, "To run Evopy:")
    
    if IS_WINDOWS:
        print_color(CYAN, "  - Using PowerShell: ./evopy.ps1")
        print_color(CYAN, "  - Using Command Prompt: evopy.bat")
    else:
        print_color(CYAN, "  - Using Python: ./evopy.py")
        print_color(CYAN, "  - Using shell scripts: ./report.sh or ./test.sh")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
