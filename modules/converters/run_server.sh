#!/bin/bash

# Skrypt do uruchamiania serwera Flask dla modułów konwersji

# Przejdź do katalogu skryptu
cd "$(dirname "$0")"

# Utwórz katalog na logi, jeśli nie istnieje
mkdir -p logs

# Data i czas uruchomienia
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="logs/run_server_${TIMESTAMP}.log"

echo "Uruchamianie serwera modułów konwersji..."
echo "Logi będą zapisywane do: $LOG_FILE"

# Sprawdź, czy Python jest dostępny
if ! command -v python3 &> /dev/null; then
    echo "Błąd: Python 3 nie jest zainstalowany" | tee -a "$LOG_FILE"
    exit 1
fi

# Sprawdź, czy pip jest dostępny
if ! command -v pip3 &> /dev/null; then
    echo "Błąd: pip3 nie jest zainstalowany" | tee -a "$LOG_FILE"
    exit 1
fi

# Zainstaluj wymagania
echo "Instalowanie wymagań..." | tee -a "$LOG_FILE"
pip3 install -r requirements.txt 2>&1 | tee -a "$LOG_FILE"

# Uruchom serwer
echo "Uruchamianie serwera..." | tee -a "$LOG_FILE"
echo "Serwer będzie dostępny pod adresem: http://localhost:5000" | tee -a "$LOG_FILE"
echo "Naciśnij Ctrl+C, aby zatrzymać serwer" | tee -a "$LOG_FILE"
echo "-------------------------------------------" | tee -a "$LOG_FILE"

# Znajdź plik serwera (server.py lub inny plik server.*)
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
    echo "Błąd: Nie znaleziono pliku serwera (server.*)" | tee -a "$LOG_FILE"
    exit 1
fi

echo "Uruchamianie serwera: $SERVER_FILE" | tee -a "$LOG_FILE"

# Uruchom serwer i zapisz logi
if [[ "$SERVER_FILE" == *.py ]]; then
    python3 "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
elif [[ "$SERVER_FILE" == *.js ]]; then
    node "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
elif [[ "$SERVER_FILE" == *.sh ]]; then
    bash "$SERVER_FILE" 2>&1 | tee -a "$LOG_FILE"
else
    echo "Błąd: Nieobsługiwany typ pliku serwera: $SERVER_FILE" | tee -a "$LOG_FILE"
    exit 1
fi
