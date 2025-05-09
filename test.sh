#!/bin/bash
# Skrypt uruchamiający testy

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
TESTS_DIR="$SCRIPT_DIR/tests"

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

# Wczytaj zmienne środowiskowe z pliku .env
if [ -f "$CONFIG_DIR/.env" ]; then
    echo -e "${BLUE}Wczytywanie konfiguracji z pliku .env...${NC}"
    source "$CONFIG_DIR/.env"
else
    echo -e "${YELLOW}Uwaga: Nie znaleziono pliku .env w $CONFIG_DIR. Używanie domyślnej konfiguracji.${NC}"
    # Ustaw domyślny model
    ACTIVE_MODEL="llama"
fi

# Funkcja do wyświetlania dostępnych modeli
function show_available_models() {
    echo -e "${BLUE}Dostępne modele LLM:${NC}"
    echo -e "1) ${YELLOW}llama${NC} - Llama 3 (domyślny)"
    echo -e "2) ${YELLOW}phi${NC} - Phi model"
    echo -e "3) ${YELLOW}llama32${NC} - Llama 3.2"
    echo -e "4) ${YELLOW}bielik${NC} - Bielik model"
    echo -e "5) ${YELLOW}deepsek${NC} - DeepSeek Coder"
    echo -e "6) ${YELLOW}qwen${NC} - Qwen model"
    echo -e "7) ${YELLOW}mistral${NC} - Mistral model"
}

# Sprawdź czy model jest określony w argumentach wiersza poleceń
MODEL_SPECIFIED=false
for arg in "$@"; do
    if [[ "$arg" == "--model="* ]]; then
        ACTIVE_MODEL="${arg#*=}"
        MODEL_SPECIFIED=true
    fi
done

# Jeśli model nie został określony w argumentach, zapytaj użytkownika
if [ "$MODEL_SPECIFIED" = false ]; then
    echo -e "${GREEN}Aktualnie wybrany model: ${YELLOW}$ACTIVE_MODEL${NC}"
    echo -e "Czy chcesz użyć innego modelu? [t/N]: "
    read -r change_model
    
    if [[ "$change_model" =~ ^[Tt]$ ]]; then
        show_available_models
        echo -e "Wybierz numer modelu lub wpisz nazwę modelu: "
        read -r model_choice
        
        case "$model_choice" in
            1) ACTIVE_MODEL="llama" ;;
            2) ACTIVE_MODEL="phi" ;;
            3) ACTIVE_MODEL="llama32" ;;
            4) ACTIVE_MODEL="bielik" ;;
            5) ACTIVE_MODEL="deepsek" ;;
            6) ACTIVE_MODEL="qwen" ;;
            7) ACTIVE_MODEL="mistral" ;;
            *) 
                if [ -n "$model_choice" ]; then
                    ACTIVE_MODEL="$model_choice"
                fi
                ;;
        esac
        
        # Aktualizuj plik .env - używamy tymczasowego pliku, aby uniknąć problemów z uprawnieniami
        if [ -f "$CONFIG_DIR/.env" ]; then
            # Sprawdź czy mamy uprawnienia do zapisu
            if [ -w "$CONFIG_DIR/.env" ]; then
                sed -i "s/^ACTIVE_MODEL=.*$/ACTIVE_MODEL=$ACTIVE_MODEL/" "$CONFIG_DIR/.env"
                sed -i "s/^#ACTIVE_MODEL=.*$/#ACTIVE_MODEL=/" "$CONFIG_DIR/.env"
                sed -i "s/^#ACTIVE_MODEL=$ACTIVE_MODEL$/ACTIVE_MODEL=$ACTIVE_MODEL/" "$CONFIG_DIR/.env"
            else
                echo -e "${YELLOW}Uwaga: Brak uprawnień do zapisu w pliku .env. Zmiany nie zostaną zapisane.${NC}"
                echo -e "${YELLOW}Używanie wybranego modelu tylko dla tej sesji.${NC}"
            fi
        fi
    fi
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

# Wyświetl informację o uruchamianych testach
echo -e "${GREEN}=== Uruchamianie testów Evopy ===${NC}"
echo -e "${BLUE}Wersja Python: $($PYTHON_CMD --version)${NC}"
echo -e "${BLUE}Używany model: ${YELLOW}$ACTIVE_MODEL${NC}"
echo

# Uruchom testy podstawowych zapytań
echo -e "${GREEN}1. Testy podstawowych zapytań:${NC}"
if [ "$MODEL_SPECIFIED" = false ]; then
    $PYTHON_CMD "$SCRIPT_DIR/test_queries.py" --model="$ACTIVE_MODEL"
else
    $PYTHON_CMD "$SCRIPT_DIR/test_queries.py" "$@"
fi
QUERIES_RESULT=$?

# Uruchom testy poprawności
echo -e "\n${GREEN}2. Testy poprawności:${NC}"
if [ "$MODEL_SPECIFIED" = false ]; then
    $PYTHON_CMD "$TESTS_DIR/correctness/correctness_test.py" --model="$ACTIVE_MODEL"
else
    $PYTHON_CMD "$TESTS_DIR/correctness/correctness_test.py" "$@"
fi
CORRECTNESS_RESULT=$?

# Uruchom testy wydajności
echo -e "\n${GREEN}3. Testy wydajności:${NC}"
if [ "$MODEL_SPECIFIED" = false ]; then
    $PYTHON_CMD "$TESTS_DIR/performance/performance_test.py" --model="$ACTIVE_MODEL"
else
    $PYTHON_CMD "$TESTS_DIR/performance/performance_test.py" "$@"
fi
PERFORMANCE_RESULT=$?

# Podsumowanie testów
echo -e "\n${GREEN}=== Podsumowanie testów ===${NC}"
if [ $QUERIES_RESULT -eq 0 ] && [ $CORRECTNESS_RESULT -eq 0 ] && [ $PERFORMANCE_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ Wszystkie testy zakończone pomyślnie${NC}"
    exit 0
else
    echo -e "${RED}✗ Niektóre testy nie powiodły się${NC}"
    echo -e "${BLUE}Testy podstawowych zapytań: $([ $QUERIES_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
    echo -e "${BLUE}Testy poprawności: $([ $CORRECTNESS_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
    echo -e "${BLUE}Testy wydajności: $([ $PERFORMANCE_RESULT -eq 0 ] && echo "${GREEN}OK" || echo "${RED}BŁĄD")${NC}"
    exit 1
fi
