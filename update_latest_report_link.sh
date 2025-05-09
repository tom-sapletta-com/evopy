#!/bin/bash
# Skrypt do aktualizacji linku do najnowszego raportu

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORTS_DIR="$SCRIPT_DIR/reports"
LATEST_LINK="$REPORTS_DIR/comparison_report_latest.md"

# Kolory dla terminala
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    NC='\033[0m' # No Color
else
    GREEN=''
    YELLOW=''
    RED=''
    NC=''
fi

# Sprawdź czy katalog raportów istnieje
if [ ! -d "$REPORTS_DIR" ]; then
    echo -e "${YELLOW}Tworzenie katalogu raportów: $REPORTS_DIR${NC}"
    mkdir -p "$REPORTS_DIR"
fi

# Znajdź najnowszy raport
LATEST_REPORT=$(find "$REPORTS_DIR" -name "comparison_report_*.md" -type f | sort -r | head -n 1)

if [ -z "$LATEST_REPORT" ]; then
    echo -e "${RED}Nie znaleziono żadnych raportów w katalogu $REPORTS_DIR${NC}"
    exit 1
fi

# Utwórz lub zaktualizuj link symboliczny
if [ -L "$LATEST_LINK" ]; then
    # Link już istnieje, aktualizuj go
    rm "$LATEST_LINK"
fi

# Utwórz link symboliczny do najnowszego raportu
REPORT_FILENAME=$(basename "$LATEST_REPORT")
ln -s "$REPORT_FILENAME" "$LATEST_LINK"

echo -e "${GREEN}Link do najnowszego raportu został zaktualizowany:${NC}"
echo -e "  ${YELLOW}$LATEST_LINK${NC} -> ${YELLOW}$REPORT_FILENAME${NC}"

# Wyświetl datę raportu
TIMESTAMP=$(echo "$REPORT_FILENAME" | grep -o "[0-9]\{8\}_[0-9]\{6\}")
if [ -n "$TIMESTAMP" ]; then
    REPORT_DATE=$(date -d "${TIMESTAMP:0:8} ${TIMESTAMP:9:2}:${TIMESTAMP:11:2}:${TIMESTAMP:13:2}" '+%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}Data raportu: ${YELLOW}$REPORT_DATE${NC}"
fi

exit 0
