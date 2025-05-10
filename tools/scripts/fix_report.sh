#!/bin/bash
# Skrypt naprawiający problemy z generowaniem raportów

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$SCRIPT_DIR/config"
REPORTS_DIR="$SCRIPT_DIR/reports"
TEST_RESULTS_DIR="$SCRIPT_DIR/test_results"

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

# Funkcja do sprawdzania i tworzenia katalogów
function check_and_create_dirs() {
    echo -e "${BLUE}Sprawdzanie i tworzenie katalogów...${NC}"
    
    # Sprawdź i utwórz katalog raportów
    if [ ! -d "$REPORTS_DIR" ]; then
        echo -e "${YELLOW}Tworzenie katalogu raportów: $REPORTS_DIR${NC}"
        mkdir -p "$REPORTS_DIR"
    fi
    
    # Sprawdź i utwórz katalog wyników testów
    if [ ! -d "$TEST_RESULTS_DIR" ]; then
        echo -e "${YELLOW}Tworzenie katalogu wyników testów: $TEST_RESULTS_DIR${NC}"
        mkdir -p "$TEST_RESULTS_DIR"
    fi
    
    # Sprawdź i utwórz katalogi dla testów wydajności i poprawności
    if [ ! -d "$SCRIPT_DIR/tests/performance/results" ]; then
        echo -e "${YELLOW}Tworzenie katalogu wyników testów wydajności${NC}"
        mkdir -p "$SCRIPT_DIR/tests/performance/results"
    fi
    
    if [ ! -d "$SCRIPT_DIR/tests/correctness/results" ]; then
        echo -e "${YELLOW}Tworzenie katalogu wyników testów poprawności${NC}"
        mkdir -p "$SCRIPT_DIR/tests/correctness/results"
    fi
}

# Funkcja do sprawdzania dostępnych modeli Ollama
function check_available_models() {
    echo -e "${BLUE}Sprawdzanie dostępnych modeli Ollama...${NC}"
    
    # Pobierz listę dostępnych modeli
    OLLAMA_MODELS=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}' | cut -d':' -f1 | sort -u)
    
    if [ -z "$OLLAMA_MODELS" ]; then
        echo -e "${RED}Nie znaleziono żadnych modeli Ollama. Sprawdź czy Ollama jest zainstalowana i uruchomiona.${NC}"
        return 1
    fi
    
    echo -e "${GREEN}Znaleziono następujące modele Ollama:${NC}"
    echo "$OLLAMA_MODELS" | while read -r model; do
        echo -e "  - ${CYAN}$model${NC}"
    done
    
    # Sprawdź czy mamy podstawowe modele
    if ! echo "$OLLAMA_MODELS" | grep -q "llama"; then
        echo -e "${YELLOW}Model llama nie został znaleziony. Próba pobrania...${NC}"
        ollama pull llama3
    fi
    
    return 0
}

# Funkcja do aktualizacji pliku .env
function update_env_file() {
    echo -e "${BLUE}Aktualizacja pliku .env...${NC}"
    
    if [ ! -f "$CONFIG_DIR/.env" ]; then
        echo -e "${YELLOW}Tworzenie pliku .env...${NC}"
        
        # Utwórz katalog konfiguracji, jeśli nie istnieje
        if [ ! -d "$CONFIG_DIR" ]; then
            mkdir -p "$CONFIG_DIR"
        fi
        
        # Utwórz podstawowy plik .env
        cat > "$CONFIG_DIR/.env" << EOF
# Konfiguracja modeli LLM dla Evopy
# Aktywny model (odkomentuj tylko jeden)
ACTIVE_MODEL=llama
#ACTIVE_MODEL=phi
#ACTIVE_MODEL=bielik
#ACTIVE_MODEL=deepsek

# Konfiguracja modelu DeepSeek
DEEPSEK_MODEL=deepseek-coder
DEEPSEK_VERSION=instruct-6.7b
DEEPSEK_REPO=deepseek-ai/deepseek-coder-instruct-6.7b
DEEPSEK_URL=https://huggingface.co/deepseek-ai/deepseek-coder-instruct-6.7b

# Konfiguracja modelu Llama
LLAMA_MODEL=llama3
LLAMA_VERSION=latest
LLAMA_REPO=meta-llama/Llama-3
LLAMA_URL=https://huggingface.co/meta-llama/Llama-3

# Konfiguracja modelu Bielik
BIELIK_MODEL=bielik
BIELIK_VERSION=latest
BIELIK_REPO=bielik/bielik
BIELIK_URL=https://huggingface.co/bielik/bielik

# Konfiguracja modelu Phi
PHI_MODEL=phi
PHI_VERSION=latest
PHI_REPO=microsoft/phi-2
PHI_URL=https://huggingface.co/microsoft/phi-2

# Limity i konfiguracja
MAX_TOKENS=4096
TIMEOUT_SECONDS=30
TEMPERATURE=0.2
EOF
        
        echo -e "${GREEN}Utworzono plik .env z domyślną konfiguracją${NC}"
    else
        echo -e "${GREEN}Plik .env już istnieje${NC}"
        
        # Sprawdź uprawnienia do pliku .env
        if [ ! -w "$CONFIG_DIR/.env" ]; then
            echo -e "${RED}Brak uprawnień do zapisu w pliku .env. Próba naprawy...${NC}"
            chmod u+w "$CONFIG_DIR/.env" 2>/dev/null
            
            if [ ! -w "$CONFIG_DIR/.env" ]; then
                echo -e "${RED}Nie można naprawić uprawnień do pliku .env. Tworzenie kopii...${NC}"
                cp "$CONFIG_DIR/.env" "$CONFIG_DIR/.env.backup"
                rm "$CONFIG_DIR/.env"
                cp "$CONFIG_DIR/.env.backup" "$CONFIG_DIR/.env"
                chmod u+w "$CONFIG_DIR/.env"
            fi
        fi
    fi
}

