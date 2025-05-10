import os
import sys
import subprocess
from pathlib import Path

REQUIRED_PACKAGES = [
    "flask",
    "matplotlib",
    "openpyxl",
    "requests",
]

def ensure_venv():
    venv_dir = Path(__file__).parent / ".venv"
    if not venv_dir.exists():
        print("[BOOTSTRAP] Tworzę środowisko wirtualne .venv...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    return venv_dir

def pip_install(packages, venv_dir):
    pip_path = venv_dir / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")
    for pkg in packages:
        print(f"[BOOTSTRAP] Instaluję {pkg} ...")
        subprocess.check_call([str(pip_path), "install", pkg])

def main():
    venv_dir = ensure_venv()
    pip_install(REQUIRED_PACKAGES, venv_dir)
    print("[BOOTSTRAP] Środowisko gotowe! Aby aktywować: \n")
    if os.name == "nt":
        print(f"{venv_dir}\\Scripts\\activate.bat")
    else:
        print(f"source {venv_dir}/bin/activate")
    print("\nMożesz uruchomić: python cli.py 'twoje zadanie' lub python api.py")

if __name__ == "__main__":
    main()
