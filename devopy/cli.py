import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))
import argparse
import os
import sys
import subprocess
from pathlib import Path

# Automatyczne tworzenie i aktywacja venv jeśli nie istnieje
venv_dir = Path(__file__).parent / ".venv"
if not venv_dir.exists():
    print("[BOOTSTRAP] Tworzę środowisko wirtualne .venv...")
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_dir)])
    # Po utworzeniu venv uruchom ponownie skrypt już w aktywnym venv
    if os.name == "nt":
        python_path = venv_dir / "Scripts" / "python.exe"
    else:
        python_path = venv_dir / "bin" / "python"
    print(f"[BOOTSTRAP] Restartuję CLI w środowisku: {python_path}")
    os.execv(str(python_path), [str(python_path)] + sys.argv)

try:
    from devopy.orchestrator import Orchestrator
except ModuleNotFoundError:
    from orchestrator import Orchestrator

from log_db import LogDB

def main():
    parser = argparse.ArgumentParser(description="devopy CLI: automatyczne środowiska dla zadań Python")
    parser.add_argument("TASK", type=str, help="Opis zadania do wykonania (np. 'pobierz dane z api i zapisz do excela')")
    parser.add_argument("--docker", action="store_true", help="Użyj sandboxa Docker zamiast venv")
    args = parser.parse_args()

    task = args.TASK
    LogDB.log(
        source="cli",
        level="info",
        message="Uruchamiam zadanie przez CLI",
        request=str({"task": task, "docker": args.docker})
    )
    orch = Orchestrator()
    print("[INFO] Uruchamiam zadanie:", task)
    try:
        result = orch.process_task(task, docker=args.docker)
        LogDB.log(
            source="cli",
            level="info",
            message="Wynik zadania CLI",
            request=str({"task": task, "docker": args.docker}),
            response=str(result)
        )
    except Exception as e:
        LogDB.log(
            source="cli",
            level="error",
            message="Błąd wykonania zadania CLI",
            request=str({"task": task, "docker": args.docker}),
            error=str(e)
        )
        raise

if __name__ == "__main__":
    try:
        from auto_diag_import import auto_diag_import
    except ImportError:
        from devopy.auto_diag_import import auto_diag_import
    auto_diag_import(main)

