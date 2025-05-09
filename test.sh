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

# Wyświetl informację o uruchamianych testach
echo "=== Uruchamianie testów Evopy ==="
echo "Wersja Python: $($PYTHON_CMD --version)"
echo

# Uruchom testy podstawowych zapytań
echo "1. Testy podstawowych zapytań:"
$PYTHON_CMD "$SCRIPT_DIR/test_queries.py"
QUERIES_RESULT=$?

# Uruchom pozostałe testy, jeśli istnieją
if [ -f "$SCRIPT_DIR/test_script.py" ]; then
    echo "\n2. Testy ogólne systemu:"
    $PYTHON_CMD "$SCRIPT_DIR/test_script.py" $@
    GENERAL_RESULT=$?
else
    GENERAL_RESULT=0
fi

# Podsumowanie testów
echo "\n=== Podsumowanie testów ==="
if [ $QUERIES_RESULT -eq 0 ] && [ $GENERAL_RESULT -eq 0 ]; then
    echo "✓ Wszystkie testy zakończone pomyślnie"
    exit 0
else
    echo "✗ Niektóre testy nie powiodły się"
    exit 1
fi