# Funkcja do naprawy skryptu report.sh
function fix_report_script() {
    echo -e "${BLUE}Sprawdzanie i naprawianie skryptu report.sh...${NC}"
    
    if [ ! -x "$SCRIPT_DIR/report.sh" ]; then
        echo -e "${YELLOW}Nadawanie uprawnień wykonywania dla report.sh...${NC}"
        chmod +x "$SCRIPT_DIR/report.sh"
    fi
    
    # Sprawdź czy skrypt report.sh działa poprawnie
    if ! bash -n "$SCRIPT_DIR/report.sh"; then
        echo -e "${RED}Skrypt report.sh zawiera błędy składniowe. Próba naprawy...${NC}"
        
        # Utwórz kopię zapasową
        cp "$SCRIPT_DIR/report.sh" "$SCRIPT_DIR/report.sh.backup"
        
        # Napraw typowe problemy
        sed -i 's/\r$//' "$SCRIPT_DIR/report.sh"  # Usuń znaki końca linii Windows
        
        # Sprawdź ponownie
        if ! bash -n "$SCRIPT_DIR/report.sh"; then
            echo -e "${RED}Nie udało się naprawić skryptu report.sh. Przywracanie kopii zapasowej...${NC}"
            mv "$SCRIPT_DIR/report.sh.backup" "$SCRIPT_DIR/report.sh"
        else
            echo -e "${GREEN}Naprawiono skrypt report.sh${NC}"
            rm "$SCRIPT_DIR/report.sh.backup"
        fi
    else
        echo -e "${GREEN}Skrypt report.sh jest poprawny składniowo${NC}"
    fi
}

# Funkcja do naprawy skryptu test.sh
function fix_test_script() {
    echo -e "${BLUE}Sprawdzanie i naprawianie skryptu test.sh...${NC}"
    
    if [ ! -x "$SCRIPT_DIR/test.sh" ]; then
        echo -e "${YELLOW}Nadawanie uprawnień wykonywania dla test.sh...${NC}"
        chmod +x "$SCRIPT_DIR/test.sh"
    fi
    
    # Sprawdź czy skrypt test.sh działa poprawnie
    if ! bash -n "$SCRIPT_DIR/test.sh"; then
        echo -e "${RED}Skrypt test.sh zawiera błędy składniowe. Próba naprawy...${NC}"
        
        # Utwórz kopię zapasową
        cp "$SCRIPT_DIR/test.sh" "$SCRIPT_DIR/test.sh.backup"
        
        # Napraw typowe problemy
        sed -i 's/\r$//' "$SCRIPT_DIR/test.sh"  # Usuń znaki końca linii Windows
        
        # Sprawdź ponownie
        if ! bash -n "$SCRIPT_DIR/test.sh"; then
            echo -e "${RED}Nie udało się naprawić skryptu test.sh. Przywracanie kopii zapasowej...${NC}"
            mv "$SCRIPT_DIR/test.sh.backup" "$SCRIPT_DIR/test.sh"
        else
            echo -e "${GREEN}Naprawiono skrypt test.sh${NC}"
            rm "$SCRIPT_DIR/test.sh.backup"
        fi
    else
        echo -e "${GREEN}Skrypt test.sh jest poprawny składniowo${NC}"
    fi
}

