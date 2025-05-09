#!/usr/bin/env python3
"""
Ewolucyjny Asystent - system konwersacyjny rozwijający się wraz z interakcjami

Ten program uruchamia minimalny, samorozwijający się system konwersacyjny, który potrafi:
1. Sprawdzić i zainstalować wymagane zależności (Docker, model DeepSeek)
2. Uruchomić model językowy w kontenerze Docker
3. Zarządzać konwersacjami w wątkach
4. Ewoluować poprzez rozszerzanie własnych możliwości w trakcie konwersacji
5. Tworzyć i zarządzać piaskownicami Docker Compose dla projektów

Autor: Claude
Data: 08.05.2024
"""

import os
import sys
import json
import time
import uuid
import shutil
import signal
import logging
import logging.handlers
import asyncio
import argparse
import platform
import readline  # Do historii w konsoli
import subprocess
import threading
import psutil
import importlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Import narzędzi interfejsu konsolowego
try:
    from console_utils import Colors, CommandCompleter, ResultFormatter, print_header, print_table, create_progress_bar
    CONSOLE_UTILS_AVAILABLE = True
except ImportError:
    CONSOLE_UTILS_AVAILABLE = False
    # Fallback do oryginalnej klasy Colors
    class Colors:
        HEADER = '\033[95m'
        BLUE = '\033[94m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

# Definicja ścieżek projektu
APP_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Import modułów lokalnych
try:
    from modules.text2python.text2python import Text2Python
    from docker_sandbox import DockerSandbox
except ImportError:
    # Jeśli moduły nie są dostępne, dodaj katalog projektu do ścieżki
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from modules.text2python.text2python import Text2Python
    from docker_sandbox import DockerSandbox

# Konfiguracja logowania z rotacją
LOG_DIR = APP_DIR / "logs"
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            "assistant.log", 
            maxBytes=100*1024*1024,  # 100MB
            backupCount=5
        )
    ]
)
logger = logging.getLogger("evo-assistant")

# Kolory dla terminala zdefiniowane w console_utils.py

# Stałe
APP_DIR = Path.home() / ".evo-assistant"
HISTORY_DIR = APP_DIR / "history"
PROJECTS_DIR = APP_DIR / "projects"
CACHE_DIR = APP_DIR / "cache"
MODELS_DIR = APP_DIR / "models"
SANDBOX_DIR = APP_DIR / "sandbox"  # Katalog dla piaskownic Docker
CODE_DIR = APP_DIR / "code"  # Katalog dla generowanego kodu
CONFIG_FILE = APP_DIR / "config.json"

# Lista dostępnych modeli
AVAILABLE_MODELS = [
    {"name": "llama3", "description": "Llama 3 - model ogólnego zastosowania"},
    {"name": "deepseek-coder:6.7b", "description": "DeepSeek 6.7B - model zoptymalizowany do kodowania"},
    {"name": "bielik:v3", "description": "Bielik v3 - polski model językowy"}
]

# Domyślny model
DEFAULT_MODEL = AVAILABLE_MODELS[0]["name"]

VERSION = "0.1.0"

# Domyślna konfiguracja
DEFAULT_CONFIG = {
    "model": DEFAULT_MODEL,
    "auto_install_dependencies": True,
    "max_history": 100,
    "max_projects": 10,
    "default_docker_network": "evo-assistant-network",
    "version": VERSION,
    "skills": [],
    "conversation_context": 2048,
    "sandbox_image": "python:3.9-slim",  # Obraz bazowy dla piaskownic
    "sandbox_timeout": 30,  # Limit czasu wykonania kodu w sekundach
    "max_code_size": 10240,  # Maksymalny rozmiar kodu w bajtach
}

