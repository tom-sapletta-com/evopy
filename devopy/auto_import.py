import importlib
import subprocess
import sys

def ensure_package(pkg_name):
    try:
        importlib.import_module(pkg_name)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])


def auto_import(packages):
    """
    Automatycznie importuje wymagane paczki (instaluje jeśli trzeba).
    Przykład: auto_import(["openpyxl", "requests"])
    """
    for pkg in packages:
        ensure_package(pkg)
