import subprocess
import sys
import os
import pytest

def test_cli_excel_plot(tmp_path):
    # Przygotuj plik Excel
    import openpyxl
    excel_file = tmp_path / "test_cli_plot.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["x", "y"])
    for i in range(10):
        ws.append([i, i*i])
    wb.save(excel_file)
    # Uruchom CLI
    cli_path = os.path.join(os.path.dirname(__file__), '../devopy/cli.py')
    result = subprocess.run([
        sys.executable, cli_path, 'stwórz wykres z pliku excel'
    ], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, f"CLI błąd: {result.stderr or result.stdout}"
    # Sprawdź czy plik PNG został wygenerowany
    pngs = list(tmp_path.glob('*.png'))
    assert pngs, f"Nie znaleziono wygenerowanego wykresu PNG! Output: {result.stdout}"
    print(f"[CLI E2E] Wygenerowany wykres: {pngs[0]}")

def test_cli_missing_excel(tmp_path):
    # Uruchom CLI bez pliku Excel
    cli_path = os.path.join(os.path.dirname(__file__), '../devopy/cli.py')
    result = subprocess.run([
        sys.executable, cli_path, 'stwórz wykres z pliku excel'
    ], cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode != 0 or 'Brak pliku Excel' in (result.stdout + result.stderr), \
        "CLI powinien zgłaszać błąd, jeśli nie ma pliku Excel!"
