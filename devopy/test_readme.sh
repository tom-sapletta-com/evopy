#!/bin/bash
# Testuje uruchamianie devopy jako standalone i jako paczka pip
set -e

# Standalone test
cd "$(dirname "$0")"
echo "[TEST] Standalone: python3 cli.py 'test standalone'"
python3 cli.py "test standalone"

# API test (standalone)
echo "[TEST] Standalone: python3 api.py (background, 3s)"
python3 api.py &
API_PID=$!
sleep 3
kill $API_PID || true

# Pip package test
cd ..
python3 -m venv .venv_test
source .venv_test/bin/activate
pip install .
echo "[TEST] Pip: python3 -m devopy.cli 'test pip'"
python3 -m devopy.cli "test pip"
echo "[TEST] Pip: python3 -m devopy.api (background, 3s)"
python3 -m devopy.api &
API_PID=$!
sleep 3
kill $API_PID || true

deactivate
rm -rf .venv_test
cd devopy

echo "[TEST] Wszystkie testy zakończone sukcesem!"
