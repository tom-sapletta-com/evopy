#!/bin/bash
set -e

SRC_DIR="$(dirname "$0")/devopy"
DST_DIR="$HOME/github/tom-sapletta-com/devopy"

# Lista plików/katalogów do skopiowania
INCLUDE_FILES=(
  "README.md"
  "setup.py"
  "devopy"
)
INCLUDE_TESTS="tests"

# Stwórz katalog docelowy jeśli nie istnieje
mkdir -p "$DST_DIR"

# Kopiuj pliki główne
for item in "${INCLUDE_FILES[@]}"; do
  if [ -e "$SRC_DIR/../$item" ]; then
    cp -r "$SRC_DIR/../$item" "$DST_DIR/"
  fi
done

# Kopiuj testy, jeśli istnieją
if [ -d "$SRC_DIR/../$INCLUDE_TESTS" ]; then
  cp -r "$SRC_DIR/../$INCLUDE_TESTS" "$DST_DIR/"
fi

# Usuń niechciane pliki/katalogi z devopy
cd "$DST_DIR/devopy"
rm -rf .venv __pycache__ *.sqlite3 sandbox_envs registry .pytest_cache *.pyc *.pyo *.egg-info

# Wypisz podsumowanie
cd "$DST_DIR"
echo "[INFO] Paczka devopy przygotowana w: $DST_DIR"
echo "[INFO] Zawartość:"
ls -l "$DST_DIR"
echo "[INFO] Gotowe do testów i publikacji!"
