#!/bin/bash
# Run script for Evopy Assistant on Linux/macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
RUN_WITH_MODULES="$SCRIPT_DIR/run_with_modules.sh"

# Funkcja wyświetlająca pomoc
show_help() {
    echo "Użycie: $0 [opcje]"
    echo ""
    echo "Opcje:"
    echo "  -h, --help          Wyświetl tę pomoc"
    echo "  -m, --modules       Uruchom serwer modułów konwersji"
    echo "  -a, --all           Uruchom asystenta i serwer modułów"
    echo ""
    echo "Bez opcji skrypt uruchamia domyślnie asystenta Evopy."
}

# Activate virtual environment
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    PYTHON_CMD="python"
else
    # Choose available Python command
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Sprawdź, czy istnieje skrypt run_with_modules.sh
if [ ! -f "$RUN_WITH_MODULES" ]; then
    echo "Błąd: Brak skryptu run_with_modules.sh. Uruchamianie standardowego asystenta."
    $PYTHON_CMD "$SCRIPT_DIR/evo.py" "$@"
    exit 1
fi

# Przetwórz argumenty
case "$1" in
    -h|--help)
        show_help
        ;;
    -m|--modules)
        bash "$RUN_WITH_MODULES" --modules
        ;;
    -a|--all)
        bash "$RUN_WITH_MODULES" --all "${@:2}"
        ;;
    *)
        # Uruchom asystenta z przekazanymi argumentami
        $PYTHON_CMD "$SCRIPT_DIR/evo.py" "$@"
        ;;
esac
