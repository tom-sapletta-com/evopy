import importlib
import subprocess
import sys
import traceback
import re
from pathlib import Path

# Wspiera dynamiczne auto-pobieranie brakujących bibliotek podczas działania kodu

PYPI_SIMPLE_URL = "https://pypi.org/simple/"


def pip_install(package, venv_path=None):
    pip_cmd = [sys.executable, "-m", "pip", "install", package]
    if venv_path:
        pip_cmd[0] = str(Path(venv_path) / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"))
    print(f"[AUTO_DIAG_IMPORT] Instaluję brakującą bibliotekę: {package}")
    subprocess.check_call(pip_cmd)


def try_import(package):
    try:
        return importlib.import_module(package)
    except ImportError:
        pip_install(package)
        return importlib.import_module(package)


def auto_diag_import(code_callable, *args, **kwargs):
    """
    Uruchamia kod, a jeśli pojawi się ImportError, automatycznie instaluje brakującą paczkę i powtarza próbę.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return code_callable(*args, **kwargs)
        except ImportError as e:
            tb = traceback.format_exc()
            print(f"[AUTO_DIAG_IMPORT] Wykryto ImportError: {e}")
            # Spróbuj wyłuskać nazwę brakującego modułu
            match = re.search(r"No module named '([^']+)'", str(e))
            if match:
                missing_pkg = match.group(1)
                pip_install(missing_pkg)
                print(f"[AUTO_DIAG_IMPORT] Zainstalowano: {missing_pkg}, ponawiam próbę...")
            else:
                print("[AUTO_DIAG_IMPORT] Nie rozpoznano brakującego pakietu. Szczegóły:")
                print(tb)
                raise
        except Exception as ex:
            print(f"[AUTO_DIAG_IMPORT] Inny wyjątek: {ex}")
            raise
    print("[AUTO_DIAG_IMPORT] Przekroczono limit prób auto-importu.")
    raise ImportError("Nie udało się automatycznie zainstalować brakującej biblioteki.")

# Przykład użycia:
if __name__ == "__main__":
    def test():
        import loremipsum12345  # nieistniejąca paczka, wywoła błąd
    try:
        auto_diag_import(test)
    except Exception as e:
        print("[AUTO_DIAG_IMPORT] Test zakończony błędem:", e)
