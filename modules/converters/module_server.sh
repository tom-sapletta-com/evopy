#!/bin/bash
# Skrypt uruchamiający serwer modułów konwersji
# Może być uruchamiany bezpośrednio lub przez główny skrypt run.sh

# Funkcja do logowania
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Przejdź do katalogu skryptu, jeśli uruchamiany bezpośrednio
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
fi

# Utwórz katalog na logi, jeśli nie istnieje
mkdir -p logs

# Data i czas uruchomienia
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/module_server_${TIMESTAMP}.log"

log_message "Uruchamianie serwera modułów konwersji..." | tee -a "$LOG_FILE"
log_message "Logi będą zapisywane do: $LOG_FILE" | tee -a "$LOG_FILE"

# Znajdź plik serwera (server.*)
SERVER_FILE=""
if [ -f "server.py" ]; then
    SERVER_FILE="server.py"
else
    # Szukaj dowolnego pliku server.*
    for file in server.*; do
        if [ -f "$file" ]; then
            SERVER_FILE="$file"
            break
        fi
    done
fi

if [ -z "$SERVER_FILE" ]; then
    log_message "Błąd: Nie znaleziono pliku serwera (server.*)" | tee -a "$LOG_FILE"
    exit 1
fi

log_message "Znaleziono plik serwera: $SERVER_FILE" | tee -a "$LOG_FILE"

# Sprawdź, czy wymagania są zainstalowane
if [ -f "requirements.txt" ]; then
    log_message "Instalowanie wymagań z requirements.txt..." | tee -a "$LOG_FILE"
    
    # Użyj aktywowanego środowiska wirtualnego, jeśli istnieje
    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD -m pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
    else
        # Wybierz dostępne polecenie Python
        if command -v python3 >/dev/null 2>&1; then
            python3 -m pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
        else
            python -m pip install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
fi

log_message "Uruchamianie serwera: $SERVER_FILE" | tee -a "$LOG_FILE"
log_message "Serwer będzie dostępny pod adresem: http://localhost:5000" | tee -a "$LOG_FILE"
log_message "Naciśnij Ctrl+C, aby zatrzymać serwer" | tee -a "$LOG_FILE"
log_message "-------------------------------------------" | tee -a "$LOG_FILE"

# Uruchom serwer i zapisz logi
if [[ "$SERVER_FILE" == *.py ]]; then
    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
    else
        if command -v python3 >/dev/null 2>&1; then
            python3 "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
        else
            python "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
        fi
    fi
elif [[ "$SERVER_FILE" == *.js ]]; then
    node "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
elif [[ "$SERVER_FILE" == *.sh ]]; then
    bash "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
else
    log_message "Błąd: Nieobsługiwany typ pliku serwera: $SERVER_FILE" | tee -a "$LOG_FILE"
    exit 1
fi
