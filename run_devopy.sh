#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "[SETUP] Tworzę środowisko wirtualne (.venv)..."
  python3 -m venv .venv
fi

source .venv/bin/activate

if [ -f "requirements.txt" ]; then
  echo "[SETUP] Instaluję zależności z requirements.txt..."
  pip install --upgrade pip
  pip install -r requirements.txt
else
  echo "[SETUP] Instaluję podstawowe zależności..."
  pip install flask matplotlib openpyxl requests
fi

cd devopy

echo "[RUN] Uruchamiam devopy API..."
python api.py
