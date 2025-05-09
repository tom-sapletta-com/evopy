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
    # Wybierz dostępną komendę Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Sprawdź dostępne modele Ollama
echo -e "${BLUE}Sprawdzanie dostępnych modeli Ollama...${NC}"
AVAILABLE_OLLAMA_MODELS=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}' | cut -d':' -f1 | sort -u)

# Domyślna lista modeli do testowania
DEFAULT_MODELS=("llama" "phi" "llama32" "bielik" "deepsek" "qwen" "mistral")

# Filtruj listę modeli na podstawie dostępnych modeli Ollama
MODELS=()
for model in "${DEFAULT_MODELS[@]}"; do
    # Sprawdź czy model jest dostępny w Ollama lub jest to model niestandardowy
    if [[ "$AVAILABLE_OLLAMA_MODELS" == *"$model"* ]] || [[ "$model" == "bielik" ]] || [[ "$model" == "deepsek" ]]; then
        MODELS+=("$model")
    fi
done

# Jeśli nie znaleziono żadnych modeli, użyj domyślnych
if [ ${#MODELS[@]} -eq 0 ]; then
    echo -e "${YELLOW}Nie znaleziono dostępnych modeli Ollama. Używanie domyślnej listy.${NC}"
    MODELS=("llama" "phi" "llama32" "bielik" "deepsek")
fi

# Funkcja do uruchamiania testów dla danego modelu
function run_tests_for_model() {
    local model=$1
    echo -e "\n${GREEN}${BOLD}=== Uruchamianie testów dla modelu: ${YELLOW}$model${NC} ===${NC}"
    
    # Uruchom testy podstawowych zapytań
    echo -e "${BLUE}1. Testy podstawowych zapytań:${NC}"
    $PYTHON_CMD "$SCRIPT_DIR/test_queries.py" --model="$model"
    QUERIES_RESULT=$?
    
    # Uruchom testy poprawności
    echo -e "\n${BLUE}2. Testy poprawności:${NC}"
    $PYTHON_CMD "$TESTS_DIR/correctness/correctness_test.py" --model="$model"
    CORRECTNESS_RESULT=$?
    
    # Uruchom testy wydajności
    echo -e "\n${BLUE}3. Testy wydajności:${NC}"
    $PYTHON_CMD "$TESTS_DIR/performance/performance_test.py" --model="$model"
    PERFORMANCE_RESULT=$?
    
    # Podsumowanie testów dla modelu
    echo -e "\n${CYAN}=== Podsumowanie testów dla modelu: ${YELLOW}$model${NC} ===${NC}"
    if [ $QUERIES_RESULT -eq 0 ] && [ $CORRECTNESS_RESULT -eq 0 ] && [ $PERFORMANCE_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ Wszystkie testy zakończone pomyślnie${NC}"
    else
        echo -e "${RED}✗ Niektóre testy nie powiodły się${NC}"
        echo -e "${BLUE}Testy podstawowych zapytań: $([ $QUERIES_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
        echo -e "${BLUE}Testy poprawności: $([ $CORRECTNESS_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
        echo -e "${BLUE}Testy wydajności: $([ $PERFORMANCE_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
    fi
    
    # Zapisz wyniki do pliku JSON dla późniejszego porównania
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local results_file="$REPORT_DIR/results_${model}_${timestamp}.json"
    
    echo "{
        \"model\": \"$model\",
        \"timestamp\": \"$timestamp\",
        \"queries_result\": $QUERIES_RESULT,
        \"correctness_result\": $CORRECTNESS_RESULT,
        \"performance_result\": $PERFORMANCE_RESULT
    }" > "$results_file"
    
    echo -e "${BLUE}Wyniki zapisane do: ${YELLOW}$results_file${NC}"
}

# Funkcja do generowania raportu porównawczego
function generate_comparison_report() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_file="$REPORT_DIR/comparison_report_${timestamp}.md"
    local format="${1:-all}"  # Format raportu: all, md, html, pdf
    local days="${2:-30}"     # Liczba dni do analizy trendów
    
    echo -e "${GREEN}${BOLD}=== Generowanie zaawansowanego raportu porównawczego ===${NC}"
    
    # Użyj nowego skryptu Python do generowania raportu
    $PYTHON_CMD "$SCRIPT_DIR/generate_report.py" \
        --format="$format" \
        --days="$days" \
        --output="$report_file"
    
    # Sprawdź czy generowanie się powiodło
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Raport porównawczy wygenerowany: ${YELLOW}$report_file${NC}"
        
        # Utwórz link do najnowszego raportu
        ln -sf "$report_file" "$REPORT_DIR/comparison_report_latest.md"
        
        # Jeśli wygenerowano HTML, wyświetl informację
        if [[ "$format" == "all" || "$format" == "html" ]]; then
            local html_file="${report_file%.md}.html"
            if [ -f "$html_file" ]; then
                echo -e "${GREEN}Raport HTML wygenerowany: ${YELLOW}$html_file${NC}"
            fi
        fi
        
        # Jeśli wygenerowano PDF, wyświetl informację
        if [[ "$format" == "all" || "$format" == "pdf" ]]; then
            local pdf_file="${report_file%.md}.pdf"
            if [ -f "$pdf_file" ]; then
                echo -e "${GREEN}Raport PDF wygenerowany: ${YELLOW}$pdf_file${NC}"
            fi
        fi
    else
        echo -e "${RED}Błąd podczas generowania raportu!${NC}"
        
        # Awaryjne generowanie prostego raportu w przypadku błędu
        echo -e "${YELLOW}Generowanie uproszczonego raportu awaryjnego...${NC}"
        
        # Nagłówek raportu
        echo "# Raport porównawczy modeli LLM dla Evopy" > "$report_file"
        echo "Data wygenerowania: $(date '+%Y-%m-%d %H:%M:%S')" >> "$report_file"
        echo "" >> "$report_file"
        
        # Tabela wyników
        echo "## Podsumowanie wyników" >> "$report_file"
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

# Główna funkcja skryptu
function main() {
    echo -e "${GREEN}${BOLD}=== Raport porównawczy modeli LLM dla Evopy ===${NC}"
    echo -e "${BLUE}Data: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}Wersja Python: $($PYTHON_CMD --version)${NC}"
    
    # Uruchom czyszczenie plików pośrednich
    cleanup_files
    
    echo
    
    # Zapytaj, które modele testować
    echo -e "${YELLOW}Dostępne modele do testowania:${NC}"
    for i in "${!MODELS[@]}"; do
        echo -e "$((i+1))) ${CYAN}${MODELS[$i]}${NC}"
    done
    echo -e "$((${#MODELS[@]}+1))) ${CYAN}Wszystkie modele${NC}"
                done
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