class EvoAssistant:
    """Główna klasa asystenta ewolucyjnego"""
    
    def __init__(self, config_path: Path = CONFIG_FILE):
        """Inicjalizacja asystenta"""
        self.config_path = config_path
        self.config = self._load_config()
        self.conversations = {}
        self.current_conversation_id = None
        self.ollama_process = None
        self.running = True
        self.skills = self.config.get("skills", [])
        
        # Inicjalizacja katalogów
        self._initialize_directories()
        
        # Inicjalizacja modułów
        self.text2python = Text2Python({
            "model": self.config.get("model", DEFAULT_MODEL),
            "code_dir": str(CODE_DIR)
        })
        
        # Inicjalizacja narzędzi interfejsu konsolowego
        if CONSOLE_UTILS_AVAILABLE:
            from console_utils import DEFAULT_COMMANDS
            self.result_formatter = ResultFormatter()
            self.command_completer = CommandCompleter(DEFAULT_COMMANDS)
        
        # Rejestracja obsługi sygnałów
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
    
    def _load_config(self) -> Dict:
        """Ładuje konfigurację z pliku lub tworzy domyślną"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Aktualizacja wersji jeśli potrzeba
                    if config.get("version") != VERSION:
                        config.update({"version": VERSION})
                        with open(self.config_path, 'w') as f:
                            json.dump(config, f, indent=2)
                    return config
            except Exception as e:
                logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
                return DEFAULT_CONFIG
        else:
            # Tworzenie domyślnej konfiguracji
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            return DEFAULT_CONFIG
    
    def _save_config(self):
        """Zapisuje konfigurację do pliku"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
    
    def _initialize_directories(self):
        """Tworzy wymagane katalogi"""
        for directory in [APP_DIR, HISTORY_DIR, PROJECTS_DIR, CACHE_DIR, MODELS_DIR, SANDBOX_DIR, CODE_DIR]:
            os.makedirs(directory, exist_ok=True)
    
    def _handle_interrupt(self, signum, frame):
        """Obsługa sygnału przerwania (Ctrl+C)"""
        print(f"\n{Colors.YELLOW}Otrzymano sygnał przerwania. Kończenie pracy...{Colors.END}")
        self.running = False
        if self.ollama_process:
            logger.info("Zatrzymywanie procesu Ollama...")
            self.ollama_process.terminate()
            try:
                self.ollama_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.ollama_process.kill()
        sys.exit(0)
    
    def check_dependencies(self) -> bool:
        """Sprawdza czy wymagane zależności są zainstalowane"""
        dependencies_ok = True
        
        # Sprawdzenie Pythona
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            logger.warning(f"Wymagany Python 3.8+. Aktualnie używany: {python_version.major}.{python_version.minor}.{python_version.micro}")
            dependencies_ok = False
        
        # Sprawdzenie Dockera
        docker_installed = shutil.which("docker") is not None
        if not docker_installed:
            logger.warning("Docker nie jest zainstalowany lub nie jest dostępny w PATH")
            dependencies_ok = False
            if self.config.get("auto_install_dependencies", True):
                self._install_docker()
        else:
            logger.info("Docker jest zainstalowany")
            # Sprawdzenie czy Docker działa
            try:
                subprocess.run(["docker", "info"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                logger.info("Docker działa poprawnie")
            except subprocess.CalledProcessError:
                logger.warning("Docker jest zainstalowany, ale nie działa poprawnie")
                dependencies_ok = False
        
        # Sprawdzenie Docker Compose
        docker_compose_installed = shutil.which("docker-compose") is not None or self._check_docker_compose_plugin()
        if not docker_compose_installed:
            logger.warning("Docker Compose nie jest zainstalowany lub nie jest dostępny w PATH")
            dependencies_ok = False
            if self.config.get("auto_install_dependencies", True):
                self._install_docker_compose()
        else:
            logger.info("Docker Compose jest zainstalowany")
        
        # Sprawdzenie Ollama
        ollama_installed = shutil.which("ollama") is not None
        if not ollama_installed:
            logger.warning("Ollama nie jest zainstalowana lub nie jest dostępna w PATH")
            dependencies_ok = False
            if self.config.get("auto_install_dependencies", True):
                self._install_ollama()
        else:
            logger.info("Ollama jest zainstalowana")
            
            # Sprawdzenie czy model jest pobrany
            model = self.config.get("model", DEFAULT_MODEL)
            if not self._check_model_exists(model):
                logger.warning(f"Model {model} nie jest pobrany")
                dependencies_ok = False
                if self.config.get("auto_install_dependencies", True):
                    # Jeśli model został pobrany, zaktualizuj status zależności
                    if self._pull_model(model):
                        dependencies_ok = True
        
        return dependencies_ok
    
    def _check_docker_compose_plugin(self) -> bool:
        """Sprawdza czy Docker Compose jest dostępny jako plugin Docker"""
        try:
            subprocess.run(["docker", "compose", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _install_docker(self):
        """Instaluje Docker"""
        system = platform.system().lower()
        
        # Sprawdź czy auto-accept jest włączone
        auto_accept = os.environ.get("EVOPY_AUTO_ACCEPT", "0") == "1"
        
        if system == "linux":
            # Instrukcje dla Linux
            if auto_accept:
                print(f"{Colors.YELLOW}Docker nie jest zainstalowany. Automatycznie akceptuję instalację.{Colors.END}")
                choice = 't'
            else:
                print(f"{Colors.YELLOW}Docker nie jest zainstalowany. Czy chcesz go zainstalować? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                
            if choice == 't':
                print(f"{Colors.BLUE}Instalowanie Dockera...{Colors.END}")
                os.system("curl -fsSL https://get.docker.com -o get-docker.sh")
                os.system("sh get-docker.sh")
                os.system("sudo usermod -aG docker $USER")
                print(f"{Colors.GREEN}Docker został zainstalowany. Może być konieczne wylogowanie i ponowne zalogowanie.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Instalacja Dockera pominięta. Asystent może nie działać poprawnie.{Colors.END}")
        
        elif system == "darwin":  # macOS
            print(f"{Colors.YELLOW}Docker nie jest zainstalowany. Proszę pobrać i zainstalować Docker Desktop ze strony: https://www.docker.com/products/docker-desktop{Colors.END}")
            input("Naciśnij Enter, aby kontynuować po zainstalowaniu Dockera...")
        
        elif system == "windows":
            print(f"{Colors.YELLOW}Docker nie jest zainstalowany. Proszę pobrać i zainstalować Docker Desktop ze strony: https://www.docker.com/products/docker-desktop{Colors.END}")
            input("Naciśnij Enter, aby kontynuować po zainstalowaniu Dockera...")
        
        else:
            print(f"{Colors.RED}Nieznany system operacyjny. Proszę zainstalować Docker ręcznie.{Colors.END}")
    
    def _install_docker_compose(self):
        """Instaluje Docker Compose"""
        system = platform.system().lower()
        
        # Sprawdź czy auto-accept jest włączone
        auto_accept = os.environ.get("EVOPY_AUTO_ACCEPT", "0") == "1"
        
        if system == "linux":
            if auto_accept:
                print(f"{Colors.YELLOW}Docker Compose nie jest zainstalowany. Automatycznie akceptuję instalację.{Colors.END}")
                choice = 't'
            else:
                print(f"{Colors.YELLOW}Docker Compose nie jest zainstalowany. Czy chcesz go zainstalować? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                
            if choice == 't':
                print(f"{Colors.BLUE}Instalowanie Docker Compose...{Colors.END}")
                os.system("sudo curl -L https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose")
                os.system("sudo chmod +x /usr/local/bin/docker-compose")
                print(f"{Colors.GREEN}Docker Compose został zainstalowany.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Instalacja Docker Compose pominięta. Asystent może nie działać poprawnie.{Colors.END}")
        
        else:
            print(f"{Colors.YELLOW}Docker Compose powinien być zainstalowany razem z Docker Desktop.{Colors.END}")
    
    def _install_ollama(self):
        """Instaluje Ollama"""
        system = platform.system().lower()
        
        # Sprawdź czy auto-accept jest włączone
        auto_accept = os.environ.get("EVOPY_AUTO_ACCEPT", "0") == "1"
        
        if system == "linux":
            if auto_accept:
                print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Automatycznie akceptuję instalację.{Colors.END}")
                choice = 't'
            else:
                print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Czy chcesz ją zainstalować? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                
            if choice == 't':
                print(f"{Colors.BLUE}Instalowanie Ollama...{Colors.END}")
                os.system("curl -fsSL https://ollama.com/install.sh | sh")
                print(f"{Colors.GREEN}Ollama została zainstalowana.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Instalacja Ollama pominięta. Asystent będzie używać Ollama w kontenerze Docker.{Colors.END}")
        
        elif system == "darwin":  # macOS
            if auto_accept:
                print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Automatycznie akceptuję instalację.{Colors.END}")
                choice = 't'
            else:
                print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Czy chcesz ją zainstalować? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                
            if choice == 't':
                print(f"{Colors.BLUE}Instalowanie Ollama...{Colors.END}")
                os.system("curl -fsSL https://ollama.com/install.sh | sh")
                print(f"{Colors.GREEN}Ollama została zainstalowana.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Instalacja Ollama pominięta. Asystent będzie używać Ollama w kontenerze Docker.{Colors.END}")
        
        elif system == "windows":
            print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Proszę pobrać i zainstalować Ollama ze strony: https://ollama.com/download{Colors.END}")
            input("Naciśnij Enter, aby kontynuować po zainstalowaniu Ollama...")
        
        else:
            print(f"{Colors.RED}Nieznany system operacyjny. Proszę zainstalować Ollama ręcznie.{Colors.END}")
    
    def _check_model_exists(self, model: str) -> bool:
        """Sprawdza czy model jest dostępny lokalnie"""
        try:
            result = subprocess.run(["ollama", "list"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return model in result.stdout
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania modelu: {e}")
            return False
    
    def _pull_model(self, model: str) -> bool:
        """Pobiera model Ollama
        
        Returns:
            bool: True jeśli model został pobrany, False w przeciwnym razie
        """
        # Sprawdź czy auto-accept jest włączone
        auto_accept = os.environ.get("EVOPY_AUTO_ACCEPT", "0") == "1"
        
        if auto_accept:
            print(f"{Colors.YELLOW}Model {model} nie jest pobrany. Automatycznie akceptuję pobieranie.{Colors.END}")
            choice = 't'
        else:
            # Jeśli już jesteśmy w trakcie pobierania, nie pytaj ponownie
            choice = 't'
        
        if choice == 't':
            print(f"{Colors.BLUE}Pobieranie modelu {model}...{Colors.END}")
            start_time = time.time()
            process = subprocess.Popen(["ollama", "pull", model], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Zmienne do śledzenia postępu
            total_size = None
            downloaded = 0
            last_percentage = 0
            estimated_time = "obliczanie..."
            
            # Wyświetlanie postępu
            while process.poll() is None:
                output = process.stdout.readline().strip()
                if output:
                    # Próba wyodrębnienia informacji o postępie
                    if "downloading" in output.lower():
                        try:
                            # Przykładowy format: "downloading: 45.54 MiB / 4.07 GiB (1.09%)"
                            parts = output.split()
                            if len(parts) >= 5 and parts[2] == "/":
                                # Pobierz informacje o rozmiarze
                                current_size_str = parts[1]
                                total_size_str = parts[3]
                                percentage_str = parts[4].strip("()%")
                                
                                # Konwersja na bajty dla dokładniejszych obliczeń
                                current_size = float(current_size_str)
                                current_unit = parts[1].split()[-1] if len(parts[1].split()) > 1 else "B"
                                total_size_value = float(total_size_str)
                                total_unit = parts[3].split()[-1] if len(parts[3].split()) > 1 else "B"
                                
                                # Konwersja jednostek na bajty
                                unit_multipliers = {"B": 1, "KiB": 1024, "MiB": 1024**2, "GiB": 1024**3, "TiB": 1024**4}
                                downloaded = current_size * unit_multipliers.get(current_unit, 1)
                                if total_size is None:
                                    total_size = total_size_value * unit_multipliers.get(total_unit, 1)
                                
                                # Obliczanie czasu pozostałego
                                percentage = float(percentage_str)
                                if percentage > 0:
                                    elapsed_time = time.time() - start_time
                                    estimated_total_time = elapsed_time / (percentage / 100)
                                    remaining_time = estimated_total_time - elapsed_time
                                    
                                    # Formatowanie czasu pozostałego
                                    if remaining_time < 60:
                                        estimated_time = f"{int(remaining_time)} sekund"
                                    elif remaining_time < 3600:
                                        estimated_time = f"{int(remaining_time / 60)} minut {int(remaining_time % 60)} sekund"
                                    else:
                                        estimated_time = f"{int(remaining_time / 3600)} godzin {int((remaining_time % 3600) / 60)} minut"
                                
                                # Tworzenie paska postępu
                                bar_length = 30
                                filled_length = int(bar_length * percentage / 100)
                                bar = '█' * filled_length + '░' * (bar_length - filled_length)
                                
                                # Wyświetlanie paska postępu i informacji
                                progress_info = f"[{bar}] {percentage:.2f}% | Pozostało: {estimated_time}"
                                print(f"\r{Colors.BLUE}{progress_info}{Colors.END}", end="")
                                last_percentage = percentage
                        except Exception as e:
                            # W przypadku błędu parsowania, wyświetl oryginalny output
                            print(f"\r{Colors.BLUE}{output}{Colors.END}", end="")
                    else:
                        print(f"\r{Colors.BLUE}{output}{Colors.END}", end="")
                time.sleep(0.1)
            
            # Po zakończeniu pobierania
            if last_percentage > 0:
                bar_length = 30
                bar = '█' * bar_length
                print(f"\r{Colors.BLUE}[{bar}] 100.00% | Zakończono!{Colors.END}")
            
            print(f"\n{Colors.GREEN}Model {model} został pobrany.{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}Pobieranie modelu pominięte. Asystent może nie działać poprawnie.{Colors.END}")
            return False
    
    def _ensure_model_downloaded(self) -> bool:
        """Upewnia się, że model jest pobrany lokalnie przed uruchomieniem Dockera"""
        model = self.config.get("model", DEFAULT_MODEL)
        
        # Sprawdź czy ollama jest zainstalowana
        ollama_installed = shutil.which("ollama") is not None
        if not ollama_installed:
            logger.warning("Ollama nie jest zainstalowana. Nie można pobrać modelu lokalnie.")
            return False
            
        # Sprawdź czy model jest już pobrany
        if self._check_model_exists(model):
            logger.info(f"Model {model} jest już pobrany lokalnie.")
            print(f"{Colors.GREEN}Model {model} jest już pobrany lokalnie.{Colors.END}")
            return True
            
        # Pobierz model
        logger.info(f"Pobieranie modelu {model} lokalnie przed uruchomieniem Dockera...")
        return self._pull_model(model)
    
    def _start_ollama_server(self):
        """Uruchamia serwer Ollama"""
        logger.info("Uruchamianie serwera Ollama...")
        model = self.config.get("model", DEFAULT_MODEL)
        
        # Sprawdź czy Ollama jest już uruchomiona
        try:
            subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            logger.info("Serwer Ollama jest już uruchomiony")
            return True
        except subprocess.CalledProcessError:
            # Ollama nie jest uruchomiona, uruchamiamy
            try:
                self.ollama_process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(2)  # Czekamy na uruchomienie serwera
                logger.info("Serwer Ollama został uruchomiony")
                return True
            except Exception as e:
                logger.error(f"Błąd podczas uruchamiania serwera Ollama: {e}")
                
                # Próba uruchomienia Ollama w kontenerze Docker
                logger.info("Próba uruchomienia Ollama w kontenerze Docker...")
                try:
                    # Określ ścieżkę do katalogu z modelami Ollama
                    ollama_models_dir = Path.home() / ".ollama" / "models"
                    docker_models_volume = "ollama-data:/root/.ollama"
                    
                    # Sprawdź czy model został pobrany lokalnie
                    model_downloaded = self._check_model_exists(model)
                    
                    # Jeśli model został pobrany lokalnie, użyj bindowania woluminu
                    if model_downloaded and ollama_models_dir.exists():
                        docker_models_volume = f"{ollama_models_dir}:/root/.ollama/models"
                        logger.info(f"Używanie lokalnie pobranych modeli: {docker_models_volume}")
                    
                    # Uruchom kontener Ollama z podpiętym woluminem modeli
                    subprocess.run(["docker", "run", "-d", "--name", "evo-assistant-ollama", "-p", "11434:11434", 
                                    "-v", docker_models_volume, "ollama/ollama"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    logger.info("Ollama została uruchomiona w kontenerze Docker")
                    
                    # Jeśli model nie został pobrany lokalnie, pobierz go w kontenerze
                    if not model_downloaded:
                        logger.info(f"Pobieranie modelu {model} w kontenerze Docker...")
                        print(f"{Colors.BLUE}Pobieranie modelu {model} w kontenerze Docker...{Colors.END}")
                        process = subprocess.Popen(["docker", "exec", "evo-assistant-ollama", "ollama", "pull", model], 
                                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                        
                        # Wyświetlanie postępu
                        while process.poll() is None:
                            output = process.stdout.readline().strip()
                            if output:
                                print(f"\r{Colors.BLUE}{output}{Colors.END}", end="")
                            time.sleep(0.1)
                        
                        print(f"\n{Colors.GREEN}Model {model} został pobrany w kontenerze Docker.{Colors.END}")
                    
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"Błąd podczas uruchamiania Ollama w kontenerze Docker: {e}")
                    return False
    
    def start(self):
        """Uruchamia asystenta"""
        print(f"{Colors.HEADER}{Colors.BOLD}Ewolucyjny Asystent v{VERSION}{Colors.END}")
        print(f"{Colors.BLUE}Sprawdzanie zależności...{Colors.END}")
        
        if not self.check_dependencies():
            print(f"{Colors.RED}Nie wszystkie zależności są spełnione. Asystent może nie działać poprawnie.{Colors.END}")
            print(f"{Colors.YELLOW}Czy chcesz kontynuować mimo to? (t/N):{Colors.END} ", end="")
            choice = input().lower()
            if choice != 't':
                print(f"{Colors.RED}Kończenie pracy.{Colors.END}")
                return
        
        # Upewnij się, że model jest pobrany lokalnie przed uruchomieniem Dockera
        model = self.config.get("model", DEFAULT_MODEL)
        print(f"{Colors.BLUE}Upewnianie się, że model {model} jest pobrany lokalnie...{Colors.END}")
        model_downloaded = self._ensure_model_downloaded()
        
        print(f"{Colors.BLUE}Uruchamianie serwera modelu językowego...{Colors.END}")
        if not self._start_ollama_server():
            print(f"{Colors.RED}Nie udało się uruchomić serwera modelu językowego. Kończenie pracy.{Colors.END}")
            return
        
        # Tworzenie nowej konwersacji
        self._create_new_conversation()
        
        print(f"{Colors.GREEN}Asystent gotowy do pracy!{Colors.END}")
        print(f"{Colors.BLUE}Wpisz '/help' aby uzyskać pomoc.{Colors.END}")
        
        # Główna pętla interakcji
        self._interactive_loop()
    
    def _create_new_conversation(self):
        """Tworzy nową konwersację"""
        conversation_id = str(uuid.uuid4())
        self.conversations[conversation_id] = {
            "id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "messages": [],
            "projects": [],
            "title": "Nowa konwersacja"
        }
        self.current_conversation_id = conversation_id
        logger.info(f"Utworzono nową konwersację: {conversation_id}")
        
        # Zapisanie konwersacji
        self._save_conversation(conversation_id)
        
        return conversation_id
    
    def _save_conversation(self, conversation_id: str):
        """Zapisuje konwersację do pliku"""
        conversation = self.conversations.get(conversation_id)
        if conversation:
            conversation_file = HISTORY_DIR / f"{conversation_id}.json"
            with open(conversation_file, 'w') as f:
                json.dump(conversation, f, indent=2)
    
    def _load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Ładuje konwersację z pliku"""
        conversation_file = HISTORY_DIR / f"{conversation_id}.json"
        if conversation_file.exists():
            with open(conversation_file, 'r') as f:
                return json.load(f)
        return None
    
    def _list_conversations(self) -> List[Dict]:
        """Zwraca listę wszystkich konwersacji"""
        conversations = []
        for file in HISTORY_DIR.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    conversation = json.load(f)
                    conversations.append({
                        "id": conversation.get("id"),
                        "title": conversation.get("title", "Bez tytułu"),
                        "created_at": conversation.get("created_at"),
                        "updated_at": conversation.get("updated_at"),
                        "messages_count": len(conversation.get("messages", [])),
                        "projects_count": len(conversation.get("projects", []))
                    })
            except Exception as e:
                logger.error(f"Błąd podczas ładowania konwersacji {file}: {e}")
        
        # Sortowanie konwersacji od najnowszej
        conversations.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
        
        return conversations
    
    def _handle_query(self, query: str):
        """Obsługuje zapytanie użytkownika"""
        try:
            logger.info(f"Rozpoczęcie obsługi zapytania: '{query}'")
            
            if not self.current_conversation_id or self.current_conversation_id not in self.conversations:
                logger.debug("Brak aktywnej konwersacji, tworzenie nowej")
                self._create_new_conversation()
            
            # Dodaj wiadomość użytkownika do historii
            self.conversations[self.current_conversation_id]["messages"].append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            
            # Aktualizacja czasu ostatniej modyfikacji
            self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
            
            # Zapisz konwersację
            self._save_conversation(self.current_conversation_id)
            logger.debug(f"Zapisano konwersację: {self.current_conversation_id}")
            
            # Konwertuj zapytanie użytkownika na kod Python i weryfikuj intencje
            print(f"{Colors.BLUE}Konwertowanie zapytania na kod Python...{Colors.END}")
            code_result = self.text2python.generate_code(query)
            
            # Sprawdź wynik generowania kodu
            if not code_result["success"]:
                error_msg = code_result.get('error', 'Nieznany błąd')
                logger.warning(f"Nie udało się wygenerować kodu: {error_msg}")
                
                # Jeśli mamy kod mimo błędu (np. dla nieprawidłowego zapytania), wyświetl go
                if code_result.get("code"):
                    print(f"{Colors.GREEN}Wygenerowano kod Python:{Colors.END}")
                    print(f"{Colors.CYAN}{code_result['code']}{Colors.END}")
                    
                    # Dodaj informację o analizie zapytania
                    if code_result.get("analysis"):
                        print(f"{Colors.YELLOW}Analiza zapytania: {code_result['analysis']}{Colors.END}")
                    
                    # Automatycznie uruchamiaj kod w piaskownicy Docker
                    print(f"{Colors.BLUE}Automatyczne uruchamianie kodu w piaskownicy Docker...{Colors.END}")
                    choice = 't'
                    
                    if choice == 't':
                        # Kontynuuj z uruchomieniem kodu
                        code = code_result["code"]
                    else:
                        print(f"{Colors.YELLOW}Pominięto uruchomienie kodu.{Colors.END}")
                        return
                else:
                    print(f"{Colors.RED}Nie udało się wygenerować kodu: {error_msg}{Colors.END}")
                    return
            else:
                # Pokaż wygenerowany kod
                code = code_result["code"]
                logger.info("Kod został pomyślnie wygenerowany")
                print(f"{Colors.GREEN}Wygenerowano kod Python:{Colors.END}")
                
                # Użyj kolorowania składni, jeśli dostępne
                if CONSOLE_UTILS_AVAILABLE:
                    print(self.result_formatter.format_code(code))
                else:
                    print(f"{Colors.CYAN}{code}{Colors.END}")
                
                # Pokaż wyjaśnienie kodu
                if code_result.get("explanation"):
                    print(f"{Colors.MAGENTA}Wyjaśnienie kodu:{Colors.END}")
                    print(f"{Colors.YELLOW}{code_result['explanation']}{Colors.END}")
                
                # Pokaż analizę kodu
                if code_result.get("analysis"):
                    print(f"{Colors.MAGENTA}Analiza kodu:{Colors.END}")
                    print(f"{Colors.YELLOW}{code_result['analysis']}{Colors.END}")
                    
                    # Jeśli są sugestie, pokaż je
                    if code_result.get("suggestions") and len(code_result["suggestions"]) > 0:
                        print(f"{Colors.MAGENTA}Sugestie:{Colors.END}")
                        for i, suggestion in enumerate(code_result["suggestions"], 1):
                            print(f"{Colors.YELLOW}{i}. {suggestion}{Colors.END}")
                
                # Automatycznie uruchamiaj kod w piaskownicy Docker
                print(f"{Colors.BLUE}Automatyczne uruchamianie kodu w piaskownicy Docker...{Colors.END}")
                choice = 't'
            
            if choice != 't':
                print(f"{Colors.YELLOW}Pominięto uruchomienie kodu.{Colors.END}")
                return
                
            # Uruchom kod w piaskownicy Docker
            print(f"{Colors.BLUE}Uruchamianie kodu w piaskownicy Docker...{Colors.END}")
            sandbox_result = self._run_code_in_sandbox(code)
            
            # Zapisz wynik uruchomienia kodu
            self._save_code_execution_result(query, code, sandbox_result)
            
            # Wyświetl sformatowany wynik wykonania kodu
            if CONSOLE_UTILS_AVAILABLE:
                print(self.result_formatter.format_execution_result(sandbox_result))
            else:
                # Standardowe wyświetlanie wyniku
                if sandbox_result["success"]:
                    print(f"{Colors.GREEN}Kod został wykonany pomyślnie!{Colors.END}")
                    print(f"{Colors.BLUE}Wynik wykonania:{Colors.END}")
                    print(f"{Colors.CYAN}{sandbox_result['output']}{Colors.END}")
                    
                    # Wyświetl link do kontenera Docker
                    if "docker_url" in sandbox_result:
                        print(f"{Colors.BLUE}Link do kontenera Docker: {Colors.CYAN}{sandbox_result['docker_url']}{Colors.END}")
                else:
                    print(f"{Colors.RED}Wystąpił błąd podczas wykonywania kodu:{Colors.END}")
                    print(f"{Colors.RED}{sandbox_result.get('error', 'Nieznany błąd')}{Colors.END}")
            
        except Exception as e:
            logger.error(f"Błąd w pętli interaktywnej: {str(e)}")
            print(f"{Colors.RED}Wystąpił błąd: {str(e)}{Colors.END}")
            return
        
        # Kontynuuj tylko jeśli kod został pomyślnie wykonany
        if not sandbox_result.get("success", False):
            print(f"{Colors.RED}Wystąpił błąd podczas wykonywania kodu:{Colors.END}")
            print(f"{Colors.RED}{sandbox_result.get('error', 'Nieznany błąd')}{Colors.END}")
            return
        
        # Wygeneruj wyjaśnienie kodu
        if sandbox_result["success"]:
            print(f"{Colors.GREEN}Kod został wykonany pomyślnie!{Colors.END}")
            print(f"{Colors.BLUE}Wynik wykonania:{Colors.END}")
            print(f"{Colors.CYAN}{sandbox_result['output']}{Colors.END}")
            
            # Wyświetl link do kontenera Docker
            if "docker_url" in sandbox_result:
                print(f"{Colors.BLUE}Link do kontenera Docker: {Colors.CYAN}{sandbox_result['docker_url']}{Colors.END}")
            
            # Wygeneruj wyjaśnienie kodu
            print(f"{Colors.BLUE}Generowanie wyjaśnienia kodu...{Colors.END}")
            explanation = self.text2python.explain_code(code)
            print(f"{Colors.MAGENTA}Wyjaśnienie kodu:{Colors.END}")
            print(f"{Colors.CYAN}{explanation}{Colors.END}")
            
            # Zapytaj użytkownika czy to jest to czego oczekiwał
            print(f"{Colors.YELLOW}Czy to jest to czego oczekiwałeś? (t/N):{Colors.END} ", end="")
            feedback = input().lower()
            
            if feedback == 't':
                print(f"{Colors.GREEN}Doskonale! Zadanie zostało wykonane pomyślnie.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Rozumiem. Co powinienem poprawić?{Colors.END}")
        else:
            print(f"{Colors.RED}Wystąpił błąd podczas wykonywania kodu:{Colors.END}")
            print(f"{Colors.RED}{sandbox_result.get('error', 'Nieznany błąd')}{Colors.END}")
    
    def _run_code_in_sandbox(self, code: str, as_service: bool = False, service_name: str = None) -> Dict[str, Any]:
        """Uruchamia kod w piaskownicy Docker
        
        Args:
            code: Kod Python do uruchomienia
            as_service: Czy uruchomić kod jako serwis webowy
            service_name: Nazwa serwisu (tylko dla as_service=True)
            
        Returns:
            Dict: Wynik wykonania kodu
        """
        try:
            # Generuj unikalny identyfikator zadania
            task_id = str(uuid.uuid4())
            
            # Sprawdź, czy kod ma być uruchomiony jako serwis
            if as_service or "@api_endpoint" in code or "web_page" in code:
                # Importuj ServiceSandbox
                try:
                    from service_sandbox import ServiceSandbox
                except ImportError:
                    logger.warning("Nie znaleziono modułu service_sandbox, używam standardowej piaskownicy")
                    as_service = False
            
            if as_service:
                # Utwórz piaskownicę serwisu
                sandbox = ServiceSandbox(
                    base_dir=SANDBOX_DIR,
                    docker_image=self.config.get("sandbox_image", "python:3.9-slim"),
                    timeout=self.config.get("sandbox_timeout", 30)
                )
                
                # Przygotuj nazwę serwisu
                if not service_name:
                    service_name = f"Evopy Service {task_id[:8]}"
                
                # Uruchom serwis
                result = sandbox.build_and_run(
                    code,
                    name=service_name,
                    description="Serwis wygenerowany przez Evopy Assistant",
                    version="1.0.0"
                )
                
                # Dodaj identyfikator zadania i link do wyniku
                result["task_id"] = task_id
                result["docker_url"] = f"http://localhost:5000/docker/{task_id}"
                result["service_url"] = sandbox.service_url
                result["is_service"] = True
                
                # Jeśli serwis został uruchomiony pomyślnie, dodaj informacje o API
                if result["success"]:
                    # Pobierz dokumentację API
                    api_docs = sandbox.get_api_docs()
                    if api_docs["success"]:
                        result["api_docs"] = api_docs["api_docs"]
                    
                    # Dodaj informacje o logach
                    logs = sandbox.get_logs()
                    if logs["success"]:
                        result["logs"] = logs["logs"]
                
                # Nie czyścimy piaskownicy, ponieważ serwis ma działać w tle
                # Zamiast tego zapisujemy informacje o piaskownicy, aby można było ją później wyczyścić
                result["sandbox_id"] = sandbox.sandbox_id
                
                # Zarejestruj kontener Docker dla zadania, jeśli uruchomienie było udane
                if result["success"] and hasattr(sandbox, "container_id") and sandbox.container_id:
                    try:
                        # Użyj nowego modułu do bezpośredniego rejestrowania zadań Docker
                        try:
                            from docker_task_register import register_docker_task
                            
                            # Pobierz zapytanie użytkownika i wyjaśnienie asystenta z konwersacji
                            user_prompt = self.conversation.get_last_user_message() if hasattr(self, 'conversation') else None
                            agent_explanation = self.conversation.get_last_assistant_message() if hasattr(self, 'conversation') else None
                            
                            # Zarejestruj zadanie Docker bezpośrednio
                            register_result = register_docker_task(
                                task_id=task_id,
                                container_id=sandbox.container_id,
                                code=code,
                                output=result.get("output", ""),
                                is_service=True,
                                service_url=sandbox.service_url,
                                service_name=service_name,
                                user_prompt=user_prompt,
                                agent_explanation=agent_explanation
                            )
                            
                            logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane: {register_result}")
                        except ImportError:
                            # Jeśli moduł nie jest dostępny, użyj bezpośredniego endpointu
                            import requests
                            
                            # Pobierz zapytanie użytkownika i wyjaśnienie asystenta z konwersacji
                            user_prompt = self.conversation.get_last_user_message() if hasattr(self, 'conversation') else None
                            agent_explanation = self.conversation.get_last_assistant_message() if hasattr(self, 'conversation') else None
                            
                            # Przygotuj dane do wysłania
                            data = {
                                "task_id": task_id,
                                "container_id": sandbox.container_id,
                                "code": code,
                                "output": result.get("output", ""),
                                "is_service": "true",
                                "service_url": sandbox.service_url,
                                "service_name": service_name
                            }
                            
                            # Dodaj prompt użytkownika i wyjaśnienie asystenta, jeśli są dostępne
                            if user_prompt:
                                data["user_prompt"] = user_prompt
                            if agent_explanation:
                                data["agent_explanation"] = agent_explanation
                            
                            response = requests.post(
                                "http://localhost:5000/docker/register",
                                data=data
                            )
                            
                            logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane przez API: {response.text}")
                    except Exception as e:
                        logger.warning(f"Nie udało się zarejestrować kontenera w serwerze modułów: {e}")
            else:
                # Standardowe uruchomienie kodu w piaskownicy
                # Utwórz piaskownicę Docker
                from docker_sandbox import DockerSandbox
                sandbox = DockerSandbox(
                    base_dir=SANDBOX_DIR,
                    docker_image=self.config.get("sandbox_image", "python:3.9-slim"),
                    timeout=self.config.get("sandbox_timeout", 30)
                )
                
                # Uruchom kod w piaskownicy
                result = sandbox.run(code)
                
                # Dodaj identyfikator zadania i link do wyniku
                result["task_id"] = task_id
                result["docker_url"] = f"http://localhost:5000/docker/{task_id}"
                result["is_service"] = False
                
                # Zarejestruj kontener Docker dla zadania, jeśli wykonanie było udane
                if result["success"] and hasattr(sandbox, "container_id") and sandbox.container_id:
                    try:
                        # Użyj nowego modułu do bezpośredniego rejestrowania zadań Docker
                        try:
                            from docker_task_register import register_docker_task
                            
                            # Pobierz zapytanie użytkownika i wyjaśnienie asystenta z konwersacji
                            user_prompt = self.conversation.get_last_user_message() if hasattr(self, 'conversation') else None
                            agent_explanation = self.conversation.get_last_assistant_message() if hasattr(self, 'conversation') else None
                            
                            # Zarejestruj zadanie Docker bezpośrednio
                            register_result = register_docker_task(
                                task_id=task_id,
                                container_id=sandbox.container_id,
                                code=code,
                                output=result.get("output", ""),
                                is_service=False,
                                user_prompt=user_prompt,
                                agent_explanation=agent_explanation
                            )
                            
                            logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane: {register_result}")
                        except ImportError:
                            # Jeśli moduł nie jest dostępny, użyj bezpośredniego endpointu
                            import requests
                            
                            # Pobierz zapytanie użytkownika i wyjaśnienie asystenta z konwersacji
                            user_prompt = self.conversation.get_last_user_message() if hasattr(self, 'conversation') else None
                            agent_explanation = self.conversation.get_last_assistant_message() if hasattr(self, 'conversation') else None
                            
                            # Przygotuj dane do wysłania
                            data = {
                                "task_id": task_id,
                                "container_id": sandbox.container_id,
                                "code": code,
                                "output": result.get("output", "")
                            }
                            
                            # Dodaj prompt użytkownika i wyjaśnienie asystenta, jeśli są dostępne
                            if user_prompt:
                                data["user_prompt"] = user_prompt
                            if agent_explanation:
                                data["agent_explanation"] = agent_explanation
                            
                            response = requests.post(
                                "http://localhost:5000/docker/register",
                                data=data
                            )
                            
                            logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane przez API: {response.text}")
                    except Exception as e:
                        logger.warning(f"Nie udało się zarejestrować kontenera w serwerze modułów: {e}")
                
                # Wyczyść piaskownicę
                sandbox.cleanup()
            
            return result
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania kodu w piaskownicy: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Błąd piaskownicy: {str(e)}",
                "execution_time": 0
            }
    
    def _save_code_execution_result(self, query: str, code: str, result: Dict[str, Any]):
        """Zapisuje wynik wykonania kodu
        
        Args:
            query: Zapytanie użytkownika
            code: Wygenerowany kod Python
            result: Wynik wykonania kodu
        """
        if not self.current_conversation_id or self.current_conversation_id not in self.conversations:
            return
        
        # Dodaj wynik wykonania kodu do historii konwersacji
        execution_record = {
            "query": query,
            "code": code,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Dodaj do historii konwersacji
        if "code_executions" not in self.conversations[self.current_conversation_id]:
            self.conversations[self.current_conversation_id]["code_executions"] = []
        
        self.conversations[self.current_conversation_id]["code_executions"].append(execution_record)
        
        # Aktualizacja czasu ostatniej modyfikacji
        self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
        
        # Zapisz konwersację
        self._save_conversation(self.current_conversation_id)
        
        # Dodaj wiadomość asystenta z wynikiem wykonania kodu
        if result["success"]:
            message = f"Kod został wykonany pomyślnie. Wynik:\n\n```\n{result['output']}\n```"
        else:
            message = f"Wystąpił błąd podczas wykonywania kodu:\n\n```\n{result.get('error', 'Nieznany błąd')}\n```"
        
        self.conversations[self.current_conversation_id]["messages"].append({
            "role": "assistant",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Zapisz konwersację
        self._save_conversation(self.current_conversation_id)
    
    def _interactive_loop(self):
        """Główna pętla interaktywna asystenta"""
        # Wyświetl powitanie
        if CONSOLE_UTILS_AVAILABLE:
            print_header(f"Ewolucyjny Asystent v{VERSION}")
            print(f"\nWpisz {Colors.BOLD}/help{Colors.END} aby uzyskać pomoc lub {Colors.BOLD}zapytanie{Colors.END} aby rozpocząć konwersację.\n")
        else:
            print(f"{Colors.HEADER}Ewolucyjny Asystent v{VERSION}{Colors.END}")
            print(f"\nWpisz /help aby uzyskać pomoc lub zapytanie aby rozpocząć konwersację.\n")
        
        while self.running:
            try:
                # Wyświetl prompt z informacją o aktualnej konwersacji
                if self.current_conversation_id and self.current_conversation_id in self.conversations:
                    conv_title = self.conversations[self.current_conversation_id].get("title", "Bez tytułu")
                    prompt = f"{Colors.GREEN}[{conv_title}]> {Colors.END}"
                else:
                    prompt = f"{Colors.GREEN}> {Colors.END}"
                
                user_input = input(prompt)
                
                # Obsługa komend
                if user_input.startswith("/"):
                    self._handle_command(user_input)
                    continue
                
                # Obsługa normalnego zapytania
                if user_input.strip():
                    self._handle_query(user_input)
            
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Wciśnij Ctrl+C jeszcze raz, aby zakończyć.{Colors.END}")
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    self._handle_interrupt(None, None)
            
            except Exception as e:
                logger.error(f"Błąd w pętli interaktywnej: {e}")
                print(f"{Colors.RED}Wystąpił błąd: {e}{Colors.END}")
    
    def _handle_command(self, command: str):
        """Obsługuje komendy asystenta"""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Obsługa podstawowych komend
        if cmd == "/help":
            self._show_help()
            return
        
        elif cmd == "/exit" or cmd == "/quit":
            print(f"{Colors.YELLOW}Kończenie pracy...{Colors.END}")
            self.running = False
            return
        
        elif cmd == "/new":
            self._create_new_conversation()
            print(f"{Colors.GREEN}Utworzono nową konwersację.{Colors.END}")
        
        elif cmd == "/list":
            self._list_conversations_command()
        
        elif cmd == "/load":
            if not args:
                print(f"{Colors.RED}Nie podano ID konwersacji. Użyj: /load <id>{Colors.END}")
                return
            
            conversation_id = args[0]
            conversation = self._load_conversation(conversation_id)
            if conversation:
                self.conversations[conversation_id] = conversation
                self.current_conversation_id = conversation_id
                print(f"{Colors.GREEN}Załadowano konwersację: {conversation.get('title', 'Bez tytułu')}{Colors.END}")
            else:
                print(f"{Colors.RED}Nie znaleziono konwersacji o ID: {conversation_id}{Colors.END}")
        
        elif cmd == "/title":
            if not args:
                print(f"{Colors.RED}Nie podano tytułu. Użyj: /title <nowy tytuł>{Colors.END}")
                return
            
            new_title = " ".join(args)
            if self.current_conversation_id and self.current_conversation_id in self.conversations:
                self.conversations[self.current_conversation_id]["title"] = new_title
                self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
                self._save_conversation(self.current_conversation_id)
                print(f"{Colors.GREEN}Zmieniono tytuł konwersacji na: {new_title}{Colors.END}")
            else:
                print(f"{Colors.RED}Brak aktywnej konwersacji.{Colors.END}")
        
        elif cmd == "/clear":
            if self.current_conversation_id and self.current_conversation_id in self.conversations:
                self.conversations[self.current_conversation_id]["messages"] = []
                self.conversations[self.current_conversation_id]["updated_at"] = datetime.now().isoformat()
                self._save_conversation(self.current_conversation_id)
                print(f"{Colors.GREEN}Wyczyszczono historię konwersacji.{Colors.END}")
            else:
                print(f"{Colors.RED}Brak aktywnej konwersacji.{Colors.END}")
        
        elif cmd == "/model":
            if not args:
                current_model = self.config.get("model", DEFAULT_MODEL)
                print(f"{Colors.BLUE}Aktualny model: {current_model}{Colors.END}")
                print(f"{Colors.BLUE}Dostępne modele:{Colors.END}")
                
                # Wyświetl listę dostępnych modeli
                for model_info in AVAILABLE_MODELS:
                    is_current = " (aktualny)" if model_info["name"] == current_model else ""
                    is_installed = " [zainstalowany]" if self._check_model_exists(model_info["name"]) else ""
                    print(f"{Colors.CYAN}- {model_info['name']}{is_current}{is_installed}: {model_info['description']}{Colors.END}")
                
                print(f"{Colors.YELLOW}Użyj /model <nazwa_modelu> aby zmienić model.{Colors.END}")
                return
            
            new_model = args[0]
            
            # Sprawdź, czy model jest na liście dostępnych modeli
            model_exists = False
            for model_info in AVAILABLE_MODELS:
                if model_info["name"] == new_model:
                    model_exists = True
                    break
            
            if not model_exists:
                print(f"{Colors.RED}Model {new_model} nie jest na liście dostępnych modeli.{Colors.END}")
                print(f"{Colors.YELLOW}Użyj /model bez argumentów, aby zobaczyć listę dostępnych modeli.{Colors.END}")
                return
            
            # Sprawdź, czy model jest zainstalowany
            if not self._check_model_exists(new_model):
                print(f"{Colors.YELLOW}Model {new_model} nie jest zainstalowany. Czy chcesz go pobrać? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                if choice == 't':
                    success = self._pull_model(new_model)
                    if not success:
                        print(f"{Colors.RED}Nie udało się pobrać modelu. Nie zmieniono modelu.{Colors.END}")
                        return
                else:
                    print(f"{Colors.RED}Nie zmieniono modelu.{Colors.END}")
                    return
            
            # Zapisz zmianę modelu w konfiguracji
            self.config["model"] = new_model
            self._save_config()
            
            # Zaktualizuj model w text2python
            self.text2python = Text2Python({
                "model": new_model,
                "code_dir": str(CODE_DIR)
            })
            
            print(f"{Colors.GREEN}Zmieniono model na: {new_model}{Colors.END}")
        
        elif cmd == "/skills":
            print(f"{Colors.BLUE}Umiejętności asystenta:{Colors.END}")
            if not self.skills:
                print(f"{Colors.YELLOW}Brak zdefiniowanych umiejętności.{Colors.END}")
            else:
                for i, skill in enumerate(self.skills, 1):
                    print(f"{Colors.BLUE}{i}. {skill.get('name', 'Bez nazwy')}: {skill.get('description', 'Bez opisu')}{Colors.END}")
        
        elif cmd == "/projects":
            self._list_projects_command()
        
        elif cmd == "/docker":
            if not args:
                print(f"{Colors.RED}Nie podano operacji. Użyj: /docker [ps|images|network|info]{Colors.END}")
                return
            
            operation = args[0].lower()
            self._docker_command(operation, args[1:])
        
        elif cmd == "/save":
            if self.current_conversation_id:
                self._save_conversation(self.current_conversation_id)
                print(f"{Colors.GREEN}Konwersacja została zapisana.{Colors.END}")
            else:
                print(f"{Colors.RED}Brak aktywnej konwersacji.{Colors.END}")
        
        # Dodatkowe komendy
        elif cmd == "/status":
            self._show_status()
        
        elif cmd == "/history":
            self._show_history()
        
        elif cmd == "/export":
            if not args:
                print(f"{Colors.RED}Nie podano nazwy pliku. Użyj: /export <plik>{Colors.END}")
                return
            self._export_conversation(args[0])
        
        elif cmd == "/import":
            if not args:
                print(f"{Colors.RED}Nie podano nazwy pliku. Użyj: /import <plik>{Colors.END}")
                return
            self._import_conversation(args[0])
        
        elif cmd == "/monitor":
            self._show_resource_usage()
        
        else:
            print(f"{Colors.RED}Nieznana komenda: {cmd}. Wpisz /help aby uzyskać pomoc.{Colors.END}")
    
    def _show_help(self):
        """Wyświetla pomoc dla komend asystenta"""
        if CONSOLE_UTILS_AVAILABLE:
            print_header("Dostępne komendy")
            
            # Przygotuj dane do tabeli
            commands = [
                ["/help", "Wyświetla tę pomoc"],
                ["/exit, /quit", "Kończy pracę asystenta"],
                ["/new", "Tworzy nową konwersację"],
                ["/list", "Wyświetla listę konwersacji"],
                ["/load <id>", "Ładuje konwersację o podanym ID"],
                ["/title <nowy tytuł>", "Zmienia tytuł aktualnej konwersacji"],
                ["/clear", "Czyści historię aktualnej konwersacji"],
                ["/model [nazwa modelu]", "Wyświetla/zmienia aktualny model"],
                ["/skills", "Wyświetla umiejętności asystenta"],
                ["/projects", "Wyświetla projekty w aktualnej konwersacji"],
                ["/docker [ps|images|network|info]", "Zarządzanie Dockerem"],
                ["/save", "Zapisuje aktualną konwersację"],
                ["/status", "Wyświetla status systemu"],
                ["/history", "Wyświetla historię konwersacji"],
                ["/export <plik>", "Eksportuje konwersację do pliku"],
                ["/import <plik>", "Importuje konwersację z pliku"],
                ["/monitor", "Wyświetla informacje o zużyciu zasobów"]
            ]
            
            print_table(["Komenda", "Opis"], commands)
        else:
            print(f"{Colors.BLUE}Dostępne komendy:{Colors.END}")
            print(f"{Colors.BLUE}/help{Colors.END} - Wyświetla tę pomoc")
            print(f"{Colors.BLUE}/exit{Colors.END}, {Colors.BLUE}/quit{Colors.END} - Kończy pracę asystenta")
            print(f"{Colors.BLUE}/new{Colors.END} - Tworzy nową konwersację")
            print(f"{Colors.BLUE}/list{Colors.END} - Wyświetla listę konwersacji")
            print(f"{Colors.BLUE}/load <id>{Colors.END} - Ładuje konwersację o podanym ID")
            print(f"{Colors.BLUE}/title <nowy tytuł>{Colors.END} - Zmienia tytuł aktualnej konwersacji")
            print(f"{Colors.BLUE}/clear{Colors.END} - Czyści historię aktualnej konwersacji")
            print(f"{Colors.BLUE}/model [nazwa modelu]{Colors.END} - Wyświetla/zmienia aktualny model")
            print(f"{Colors.BLUE}/skills{Colors.END} - Wyświetla umiejętności asystenta")
            print(f"{Colors.BLUE}/projects{Colors.END} - Wyświetla projekty w aktualnej konwersacji")
            print(f"{Colors.BLUE}/docker [ps|images|network|info]{Colors.END} - Zarządzanie Dockerem")
            print(f"{Colors.BLUE}/save{Colors.END} - Zapisuje aktualną konwersację")
            print(f"{Colors.BLUE}/status{Colors.END} - Wyświetla status systemu")
            print(f"{Colors.BLUE}/history{Colors.END} - Wyświetla historię konwersacji")
            print(f"{Colors.BLUE}/export <plik>{Colors.END} - Eksportuje konwersację do pliku")
            print(f"{Colors.BLUE}/import <plik>{Colors.END} - Importuje konwersację z pliku")
            print(f"{Colors.BLUE}/monitor{Colors.END} - Wyświetla informacje o zużyciu zasobów")
    
    def _list_conversations_command(self):
        """Wyświetla listę konwersacji"""
        conversations = self._list_conversations()
        
        if not conversations:
            print(f"{Colors.YELLOW}Brak zapisanych konwersacji.{Colors.END}")
            return
        
        print(f"{Colors.BLUE}Lista konwersacji:{Colors.END}")
        for i, conv in enumerate(conversations, 1):
            created_at = datetime.fromisoformat(conv.get("created_at", "")).strftime("%Y-%m-%d %H:%M")
            is_current = " (aktualna)" if conv.get("id") == self.current_conversation_id else ""
            print(f"{Colors.BLUE}{i}. {conv.get('title', 'Bez tytułu')} - {created_at}{is_current}{Colors.END}")
    
    def _save_conversation(self, conversation_id=None):
        """Zapisuje konwersację do pliku"""
        if not conversation_id:
            conversation_id = self.current_conversation_id
            
        if not conversation_id:
            print(f"{Colors.RED}Brak aktywnej konwersacji.{Colors.END}")
            return
        
        # Pobierz konwersację
        conversation = self.conversations.get(conversation_id)
        if not conversation:
            print(f"{Colors.RED}Nie można znaleźć konwersacji o ID {conversation_id}.{Colors.END}")
            return
        
        # Zapisz konwersację do pliku
        conversation_path = HISTORY_DIR / f"{conversation_id}.json"
        with open(conversation_path, "w", encoding="utf-8") as f:
            json.dump(conversation, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Konwersacja {conversation_id} została zapisana")
        
    def _export_conversation(self, filename: str):
        """Eksportuje aktualną konwersację do pliku"""
        if not self.current_conversation_id:
            print(f"{Colors.RED}Brak aktywnej konwersacji do eksportu.{Colors.END}")
            return
        
        # Pobierz aktualną konwersację
        conversation = self.conversations.get(self.current_conversation_id)
        if not conversation:
            print(f"{Colors.RED}Nie można znaleźć aktualnej konwersacji.{Colors.END}")
            return
        
        # Jeśli nie podano rozszerzenia, dodaj .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Jeśli podano ścieżkę względną, dodaj ścieżkę do katalogu domowego
        if not os.path.isabs(filename):
            export_path = Path.home() / filename
        else:
            export_path = Path(filename)
        
        # Zapisz konwersację do pliku
        try:
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)
            print(f"{Colors.GREEN}Konwersacja została wyeksportowana do {export_path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Błąd podczas eksportu konwersacji: {e}{Colors.END}")
    
    def _import_conversation(self, filename: str):
        """Importuje konwersację z pliku"""
        # Jeśli nie podano rozszerzenia, dodaj .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Jeśli podano ścieżkę względną, dodaj ścieżkę do katalogu domowego
        if not os.path.isabs(filename):
            import_path = Path.home() / filename
        else:
            import_path = Path(filename)
        
        # Sprawdź, czy plik istnieje
        if not import_path.exists():
            print(f"{Colors.RED}Plik {import_path} nie istnieje.{Colors.END}")
            return
        
        # Wczytaj konwersację z pliku
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                conversation = json.load(f)
            
            # Sprawdź, czy to prawidłowa konwersacja
            if not isinstance(conversation, dict) or "messages" not in conversation:
                print(f"{Colors.RED}Plik nie zawiera prawidłowej konwersacji.{Colors.END}")
                return
            
            # Dodaj konwersację do listy konwersacji
            conversation_id = conversation.get("id", str(uuid.uuid4()))
            self.conversations[conversation_id] = conversation
            self.current_conversation_id = conversation_id
            
            # Zapisz konwersację do pliku
            conversation_path = CONVERSATIONS_DIR / f"{conversation_id}.json"
            with open(conversation_path, "w", encoding="utf-8") as f:
                json.dump(conversation, f, ensure_ascii=False, indent=2)
            
            print(f"{Colors.GREEN}Konwersacja została zaimportowana i ustawiona jako aktualna.{Colors.END}")
        except Exception as e:
            print(f"{Colors.RED}Błąd podczas importu konwersacji: {e}{Colors.END}")
    
    def _show_history(self):
        """Wyświetla historię aktualnej konwersacji"""
        if not self.current_conversation_id:
            print(f"{Colors.RED}Brak aktywnej konwersacji.{Colors.END}")
            return
        
        # Pobierz aktualną konwersację
        conversation = self.conversations.get(self.current_conversation_id)
        if not conversation:
            print(f"{Colors.RED}Nie można znaleźć aktualnej konwersacji.{Colors.END}")
            return
        
        # Pobierz wiadomości
        messages = conversation.get("messages", [])
        if not messages:
            print(f"{Colors.YELLOW}Konwersacja nie zawiera żadnych wiadomości.{Colors.END}")
            return
        
        # Wyświetl historię
        print(f"{Colors.BLUE}Historia konwersacji '{conversation.get('title', 'Bez tytułu')}' ({len(messages)} wiadomości):{Colors.END}")
        
        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            if timestamp:
                try:
                    timestamp = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            if role == "user":
                print(f"\n{Colors.GREEN}[{i}] Użytkownik ({timestamp}):{Colors.END}")
                print(f"{content}")
            elif role == "assistant":
                print(f"\n{Colors.BLUE}[{i}] Asystent ({timestamp}):{Colors.END}")
                print(f"{content}")
            elif role == "system":
                print(f"\n{Colors.YELLOW}[{i}] System ({timestamp}):{Colors.END}")
                print(f"{content}")
            else:
                print(f"\n{Colors.MAGENTA}[{i}] {role.capitalize()} ({timestamp}):{Colors.END}")
                print(f"{content}")
    
    def _show_status(self):
        """Wyświetla status systemu"""
        # Informacje o systemie
        print(f"{Colors.BLUE}Informacje o systemie:{Colors.END}")
        print(f"System: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print(f"Katalog aplikacji: {APP_DIR}")
        
        # Informacje o modelu
        print(f"\n{Colors.BLUE}Informacje o modelu:{Colors.END}")
        print(f"Model: {self.config.get('model', DEFAULT_MODEL)}")
        
        # Informacje o konwersacjach
        print(f"\n{Colors.BLUE}Informacje o konwersacjach:{Colors.END}")
        print(f"Liczba konwersacji: {len(self.conversations)}")
        if self.current_conversation_id:
            conversation = self.conversations.get(self.current_conversation_id, {})
            print(f"Aktualna konwersacja: {conversation.get('title', 'Bez tytułu')}")
            print(f"Liczba wiadomości: {len(conversation.get('messages', []))}")
        
        # Informacje o zasobach
        print(f"\n{Colors.BLUE}Informacje o zasobach:{Colors.END}")
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"CPU: {cpu_percent}%")
        print(f"RAM: {memory.percent}% (używane: {self._format_bytes(memory.used)}, całkowite: {self._format_bytes(memory.total)})")
        print(f"Dysk: {disk.percent}% (używane: {self._format_bytes(disk.used)}, całkowite: {self._format_bytes(disk.total)})")
    
    def _show_resource_usage(self):
        """Wyświetla szczegółowe informacje o zużyciu zasobów"""
        try:
            # Uruchom monitor_resources.py w trybie raportowania
            script_path = Path(__file__).parent / "monitor_resources.py"
            if not script_path.exists():
                print(f"{Colors.RED}Nie znaleziono skryptu monitor_resources.py{Colors.END}")
                return
            
            print(f"{Colors.BLUE}Pobieranie informacji o zasobach...{Colors.END}")
            result = subprocess.run([sys.executable, str(script_path), "--report"], 
                                   capture_output=True, text=True, check=False)
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"{Colors.RED}Błąd podczas pobierania informacji o zasobach:{Colors.END}")
                print(result.stderr)
        except Exception as e:
            print(f"{Colors.RED}Błąd podczas wyświetlania informacji o zasobach: {e}{Colors.END}")
    
    def _docker_command(self, operation: str, args: List[str]):
        """Wykonuje operacje Docker
        
        Args:
            operation: Rodzaj operacji (ps, images, network, info)
            args: Dodatkowe argumenty dla operacji
        """
        try:
            # Sprawdź, czy Docker jest zainstalowany
            try:
                subprocess.run(["docker", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"{Colors.RED}Docker nie jest zainstalowany lub nie jest dostępny.{Colors.END}")
                print(f"{Colors.YELLOW}Możesz uruchomić serwer modułów bez Dockera: /docker modules{Colors.END}")
                return
            
            # Wykonaj odpowiednią operację Docker
            if operation == "ps":
                # Listowanie kontenerów
                cmd = ["docker", "ps", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"]
                if args and args[0] == "-a":
                    cmd = ["docker", "ps", "-a", "--format", "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Names}}"]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Aktywne kontenery Docker:{Colors.END}")
                    print(f"{Colors.CYAN}{result.stdout}{Colors.END}")
                    
                    # Dodaj link do interfejsu webowego Docker
                    print(f"{Colors.YELLOW}Interfejs webowy Docker: {Colors.CYAN}http://localhost:5000/docker{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas listowania kontenerów: {result.stderr}{Colors.END}")
            
            elif operation == "images":
                # Listowanie obrazów
                cmd = ["docker", "images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Obrazy Docker:{Colors.END}")
                    print(f"{Colors.CYAN}{result.stdout}{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas listowania obrazów: {result.stderr}{Colors.END}")
            
            elif operation == "network":
                # Listowanie sieci
                cmd = ["docker", "network", "ls", "--format", "table {{.ID}}\t{{.Name}}\t{{.Driver}}"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Sieci Docker:{Colors.END}")
                    print(f"{Colors.CYAN}{result.stdout}{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas listowania sieci: {result.stderr}{Colors.END}")
            
            elif operation == "info":
                # Informacje o systemie Docker
                cmd = ["docker", "info"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Informacje o systemie Docker:{Colors.END}")
                    print(f"{Colors.CYAN}{result.stdout}{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas pobierania informacji: {result.stderr}{Colors.END}")
            
            elif operation == "logs":
                # Logi kontenera
                if not args:
                    print(f"{Colors.RED}Nie podano nazwy kontenera. Użyj: /docker logs <nazwa_kontenera>{Colors.END}")
                    return
                
                container_name = args[0]
                cmd = ["docker", "logs", container_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Logi kontenera {container_name}:{Colors.END}")
                    print(f"{Colors.CYAN}{result.stdout}{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas pobierania logów: {result.stderr}{Colors.END}")
            
            elif operation == "stop":
                # Zatrzymanie kontenera
                if not args:
                    print(f"{Colors.RED}Nie podano nazwy kontenera. Użyj: /docker stop <nazwa_kontenera>{Colors.END}")
                    return
                
                container_name = args[0]
                cmd = ["docker", "stop", container_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Kontener {container_name} został zatrzymany.{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas zatrzymywania kontenera: {result.stderr}{Colors.END}")
            
            elif operation == "start":
                # Uruchomienie kontenera
                if not args:
                    print(f"{Colors.RED}Nie podano nazwy kontenera. Użyj: /docker start <nazwa_kontenera>{Colors.END}")
                    return
                
                container_name = args[0]
                cmd = ["docker", "start", container_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Kontener {container_name} został uruchomiony.{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas uruchamiania kontenera: {result.stderr}{Colors.END}")
            
            elif operation == "rm":
                # Usunięcie kontenera
                if not args:
                    print(f"{Colors.RED}Nie podano nazwy kontenera. Użyj: /docker rm <nazwa_kontenera>{Colors.END}")
                    return
                
                container_name = args[0]
                cmd = ["docker", "rm", container_name]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"{Colors.GREEN}Kontener {container_name} został usunięty.{Colors.END}")
                else:
                    print(f"{Colors.RED}Błąd podczas usuwania kontenera: {result.stderr}{Colors.END}")
            
            elif operation == "modules":
                # Uruchomienie serwera modułów konwersji
                print(f"{Colors.YELLOW}Uruchamianie serwera modułów konwersji...{Colors.END}")
                try:
                    # Sprawdź, czy serwer jest już uruchomiony
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    result = sock.connect_ex(('localhost', 5000))
                    sock.close()
                    
                    if result == 0:
                        print(f"{Colors.GREEN}Serwer modułów jest już uruchomiony na porcie 5000.{Colors.END}")
                        print(f"{Colors.GREEN}Dostęp przez przeglądarkę: http://localhost:5000{Colors.END}")
                        print(f"{Colors.GREEN}Kontenery Docker: http://localhost:5000/docker{Colors.END}")
                        return
                    
                    # Uruchom serwer modułów w tle
                    server_script = os.path.join(APP_DIR, "modules", "run_server.py")
                    if os.path.exists(server_script):
                        subprocess.Popen([sys.executable, server_script], 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
                        print(f"{Colors.GREEN}Serwer modułów został uruchomiony na porcie 5000.{Colors.END}")
                        print(f"{Colors.GREEN}Dostęp przez przeglądarkę: http://localhost:5000{Colors.END}")
                        print(f"{Colors.GREEN}Kontenery Docker: http://localhost:5000/docker{Colors.END}")
                    else:
                        print(f"{Colors.RED}Nie znaleziono skryptu serwera modułów.{Colors.END}")
                except Exception as e:
                    print(f"{Colors.RED}Błąd podczas uruchamiania serwera modułów: {str(e)}{Colors.END}")
        
        except Exception as e:
            logger.error(f"Błąd podczas wykonywania komendy Docker: {str(e)}")
            print(f"{Colors.RED}Wystąpił błąd: {str(e)}{Colors.END}")
    
    def _format_bytes(self, bytes_value):
        """Formatuje bajty do czytelnej postaci"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


def main():
    """Główna funkcja programu"""
    parser = argparse.ArgumentParser(description="Ewolucyjny Asystent - system konwersacyjny rozwijający się wraz z interakcjami")
    parser.add_argument("--model", type=str, help="Model językowy do użycia")
    parser.add_argument("--config", type=str, help="Ścieżka do pliku konfiguracyjnego")
    parser.add_argument("--no-color", action="store_true", help="Wyłącz kolorowanie w terminalu")
    args = parser.parse_args()
    
    # Obsługa wyłączenia kolorów
    if args.no_color:
        # Nadpisz klasę Colors pustymi kodami
        for attr in dir(Colors):
            if not attr.startswith('__'):
                setattr(Colors, attr, '')
    
    # Utwórz instancję asystenta
    config_path = Path(args.config) if args.config else CONFIG_FILE
    assistant = EvoAssistant(config_path=config_path)
    
    # Ustaw model z argumentów wiersza poleceń, jeśli podano
    if args.model:
        assistant.config["model"] = args.model
        assistant._save_config()
    
    # Uruchom asystenta
    assistant.start()


if __name__ == "__main__":
    main()