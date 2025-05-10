import subprocess
import sys
import os

class PyPIRegistry:
    @staticmethod
    def install_package(package_name, venv_path=None):
        if venv_path:
            pip_cmd = [os.path.join(venv_path, "bin", "python"), "-m", "pip", "install", package_name]
        else:
            pip_cmd = [sys.executable, "-m", "pip", "install", package_name]
        try:
            subprocess.check_call(pip_cmd)
            return True
        except Exception as e:
            print(f"[ERROR] PyPI install failed: {e}")
            return False

    @staticmethod
    def check_package(package_name):
        # Możesz dodać sprawdzanie dostępności paczki przez PyPI API
        return True
