#!/bin/bash
# Skrypt do generowania raportów porównawczych dla różnych modeli LLM
# Wersja z rozszerzonymi logami diagnostycznymi

# Ustawienia
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
REPORTS_DIR="$SCRIPT_DIR/reports"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/report_debug_$(date +%Y%m%d_%H%M%S).log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Kolory dla terminala
if [ -t 1 ]; then
    BLUE='\033[0;34m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    CYAN='\033[0;36m'
    BOLD='\033[1m'
    NC='\033[0m' # No Color
else
    BLUE=''
    GREEN=''
    YELLOW=''
    RED=''
    CYAN=''
    BOLD=''
    NC=''
fi

# Funkcja do logowania
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Utwórz katalog logów, jeśli nie istnieje
    mkdir -p "$LOG_DIR"
    
    # Zapisz do pliku logów
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
    
    # Wyświetl na ekranie z odpowiednim kolorem
    case "$level" in
        "INFO")
            echo -e "${BLUE}[$timestamp] [INFO] $message${NC}"
            ;;
        "WARNING")
            echo -e "${YELLOW}[$timestamp] [WARNING] $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}[$timestamp] [ERROR] $message${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[$timestamp] [SUCCESS] $message${NC}"
            ;;
        "DEBUG")
            echo -e "${CYAN}[$timestamp] [DEBUG] $message${NC}"
            ;;
        *)
            echo -e "[$timestamp] [$level] $message"
            ;;
    esac
}

# Funkcja do sprawdzania dostępnych modeli Ollama
check_available_models() {
    log "INFO" "Sprawdzanie dostępnych modeli Ollama..."
    
    # Sprawdź czy Ollama jest zainstalowana
    if ! command -v ollama &> /dev/null; then
        log "ERROR" "Ollama nie jest zainstalowana. Zainstaluj Ollama przed uruchomieniem testów."
        return 1
    fi
    
    # Sprawdź czy Ollama jest uruchomiona
    if ! pgrep -x "ollama" > /dev/null; then
        log "WARNING" "Proces Ollama nie jest uruchomiony. Próba uruchomienia..."
        ollama serve &> /dev/null &
        sleep 2
        
        if ! pgrep -x "ollama" > /dev/null; then
            log "ERROR" "Nie można uruchomić Ollama. Uruchom Ollama ręcznie przed kontynuowaniem."
            return 1
        else
            log "SUCCESS" "Ollama została pomyślnie uruchomiona."
        fi
    else
        log "INFO" "Ollama jest już uruchomiona."
    fi
    
    # Pobierz listę dostępnych modeli
    log "DEBUG" "Wykonuję: ollama list"
    OLLAMA_LIST_OUTPUT=$(ollama list 2>&1)
    OLLAMA_LIST_EXIT_CODE=$?
    
    if [ $OLLAMA_LIST_EXIT_CODE -ne 0 ]; then
        log "ERROR" "Błąd podczas pobierania listy modeli Ollama: $OLLAMA_LIST_OUTPUT"
        return 1
    fi
    
    log "DEBUG" "Wyjście komendy 'ollama list':\n$OLLAMA_LIST_OUTPUT"
    
    # Przetwórz listę modeli
    OLLAMA_MODELS=$(echo "$OLLAMA_LIST_OUTPUT" | awk 'NR>1 {print $1}' | cut -d':' -f1 | sort -u)
    
    if [ -z "$OLLAMA_MODELS" ]; then
        log "WARNING" "Nie znaleziono żadnych modeli Ollama. Czy chcesz pobrać domyślny model llama3? (t/n)"
        read -r answer
        if [[ "$answer" =~ ^[Tt]$ ]]; then
            log "INFO" "Pobieranie modelu llama3..."
            ollama pull llama3
            OLLAMA_MODELS="llama3"
        else
            log "ERROR" "Brak dostępnych modeli. Nie można kontynuować."
            return 1
        fi
    fi
    
    # Wyświetl znalezione modele
    log "SUCCESS" "Znaleziono następujące modele Ollama:"
    echo "$OLLAMA_MODELS" | while read -r model; do
        log "INFO" "  - $model"
    done
    
    # Zapisz listę modeli do pliku tymczasowego
    echo "$OLLAMA_MODELS" > /tmp/evopy_available_models.txt
    
    return 0
}

