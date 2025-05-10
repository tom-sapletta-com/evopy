import subprocess
import sys
import pytest

def test_pep668_error():
    # Symuluj próbę instalacji pakietu w systemowym Pythonie
    result = subprocess.run([
        sys.executable, '-m', 'pip', 'install', 'flask'
    ], capture_output=True, text=True)
    if 'externally-managed-environment' in result.stderr:
        pytest.skip('System Python jest zarządzany przez PEP 668 (Debian/Ubuntu). Test pominięty.')
    else:
        assert result.returncode == 0, f"pip install flask nie powiodło się: {result.stderr or result.stdout}"
