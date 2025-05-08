#!/bin/bash
# Skrypt uruchamiający testy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
else
    # Wybierz dostępną komendę Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Uruchom testy
$PYTHON_CMD "$SCRIPT_DIR/test_script.py" $@
