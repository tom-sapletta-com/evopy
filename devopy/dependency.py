import subprocess
import sys
from devopy.config import PYTHON_BIN
from devopy.logger import info, error

def install_package(package_name):
    try:
        info(f"Instaluję paczkę: {package_name}")
        subprocess.check_call([str(PYTHON_BIN), "-m", "pip", "install", package_name])
        info(f"Paczka {package_name} zainstalowana.")
        return True
    except Exception as e:
        error(f"Błąd instalacji {package_name}: {e}")
        return False

def ensure_package(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return install_package(package_name)