# Funkcja do wyboru modeli do testowania
select_models_to_test() {
    log "INFO" "Wybieranie modeli do testowania..."
    
    # Pobierz listę dostępnych modeli
    AVAILABLE_MODELS=$(cat /tmp/evopy_available_models.txt)
    
    # Utwórz numerowaną listę modeli
    MODEL_COUNT=0
    declare -a MODEL_ARRAY
    
    echo "$AVAILABLE_MODELS" | while read -r model; do
        MODEL_COUNT=$((MODEL_COUNT + 1))
        MODEL_ARRAY[$MODEL_COUNT]=$model
        echo "$MODEL_COUNT) $model"
    done
    
    # Poproś użytkownika o wybór modeli
    echo
    echo "Wybierz modele do testowania (podaj numery oddzielone spacją, np. '1 3 5')"
    echo "Wpisz 'all' aby wybrać wszystkie modele"
    echo "Lub wybierz z poniższych opcji:"
    echo "a) Wszystkie modele"
    echo "q) Anuluj"
    echo
    read -r -p "Twój wybór: " choice
    
    # Przetwórz wybór użytkownika
    if [[ "$choice" == "q" ]]; then
        log "INFO" "Anulowano wybór modeli."
        return 1
    elif [[ "$choice" == "a" || "$choice" == "all" ]]; then
        log "INFO" "Wybrano wszystkie modele."
        SELECTED_MODELS="$AVAILABLE_MODELS"
    else
        # Przetwórz wybrane numery
        SELECTED_MODELS=""
        for num in $choice; do
            if [[ "$num" =~ ^[0-9]+$ ]] && [ "$num" -le "$MODEL_COUNT" ] && [ "$num" -gt 0 ]; then
                model_name=${MODEL_ARRAY[$num]}
                SELECTED_MODELS="$SELECTED_MODELS $model_name"
                log "DEBUG" "Dodano model $model_name do listy wybranych modeli."
            else
                log "WARNING" "Nieprawidłowy numer modelu: $num. Pomijam."
            fi
        done
    fi
    
    # Sprawdź czy wybrano jakiekolwiek modele
    if [ -z "$SELECTED_MODELS" ]; then
        log "ERROR" "Nie wybrano żadnych modeli. Nie można kontynuować."
        return 1
    fi
    
    # Zapisz wybrane modele do pliku tymczasowego
    echo "$SELECTED_MODELS" > /tmp/evopy_selected_models.txt
    log "SUCCESS" "Wybrano następujące modele do testowania: $SELECTED_MODELS"
    
    return 0
}

# Funkcja do uruchamiania testów dla pojedynczego modelu
run_tests_for_model() {
    local model_id="$1"
    log "INFO" "=== Uruchamianie testów dla modelu: $model_id ==="
    
    # Sprawdź czy model jest dostępny
    if ! grep -q "$model_id" /tmp/evopy_available_models.txt; then
        log "WARNING" "Model $model_id nie jest dostępny w Ollama. Próba pobrania..."
        
        # Próba pobrania modelu
        log "DEBUG" "Wykonuję: ollama pull $model_id"
        PULL_OUTPUT=$(ollama pull "$model_id" 2>&1)
        PULL_EXIT_CODE=$?
        
        if [ $PULL_EXIT_CODE -ne 0 ]; then
            log "ERROR" "Nie można pobrać modelu $model_id: $PULL_OUTPUT"
            log "WARNING" "Testy dla modelu $model_id zostaną uruchomione, ale mogą zakończyć się niepowodzeniem."
        else
            log "SUCCESS" "Model $model_id został pomyślnie pobrany."
        fi
    fi
    
    # Ustaw model w pliku .env
    log "DEBUG" "Aktualizacja pliku .env dla modelu $model_id..."
    
    # Sprawdź czy plik .env istnieje
    if [ ! -f "$CONFIG_DIR/.env" ]; then
        log "WARNING" "Plik .env nie istnieje. Tworzenie..."
        mkdir -p "$CONFIG_DIR"
        echo "ACTIVE_MODEL=$model_id" > "$CONFIG_DIR/.env"
    else
        # Sprawdź uprawnienia do pliku .env
        if [ ! -w "$CONFIG_DIR/.env" ]; then
            log "WARNING" "Brak uprawnień do zapisu w pliku .env. Zmiany będą obowiązywać tylko dla bieżącej sesji."
        else
            # Aktualizuj plik .env
            if grep -q "^ACTIVE_MODEL=" "$CONFIG_DIR/.env"; then
                # Zastąp istniejącą linię
                sed -i "s/^ACTIVE_MODEL=.*/ACTIVE_MODEL=$model_id/" "$CONFIG_DIR/.env"
            else
                # Dodaj nową linię
                echo "ACTIVE_MODEL=$model_id" >> "$CONFIG_DIR/.env"
            fi
        fi
    fi
    
    # Ustaw zmienną środowiskową dla bieżącej sesji
    export ACTIVE_MODEL="$model_id"
    log "DEBUG" "Ustawiono ACTIVE_MODEL=$model_id"
    
    # Uruchom testy podstawowych zapytań
    log "INFO" "1. Testy podstawowych zapytań:"
    log "DEBUG" "Wykonuję: python test_queries.py --model=$model_id"
    
    echo
    echo "=== Uruchamianie testów podstawowych zapytań ==="
    echo
    
    python "$SCRIPT_DIR/test_queries.py" --model="$model_id"
    QUERIES_EXIT_CODE=$?
    
    if [ $QUERIES_EXIT_CODE -ne 0 ]; then
        log "ERROR" "Testy podstawowych zapytań zakończyły się niepowodzeniem z kodem: $QUERIES_EXIT_CODE"
    else
        log "SUCCESS" "Testy podstawowych zapytań zakończone pomyślnie."
    fi
    
    # Uruchom testy poprawności
    log "INFO" "2. Testy poprawności:"
    log "DEBUG" "Wykonuję: python tests/correctness/correctness_test.py --model=$model_id"
    
    echo
    echo "=== Uruchamianie testów poprawności ==="
    echo
    
    python "$SCRIPT_DIR/tests/correctness/correctness_test.py" --model="$model_id"
    CORRECTNESS_EXIT_CODE=$?
    
    if [ $CORRECTNESS_EXIT_CODE -ne 0 ]; then
        log "ERROR" "Testy poprawności zakończyły się niepowodzeniem z kodem: $CORRECTNESS_EXIT_CODE"
    else
        log "SUCCESS" "Testy poprawności zakończone pomyślnie."
    fi
    
    # Uruchom testy wydajności
    log "INFO" "3. Testy wydajności:"
    log "DEBUG" "Wykonuję: python tests/performance/performance_test.py --model=$model_id"
    
    echo
    echo "=== Uruchamianie testów wydajności ==="
    echo
    
    python "$SCRIPT_DIR/tests/performance/performance_test.py" --model="$model_id"
    PERFORMANCE_EXIT_CODE=$?
    
    if [ $PERFORMANCE_EXIT_CODE -ne 0 ]; then
        log "ERROR" "Testy wydajności zakończyły się niepowodzeniem z kodem: $PERFORMANCE_EXIT_CODE"
    else
        log "SUCCESS" "Testy wydajności zakończone pomyślnie."
    fi
    
    # Zapisz wyniki testów do pliku JSON
    RESULTS_FILE="$REPORTS_DIR/results_${model_id}_$TIMESTAMP.json"
    
    # Utwórz katalog raportów, jeśli nie istnieje
    mkdir -p "$REPORTS_DIR"
    
    # Utwórz plik wyników
    cat > "$RESULTS_FILE" << EOF
{
    "model_id": "$model_id",
    "timestamp": "$TIMESTAMP",
    "queries_test": {
        "exit_code": $QUERIES_EXIT_CODE,
        "status": $([ $QUERIES_EXIT_CODE -eq 0 ] && echo '"success"' || echo '"failure"')
    },
    "correctness_test": {
        "exit_code": $CORRECTNESS_EXIT_CODE,
        "status": $([ $CORRECTNESS_EXIT_CODE -eq 0 ] && echo '"success"' || echo '"failure"')
    },
    "performance_test": {
        "exit_code": $PERFORMANCE_EXIT_CODE,
        "status": $([ $PERFORMANCE_EXIT_CODE -eq 0 ] && echo '"success"' || echo '"failure"')
    }
}
EOF
    
    log "SUCCESS" "Wyniki zapisane do: $RESULTS_FILE"
    
    # Podsumowanie testów dla modelu
    echo
    echo "=== Podsumowanie testów dla modelu: $model_id ==="
    if [ $QUERIES_EXIT_CODE -eq 0 ] && [ $CORRECTNESS_EXIT_CODE -eq 0 ] && [ $PERFORMANCE_EXIT_CODE -eq 0 ]; then
        echo "✓ Wszystkie testy zakończone pomyślnie"
    else
        echo "✗ Niektóre testy zakończyły się niepowodzeniem"
    fi
    echo "Wyniki zapisane do: $RESULTS_FILE"
    echo
    
    return 0
}