# Funkcja do generowania przykładowego raportu
function generate_sample_report() {
    echo -e "${BLUE}Generowanie przykładowego raportu...${NC}"
    
    # Sprawdź, czy istnieje jakikolwiek model
    AVAILABLE_MODEL=$(ollama list 2>/dev/null | awk 'NR>1 {print $1}' | cut -d':' -f1 | head -n 1)
    
    if [ -z "$AVAILABLE_MODEL" ]; then
        echo -e "${RED}Brak dostępnych modeli do wygenerowania przykładowego raportu${NC}"
        return 1
    fi
    
    # Utwórz przykładowy plik wyników dla text2python
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local model_name="${AVAILABLE_MODEL}"
    local results_file="$TEST_RESULTS_DIR/test_results_${model_name}_${timestamp}.json"
    
    echo '{
        "timestamp": "'$timestamp'",
        "model_id": "'$model_name'",
        "passed_tests": 2,
        "failed_tests": 1,
        "total_tests": 3,
        "test_results": [
            {
                "name": "Proste zapytanie tekstowe",
                "status": "PASSED",
                "reason": "Kod zawiera wszystkie oczekiwane elementy"
            },
            {
                "name": "Zapytanie matematyczne",
                "status": "PASSED",
                "reason": "Kod zawiera wszystkie oczekiwane elementy"
            },
            {
                "name": "Zapytanie z przetwarzaniem tekstu",
                "status": "FAILED",
                "reason": "Brakujące elementy w kodzie: re.findall"
            }
        ]
    }' > "$results_file"
    
    echo -e "${GREEN}Wygenerowano przykładowy plik wyników: $results_file${NC}"
    
    # Utwórz przykładowy raport
    local report_file="$REPORTS_DIR/comparison_report_${timestamp}.md"
    
    echo "# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: $(date '+%Y-%m-%d %H:%M:%S')

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| $model_name | ✅ | ❓ | ❓ | 1/3 |

## Szczegółowe wyniki testów

### Model: $model_name

