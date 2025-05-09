#!/bin/bash
# Skrypt uruchamiający usługi API jako usługi systemowe

# Katalog główny projektu
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
API_SERVICES_DIR="$PROJECT_DIR/api_services"

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

# Funkcja do uruchamiania usługi API
run_api_service() {
    local service_name="$1"
    local service_file="$2"
    local log_file="$LOG_DIR/${service_name}_$(date +%Y%m%d_%H%M%S).log"
    
    echo "Uruchamianie usługi $service_name..."
    echo "Logi będą zapisywane do: $log_file"
    
    # Uruchom usługę API w tle
    nohup $PYTHON_CMD "$service_file" > "$log_file" 2>&1 &
    
    # Zapisz PID usługi
    echo $! > "$LOG_DIR/${service_name}.pid"
    
    echo "Usługa $service_name uruchomiona z PID: $!"
}

# Funkcja do zatrzymywania usługi API
stop_api_service() {
    local service_name="$1"
    local pid_file="$LOG_DIR/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "Zatrzymywanie usługi $service_name (PID: $pid)..."
        
        # Zatrzymaj usługę API
        kill -15 $pid 2>/dev/null || true
        
        # Usuń plik PID
        rm -f "$pid_file"
        
        echo "Usługa $service_name zatrzymana"
    else
        echo "Usługa $service_name nie jest uruchomiona"
    fi
}

# Funkcja do sprawdzania statusu usługi API
check_api_service() {
    local service_name="$1"
    local pid_file="$LOG_DIR/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        
        if ps -p $pid > /dev/null; then
            echo "Usługa $service_name jest uruchomiona (PID: $pid)"
            return 0
        else
            echo "Usługa $service_name nie działa (PID: $pid nie istnieje)"
            rm -f "$pid_file"
            return 1
        fi
    else
        echo "Usługa $service_name nie jest uruchomiona"
        return 1
    fi
}

# Funkcja do wyświetlania pomocy
show_help() {
    echo "Użycie: $0 [opcja] [usługa]"
    echo "Opcje:"
    echo "  start [usługa]    - Uruchamia usługę API (wszystkie, jeśli nie podano nazwy)"
    echo "  stop [usługa]     - Zatrzymuje usługę API (wszystkie, jeśli nie podano nazwy)"
    echo "  restart [usługa]  - Restartuje usługę API (wszystkie, jeśli nie podano nazwy)"
    echo "  status [usługa]   - Sprawdza status usługi API (wszystkie, jeśli nie podano nazwy)"
    echo "  help              - Wyświetla tę pomoc"
    echo ""
    echo "Dostępne usługi:"
    echo "  equation          - Usługa API do analizy równania matematycznego"
    echo "  text2docker       - Usługa API do konwersji tekstu na polecenia Docker"
    echo "  all               - Wszystkie usługi API"
}

# Funkcja do uruchamiania wszystkich usług API
start_all_services() {
    run_api_service "equation" "$API_SERVICES_DIR/equation_api.py"
    run_api_service "text2docker" "$API_SERVICES_DIR/text2docker_api.py"
}

# Funkcja do zatrzymywania wszystkich usług API
stop_all_services() {
    stop_api_service "equation"
    stop_api_service "text2docker"
}

# Funkcja do sprawdzania statusu wszystkich usług API
check_all_services() {
    check_api_service "equation"
    check_api_service "text2docker"
}

# Główna logika skryptu
case "$1" in
    start)
        case "$2" in
            equation)
                run_api_service "equation" "$API_SERVICES_DIR/equation_api.py"
                ;;
            text2docker)
                run_api_service "text2docker" "$API_SERVICES_DIR/text2docker_api.py"
                ;;
            all|"")
                start_all_services
                ;;
            *)
                echo "Nieznana usługa: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    stop)
        case "$2" in
            equation)
                stop_api_service "equation"
                ;;
            text2docker)
                stop_api_service "text2docker"
                ;;
            all|"")
                stop_all_services
                ;;
            *)
                echo "Nieznana usługa: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    restart)
        case "$2" in
            equation)
                stop_api_service "equation"
                run_api_service "equation" "$API_SERVICES_DIR/equation_api.py"
                ;;
            text2docker)
                stop_api_service "text2docker"
                run_api_service "text2docker" "$API_SERVICES_DIR/text2docker_api.py"
                ;;
            all|"")
                stop_all_services
                start_all_services
                ;;
            *)
                echo "Nieznana usługa: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    status)
        case "$2" in
            equation)
                check_api_service "equation"
                ;;
            text2docker)
                check_api_service "text2docker"
                ;;
            all|"")
                check_all_services
                ;;
            *)
                echo "Nieznana usługa: $2"
                show_help
                exit 1
                ;;
        esac
        ;;
    help|"")
        show_help
        ;;
    *)
        echo "Nieznana opcja: $1"
        show_help
        exit 1
        ;;
esac

exit 0
