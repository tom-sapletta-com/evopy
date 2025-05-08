#!/bin/bash

#!/bin/bash
# setup.sh - Skrypt do instalacji i konfiguracji Ewolucyjnego Asystenta
# Autor: Claude
# Data: 08.05.2024

# Kolory dla terminala
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Banner
echo -e "${MAGENTA}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              EWOLUCYJNY ASYSTENT - INSTALACJA                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Sprawdź czy skrypt jest uruchamiany z odpowiednimi uprawnieniami
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Błąd: Ten skrypt nie powinien być uruchamiany jako root.${NC}"
    exit 1
fi

# Funkcje pomocnicze
check_command() {
    command -v $1 >/dev/null 2>&1
}

create_directory() {
    mkdir -p "$1"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Utworzono katalog: $1${NC}"
    else
        echo -e "${RED}✗ Nie udało się utworzyć katalogu: $1${NC}"
        exit 1
    fi
}

# Konfiguracja i zmienne
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.evo-assistant"
LOG_DIR="$SCRIPT_DIR/logs"
DEBUG_DIR="$SCRIPT_DIR/debug_logs"

# Utworzenie potrzebnych katalogów
echo -e "${BLUE}Tworzenie katalogów...${NC}"
create_directory "$INSTALL_DIR"
create_directory "$LOG_DIR"
create_directory "$DEBUG_DIR"

# Sprawdzenie wymagań
echo -e "${BLUE}Sprawdzanie wymagań systemowych...${NC}"

# Python 3.8+
if check_command python3; then
    PYTHON_CMD="python3"
elif check_command python; then
    PYTHON_CMD="python"
else
    echo -e "${RED}✗ Python nie został znaleziony. Proszę zainstalować Python 3.8 lub nowszy.${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_VERSION_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_VERSION_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ $PYTHON_VERSION_MAJOR -lt 3 ] || ([ $PYTHON_VERSION_MAJOR -eq 3 ] && [ $PYTHON_VERSION_MINOR -lt 8 ]); then
    echo -e "${RED}✗ Wymagany jest Python 3.8 lub nowszy. Znaleziono Python $PYTHON_VERSION.${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Python $PYTHON_VERSION znaleziony.${NC}"
fi

# Docker
if check_command docker; then
    echo -e "${GREEN}✓ Docker znaleziony.${NC}"
else
    echo -e "${YELLOW}⚠ Docker nie został znaleziony.${NC}"
    echo -e "${YELLOW}Asystent spróbuje zainstalować Docker automatycznie przy pierwszym uruchomieniu.${NC}"
fi

# Docker Compose
if check_command docker-compose || docker compose >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Docker Compose znaleziony.${NC}"
else
    echo -e "${YELLOW}⚠ Docker Compose nie został znaleziony.${NC}"
    echo -e "${YELLOW}Asystent spróbuje zainstalować Docker Compose automatycznie przy pierwszym uruchomieniu.${NC}"
fi

# Ollama
if check_command ollama; then
    echo -e "${GREEN}✓ Ollama znaleziona.${NC}"
else
    echo -e "${YELLOW}⚠ Ollama nie została znaleziona.${NC}"
    echo -e "${YELLOW}Asystent spróbuje zainstalować Ollama automatycznie przy pierwszym uruchomieniu.${NC}"
fi

# Instalacja zależności Python
echo -e "${BLUE}Instalacja zależności Python...${NC}"

# Sprawdź czy pip jest zainstalowany
if check_command pip3; then
    PIP_CMD="pip3"
elif check_command pip; then
    PIP_CMD="pip"
else
    echo -e "${RED}✗ pip nie został znaleziony. Proszę zainstalować pip.${NC}"
    exit 1
fi

