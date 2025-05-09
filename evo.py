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
import asyncio
import argparse
import platform
import readline  # Do historii w konsoli
import subprocess
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Import modułów lokalnych
try:
    from text2python import Text2Python
    from docker_sandbox import DockerSandbox
except ImportError:
    # Jeśli moduły nie są dostępne, dodaj katalog projektu do ścieżki
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from text2python import Text2Python
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

# Kolory dla terminala
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

# Stałe
APP_DIR = Path.home() / ".evo-assistant"
HISTORY_DIR = APP_DIR / "history"
PROJECTS_DIR = APP_DIR / "projects"
CACHE_DIR = APP_DIR / "cache"
MODELS_DIR = APP_DIR / "models"
SANDBOX_DIR = APP_DIR / "sandbox"  # Katalog dla piaskownic Docker
CODE_DIR = APP_DIR / "code"  # Katalog dla generowanego kodu
CONFIG_FILE = APP_DIR / "config.json"
DEFAULT_MODEL = "llama3"
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
        self.text2python = Text2Python(
            model_name=self.config.get("model", DEFAULT_MODEL),
            code_dir=CODE_DIR
        )
        
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
            print(f"{Colors.YELLOW}Model {model} nie jest pobrany. Czy chcesz go pobrać? (t/N):{Colors.END} ", end="")
            choice = input().lower()
            
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
                    
                    # Zapytaj użytkownika czy chce uruchomić kod mimo błędu
                    print(f"{Colors.YELLOW}Czy chcesz uruchomić ten kod w piaskownicy Docker? (t/N):{Colors.END} ", end="")
                    choice = input().lower()
                    
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
                
                # Zapytaj użytkownika czy to jest to, czego oczekiwał
                print(f"{Colors.BLUE}Czy to jest to, czego oczekiwałeś? (t/n/e):{Colors.END} ", end="")
                intent_choice = input().lower()
                
                if intent_choice == 'n':
                    print(f"{Colors.YELLOW}Co dokładnie nie działa zgodnie z oczekiwaniami?{Colors.END} ", end="")
                    feedback = input()
                    print(f"{Colors.YELLOW}Dziękuję za informację. Spróbuję poprawić kod w przyszłości.{Colors.END}")
                    
                    # Zapisz informację o niezgodności z intencją użytkownika
                    self.conversations[self.current_conversation_id]["messages"].append({
                        "role": "system",
                        "content": f"Użytkownik zaznaczył, że kod nie spełnia jego oczekiwań. Feedback: {feedback}",
                        "timestamp": datetime.now().isoformat()
                    })
                    self._save_conversation(self.current_conversation_id)
                    return
                elif intent_choice == 'e':
                    print(f"{Colors.YELLOW}Podaj dodatkowe wyjaśnienia lub modyfikacje:{Colors.END} ", end="")
                    modifications = input()
                    
                    # Zapisz informację o modyfikacjach
                    self.conversations[self.current_conversation_id]["messages"].append({
                        "role": "user",
                        "content": f"Modyfikacje do kodu: {modifications}",
                        "timestamp": datetime.now().isoformat()
                    })
                    self._save_conversation(self.current_conversation_id)
                    
                    # Tutaj można byłoby dodać logikę do modyfikacji kodu, ale to wykracza poza zakres obecnej implementacji
                    print(f"{Colors.YELLOW}Dziękuję za informację. Czy chcesz uruchomić obecny kod mimo to? (t/N):{Colors.END} ", end="")
                    choice = input().lower()
                else:
                    # Użytkownik zatwierdził kod (t) lub nie podał odpowiedzi
                    print(f"{Colors.YELLOW}Czy chcesz uruchomić ten kod w piaskownicy Docker? (t/N):{Colors.END} ", end="")
                    choice = input().lower()
            
            if choice != 't':
                print(f"{Colors.YELLOW}Pominięto uruchomienie kodu.{Colors.END}")
                return
                
            # Uruchom kod w piaskownicy Docker
            print(f"{Colors.BLUE}Uruchamianie kodu w piaskownicy Docker...{Colors.END}")
            sandbox_result = self._run_code_in_sandbox(code)
            
            # Zapisz wynik uruchomienia kodu
            self._save_code_execution_result(query, code, sandbox_result)
            
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
    
    def _run_code_in_sandbox(self, code: str) -> Dict[str, Any]:
        """Uruchamia kod w piaskownicy Docker
        
        Args:
            code: Kod Python do uruchomienia
            
        Returns:
            Dict: Wynik wykonania kodu
        """
        try:
            # Utwórz piaskownicę Docker
            sandbox = DockerSandbox(
                base_dir=SANDBOX_DIR,
                docker_image=self.config.get("sandbox_image", "python:3.9-slim"),
                timeout=self.config.get("sandbox_timeout", 30)
            )
            
            # Uruchom kod w piaskownicy
            result = sandbox.run(code)
            
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
        while self.running:
            try:
                user_input = input(f"{Colors.GREEN}> {Colors.END}")
                
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
        
        if cmd == "/help":
            self._show_help()
        
        elif cmd == "/exit" or cmd == "/quit":
            print(f"{Colors.YELLOW}Kończenie pracy...{Colors.END}")
            self.running = False
        
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
                return
            
            new_model = args[0]
            if not self._check_model_exists(new_model):
                print(f"{Colors.YELLOW}Model {new_model} nie jest zainstalowany. Czy chcesz go pobrać? (t/N):{Colors.END} ", end="")
                choice = input().lower()
                if choice == 't':
                    self._pull_model(new_model)
                else:
                    print(f"{Colors.RED}Nie zmieniono modelu.{Colors.END}")
                    return
            
            self.config["model"] = new_model
            self._save_config()
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
        
        else:
            print(f"{Colors.RED}Nieznana komenda: {cmd}. Wpisz /help aby uzyskać pomoc.{Colors.END}")
    
    def _show_help(self):
        """Wyświetla pomoc dla komend asystenta"""
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


def main():
    """Entry point for the evopy package"""
    parser = argparse.ArgumentParser(description="Ewolucyjny Asystent - system konwersacyjny")
    parser.add_argument("--config", type=str, help="Ścieżka do pliku konfiguracyjnego")
    parser.add_argument("--debug", action="store_true", help="Włącza tryb debugowania")
    parser.add_argument("--auto-accept", action="store_true", help="Automatycznie akceptuje wszystkie pytania")
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    
    # Jeśli auto-accept jest włączone, ustawiamy zmienną środowiskową
    if args.auto_accept:
        os.environ["EVOPY_AUTO_ACCEPT"] = "1"
    
    config_path = Path(args.config) if args.config else CONFIG_FILE
    assistant = EvoAssistant(config_path=config_path)
    assistant.start()


if __name__ == "__main__":
    main()