#### Wyniki testów zapytań
\`\`\`json
$(cat "$results_file")
\`\`\`

## Wnioski

Ten raport zawiera przykładowe wyniki dla modelu $model_name. Aby wygenerować pełny raport porównawczy, uruchom skrypt \`report.sh\` i wybierz modele do przetestowania.
" > "$report_file"
    
    echo -e "${GREEN}Wygenerowano przykładowy raport: $report_file${NC}"
    
    # Wyświetl informację o tym, jak wyświetlić raport
    echo -e "${CYAN}Aby wyświetlić raport, użyj jednej z poniższych komend:${NC}"
    echo -e "  ${YELLOW}cat $report_file${NC}"
    echo -e "  ${YELLOW}less $report_file${NC}"
    
    return 0
}

# Funkcja do aktualizacji dokumentacji
function update_documentation() {
    echo -e "${BLUE}Sprawdzanie i aktualizacja dokumentacji...${NC}"
    
    # Sprawdź czy istnieje katalog docs
    if [ ! -d "$SCRIPT_DIR/docs" ]; then
        echo -e "${YELLOW}Tworzenie katalogu dokumentacji...${NC}"
        mkdir -p "$SCRIPT_DIR/docs"
    fi
    
    # Sprawdź czy istnieje plik TESTING.md
    if [ ! -f "$SCRIPT_DIR/docs/TESTING.md" ]; then
        echo -e "${YELLOW}Plik TESTING.md nie istnieje. Tworzenie...${NC}"
        
        # Utwórz podstawowy plik TESTING.md
        cat > "$SCRIPT_DIR/docs/TESTING.md" << 'EOF'
# Evopy Testing System Documentation

## Overview

The Evopy testing system provides comprehensive testing capabilities for both the `text2python` and `python2text` modules. It allows you to test different language models (LLMs) and compare their performance, accuracy, and capabilities.

## Available Scripts

### 1. `test.sh` - Single Model Testing

This script runs tests for a single model on all Evopy components.

#### Usage:

```bash
./test.sh [--model=MODEL_NAME]
```

#### Features:

- Interactive model selection at startup
- Automatic fallback to available models if the requested one isn't available
- Comprehensive testing of basic queries, correctness, and performance
- Detailed test results saved to the `test_results` directory

### 2. `report.sh` - Multi-Model Comparison

This script generates a comprehensive comparison report across multiple LLM models.

#### Usage:

```bash
./report.sh
```

#### Features:

- Tests multiple models in sequence
- Automatically detects available models in your Ollama installation
- Generates a markdown report comparing all tested models
- Creates a summary table showing success/failure for each test type
- Calculates performance metrics across models

## Generating Reports

To generate a comprehensive comparison report:

1. Run the report script:
   ```bash
   ./report.sh
   ```

2. Select which models to test:
   - Enter specific model numbers (e.g., `1 3 5`)
   - Enter `all` to test all available models
   - Select the "All models" option

3. Wait for all tests to complete. This may take some time depending on the number of models selected.

4. The report will be generated in the `reports` directory with a filename like `comparison_report_YYYYMMDD_HHMMSS.md`.

## Report Structure

The generated report includes:

1. **Summary Table**: A comparison table showing test results for all models:
   - Basic query tests (✅/❌)
   - Correctness tests (✅/❌)
   - Performance tests (✅/❌)
   - Total score for each model

2. **Detailed Results**: For each model, detailed test results including:
   - Execution times
   - Success rates
   - Specific test case results

## Troubleshooting

### Model Not Available

If a model isn't available in your Ollama installation:

1. The system will attempt to download it automatically
2. If download fails, it will fall back to an available model
3. You'll see warnings in the log about model availability

### Permission Issues

If you encounter permission issues with the `.env` file:

1. The script will notify you about the permission problem
2. Changes will only apply to the current session
3. To fix permanently, adjust permissions: `chmod u+w config/.env`

### Report Not Generated for All Models

If the report doesn't include all models:

1. **Availability**: Only models available in your Ollama installation will be tested
2. **Selection**: Ensure you've selected all desired models during the prompt
3. **Timeouts**: Long-running tests might time out; adjust the timeout in the script if needed

## Available Models

The system supports the following models:

1. **llama** - Llama 3 (default)
2. **phi** - Phi model
3. **llama32** - Llama 3.2
4. **bielik** - Bielik model
5. **deepsek** - DeepSeek Coder
6. **qwen** - Qwen model
7. **mistral** - Mistral model

Only models available in your Ollama installation will be listed for testing.

## Customizing Tests

To add new test cases or modify existing ones:

1. Edit `test_queries.py` for basic query tests
2. Edit files in `tests/correctness/` for correctness tests
3. Edit files in `tests/performance/` for performance tests

## Rendering and Viewing Reports

The reports are generated in Markdown format for easy viewing:

1. **Command Line**: Use tools like `mdless` or `glow` to view reports in the terminal:
   ```bash
   glow reports/comparison_report_YYYYMMDD_HHMMSS.md
   ```

2. **Web Browser**: Convert to HTML for better visualization:
   ```bash
   pandoc -s reports/comparison_report_YYYYMMDD_HHMMSS.md -o report.html
   ```

3. **IDE/Editor**: Open the markdown file in any markdown-supporting editor

## Best Practices

1. **Regular Testing**: Run reports periodically to track model improvements
2. **Model Comparison**: Test multiple models to find the best for your use case
3. **Test Case Coverage**: Ensure test cases cover your specific usage scenarios
4. **Performance Monitoring**: Track performance metrics over time to identify trends
EOF
        
        echo -e "${GREEN}Utworzono plik TESTING.md${NC}"
    else
        echo -e "${GREEN}Plik TESTING.md już istnieje${NC}"
    fi
}

# Główna funkcja
function main() {
    echo -e "${GREEN}${BOLD}=== Naprawa systemu raportowania Evopy ===${NC}"
    echo -e "${BLUE}Data: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo
    
    # Sprawdź i utwórz katalogi
    check_and_create_dirs
    
    # Sprawdź dostępne modele
    check_available_models
    
    # Aktualizuj plik .env
    update_env_file
    
    # Napraw skrypty
    fix_report_script
    fix_test_script
    
    # Aktualizuj dokumentację
    update_documentation
    
    # Wygeneruj przykładowy raport
    generate_sample_report
    
    echo
    echo -e "${GREEN}${BOLD}=== Naprawa zakończona ===${NC}"
    echo -e "${BLUE}Teraz możesz uruchomić:${NC}"
    echo -e "  ${YELLOW}./test.sh${NC} - aby przetestować pojedynczy model"
    echo -e "  ${YELLOW}./report.sh${NC} - aby wygenerować raport porównawczy dla wielu modeli"
    echo
}

# Uruchom główną funkcję
main
