#!/bin/bash
# Skrypt generujący raport porównawczy dla wszystkich modeli LLM

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
TESTS_DIR="$SCRIPT_DIR/tests"
RESULTS_DIR="$SCRIPT_DIR/test_results"
REPORT_DIR="$SCRIPT_DIR/reports"

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

# Utwórz katalogi wyników i raportów, jeśli nie istnieją
mkdir -p "$RESULTS_DIR"
mkdir -p "$REPORT_DIR"

# Wczytaj zmienne środowiskowe z pliku .env
if [ -f "$CONFIG_DIR/.env" ]; then
    echo -e "${BLUE}Wczytywanie konfiguracji z pliku .env...${NC}"
    source "$CONFIG_DIR/.env"
else
    echo -e "${YELLOW}Uwaga: Nie znaleziono pliku .env w $CONFIG_DIR. Używanie domyślnej konfiguracji.${NC}"
fi

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${BLUE}Aktywacja wirtualnego środowiska...${NC}"
    source "$SCRIPT_DIR/.venv/bin/activate"
    PYTHON_CMD="python"
elif [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${BLUE}Aktywacja wirtualnego środowiska...${NC}"
    source "$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="$SCRIPT_DIR/venv/bin/python"
else
    echo -e "${BLUE}Nie znaleziono wirtualnego środowiska, używanie systemowego Pythona...${NC}"
    PYTHON_CMD="python"
fi

# Sprawdź dostępne modele Ollama
echo -e "${BLUE}Sprawdzanie dostępnych modeli Ollama...${NC}"
if command -v ollama &> /dev/null; then
    OLLAMA_MODELS=$(ollama list | grep -v "NAME" | awk '{print $1}')
    if [ -n "$OLLAMA_MODELS" ]; then
        echo -e "${GREEN}Znaleziono modele Ollama: ${YELLOW}$OLLAMA_MODELS${NC}"
    else
        echo -e "${YELLOW}Nie znaleziono żadnych modeli Ollama.${NC}"
    fi
else
    echo -e "${YELLOW}Ollama nie jest zainstalowana. Pomijanie sprawdzania modeli Ollama.${NC}"
fi

# Lista modeli do testowania (domyślna)
if [ -z "$MODELS" ]; then
    MODELS=("llama3" "gpt-4" "claude" "gemini" "deepsek")
fi

# Domyślne ustawienia
specific_model=""
report_format="all"
trend_days=30
compare_models=()
metrics="all"
only_report=false

# Funkcja do uruchamiania testów dla danego modelu
function run_tests_for_model() {
    local model=$1
    
    echo -e "${GREEN}=== Uruchamianie testów dla modelu: $model ===${NC}"
    
    # Uruchom testy zapytań
    echo -e "${BLUE}Uruchamianie testów zapytań...${NC}"
    "$PYTHON_CMD" "$SCRIPT_DIR/test_queries.py" --model="$model"
    local queries_result=$?
    
    # Uruchom testy poprawności
    echo -e "${BLUE}Uruchamianie testów poprawności...${NC}"
    if [ -f "$SCRIPT_DIR/test_correctness.py" ]; then
        "$PYTHON_CMD" "$SCRIPT_DIR/test_correctness.py" --model="$model"
        local correctness_result=$?
    else
        echo -e "${YELLOW}Skrypt test_correctness.py nie istnieje. Pomijanie testów poprawności.${NC}"
        local correctness_result=0
    fi
    
    # Uruchom testy wydajności
    echo -e "${BLUE}Uruchamianie testów wydajności...${NC}"
    if [ -f "$SCRIPT_DIR/test_performance.py" ]; then
        "$PYTHON_CMD" "$SCRIPT_DIR/test_performance.py" --model="$model"
        local performance_result=$?
    else
        echo -e "${YELLOW}Skrypt test_performance.py nie istnieje. Pomijanie testów wydajności.${NC}"
        local performance_result=0
    fi
    
    # Zapisz wyniki testów
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local results_file="$REPORT_DIR/results_${model}_${timestamp}.json"
    
    echo "{" > "$results_file"
    echo "  \"model\": \"$model\"," >> "$results_file"
    echo "  \"timestamp\": \"$timestamp\"," >> "$results_file"
    echo "  \"queries_result\": $queries_result," >> "$results_file"
    echo "  \"correctness_result\": $correctness_result," >> "$results_file"
    echo "  \"performance_result\": $performance_result" >> "$results_file"
    echo "}" >> "$results_file"
    
    echo -e "${GREEN}Wyniki testów zapisane w pliku: ${YELLOW}$results_file${NC}"
    echo
}

# Funkcja do generowania raportu porównawczego
function generate_comparison_report() {
    local format=$1
    local days=$2
    
    echo -e "${GREEN}=== Generowanie raportu porównawczego ===${NC}"
    
    # Uruchom generowanie raportu
    "$PYTHON_CMD" "$SCRIPT_DIR/generate_report.py" --format="$format" --trend="$days"
    local report_result=$?
    
    if [ $report_result -eq 0 ]; then
        echo -e "${GREEN}Raport porównawczy wygenerowany pomyślnie.${NC}"
    else
        echo -e "${RED}Wystąpił błąd podczas generowania raportu porównawczego.${NC}"
        
        # Wygeneruj uproszczony raport w Markdown
        echo -e "${YELLOW}Generowanie uproszczonego raportu w formacie Markdown...${NC}"
        
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local report_file="$REPORT_DIR/report_simplified_${timestamp}.md"
        
        echo "# Uproszczony raport porównawczy modeli LLM" > "$report_file"
        echo "" >> "$report_file"
        echo "Data: $(date '+%Y-%m-%d %H:%M:%S')" >> "$report_file"
        echo "" >> "$report_file"
        echo "## Podsumowanie wyników testów" >> "$report_file"
        echo "" >> "$report_file"
        echo "| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |" >> "$report_file"
        echo "|-------|--------------|-------------------|------------------|-----------------|" >> "$report_file"
        
        # Zbierz najnowsze wyniki dla każdego modelu
        for model in "${MODELS[@]}"; do
            local latest_result=$(ls -t "$REPORT_DIR"/results_${model}_*.json 2>/dev/null | head -n 1)
            
            if [ -n "$latest_result" ] && [ -f "$latest_result" ]; then
                local queries_result=$(grep -o '"queries_result": [0-9]*' "$latest_result" | awk '{print $2}')
                local correctness_result=$(grep -o '"correctness_result": [0-9]*' "$latest_result" | awk '{print $2}')
                local performance_result=$(grep -o '"performance_result": [0-9]*' "$latest_result" | awk '{print $2}')
                
                # Konwertuj kody wyjścia na symbole
                local queries_symbol=$([ "$queries_result" -eq 0 ] && echo "✅" || echo "❌")
                local correctness_symbol=$([ "$correctness_result" -eq 0 ] && echo "✅" || echo "❌")
                local performance_symbol=$([ "$performance_result" -eq 0 ] && echo "✅" || echo "❌")
                
                # Oblicz całkowity wynik
                local total_score=0
                [ "$queries_result" -eq 0 ] && ((total_score++))
                [ "$correctness_result" -eq 0 ] && ((total_score++))
                [ "$performance_result" -eq 0 ] && ((total_score++))
                
                # Dodaj wiersz do tabeli
                echo "| $model | $queries_symbol | $correctness_symbol | $performance_symbol | $total_score/3 |" >> "$report_file"
            else
                echo "| $model | ❓ | ❓ | ❓ | 0/3 |" >> "$report_file"
            fi
        done
        
        # Dodaj szczegółowe wyniki z plików JSON
        echo "" >> "$report_file"
        echo "## Szczegółowe wyniki testów" >> "$report_file"
        echo "" >> "$report_file"
        
        # Zbierz dane z plików wyników testów
        for model in "${MODELS[@]}"; do
            echo "### Model: $model" >> "$report_file"
            echo "" >> "$report_file"
            
            # Znajdź najnowsze pliki wyników dla danego modelu
            local queries_file=$(ls -t "$RESULTS_DIR"/test_results_${model}_*.json 2>/dev/null | head -n 1)
            
            if [ -n "$queries_file" ] && [ -f "$queries_file" ]; then
                echo "#### Wyniki testów zapytań" >> "$report_file"
                echo '```json' >> "$report_file"
                cat "$queries_file" >> "$report_file"
                echo '```' >> "$report_file"
                echo "" >> "$report_file"
            else
                echo "Brak wyników testów zapytań dla modelu $model." >> "$report_file"
                echo "" >> "$report_file"
            fi
        done
        
        echo -e "${YELLOW}Uproszczony raport wygenerowany: ${GREEN}$report_file${NC}"
    fi
    
    # Wyświetl raport w terminalu
    echo -e "\n${CYAN}${BOLD}=== Podsumowanie porównawcze wszystkich modeli ===${NC}"
    echo -e "${BLUE}Model\t\tZapytania\tPoprawność\tWydajność\tWynik${NC}"
    echo -e "${BLUE}---------------------------------------------------------------------${NC}"
    
    for model in "${MODELS[@]}"; do
        local latest_result=$(ls -t "$REPORT_DIR"/results_${model}_*.json 2>/dev/null | head -n 1)
        
        if [ -n "$latest_result" ] && [ -f "$latest_result" ]; then
            local queries_result=$(grep -o '"queries_result": [0-9]*' "$latest_result" | awk '{print $2}')
            local correctness_result=$(grep -o '"correctness_result": [0-9]*' "$latest_result" | awk '{print $2}')
            local performance_result=$(grep -o '"performance_result": [0-9]*' "$latest_result" | awk '{print $2}')
            
            # Konwertuj kody wyjścia na symbole
            local queries_symbol=$([ "$queries_result" -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")
            local correctness_symbol=$([ "$correctness_result" -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")
            local performance_symbol=$([ "$performance_result" -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")
            
            # Oblicz całkowity wynik
            local total_score=0
            [ "$queries_result" -eq 0 ] && ((total_score++))
            [ "$correctness_result" -eq 0 ] && ((total_score++))
            [ "$performance_result" -eq 0 ] && ((total_score++))
            
            # Wyświetl wiersz w tabeli
            printf "${YELLOW}%-10s${NC}\t${queries_symbol}${NC}\t\t${correctness_symbol}${NC}\t\t${performance_symbol}${NC}\t\t${CYAN}%d/3${NC}\n" "$model" "$total_score"
        else
            printf "${YELLOW}%-10s${NC}\t${RED}BRAK${NC}\t\t${RED}BRAK${NC}\t\t${RED}BRAK${NC}\t\t${CYAN}0/3${NC}\n" "$model"
        fi
    done
}

# Funkcja do czyszczenia plików pośrednich
function cleanup_files() {
    if [ -f "$SCRIPT_DIR/cleanup.sh" ]; then
        echo -e "${YELLOW}Czyszczenie plików pośrednich przed generowaniem raportu...${NC}"
        bash "$SCRIPT_DIR/cleanup.sh"
    else
        echo -e "${RED}Skrypt cleanup.sh nie istnieje. Pliki pośrednie nie zostaną wyczyszczone.${NC}"
    fi
}

# Przetwarzanie argumentów wiersza poleceń
while [[ $# -gt 0 ]]; do
    case $1 in
        --model=*)
            specific_model="${1#*=}"
            shift
            ;;
        --format=*)
            report_format="${1#*=}"
            shift
            ;;
        --trend=*)
            trend_days="${1#*=}"
            shift
            ;;
        --compare=*)
            IFS=',' read -ra compare_models <<< "${1#*=}"
            shift
            ;;
        --metrics=*)
            metrics="${1#*=}"
            shift
            ;;
        --only-report)
            only_report=true
            shift
            ;;
        --help)
            echo -e "${BLUE}Użycie: $0 [opcje]${NC}"
            echo -e "${BLUE}Opcje:${NC}"
            echo -e "  ${GREEN}--model=NAZWA${NC}       Uruchom testy tylko dla wybranego modelu"
            echo -e "  ${GREEN}--format=FORMAT${NC}     Format raportu: all, md, html, pdf (domyślnie: all)"
            echo -e "  ${GREEN}--trend=DNI${NC}         Liczba dni do analizy trendów (domyślnie: 30)"
            echo -e "  ${GREEN}--compare=MODEL1,MODEL2${NC} Porównaj tylko wybrane modele"
            echo -e "  ${GREEN}--metrics=METRYKI${NC}   Wybrane metryki do analizy (domyślnie: all)"
            echo -e "  ${GREEN}--only-report${NC}       Wygeneruj tylko raport bez uruchamiania testów"
            echo -e "  ${GREEN}--help${NC}              Wyświetl tę pomoc"
            exit 0
            ;;
        *)
            echo -e "${RED}Błąd: Nieznana opcja '$1'${NC}"
            echo -e "${BLUE}Użyj '$0 --help' aby wyświetlić dostępne opcje${NC}"
            exit 1
            ;;
    esac
done

# Główna funkcja skryptu
function main() {
    echo -e "${GREEN}${BOLD}=== Raport porównawczy modeli LLM dla Evopy ===${NC}"
    echo -e "${BLUE}Data: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}Wersja Python: $($PYTHON_CMD --version)${NC}"
    
    # Uruchom czyszczenie plików pośrednich
    cleanup_files
    
    echo
    
    # Zapytaj, które modele testować, jeśli nie podano w argumentach
    if [ -z "$specific_model" ] && [ ${#compare_models[@]} -eq 0 ]; then
        echo -e "${YELLOW}Dostępne modele do testowania:${NC}"
        for i in "${!MODELS[@]}"; do
            echo -e "$((i+1))) ${CYAN}${MODELS[$i]}${NC}"
        done
        echo -e "$((${#MODELS[@]}+1))) ${CYAN}Wszystkie modele${NC}"
        
        # Pobierz wybór użytkownika
        read -p "${YELLOW}Wybierz model (1-$((${#MODELS[@]}+1))): ${NC}" choice
        echo
        
        # Sprawdź wybór użytkownika
        if [ "$choice" -eq "$((${#MODELS[@]}+1))" ]; then
            # Wybrano wszystkie modele
            echo -e "${BLUE}Wybrano wszystkie modele${NC}"
        elif [ "$choice" -ge 1 ] && [ "$choice" -le "${#MODELS[@]}" ]; then
            # Wybrano konkretny model
            specific_model="${MODELS[$((choice-1))]}"
            echo -e "${BLUE}Wybrano model: ${YELLOW}$specific_model${NC}"
        else
            echo -e "${RED}Błędny wybór. Używanie wszystkich modeli.${NC}"
        fi
    fi
    
    # Wyświetl informacje o uruchamianych testach
    if [ "$only_report" = false ]; then
        if [ -n "$specific_model" ]; then
            echo -e "${BLUE}Uruchamianie testów dla modelu: ${YELLOW}$specific_model${NC}\n"
            run_tests_for_model "$specific_model"
        else
            echo -e "${BLUE}Uruchamianie testów dla modeli: ${YELLOW}${MODELS[*]}${NC}\n"
            # Uruchom testy dla wszystkich modeli
            for model in "${MODELS[@]}"; do
                run_tests_for_model "$model"
            done
        fi
    else
        echo -e "${BLUE}Pomijanie testów, generowanie tylko raportu...${NC}\n"
    fi
    
    # Wygeneruj raport porównawczy
    if [ ${#compare_models[@]} -gt 0 ]; then
        # Tymczasowo zachowaj oryginalne modele
        local original_models=("${MODELS[@]}")
        # Ustaw tylko wybrane modele do porównania
        MODELS=("${compare_models[@]}")
        # Wygeneruj raport
        generate_comparison_report "$report_format" "$trend_days"
        # Przywróć oryginalne modele
        MODELS=("${original_models[@]}")
    else
        # Wygeneruj raport dla wszystkich modeli
        generate_comparison_report "$report_format" "$trend_days"
    fi
    
    # Wyświetl podsumowanie
    echo -e "\n${GREEN}${BOLD}=== Wszystkie operacje zakończone ===${NC}"
    if [ "$only_report" = false ]; then
        echo -e "${BLUE}Wyniki testów zapisane w katalogu: ${YELLOW}$RESULTS_DIR${NC}"
    fi
    echo -e "${BLUE}Raporty porównawcze zapisane w katalogu: ${YELLOW}$REPORT_DIR${NC}"
}

# Uruchom główną funkcję skryptu
main