# Opcjonalna instalacja virtualenv
if [ "$1" == "--venv" ]; then
    echo -e "${BLUE}Tworzenie wirtualnego środowiska...${NC}"
    
    # Sprawdź czy virtualenv jest zainstalowany
    if ! check_command virtualenv; then
        echo -e "${YELLOW}⚠ Instalacja virtualenv...${NC}"
        $PIP_CMD install virtualenv
    fi
    
    # Tworzenie wirtualnego środowiska
    VENV_DIR="$SCRIPT_DIR/venv"
    virtualenv "$VENV_DIR"
    
    # Aktywacja wirtualnego środowiska
    source "$VENV_DIR/bin/activate"
    
    PIP_CMD="$VENV_DIR/bin/pip"
    PYTHON_CMD="$VENV_DIR/bin/python"
    
    echo -e "${GREEN}✓ Wirtualne środowisko aktywowane.${NC}"
fi

# Instalacja zależności z requirements.txt
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    echo -e "${BLUE}Instalacja zależności z pliku requirements.txt...${NC}"
    $PIP_CMD install -r "$SCRIPT_DIR/requirements.txt"
else
    echo -e "${YELLOW}⚠ Plik requirements.txt nie został znaleziony. Instalacja podstawowych zależności...${NC}"
    $PIP_CMD install httpx
    
    # Instalacja readline w zależności od systemu operacyjnego
    if [[ "$OSTYPE" == "darwin"* ]]; then
        $PIP_CMD install readline
    elif [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
        $PIP_CMD install pyreadline3
    fi
    
    # Zależności dla narzędzi testowych i debugowania
    $PIP_CMD install pexpect psutil docker
    
    # Instalacja pyshark jeśli nie jest to ARM64
    ARCH=$(uname -m)
    if [ "$ARCH" != "arm64" ] && [ "$ARCH" != "aarch64" ]; then
        $PIP_CMD install pyshark || echo -e "${YELLOW}⚠ Nie udało się zainstalować pyshark. Monitor debugowania będzie miał ograniczoną funkcjonalność.${NC}"
    fi
fi

# Kopiowanie plików
echo -e "${BLUE}Kopiowanie plików...${NC}"

# Kopiowanie pliku evo_assistant.py jeśli istnieje
if [ -f "$SCRIPT_DIR/evolutionary_assistant.py" ]; then
    cp "$SCRIPT_DIR/evolutionary_assistant.py" "$SCRIPT_DIR/evo_assistant.py"
    chmod +x "$SCRIPT_DIR/evo_assistant.py"
    echo -e "${GREEN}✓ Skopiowano evolutionary_assistant.py do evo_assistant.py${NC}"
fi

# Kopiowanie pliku test_script.py jeśli istnieje
if [ -f "$SCRIPT_DIR/test_script.py" ]; then
    chmod +x "$SCRIPT_DIR/test_script.py"
    echo -e "${GREEN}✓ Ustawiono uprawnienia wykonywania dla test_script.py${NC}"
fi

# Kopiowanie pliku debug_monitor.py jeśli istnieje
if [ -f "$SCRIPT_DIR/debug_monitor.py" ]; then
    chmod +x "$SCRIPT_DIR/debug_monitor.py"
    echo -e "${GREEN}✓ Ustawiono uprawnienia wykonywania dla debug_monitor.py${NC}"
fi

# Tworzenie plików uruchomieniowych
echo -e "${BLUE}Tworzenie skryptów uruchomieniowych...${NC}"

# Plik run.sh do uruchamiania asystenta
cat > "$SCRIPT_DIR/run.sh" << EOL
#!/bin/bash
# Skrypt uruchamiający Ewolucyjnego Asystenta

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "\$SCRIPT_DIR/venv" ]; then
    source "\$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="\$SCRIPT_DIR/venv/bin/python"
else
    # Wybierz dostępną komendę Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Uruchom asystenta
\$PYTHON_CMD "\$SCRIPT_DIR/evo_assistant.py" \$@
EOL

chmod +x "$SCRIPT_DIR/run.sh"
echo -e "${GREEN}✓ Utworzono skrypt run.sh${NC}"

