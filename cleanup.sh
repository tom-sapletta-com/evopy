#!/bin/bash
# Skrypt czyszczący pliki pośrednie przed generowaniem nowego raportu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Kolory dla terminala
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
else
    GREEN=''
    YELLOW=''
    RED=''
    BLUE=''
    NC=''
fi

# Funkcja do czyszczenia katalogu
clean_directory() {
    local dir="$1"
    local pattern="$2"
    
    if [ -d "$dir" ]; then
        echo -e "${BLUE}Czyszczenie katalogu: ${YELLOW}$dir${NC}"
        if [ -n "$pattern" ]; then
            find "$dir" -name "$pattern" -type f -delete
            echo -e "${GREEN}Usunięto pliki pasujące do wzorca: ${YELLOW}$pattern${NC}"
        else
            rm -rf "$dir"/*
            echo -e "${GREEN}Usunięto wszystkie pliki${NC}"
        fi
    else
        echo -e "${YELLOW}Katalog $dir nie istnieje, tworzenie...${NC}"
        mkdir -p "$dir"
    fi
}

echo -e "${GREEN}=== Czyszczenie plików pośrednich przed generowaniem raportu ===${NC}"

# Czyszczenie katalogów z wynikami testów
clean_directory "$SCRIPT_DIR/tests/performance/results" "*.json"
clean_directory "$SCRIPT_DIR/tests/correctness/results" "*.json"
clean_directory "$SCRIPT_DIR/test_results" "*.json"
clean_directory "$SCRIPT_DIR/generated_code" "*"

# Usuwanie wygenerowanych plików Pythona z hashami
echo -e "${BLUE}Usuwanie wygenerowanych plików Python z hashami...${NC}"
find "$SCRIPT_DIR" -name "*_[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]*.py" -type f -delete
echo -e "${GREEN}Usunięto wygenerowane pliki Python z hashami${NC}"

echo -e "${GREEN}=== Czyszczenie zakończone ===${NC}"
echo -e "${YELLOW}Możesz teraz uruchomić raport, aby wygenerować nowe wyniki.${NC}"
