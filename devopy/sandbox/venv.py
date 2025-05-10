import subprocess
import os
from pathlib import Path

class VenvSandbox:
    def __init__(self, base_dir="sandbox_envs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_env(self, env_name):
        env_path = self.base_dir / env_name
        subprocess.check_call(["python3", "-m", "venv", str(env_path)])
        # Upewnij się, że pip jest dostępny
        subprocess.check_call([str(env_path / "bin/python"), "-m", "ensurepip", "--upgrade"])
        subprocess.check_call([str(env_path / "bin/python"), "-m", "pip", "install", "--upgrade", "pip"])
        return env_path

    def test_package(self, env_path, package_name):
        try:
            subprocess.check_call([str(env_path / "bin/python"), "-c", f"import {package_name}"])
            return True
        except Exception as e:
            print(f"[ERROR] Test import {package_name}: {e}")
            return False
