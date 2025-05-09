#!/bin/bash
# Skrypt uruchamiający monitor zasobów systemowych dla projektu Evopy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kolory dla terminala
if [ -t 1 ]; then
    BLUE='\033[0;34m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
else
    BLUE=''
    GREEN=''
    YELLOW=''
    RED=''
    NC=''
fi

# Aktywacja środowiska wirtualnego i sprawdzenie zależności
function check_dependencies() {
    echo -e "${BLUE}Sprawdzanie środowiska wirtualnego...${NC}"
    
    # Sprawdź czy istnieje środowisko wirtualne
    if [ -d "$SCRIPT_DIR/.venv" ]; then
        VENV_DIR="$SCRIPT_DIR/.venv"
        PYTHON_CMD="$VENV_DIR/bin/python"
        PIP_CMD="$VENV_DIR/bin/pip"
        echo -e "${GREEN}Znaleziono środowisko wirtualne w .venv${NC}"
    elif [ -d "$SCRIPT_DIR/venv" ]; then
        VENV_DIR="$SCRIPT_DIR/venv"
        PYTHON_CMD="$VENV_DIR/bin/python"
        PIP_CMD="$VENV_DIR/bin/pip"
        echo -e "${GREEN}Znaleziono środowisko wirtualne w venv${NC}"
    else
        echo -e "${YELLOW}Nie znaleziono środowiska wirtualnego. Tworzenie nowego...${NC}"
        python3 -m venv "$SCRIPT_DIR/.venv"
        VENV_DIR="$SCRIPT_DIR/.venv"
        PYTHON_CMD="$VENV_DIR/bin/python"
        PIP_CMD="$VENV_DIR/bin/pip"
    fi
    
    # Sprawdź czy wymagane pakiety Pythona są zainstalowane
    echo -e "${BLUE}Sprawdzanie wymaganych pakietów Pythona...${NC}"
    
    # Lista wymaganych pakietów
    REQUIRED_PACKAGES=("psutil")
    
    for package in "${REQUIRED_PACKAGES[@]}"; do
        if ! $PIP_CMD list | grep -q "$package"; then
            echo -e "${YELLOW}Pakiet $package nie jest zainstalowany. Instalowanie...${NC}"
            $PIP_CMD install "$package"
        fi
    done
    
    echo -e "${GREEN}Wszystkie zależności są zainstalowane.${NC}"
    
    # Eksportuj zmienne dla innych funkcji
    export PYTHON_CMD
    export PIP_CMD
}

# Funkcja do uruchomienia monitora zasobów
function start_monitor() {
    echo -e "${BLUE}Uruchamianie monitora zasobów systemowych...${NC}"
    
    # Sprawdź, czy monitor już działa
    if pgrep -f "$SCRIPT_DIR/monitor_resources.py" > /dev/null; then
        echo -e "${YELLOW}Monitor zasobów już działa.${NC}"
        return 0
    fi
    
    # Uruchom monitor w tle
    $PYTHON_CMD "$SCRIPT_DIR/monitor_resources.py" > "$SCRIPT_DIR/logs/monitor.log" 2>&1 &
    MONITOR_PID=$!
    
    # Zapisz PID do pliku
    echo $MONITOR_PID > "$SCRIPT_DIR/monitor.pid"
    
    # Sprawdź, czy monitor został uruchomiony
    sleep 2
    if ps -p $MONITOR_PID > /dev/null; then
        echo -e "${GREEN}Monitor zasobów został uruchomiony pomyślnie (PID: $MONITOR_PID).${NC}"
    else
        echo -e "${RED}Nie udało się uruchomić monitora zasobów.${NC}"
        # Spróbuj uruchomić w trybie interaktywnym
        echo -e "${YELLOW}Próba uruchomienia w trybie interaktywnym...${NC}"
        $PYTHON_CMD "$SCRIPT_DIR/monitor_resources.py" &
    fi
}

# Funkcja do zatrzymania monitora zasobów
function stop_monitor() {
    echo -e "${BLUE}Zatrzymywanie monitora zasobów systemowych...${NC}"
    
    # Sprawdź, czy istnieje plik PID
    if [ -f "$SCRIPT_DIR/monitor.pid" ]; then
        MONITOR_PID=$(cat "$SCRIPT_DIR/monitor.pid")
    else
        # Znajdź PID procesu monitora
        MONITOR_PID=$(pgrep -f "$SCRIPT_DIR/monitor_resources.py")
    fi
    
    if [ -z "$MONITOR_PID" ]; then
        echo -e "${YELLOW}Monitor zasobów nie jest uruchomiony.${NC}"
        return 0
    fi
    
    # Zatrzymaj proces
    kill "$MONITOR_PID" 2>/dev/null
    
    # Sprawdź, czy proces został zatrzymany
    sleep 2
    if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
        echo -e "${RED}Nie udało się zatrzymać monitora zasobów. Próba użycia SIGKILL...${NC}"
        kill -9 "$MONITOR_PID" 2>/dev/null
    else
        echo -e "${GREEN}Monitor zasobów został zatrzymany pomyślnie.${NC}"
    fi
    
    # Usuń plik PID
    if [ -f "$SCRIPT_DIR/monitor.pid" ]; then
        rm "$SCRIPT_DIR/monitor.pid"
    fi
}

