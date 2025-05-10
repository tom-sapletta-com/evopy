#!/bin/bash
# Run script for Evopy Assistant on Linux/macOS

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
RUN_WITH_MODULES="$SCRIPT_DIR/run_with_modules.sh"
MODULES_SERVER="$SCRIPT_DIR/modules/run_server.sh"

# Funkcja wyświetlająca pomoc
show_help() {
    echo "Użycie: $0 [opcje]"
    echo ""
    echo "Opcje:"
    echo "  -h, --help          Wyświetl tę pomoc"
    echo "  -m, --modules       Uruchom tylko serwer modułów konwersji"
    echo "  -a, --all           Uruchom asystenta i serwer modułów (domyślne zachowanie)"
    echo "  -n, --no-modules    Uruchom tylko asystenta bez serwera modułów"
    echo ""
    echo "Bez opcji skrypt uruchamia domyślnie asystenta Evopy wraz z serwerem modułów."
}

# Funkcja uruchamiająca serwer modułów w tle
run_modules_server() {
    echo "Uruchamianie serwera modułów w tle..."
    if [ -f "$MODULES_SERVER" ]; then
        # Sprawdź, czy serwer już nie działa
        if pgrep -f "python.*modules/server.py" > /dev/null; then
            echo "Serwer modułów już działa."
        else
            # Uruchom serwer modułów w tle
            bash "$MODULES_SERVER" > /dev/null 2>&1 &
            # Poczekaj chwilę, aby serwer mógł się uruchomić
            sleep 2
            echo "Serwer modułów uruchomiony. Dostępny pod adresem: http://localhost:5000"
        fi
    else
        echo "Ostrzeżenie: Nie znaleziono skryptu serwera modułów: $MODULES_SERVER"
    fi
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

# Przetwórz argumenty
case "$1" in
    "-h"|"--help")
        show_help
        ;;
    "-m"|"--modules")
        # Uruchom tylko serwer modułów
        run_modules_server
        echo "Serwer modułów uruchomiony. Naciśnij Ctrl+C, aby zakończyć."
        # Czekaj na zakończenie przez użytkownika
        while true; do sleep 1; done
        ;;
    -n|--no-modules)
        # Uruchom tylko asystenta bez serwera modułów
        echo "Uruchamianie asystenta bez serwera modułów..."
        $PYTHON_CMD "$SCRIPT_DIR/evo.py" "${@:2}"
        ;;
    *)
        # Domyślnie uruchom serwer modułów i asystenta
        run_modules_server
        echo "Uruchamianie asystenta Evopy..."
        $PYTHON_CMD "$SCRIPT_DIR/evo.py" "$@"
        ;;
esac
