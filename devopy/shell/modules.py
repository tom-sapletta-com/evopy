import importlib
import subprocess
import sys
from devopy.config import MODULES_DIR, PYTHON_BIN
from devopy.logger import info, error
from pathlib import Path

def ensure_module(module_name):
    sys.path.insert(0, str(MODULES_DIR))
    try:
        importlib.import_module(module_name)
        info(f"Moduł '{module_name}' już dostępny.")
    except ImportError:
        info(f"Moduł '{module_name}' nie jest zainstalowany. Instaluję...")
        subprocess.check_call([
            str(PYTHON_BIN), "-m", "pip", "install", f"--target={MODULES_DIR}", module_name
        ])
        info(f"Moduł '{module_name}' zainstalowany.")
        importlib.invalidate_caches()
        importlib.import_module(module_name)