# Funkcja do generowania raportu porównawczego
generate_comparison_report() {
    log "INFO" "Generowanie raportu porównawczego..."
    
    # Utwórz katalog raportów, jeśli nie istnieje
    mkdir -p "$REPORTS_DIR"
    
    # Plik raportu
    REPORT_FILE="$REPORTS_DIR/comparison_report_$TIMESTAMP.md"
    
    # Nagłówek raportu
    cat > "$REPORT_FILE" << EOF
# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: $(date '+%Y-%m-%d %H:%M:%S')

## Podsumowanie wyników

| Model | Wersja | Rozmiar | Parametry | Testy zapytań (linie kodu) | Testy poprawności (%) | Testy wydajności (s) | Całkowity wynik |
|-------|--------|---------|-----------|----------------------------|----------------------|----------------------|------------------|
EOF
    
    # Pobierz listę przetestowanych modeli
    TESTED_MODELS=$(ls "$REPORTS_DIR"/results_*_"$TIMESTAMP".json 2>/dev/null | sed -E "s/.*results_(.*)_$TIMESTAMP.json/\1/")
    
    if [ -z "$TESTED_MODELS" ]; then
        log "ERROR" "Nie znaleziono wyników testów. Nie można wygenerować raportu."
        return 1
    fi
    
    # Dodaj wiersz dla każdego modelu
    for model in $TESTED_MODELS; do
        log "DEBUG" "Przetwarzanie wyników dla modelu: $model"
        
        # Pobierz wyniki testów
        RESULTS_FILE="$REPORTS_DIR/results_${model}_$TIMESTAMP.json"
        
        if [ ! -f "$RESULTS_FILE" ]; then
            log "WARNING" "Nie znaleziono pliku wyników dla modelu $model. Pomijam."
            continue
        fi
        
        # Pobierz wyniki testów zapytań (linie kodu)
        QUERIES_RESULTS_FILE=$(ls "$SCRIPT_DIR/test_results"/test_results_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        if [ -n "$QUERIES_RESULTS_FILE" ] && [ -f "$QUERIES_RESULTS_FILE" ]; then
            # Pobierz liczbę linii wygenerowanego kodu
            CODE_LINES=$(grep -o '"code_length":[0-9]*' "$QUERIES_RESULTS_FILE" | awk -F':' '{sum += $2} END {print sum}')
            # Jeśli nie znaleziono, sprawdź alternatywne pola
            if [ -z "$CODE_LINES" ] || [ "$CODE_LINES" == "0" ]; then
                CODE_LINES=$(grep -o '"code_size":[0-9]*' "$QUERIES_RESULTS_FILE" | awk -F':' '{sum += $2} END {print sum}')
            fi
            # Jeśli nadal nie znaleziono, użyj liczby testów
            if [ -z "$CODE_LINES" ] || [ "$CODE_LINES" == "0" ]; then
                PASSED_TESTS=$(grep -o '"passed_tests":[0-9]*' "$QUERIES_RESULTS_FILE" | cut -d':' -f2)
                TOTAL_TESTS=$(grep -o '"total_tests":[0-9]*' "$QUERIES_RESULTS_FILE" | cut -d':' -f2)
                CODE_LINES="${PASSED_TESTS:-0}/${TOTAL_TESTS:-0}"
            fi
        else
            CODE_LINES="N/A"
        fi
        
        # Pobierz wyniki testów poprawności (%)
        T2P_CORRECTNESS_FILE=$(ls "$SCRIPT_DIR/tests/correctness/results"/text2python_correctness_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        P2T_CORRECTNESS_FILE=$(ls "$SCRIPT_DIR/tests/correctness/results"/python2text_correctness_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        
        CORRECTNESS_PERCENT="N/A"
        T2P_PASSED=0
        T2P_TOTAL=0
        P2T_PASSED=0
        P2T_TOTAL=0
        
        if [ -n "$T2P_CORRECTNESS_FILE" ] && [ -f "$T2P_CORRECTNESS_FILE" ]; then
            T2P_PASSED=$(grep -o '"passed_tests":[0-9]*' "$T2P_CORRECTNESS_FILE" | cut -d':' -f2)
            T2P_TOTAL=$(grep -o '"total_tests":[0-9]*' "$T2P_CORRECTNESS_FILE" | cut -d':' -f2)
        fi
        
        if [ -n "$P2T_CORRECTNESS_FILE" ] && [ -f "$P2T_CORRECTNESS_FILE" ]; then
            P2T_PASSED=$(grep -o '"passed_tests":[0-9]*' "$P2T_CORRECTNESS_FILE" | cut -d':' -f2)
            P2T_TOTAL=$(grep -o '"total_tests":[0-9]*' "$P2T_CORRECTNESS_FILE" | cut -d':' -f2)
        fi
        
        # Oblicz procent poprawności
        TOTAL_PASSED=$((T2P_PASSED + P2T_PASSED))
        TOTAL_TESTS=$((T2P_TOTAL + P2T_TOTAL))
        
        if [ "$TOTAL_TESTS" -gt 0 ]; then
            CORRECTNESS_PERCENT=$(( (TOTAL_PASSED * 100) / TOTAL_TESTS ))
            CORRECTNESS_PERCENT="${CORRECTNESS_PERCENT}%"
        fi
        
        # Pobierz wyniki testów wydajności (czas)
        T2P_PERFORMANCE_FILE=$(ls "$SCRIPT_DIR/tests/performance/results"/text2python_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        P2T_PERFORMANCE_FILE=$(ls "$SCRIPT_DIR/tests/performance/results"/python2text_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        
        PERFORMANCE_TIME="N/A"
        T2P_TIME=0
        P2T_TIME=0
        T2P_COUNT=0
        P2T_COUNT=0
        
        if [ -n "$T2P_PERFORMANCE_FILE" ] && [ -f "$T2P_PERFORMANCE_FILE" ]; then
            T2P_TIME=$(grep -o '"avg_time":[0-9.]*' "$T2P_PERFORMANCE_FILE" | cut -d':' -f2)
            T2P_COUNT=$(grep -o '"tests":[0-9]*' "$T2P_PERFORMANCE_FILE" | cut -d':' -f2)
            T2P_COUNT=${T2P_COUNT:-0}
        fi
        
        if [ -n "$P2T_PERFORMANCE_FILE" ] && [ -f "$P2T_PERFORMANCE_FILE" ]; then
            P2T_TIME=$(grep -o '"avg_time":[0-9.]*' "$P2T_PERFORMANCE_FILE" | cut -d':' -f2)
            P2T_COUNT=$(grep -o '"tests":[0-9]*' "$P2T_PERFORMANCE_FILE" | cut -d':' -f2)
            P2T_COUNT=${P2T_COUNT:-0}
        fi
        
        # Oblicz średni czas
        if [ "$T2P_COUNT" -gt 0 ] || [ "$P2T_COUNT" -gt 0 ]; then
            if [ "$T2P_COUNT" -gt 0 ] && [ "$P2T_COUNT" -gt 0 ]; then
                # Jeśli mamy oba czasy, oblicz średnią ważoną
                TOTAL_TIME=$(echo "$T2P_TIME * $T2P_COUNT + $P2T_TIME * $P2T_COUNT" | bc)
                TOTAL_COUNT=$((T2P_COUNT + P2T_COUNT))
                PERFORMANCE_TIME=$(echo "scale=2; $TOTAL_TIME / $TOTAL_COUNT" | bc)
            elif [ "$T2P_COUNT" -gt 0 ]; then
                PERFORMANCE_TIME=$T2P_TIME
            else
                PERFORMANCE_TIME=$P2T_TIME
            fi
            PERFORMANCE_TIME="${PERFORMANCE_TIME}s"
        fi
        
        # Oblicz całkowity wynik
        SCORE=0
        MAX_SCORE=3
        
        # Punkt za zapytania
        if [ "$CODE_LINES" != "N/A" ] && [ "$CODE_LINES" != "0/0" ]; then
            SCORE=$((SCORE + 1))
        fi
        
        # Punkt za poprawność
        if [ "$CORRECTNESS_PERCENT" != "N/A" ] && [ "$CORRECTNESS_PERCENT" != "0%" ]; then
            SCORE=$((SCORE + 1))
        fi
        
        # Punkt za wydajność
        if [ "$PERFORMANCE_TIME" != "N/A" ]; then
            SCORE=$((SCORE + 1))
        fi
        
        # Pobierz szczegółowe informacje o modelu
        log "DEBUG" "Pobieranie szczegółowych informacji o modelu $model..."
        MODEL_INFO=$(ollama show $model 2>/dev/null)
        
        # Wyodrębnij informacje o modelu
        MODEL_VERSION="-"
        MODEL_SIZE="-"
        MODEL_PARAMS="-"
        
        # Pobierz wersję modelu
        if echo "$MODEL_INFO" | grep -q "Version:"; then
            MODEL_VERSION=$(echo "$MODEL_INFO" | grep "Version:" | awk '{print $2}')
        elif echo "$MODEL_INFO" | grep -q "version:"; then
            MODEL_VERSION=$(echo "$MODEL_INFO" | grep "version:" | awk '{print $2}')
        fi
        
        # Pobierz rozmiar modelu
        if echo "$MODEL_INFO" | grep -q "Size:"; then
            MODEL_SIZE=$(echo "$MODEL_INFO" | grep "Size:" | awk '{print $2" "$3}')
        elif echo "$MODEL_INFO" | grep -q "size:"; then
            MODEL_SIZE=$(echo "$MODEL_INFO" | grep "size:" | awk '{print $2" "$3}')
        fi
        
        # Pobierz liczbę parametrów modelu
        if echo "$MODEL_INFO" | grep -q "Parameters:"; then
            MODEL_PARAMS=$(echo "$MODEL_INFO" | grep "Parameters:" | awk '{print $2" "$3}')
        elif echo "$MODEL_INFO" | grep -q "parameters:"; then
            MODEL_PARAMS=$(echo "$MODEL_INFO" | grep "parameters:" | awk '{print $2" "$3}')
        fi
        
        # Sprawdź w pliku .env, jeśli informacje nie są dostępne
        if [ "$MODEL_VERSION" = "-" ] || [ "$MODEL_SIZE" = "-" ] || [ "$MODEL_PARAMS" = "-" ]; then
            log "DEBUG" "Sprawdzanie informacji o modelu w pliku .env..."
            if [ -f "$CONFIG_DIR/.env" ]; then
                # Pobierz informacje z pliku .env
                MODEL_UPPER=$(echo "$model" | tr '[:lower:]' '[:upper:]')
                
                # Sprawdź wersję
                if [ "$MODEL_VERSION" = "-" ] && grep -q "${MODEL_UPPER}_VERSION=" "$CONFIG_DIR/.env"; then
                    MODEL_VERSION=$(grep "${MODEL_UPPER}_VERSION=" "$CONFIG_DIR/.env" | cut -d'=' -f2)
                fi
                
                # Sprawdź parametry
                if [ "$MODEL_PARAMS" = "-" ]; then
                    # Sprawdź różne formaty zapisów parametrów
                    if grep -q "${MODEL_UPPER}_PARAMS=" "$CONFIG_DIR/.env"; then
                        MODEL_PARAMS=$(grep "${MODEL_UPPER}_PARAMS=" "$CONFIG_DIR/.env" | cut -d'=' -f2)
                    elif grep -q "${MODEL_UPPER}_PARAMETERS=" "$CONFIG_DIR/.env"; then
                        MODEL_PARAMS=$(grep "${MODEL_UPPER}_PARAMETERS=" "$CONFIG_DIR/.env" | cut -d'=' -f2)
                    fi
                fi
            fi
        fi
        
        # Dodatkowe informacje o znanych modelach
        case "$model" in
            "llama3")
                if [ "$MODEL_PARAMS" = "-" ]; then MODEL_PARAMS="8B"; fi
                if [ "$MODEL_VERSION" = "-" ]; then MODEL_VERSION="3.0"; fi
                ;;
            "llama3.2")
                if [ "$MODEL_PARAMS" = "-" ]; then MODEL_PARAMS="8B"; fi
                if [ "$MODEL_VERSION" = "-" ]; then MODEL_VERSION="3.2"; fi
                ;;
            "deepseek-coder")
                if [ "$MODEL_PARAMS" = "-" ]; then MODEL_PARAMS="6.7B"; fi
                if [ "$MODEL_VERSION" = "-" ]; then MODEL_VERSION="instruct"; fi
                ;;
            "phi")
                if [ "$MODEL_PARAMS" = "-" ]; then MODEL_PARAMS="2.7B"; fi
                if [ "$MODEL_VERSION" = "-" ]; then MODEL_VERSION="2.0"; fi
                ;;
            "mistral")
                if [ "$MODEL_PARAMS" = "-" ]; then MODEL_PARAMS="7B"; fi
                if [ "$MODEL_VERSION" = "-" ]; then MODEL_VERSION="instruct"; fi
                ;;
        esac
        
        log "DEBUG" "Informacje o modelu $model: Wersja=$MODEL_VERSION, Rozmiar=$MODEL_SIZE, Parametry=$MODEL_PARAMS"
        
        # Dodaj wiersz do tabeli
        echo "| $model | $MODEL_VERSION | $MODEL_SIZE | $MODEL_PARAMS | $CODE_LINES | $CORRECTNESS_PERCENT | $PERFORMANCE_TIME | $SCORE/$MAX_SCORE |" >> "$REPORT_FILE"
    done
    
    # Dodaj sekcję szczegółowych wyników
    cat >> "$REPORT_FILE" << EOF

## Szczegółowe wyniki testów

EOF
    
    # Dodaj szczegółowe wyniki dla każdego modelu
    for model in $TESTED_MODELS; do
        log "DEBUG" "Dodawanie szczegółowych wyników dla modelu: $model"
        
        echo "### Model: $model" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Pobierz wyniki testów zapytań
        QUERIES_RESULTS_FILE=$(ls "$SCRIPT_DIR/test_results"/test_results_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        
        echo "#### Wyniki testów zapytań" >> "$REPORT_FILE"
        
        # Dodaj linki do wszystkich plików wyników testów zapytań
        echo "##### Pliki wyników:" >> "$REPORT_FILE"
        
        # Znajdź wszystkie pliki wyników testów zapytań dla tego modelu
        ALL_QUERY_FILES=$(find "$SCRIPT_DIR/test_results" -name "test_results_${model}_*.json" -type f | sort -r)
        
        if [ -n "$ALL_QUERY_FILES" ]; then
            echo "Lista plików wyników testów zapytań:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                TIMESTAMP=$(echo "$FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
                
                echo "- [$FILENAME]($REL_PATH) - $(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
            done <<< "$ALL_QUERY_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wyników testów zapytań." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Wyświetl zawartość najnowszego pliku wyników
        if [ -n "$QUERIES_RESULTS_FILE" ] && [ -f "$QUERIES_RESULTS_FILE" ]; then
            echo "##### Najnowsze wyniki:" >> "$REPORT_FILE"
            echo '```json' >> "$REPORT_FILE"
            cat "$QUERIES_RESULTS_FILE" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            log "WARNING" "Nie znaleziono wyników testów zapytań dla modelu $model."
            echo "##### Najnowsze wyniki:" >> "$REPORT_FILE"
            echo "Brak wyników testów zapytań." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Pobierz wyniki testów poprawności
        T2P_CORRECTNESS_FILE=$(ls "$SCRIPT_DIR/tests/correctness/results"/text2python_correctness_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        P2T_CORRECTNESS_FILE=$(ls "$SCRIPT_DIR/tests/correctness/results"/python2text_correctness_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        
        echo "#### Wyniki testów poprawności" >> "$REPORT_FILE"
        
        # Dodaj linki do wszystkich plików wyników testów poprawności
        echo "##### Pliki wyników:" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Text2Python
        echo "###### Text2Python:" >> "$REPORT_FILE"
        
        # Znajdź wszystkie pliki wyników testów poprawności Text2Python dla tego modelu
        ALL_T2P_FILES=$(find "$SCRIPT_DIR/tests/correctness/results" -name "text2python_correctness_${model}_*.json" -type f | sort -r)
        
        if [ -n "$ALL_T2P_FILES" ]; then
            echo "Lista plików wyników testów poprawności Text2Python:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                TIMESTAMP=$(echo "$FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
                
                echo "- [$FILENAME]($REL_PATH) - $(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
            done <<< "$ALL_T2P_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wyników testów poprawności Text2Python." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Python2Text
        echo "###### Python2Text:" >> "$REPORT_FILE"
        
        # Znajdź wszystkie pliki wyników testów poprawności Python2Text dla tego modelu
        ALL_P2T_FILES=$(find "$SCRIPT_DIR/tests/correctness/results" -name "python2text_correctness_${model}_*.json" -type f | sort -r)
        
        if [ -n "$ALL_P2T_FILES" ]; then
            echo "Lista plików wyników testów poprawności Python2Text:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                TIMESTAMP=$(echo "$FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
                
                echo "- [$FILENAME]($REL_PATH) - $(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
            done <<< "$ALL_P2T_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wyników testów poprawności Python2Text." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Wyświetl zawartość najnowszych plików wyników
        echo "##### Najnowsze wyniki:" >> "$REPORT_FILE"
        
        if [ -n "$T2P_CORRECTNESS_FILE" ] && [ -f "$T2P_CORRECTNESS_FILE" ]; then
            echo "###### Text2Python" >> "$REPORT_FILE"
            echo '```json' >> "$REPORT_FILE"
            cat "$T2P_CORRECTNESS_FILE" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            log "WARNING" "Nie znaleziono wyników testów poprawności Text2Python dla modelu $model."
            echo "###### Text2Python" >> "$REPORT_FILE"
            echo "Brak wyników testów poprawności Text2Python." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        if [ -n "$P2T_CORRECTNESS_FILE" ] && [ -f "$P2T_CORRECTNESS_FILE" ]; then
            echo "###### Python2Text" >> "$REPORT_FILE"
            echo '```json' >> "$REPORT_FILE"
            cat "$P2T_CORRECTNESS_FILE" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            log "WARNING" "Nie znaleziono wyników testów poprawności Python2Text dla modelu $model."
            echo "###### Python2Text" >> "$REPORT_FILE"
            echo "Brak wyników testów poprawności Python2Text." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Pobierz wyniki testów wydajności
        T2P_PERFORMANCE_FILE=$(ls "$SCRIPT_DIR/tests/performance/results"/text2python_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        P2T_PERFORMANCE_FILE=$(ls "$SCRIPT_DIR/tests/performance/results"/python2text_"${model}"_*.json 2>/dev/null | sort -r | head -n 1)
        
        echo "#### Wyniki testów wydajności" >> "$REPORT_FILE"
        
        # Dodaj linki do wszystkich plików wyników testów wydajności
        echo "##### Pliki wyników:" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Text2Python
        echo "###### Text2Python:" >> "$REPORT_FILE"
        
        # Znajdź wszystkie pliki wyników testów wydajności Text2Python dla tego modelu
        ALL_T2P_PERF_FILES=$(find "$SCRIPT_DIR/tests/performance/results" -name "text2python_${model}_*.json" -type f | sort -r)
        
        if [ -n "$ALL_T2P_PERF_FILES" ]; then
            echo "Lista plików wyników testów wydajności Text2Python:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                TIMESTAMP=$(echo "$FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
                
                echo "- [$FILENAME]($REL_PATH) - $(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
            done <<< "$ALL_T2P_PERF_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wyników testów wydajności Text2Python." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Python2Text
        echo "###### Python2Text:" >> "$REPORT_FILE"
        
        # Znajdź wszystkie pliki wyników testów wydajności Python2Text dla tego modelu
        ALL_P2T_PERF_FILES=$(find "$SCRIPT_DIR/tests/performance/results" -name "python2text_${model}_*.json" -type f | sort -r)
        
        if [ -n "$ALL_P2T_PERF_FILES" ]; then
            echo "Lista plików wyników testów wydajności Python2Text:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                TIMESTAMP=$(echo "$FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
                
                echo "- [$FILENAME]($REL_PATH) - $(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')" >> "$REPORT_FILE"
            done <<< "$ALL_P2T_PERF_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wyników testów wydajności Python2Text." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Dodaj linki do plików wygenerowanego kodu i wyników
        echo "##### Wygenerowany kod i wyniki:" >> "$REPORT_FILE"
        
        # Znajdź pliki wygenerowanego kodu dla tego modelu
        GEN_CODE_FILES=$(find "$SCRIPT_DIR/generated_code" -name "*${model}*" -type f 2>/dev/null | sort -r)
        
        if [ -n "$GEN_CODE_FILES" ]; then
            echo "Lista plików wygenerowanego kodu:" >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
            
            while IFS= read -r file; do
                # Utwórz relatywną ścieżkę do pliku
                REL_PATH=$(realpath --relative-to="$SCRIPT_DIR" "$file")
                FILENAME=$(basename "$file")
                
                echo "- [$FILENAME]($REL_PATH)" >> "$REPORT_FILE"
            done <<< "$GEN_CODE_FILES"
            echo "" >> "$REPORT_FILE"
        else
            echo "Brak plików wygenerowanego kodu dla tego modelu." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        # Wyświetl zawartość najnowszych plików wyników
        echo "##### Najnowsze wyniki:" >> "$REPORT_FILE"
        
        if [ -n "$T2P_PERFORMANCE_FILE" ] && [ -f "$T2P_PERFORMANCE_FILE" ]; then
            echo "###### Text2Python" >> "$REPORT_FILE"
            echo '```json' >> "$REPORT_FILE"
            cat "$T2P_PERFORMANCE_FILE" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            log "WARNING" "Nie znaleziono wyników testów wydajności Text2Python dla modelu $model."
            echo "###### Text2Python" >> "$REPORT_FILE"
            echo "Brak wyników testów wydajności Text2Python." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
        
        if [ -n "$P2T_PERFORMANCE_FILE" ] && [ -f "$P2T_PERFORMANCE_FILE" ]; then
            echo "###### Python2Text" >> "$REPORT_FILE"
            echo '```json' >> "$REPORT_FILE"
            cat "$P2T_PERFORMANCE_FILE" >> "$REPORT_FILE"
            echo '```' >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        else
            log "WARNING" "Nie znaleziono wyników testów wydajności Python2Text dla modelu $model."
            echo "###### Python2Text" >> "$REPORT_FILE"
            echo "Brak wyników testów wydajności Python2Text." >> "$REPORT_FILE"
            echo "" >> "$REPORT_FILE"
        fi
    done
    
    # Dodaj sekcję wniosków
    cat >> "$REPORT_FILE" << EOF

## Wnioski

Na podstawie przeprowadzonych testów można wyciągnąć następujące wnioski:

1. **Najlepszy model pod względem poprawności**: Model z najwyższym wynikiem w testach poprawności
2. **Najszybszy model**: Model z najniższym średnim czasem wykonania w testach wydajności
3. **Najlepszy model ogólnie**: Model z najwyższym całkowitym wynikiem

## Metodologia testów

Testy zostały przeprowadzone w trzech kategoriach:

1. **Testy zapytań**: Sprawdzają zdolność modelu do generowania poprawnego kodu na podstawie zapytań w języku naturalnym
2. **Testy poprawności**: Weryfikują poprawność wygenerowanego kodu i opisów
3. **Testy wydajności**: Mierzą czas wykonania różnych operacji przez model

## Zalecenia

Na podstawie wyników testów zaleca się:

1. Używanie modelu z najwyższym całkowitym wynikiem do większości zastosowań
2. W przypadku zadań wymagających wysokiej wydajności, rozważenie użycia najszybszego modelu
3. Dla zadań wymagających wysokiej dokładności, wybór modelu z najlepszymi wynikami w testach poprawności

EOF
    
    log "SUCCESS" "Raport porównawczy wygenerowany: $REPORT_FILE"
    
    # Generuj wersje HTML i PDF, jeśli dostępne są narzędzia
    if command -v pandoc &> /dev/null && command -v wkhtmltopdf &> /dev/null; then
        log "INFO" "Generowanie wersji HTML i PDF raportu..."
        
        # Generuj HTML
        HTML_REPORT_FILE="${REPORT_FILE%.md}.html"
        log "DEBUG" "Wykonuję: pandoc -f markdown -t html -s -o $HTML_REPORT_FILE $REPORT_FILE"
        
        if pandoc -f markdown -t html -s -o "$HTML_REPORT_FILE" "$REPORT_FILE"; then
            log "SUCCESS" "Wygenerowano raport HTML: $HTML_REPORT_FILE"
        else
            log "ERROR" "Nie udało się wygenerować raportu HTML."
        fi
        
        # Generuj PDF
        PDF_REPORT_FILE="${REPORT_FILE%.md}.pdf"
        log "DEBUG" "Wykonuję: wkhtmltopdf --orientation Landscape $HTML_REPORT_FILE $PDF_REPORT_FILE"
        
        if wkhtmltopdf --orientation Landscape "$HTML_REPORT_FILE" "$PDF_REPORT_FILE"; then
            log "SUCCESS" "Wygenerowano raport PDF: $PDF_REPORT_FILE"
        else
            log "ERROR" "Nie udało się wygenerować raportu PDF."
        fi
    else
        log "INFO" "Narzędzia pandoc i/lub wkhtmltopdf nie są dostępne. Raport został wygenerowany tylko w formacie Markdown."
        log "INFO" "Aby zainstalować narzędzia, użyj: sudo apt-get install pandoc wkhtmltopdf"
    fi
    
    # Wyświetl informacje o raporcie
    echo
    echo "=== Raport porównawczy wygenerowany ==="
    echo "Raport Markdown: $REPORT_FILE"
    
    if [ -f "${REPORT_FILE%.md}.html" ]; then
        echo "Raport HTML: ${REPORT_FILE%.md}.html"
    fi
    
    if [ -f "${REPORT_FILE%.md}.pdf" ]; then
        echo "Raport PDF: ${REPORT_FILE%.md}.pdf"
    fi
    
    echo
    echo "Aby wyświetlić raport, użyj jednej z poniższych komend:"
    echo "  less $REPORT_FILE               # Wyświetl raport Markdown w terminalu"
    
    if [ -f "${REPORT_FILE%.md}.html" ]; then
        echo "  xdg-open ${REPORT_FILE%.md}.html  # Otwórz raport HTML w przeglądarce"
    fi
    
    if [ -f "${REPORT_FILE%.md}.pdf" ]; then
        echo "  xdg-open ${REPORT_FILE%.md}.pdf   # Otwórz raport PDF w przeglądarce"
    fi
    
    echo
    
    return 0
}

# Główna funkcja
main() {
    log "INFO" "=== Rozpoczynanie generowania raportu porównawczego ==="
    log "INFO" "Katalog skryptu: $SCRIPT_DIR"
    log "INFO" "Plik logów: $LOG_FILE"
    
    # Sprawdź dostępne modele
    check_available_models || {
        log "ERROR" "Nie można kontynuować bez dostępnych modeli."
        return 1
    }
    
    # Wybierz modele do testowania
    select_models_to_test || {
        log "ERROR" "Wybór modeli anulowany lub nieprawidłowy."
        return 1
    }
    
    # Pobierz wybrane modele
    SELECTED_MODELS=$(cat /tmp/evopy_selected_models.txt)
    
    # Uruchom testy dla każdego wybranego modelu
    for model in $SELECTED_MODELS; do
        run_tests_for_model "$model"
    done
    
    # Generuj raport porównawczy
    generate_comparison_report
    
    # Aktualizuj link do najnowszego raportu
    if [ -f "$SCRIPT_DIR/update_latest_report_link.sh" ]; then
        log "INFO" "Aktualizacja linku do najnowszego raportu..."
        bash "$SCRIPT_DIR/update_latest_report_link.sh"
    else
        log "WARNING" "Skrypt update_latest_report_link.sh nie istnieje. Link do najnowszego raportu nie zostanie zaktualizowany."
    fi
    
    log "SUCCESS" "=== Generowanie raportu zakończone ==="
    log "INFO" "Pełne logi dostępne w pliku: $LOG_FILE"
    log "INFO" "Najnowszy raport jest dostępny pod linkiem: $REPORTS_DIR/comparison_report_latest.md"
    
    return 0
}

# Uruchom główną funkcję
main

# Wyczyść pliki tymczasowe
rm -f /tmp/evopy_available_models.txt /tmp/evopy_selected_models.txt
