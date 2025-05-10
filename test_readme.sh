#!/bin/bash
set -e

# Test CLI commands from README.md
echo "[TEST] CLI: pobierz dane z api i zapisz do excela (venv)"
python3 -m devopy.cli run "pobierz dane z api i zapisz do excela"

echo "[TEST] CLI: stwórz wykres z pliku excel (docker)"
python3 -m devopy.cli run "stwórz wykres z pliku excel" --docker

# Start API in background and test curl
FLASK_PID=""
echo "[TEST] API: start Flask in background"
python3 devopy/api.py &
FLASK_PID=$!
sleep 3

echo "[TEST] API: POST /run (docker)"
curl -s -X POST http://localhost:5001/run -H 'Content-Type: application/json' \
  -d '{"task": "pobierz dane z api i zapisz do excela", "docker": true}'

# Kill Flask server
echo "[TEST] API: stop Flask server"
kill $FLASK_PID
