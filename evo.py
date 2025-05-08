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

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("assistant.log")
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
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Stałe
APP_DIR = Path.home() / ".evo-assistant"
HISTORY_DIR = APP_DIR / "history"
PROJECTS_DIR = APP_DIR / "projects"
CACHE_DIR = APP_DIR / "cache"
MODELS_DIR = APP_DIR / "models"
CONFIG_FILE = APP_DIR / "config.json"
DEFAULT_MODEL = "deepseek-coder:instruct-6.7b"
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
        for directory in [APP_DIR, HISTORY_DIR, PROJECTS_DIR, CACHE_DIR, MODELS_DIR]:
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
                    self._pull_model(model)
        
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
        
        if system == "linux":
            # Instrukcje dla Linux
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
        
        if system == "linux":
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
        
        if system == "linux":
            print(f"{Colors.YELLOW}Ollama nie jest zainstalowana. Czy chcesz ją zainstalować? (t/N):{Colors.END} ", end="")
            choice = input().lower()
            if choice == 't':
                print(f"{Colors.BLUE}Instalowanie Ollama...{Colors.END}")
                os.system("curl -fsSL https://ollama.com/install.sh | sh")
                print(f"{Colors.GREEN}Ollama została zainstalowana.{Colors.END}")
            else:
                print(f"{Colors.YELLOW}Instalacja Ollama pominięta. Asystent będzie używać Ollama w kontenerze Docker.{Colors.END}")
        
        elif system == "darwin":  # macOS
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
    
    def _pull_model(self, model: str):
        """Pobiera model Ollama"""
        print(f"{Colors.YELLOW}Model {model} nie jest pobrany. Czy chcesz go pobrać? (t/N):{Colors.END} ", end="")
        choice = input().lower()
        if choice == 't':
            print(f"{Colors.BLUE}Pobieranie modelu {model}...{Colors.END}")
            process = subprocess.Popen(["ollama", "pull", model], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wyświetlanie postępu
            while process.poll() is None:
                output = process.stdout.readline().strip()
                if output:
                    print(f"\r{Colors.BLUE}{output}{Colors.END}", end="")
                time.sleep(0.1)
            
            print(f"\n{Colors.GREEN}Model {model} został pobrany.{Colors.END}")
        else:
            print(f"{Colors.YELLOW}Pobieranie modelu pominięte. Asystent może nie działać poprawnie.{Colors.END}")
    
    def _start_ollama_server(self):
        """Uruchamia serwer Ollama"""
        logger.info("Uruchamianie serwera Ollama...")
        
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
                    subprocess.run(["docker", "run", "-d", "--name", "evo-assistant-ollama", "-p", "11434:11434", 
                                    "-v", "ollama-data:/root/.ollama", "ollama/ollama"], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    logger.info("Ollama została uruchomiona w kontenerze Docker")
                    
                    # Pobieranie modelu
                    model = self.config.get("model", DEFAULT_MODEL)
                    logger.info(f"Pobieranie modelu {model} w kontenerze Docker...")
                    subprocess.run(["docker", "exec", "evo-assistant-ollama", "ollama", "pull", model], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                    
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
            print(f"{Colors.BLUE}{i}. {conv.get('title', 'Bez tytułu')} -