# Funkcja do sprawdzenia statusu monitora zasobów
function status_monitor() {
    # Sprawdź, czy istnieje plik PID
    if [ -f "$SCRIPT_DIR/monitor.pid" ]; then
        MONITOR_PID=$(cat "$SCRIPT_DIR/monitor.pid")
        if ps -p "$MONITOR_PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Monitor zasobów jest uruchomiony (PID: $MONITOR_PID).${NC}"
            
            # Pokaż zużycie zasobów przez monitor
            echo -e "${BLUE}Zużycie zasobów przez monitor:${NC}"
            ps -p "$MONITOR_PID" -o %cpu,%mem,rss
            
            # Pokaż aktualne zużycie systemu
            echo -e "${BLUE}Aktualne zużycie systemu:${NC}"
            free -h | grep -v total
            df -h / | grep -v Filesystem
            
            # Pokaż ostatnie wpisy z logu monitora
            LOG_FILE="$SCRIPT_DIR/logs/monitor.log"
            if [ -f "$LOG_FILE" ]; then
                echo -e "${BLUE}Ostatnie wpisy z logu monitora:${NC}"
                tail -n 10 "$LOG_FILE"
            fi
            return 0
        fi
    fi
    
    # Sprawdź, czy monitor działa (alternatywna metoda)
    MONITOR_PID=$(pgrep -f "$SCRIPT_DIR/monitor_resources.py")
    if [ -n "$MONITOR_PID" ]; then
        echo -e "${GREEN}Monitor zasobów jest uruchomiony (PID: $MONITOR_PID).${NC}"
        
        # Pokaż zużycie zasobów przez monitor
        echo -e "${BLUE}Zużycie zasobów przez monitor:${NC}"
        ps -p "$MONITOR_PID" -o %cpu,%mem,rss
        
        # Pokaż aktualne zużycie systemu
        echo -e "${BLUE}Aktualne zużycie systemu:${NC}"
        free -h | grep -v total
        df -h / | grep -v Filesystem
        
        # Zapisz PID do pliku
        echo $MONITOR_PID > "$SCRIPT_DIR/monitor.pid"
    else
        echo -e "${YELLOW}Monitor zasobów nie jest uruchomiony.${NC}"
    fi
}

# Funkcja do jednorazowego sprawdzenia zasobów
function check_resources() {
    echo -e "${BLUE}Wykonywanie jednorazowego sprawdzenia zasobów...${NC}"
    
    # Utwórz katalog logów jeśli nie istnieje
    mkdir -p "$SCRIPT_DIR/logs"
    
    # Pokaż aktualne zużycie systemu
    echo -e "${BLUE}Aktualne zużycie systemu:${NC}"
    echo -e "${YELLOW}Pamięć RAM:${NC}"
    free -h | grep -v total
    
    echo -e "${YELLOW}Dysk:${NC}"
    df -h / | grep -v Filesystem
    
    echo -e "${YELLOW}Największe pliki w projekcie Evopy:${NC}"
    find "$SCRIPT_DIR" -type f -exec du -h {} \; | sort -rh | head -n 10
    
    echo -e "${YELLOW}Procesy zużywające najwięcej pamięci:${NC}"
    ps aux --sort=-%mem | head -n 6
    
    # Sprawdź procesy zombie
    ZOMBIE_COUNT=$(ps aux | grep -w Z | grep -v grep | wc -l)
    if [ "$ZOMBIE_COUNT" -gt 0 ]; then
        echo -e "${RED}Znaleziono $ZOMBIE_COUNT procesów zombie:${NC}"
        ps aux | grep -w Z | grep -v grep
    else
        echo -e "${GREEN}Brak procesów zombie.${NC}"
    fi
    
    # Sprawdź kontenery Docker
    if command -v docker &> /dev/null; then
        CONTAINERS=$(docker ps -a --filter "name=evopy" -q | wc -l)
        if [ "$CONTAINERS" -gt 0 ]; then
            echo -e "${YELLOW}Znaleziono $CONTAINERS kontenerów Docker związanych z Evopy:${NC}"
            docker ps -a --filter "name=evopy"
        else
            echo -e "${GREEN}Brak kontenerów Docker związanych z Evopy.${NC}"
        fi
    fi
    
    # Sprawdź rozmiar pliku assistant.log
    if [ -f "$SCRIPT_DIR/assistant.log" ]; then
        LOG_SIZE=$(du -h "$SCRIPT_DIR/assistant.log" | cut -f1)
        echo -e "${YELLOW}Rozmiar pliku assistant.log: $LOG_SIZE${NC}"
    fi
}

