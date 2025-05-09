#!/bin/bash
# Run script for Evopy Assistant on Linux/macOS with modules support

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
MODULES_DIR="$SCRIPT_DIR/modules/converters"

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

# Aktywuj środowisko wirtualne
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

# Uruchom serwer modułów
run_modules_server() {
    echo "Uruchamianie serwera modułów konwersji..."
    
    # Sprawdź, czy katalog modułów istnieje
    if [ ! -d "$MODULES_DIR" ]; then
        echo "Błąd: Katalog modułów nie istnieje: $MODULES_DIR"
        return 1
    fi
    
    # Przejdź do katalogu modułów
    cd "$MODULES_DIR"
    
    # Uruchom skrypt modułu
    if [ -f "module_server.sh" ]; then
        # Eksportuj zmienne dla skryptu modułu
        export SCRIPT_DIR="$MODULES_DIR"
        export PYTHON_CMD="$PYTHON_CMD"
        
        # Uruchom skrypt
        bash module_server.sh
    else
        echo "Błąd: Skrypt modułu nie istnieje: $MODULES_DIR/module_server.sh"
        return 1
    fi
}

# Uruchom asystenta
run_assistant() {
    echo "Uruchamianie asystenta Evopy..."
    cd "$SCRIPT_DIR"
    $PYTHON_CMD "$SCRIPT_DIR/evo.py" "$@"
}

# Przetwórz argumenty
if [ $# -eq 0 ]; then
    # Bez argumentów uruchom asystenta
    run_assistant
else
    case "$1" in
        -h|--help)
            show_help
            ;;
        -m|--modules)
            run_modules_server
            ;;
        -a|--all)
            # Uruchom serwer modułów w tle
            echo "Uruchamianie serwera modułów w tle..."
            (run_modules_server) &
            
            # Poczekaj chwilę, aby serwer mógł się uruchomić
            sleep 2
            
            # Uruchom asystenta
            run_assistant "${@:2}"
            ;;
        *)
            # Przekaż wszystkie argumenty do asystenta
            run_assistant "$@"
            ;;
    esac
fi
