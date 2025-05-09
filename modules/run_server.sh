#!/bin/bash
# Skrypt uruchamiający serwer modułów w nowej strukturze katalogów

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/.venv"
LOG_DIR="$SCRIPT_DIR/logs"

# Utwórz katalog logów, jeśli nie istnieje
mkdir -p "$LOG_DIR"

# Aktywuj środowisko wirtualne, jeśli istnieje
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
else
    # Wybierz dostępne polecenie Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Nazwa pliku logu z datą i godziną
LOG_FILE="$LOG_DIR/server_$(date +%Y%m%d_%H%M%S).log"

echo "Uruchamianie serwera modułów..."
echo "Logi będą zapisywane do: $LOG_FILE"

# Uruchom serwer modułów
$PYTHON_CMD "$SCRIPT_DIR/server.py" 2>&1 | tee -a "$LOG_FILE"