# Funkcja do czyszczenia logów
function clean_logs() {
    echo -e "${BLUE}Czyszczenie plików logów...${NC}"
    
    # Główny plik logu asystenta
    ASSISTANT_LOG="$SCRIPT_DIR/assistant.log"
    if [ -f "$ASSISTANT_LOG" ]; then
        echo -e "${YELLOW}Ograniczanie rozmiaru pliku assistant.log...${NC}"
        # Ogranicz rozmiar do 10MB
        truncate -s 10M "$ASSISTANT_LOG"
    fi
    
    # Katalog logów
    LOG_DIR="$SCRIPT_DIR/logs"
    if [ -d "$LOG_DIR" ]; then
        echo -e "${YELLOW}Usuwanie starych plików logów (starszych niż 30 dni)...${NC}"
        find "$LOG_DIR" -name "*.log*" -type f -mtime +30 -delete
    fi
    
    echo -e "${GREEN}Czyszczenie logów zakończone.${NC}"
}

# Funkcja do czyszczenia kontenerów Docker
function clean_docker() {
    echo -e "${BLUE}Czyszczenie kontenerów Docker...${NC}"
    
    # Sprawdź, czy Docker jest zainstalowany
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}Docker nie jest zainstalowany.${NC}"
        return 1
    fi
    
    # Znajdź i usuń kontenery związane z Evopy
    CONTAINERS=$(docker ps -a --filter "name=evopy" -q)
    if [ -n "$CONTAINERS" ]; then
        echo -e "${YELLOW}Znaleziono kontenery Evopy. Usuwanie...${NC}"
        docker stop $CONTAINERS 2>/dev/null
        docker rm $CONTAINERS 2>/dev/null
        echo -e "${GREEN}Kontenery zostały usunięte.${NC}"
    else
        echo -e "${GREEN}Nie znaleziono kontenerów Docker związanych z Evopy.${NC}"
    fi
}

# Funkcja do generowania raportu o zasobach
function generate_report() {
    echo -e "${BLUE}Generowanie raportu o zasobach systemowych...${NC}"
    
    # Uruchom monitor_resources.py z argumentem --report
    if [ -f "$SCRIPT_DIR/monitor_resources.py" ]; then
        $PYTHON_CMD "$SCRIPT_DIR/monitor_resources.py" --report
    else
        echo -e "${RED}Nie znaleziono skryptu monitor_resources.py${NC}"
        
        # Wygeneruj podstawowy raport za pomocą narzędzi systemowych
        echo -e "\n${YELLOW}=== PODSTAWOWY RAPORT ZASOBÓW SYSTEMU ===${NC}\n"
        
        # Informacje o CPU
        echo -e "${YELLOW}CPU:${NC}"
        top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "  Użycie CPU: " 100-$1 "%"}'
        
        # Informacje o pamięci RAM
        echo -e "\n${YELLOW}Pamięć RAM:${NC}"
        free -h | grep -v total | grep Mem | awk '{print "  Całkowita: "$2"\n  Używana: "$3"\n  Wolna: "$4}'
        
        # Informacje o dysku
        echo -e "\n${YELLOW}Dysk:${NC}"
        df -h / | grep -v Filesystem | awk '{print "  Całkowita: "$2"\n  Używana: "$3" ("$5")\n  Wolna: "$4}'
        
        # Informacje o procesach
        echo -e "\n${YELLOW}Najbardziej obciążające procesy:${NC}"
        ps aux --sort=-%mem | head -n 6
        
        # Informacje o kontenerach Docker
        if command -v docker &> /dev/null; then
            echo -e "\n${YELLOW}Kontenery Docker:${NC}"
            docker ps -a --filter "name=evopy" || echo "  Brak działających kontenerów"
        fi
    fi
}

# Funkcja wyświetlająca pomoc
function show_help() {
    echo -e "${BLUE}Monitor zasobów dla projektu Evopy${NC}"
    echo -e "Użycie: $0 [opcja]"
    echo ""
    echo -e "${YELLOW}Opcje:${NC}"
    echo -e "  start     - Uruchamia monitor zasobów w tle"
    echo -e "  stop      - Zatrzymuje monitor zasobów"
    echo -e "  status    - Sprawdza status monitora zasobów"
    echo -e "  check     - Wykonuje jednorazowe sprawdzenie zasobów"
    echo -e "  report    - Generuje raport o zasobach systemowych"
    echo -e "  clean     - Czyści logi i nieaktywne kontenery Docker"
    echo -e "  help      - Wyświetla tę pomoc"
    echo ""
}

# Główna funkcja
function main() {
    # Sprawdź czy podano argument
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # Sprawdź zależności
    check_dependencies
    
    # Obsługa argumentów
    case "$1" in
        start)
            start_monitor
            ;;
        stop)
            stop_monitor
            ;;
        status)
            status_monitor
            ;;
        check)
            check_resources
            ;;
        report)
            generate_report
            ;;
        clean)
            clean_logs
            clean_docker
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}Nieznana opcja: $1${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Uruchom główną funkcję z przekazanymi argumentami
main "$@"
