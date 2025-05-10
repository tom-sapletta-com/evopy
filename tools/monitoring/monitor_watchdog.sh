#!/bin/bash
# Monitor Watchdog - skrypt zapewniający ciągłe działanie monitora zasobów
# Uruchamiany przez cron co godzinę

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
WATCHDOG_LOG="$LOG_DIR/watchdog.log"

# Utwórz katalog logów, jeśli nie istnieje
mkdir -p "$LOG_DIR"

# Funkcja logowania
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$WATCHDOG_LOG"
    echo "$1"
}

# Sprawdź, czy monitor zasobów działa
if "$SCRIPT_DIR/resource_monitor.sh" status | grep -q "Monitor zasobów jest uruchomiony"; then
    log "Monitor zasobów działa poprawnie."
else
    log "Monitor zasobów nie działa. Uruchamianie..."
    "$SCRIPT_DIR/resource_monitor.sh" start
    
    # Sprawdź, czy uruchomienie się powiodło
    if "$SCRIPT_DIR/resource_monitor.sh" status | grep -q "Monitor zasobów jest uruchomiony"; then
        log "Monitor zasobów został pomyślnie uruchomiony."
    else
        log "BŁĄD: Nie udało się uruchomić monitora zasobów."
    fi
fi

# Sprawdź zużycie zasobów
RAM_USAGE=$(free -m | awk '/^Mem:/ {print $3}')
RAM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
RAM_PERCENT=$((RAM_USAGE * 100 / RAM_TOTAL))

DISK_USAGE=$(df -m / | awk 'NR==2 {print $3}')
DISK_TOTAL=$(df -m / | awk 'NR==2 {print $2}')
DISK_PERCENT=$((DISK_USAGE * 100 / DISK_TOTAL))

log "Aktualne zużycie RAM: $RAM_USAGE MB / $RAM_TOTAL MB ($RAM_PERCENT%)"
log "Aktualne zużycie dysku: $DISK_USAGE MB / $DISK_TOTAL MB ($DISK_PERCENT%)"

# Sprawdź rozmiar pliku assistant.log
if [ -f "$SCRIPT_DIR/assistant.log" ]; then
    LOG_SIZE=$(du -m "$SCRIPT_DIR/assistant.log" | cut -f1)
    log "Rozmiar pliku assistant.log: $LOG_SIZE MB"
    
    # Jeśli plik jest większy niż 1GB, wykonaj rotację
    if [ "$LOG_SIZE" -gt 1000 ]; then
        log "Plik assistant.log przekroczył 1GB. Wykonywanie rotacji..."
        "$SCRIPT_DIR/resource_monitor.sh" clean
    fi
fi

# Sprawdź procesy zombie
ZOMBIE_COUNT=$(ps aux | grep -w Z | grep -v grep | wc -l)
if [ "$ZOMBIE_COUNT" -gt 0 ]; then
    log "Znaleziono $ZOMBIE_COUNT procesów zombie. Próba czyszczenia..."
    
    # Wyświetl procesy zombie
    ZOMBIE_PROCS=$(ps aux | grep -w Z | grep -v grep)
    log "Procesy zombie: $ZOMBIE_PROCS"
    
    # Próba wysłania sygnału SIGCHLD do procesów-rodziców
    for PPID in $(ps aux | grep -w Z | grep -v grep | awk '{print $3}'); do
        if [ -n "$PPID" ] && [ "$PPID" -ne 1 ]; then
            log "Wysyłanie sygnału SIGCHLD do procesu rodzica (PID: $PPID)..."
            kill -s SIGCHLD "$PPID" 2>/dev/null
        fi
    done
fi

# Sprawdź kontenery Docker
if command -v docker &>/dev/null; then
    CONTAINERS=$(docker ps -a --filter "name=evopy" -q | wc -l)
    if [ "$CONTAINERS" -gt 0 ]; then
        log "Znaleziono $CONTAINERS kontenerów Docker związanych z Evopy. Czyszczenie..."
        "$SCRIPT_DIR/resource_monitor.sh" clean
    fi
fi

# Ogranicz rozmiar pliku watchdog.log
if [ -f "$WATCHDOG_LOG" ] && [ "$(du -m "$WATCHDOG_LOG" | cut -f1)" -gt 10 ]; then
    log "Ograniczanie rozmiaru pliku watchdog.log..."
    tail -n 1000 "$WATCHDOG_LOG" > "$WATCHDOG_LOG.tmp"
    mv "$WATCHDOG_LOG.tmp" "$WATCHDOG_LOG"
fi

log "Watchdog zakończył działanie."
