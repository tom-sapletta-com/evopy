import os
import sys
import subprocess
from pathlib import Path
import shutil
import pytest

def run_shell_command(cmd, cwd=None, env=None, input_data=None):
    """Helper to run shell command and capture output."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        input=input_data,
        capture_output=True,
        text=True,
        shell=True,
        env=env
    )
    return result.returncode, result.stdout, result.stderr

@pytest.fixture(scope="module")
def setup_venv():
    venv_dir = Path(".devopy_venv")
    if venv_dir.exists():
        shutil.rmtree(venv_dir)
    code, out, err = run_shell_command("python3 -m venv .devopy_venv")
    assert code == 0, f"venv creation failed: {err}"
    yield venv_dir
    shutil.rmtree(venv_dir)

@pytest.fixture(scope="module")
def setup_devopy_dirs():
    app_dir = Path.home() / ".devopy"
    modules_dir = app_dir / "modules"
    if modules_dir.exists():
        shutil.rmtree(modules_dir)
    modules_dir.mkdir(parents=True, exist_ok=True)
    yield modules_dir
    shutil.rmtree(app_dir)

def test_shell_module_install_and_import(setup_venv, setup_devopy_dirs):
    """
    E2E: Sprawdza, czy devopy shell instaluje i importuje moduł (np. text2python) oraz czy środowisko venv działa.
    """
    # Przygotuj komendę do uruchomienia shellu devopy w venv
    venv_python = Path(".devopy_venv") / ("Scripts/python.exe" if os.name == "nt" else "bin/python3")
    main_py = Path("devopy/main.py")
    assert main_py.exists(), "Brak pliku main.py"

    # Symuluj wejście do shellu i polecenie 'użyj text2python', potem exit
    input_script = "użyj text2python\nexit\n"
    code, out, err = run_shell_command(f"{venv_python} {main_py}", input_data=input_script)

    assert code == 0, f"Shell devopy zakończył się błędem: {err}"
    assert "Moduł 'text2python'" in out, "Brak komunikatu o module text2python"
    assert "Kończę pracę shellu devopy." in out, "Shell nie zakończył się poprawnie"


def test_shell_unknown_command(setup_venv, setup_devopy_dirs):
    """
    E2E: Sprawdza reakcję devopy shell na nieznane polecenie.
    """
    venv_python = Path(".devopy_venv") / ("Scripts/python.exe" if os.name == "nt" else "bin/python3")
    main_py = Path("devopy/main.py")
    input_script = "nieznane_polecenie\nexit\n"
    code, out, err = run_shell_command(f"{venv_python} {main_py}", input_data=input_script)
    assert code == 0
    assert "Nieznane polecenie" in out
    assert "Kończę pracę shellu devopy." in out
