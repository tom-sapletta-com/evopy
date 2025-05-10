from pathlib import Path
import os

APP_DIR = Path.home() / ".devopy"
MODULES_DIR = APP_DIR / "modules"
VENV_DIR = Path.cwd() / ".devopy_venv"

# Tworzenie katalogów na moduły
MODULES_DIR.mkdir(parents=True, exist_ok=True)

# Ścieżka do interpretera Pythona w venv
if os.name == "nt":
    PYTHON_BIN = VENV_DIR / "Scripts" / "python.exe"
else:
    PYTHON_BIN = VENV_DIR / "bin" / "python3"
