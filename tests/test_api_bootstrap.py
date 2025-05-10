import subprocess
import sys
import os
import pytest

def test_api_bootstrap():
    # Próba uruchomienia api.py w podprocesie
    api_path = os.path.join(os.path.dirname(__file__), '../devopy/api.py')
    result = subprocess.run([sys.executable, api_path, '--help'], capture_output=True, text=True)
    assert result.returncode in (0, 2, 1), f"api.py nie uruchamia się poprawnie! Wyjście: {result.stderr or result.stdout}"
    # Sprawdź komunikaty o środowisku
    assert 'flask' not in result.stderr.lower(), "Błąd: Flask nie jest zainstalowany lub nie jest wykrywany przez api.py!"
    assert 'externally-managed-environment' not in result.stderr.lower(), "Błąd: PEP 668 - środowisko zarządzane zewnętrznie!"