# Plik debug.sh do uruchamiania monitora debugowania
cat > "$SCRIPT_DIR/debug.sh" << EOL
#!/bin/bash
# Skrypt uruchamiający monitor debugowania

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "\$SCRIPT_DIR/venv" ]; then
    source "\$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="\$SCRIPT_DIR/venv/bin/python"
else
    # Wybierz dostępną komendę Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Uruchom monitor debugowania
\$PYTHON_CMD "\$SCRIPT_DIR/debug_monitor.py" --script "\$SCRIPT_DIR/evo_assistant.py" \$@
EOL

chmod +x "$SCRIPT_DIR/debug.sh"
echo -e "${GREEN}✓ Utworzono skrypt debug.sh${NC}"

# Plik test.sh do uruchamiania skryptu testującego
cat > "$SCRIPT_DIR/test.sh" << EOL
#!/bin/bash
# Skrypt uruchamiający testy

SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"

# Aktywacja wirtualnego środowiska, jeśli istnieje
if [ -d "\$SCRIPT_DIR/venv" ]; then
    source "\$SCRIPT_DIR/venv/bin/activate"
    PYTHON_CMD="\$SCRIPT_DIR/venv/bin/python"
else
    # Wybierz dostępną komendę Python
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

# Uruchom testy
\$PYTHON_CMD "\$SCRIPT_DIR/test_script.py" \$@
EOL

chmod +x "$SCRIPT_DIR/test.sh"
echo -e "${GREEN}✓ Utworzono skrypt test.sh${NC}"

# Tworzenie skrótów dla Windows
if [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]]; then
    echo -e "${BLUE}Tworzenie skrótów dla Windows...${NC}"
    
    # Plik run.bat
    cat > "$SCRIPT_DIR/run.bat" << EOL
@echo off
cd "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python evo_assistant.py %*
) else (
    python evo_assistant.py %*
)
EOL
    echo -e "${GREEN}✓ Utworzono skrypt run.bat${NC}"
    
    # Plik debug.bat
    cat > "$SCRIPT_DIR/debug.bat" << EOL
@echo off
cd "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python debug_monitor.py --script evo_assistant.py %*
) else (
    python debug_monitor.py --script evo_assistant.py %*
)
EOL
    echo -e "${GREEN}✓ Utworzono skrypt debug.bat${NC}"
    
    # Plik test.bat
    cat > "$SCRIPT_DIR/test.bat" << EOL
@echo off
cd "%~dp0"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    python test_script.py %*
) else (
    python test_script.py %*
)
EOL
    echo -e "${GREEN}✓ Utworzono skrypt test.bat${NC}"
fi

# Podsumowanie
echo -e "${MAGENTA}${BOLD}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              INSTALACJA ZAKOŃCZONA POMYŚLNIE!                 ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${CYAN}Aby uruchomić asystenta, użyj:${NC}"
echo -e "${GREEN}  ${SCRIPT_DIR}/run.sh${NC}"
echo -e "${CYAN}Aby uruchomić monitor debugowania, użyj:${NC}"
echo -e "${GREEN}  ${SCRIPT_DIR}/debug.sh${NC}"
echo -e "${CYAN}Aby uruchomić testy, użyj:${NC}"
echo -e "${GREEN}  ${SCRIPT_DIR}/test.sh${NC}"

echo ""
echo -e "${YELLOW}Uwaga: Przy pierwszym uruchomieniu asystent sprawdzi i zainstaluje brakujące zależności,${NC}"
echo -e "${YELLOW}       takie jak Docker, Docker Compose czy Ollama, jeśli ich nie znaleziono.${NC}"
echo ""

# Pytanie o uruchomienie asystenta
echo -e "${BLUE}Czy chcesz uruchomić asystenta teraz? (t/N)${NC}"
read -r choice

if [[ "$choice" == "t" ]] || [[ "$choice" == "T" ]]; then
    echo -e "${BLUE}Uruchamianie asystenta...${NC}"
    "${SCRIPT_DIR}/run.sh"
else
    echo -e "${BLUE}Możesz uruchomić asystenta później za pomocą ${GREEN}${SCRIPT_DIR}/run.sh${NC}"
fi