#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na polecenia Docker
"""

import os
import sys
import logging
import json
import subprocess
from pathlib import Path

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2docker')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Text2Docker:
    """Klasa konwertująca tekst na polecenia Docker"""
    
    def __init__(self, model="llama3"):
        """Inicjalizacja konwertera text2docker"""
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
    
    def convert(self, text):
        """
        Konwertuje tekst na polecenia Docker
        
        Args:
            text (str): Tekst do konwersji
            
        Returns:
            str: Wygenerowane polecenie Docker
        """
        if not text:
            return "# Nie podano tekstu do konwersji"
        
        if not self.ollama_api:
            return "# Błąd: Moduł ollama_api nie jest dostępny"
        
        # Przygotuj prompt dla modelu
        prompt = f"""Przekształć poniższy opis w polecenie Docker. Zwróć TYLKO polecenie Docker bez dodatkowych wyjaśnień.
Jeśli opis jest niejasny lub brakuje informacji, użyj rozsądnych wartości domyślnych.

Opis:
{text}

Polecenie Docker:
"""
        
        try:
            # Generuj polecenie Docker za pomocą modelu
            logger.info("Generowanie polecenia Docker...")
            response = self.ollama_api.generate(self.model, prompt)
            
            # Wyodrębnij polecenie Docker z odpowiedzi
            docker_command = response.strip()
            
            # Sprawdź poprawność polecenia Docker
            if not docker_command.startswith("docker"):
                docker_command = "docker " + docker_command
            
            return docker_command
        except Exception as e:
            logger.error(f"Błąd podczas generowania polecenia Docker: {e}")
            return f"# Błąd: {str(e)}"
    
    def validate_command(self, command):
        """
        Sprawdza poprawność polecenia Docker
        
        Args:
            command (str): Polecenie Docker do sprawdzenia
            
        Returns:
            bool: True jeśli polecenie jest poprawne, False w przeciwnym razie
        """
        if not command or not isinstance(command, str):
            return False
        
        # Usuń komentarze
        command = command.split('#')[0].strip()
        
        # Sprawdź czy polecenie zaczyna się od "docker"
        if not command.startswith("docker"):
            return False
        
        # Sprawdź podstawowe podpolecenia Docker
        valid_subcommands = [
            "run", "build", "pull", "push", "images", "ps", "container", "volume",
            "network", "compose", "exec", "logs", "start", "stop", "restart", "rm"
        ]
        
        parts = command.split()
        if len(parts) < 2:
            return False
        
        # Sprawdź czy drugie słowo to znane podpolecenie Docker
        subcommand = parts[1]
        if subcommand not in valid_subcommands:
            # Sprawdź czy to może być złożone podpolecenie (np. container ls)
            if len(parts) >= 3 and parts[1] in ["container", "volume", "network"]:
                return True
            return False
        
        return True
    
    def execute_command(self, command, safe_mode=True):
        """
        Wykonuje polecenie Docker
        
        Args:
            command (str): Polecenie Docker do wykonania
            safe_mode (bool): Czy używać trybu bezpiecznego (tylko odczyt)
            
        Returns:
            dict: Wynik wykonania polecenia
        """
        if not command:
            return {"success": False, "output": "", "error": "Puste polecenie"}
        
        # Usuń komentarze
        command = command.split('#')[0].strip()
        
        # Sprawdź poprawność polecenia
        if not self.validate_command(command):
            return {"success": False, "output": "", "error": "Niepoprawne polecenie Docker"}
        
        # W trybie bezpiecznym zezwalaj tylko na polecenia odczytu
        if safe_mode:
            safe_commands = ["images", "ps", "logs", "inspect", "version", "info"]
            parts = command.split()
            
            is_safe = False
            for cmd in safe_commands:
                if cmd in parts:
                    is_safe = True
                    break
            
            if not is_safe:
                return {
                    "success": False,
                    "output": "",
                    "error": "Polecenie nie jest dozwolone w trybie bezpiecznym. Dozwolone są tylko: " + ", ".join(safe_commands)
                }
        
        try:
            # Wykonaj polecenie Docker
            logger.info(f"Wykonywanie polecenia: {command}")
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout, "error": ""}
            else:
                return {"success": False, "output": result.stdout, "error": result.stderr}
        except Exception as e:
            logger.error(f"Błąd podczas wykonywania polecenia Docker: {e}")
            return {"success": False, "output": "", "error": str(e)}
    
    def explain_command(self, command):
        """
        Wyjaśnia polecenie Docker
        
        Args:
            command (str): Polecenie Docker do wyjaśnienia
            
        Returns:
            str: Wyjaśnienie polecenia Docker
        """
        if not command:
            return "Nie podano polecenia do wyjaśnienia"
        
        if not self.ollama_api:
            return "Błąd: Moduł ollama_api nie jest dostępny"
        
        # Przygotuj prompt dla modelu
        prompt = f"""Wyjaśnij poniższe polecenie Docker. Opisz co robi każda opcja i parametr.
Wyjaśnienie powinno być szczegółowe i zrozumiałe dla osoby, która nie zna Dockera.

Polecenie Docker:
{command}

Wyjaśnienie:
"""
        
        try:
            # Generuj wyjaśnienie za pomocą modelu
            logger.info("Generowanie wyjaśnienia polecenia Docker...")
            response = self.ollama_api.generate(self.model, prompt)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Błąd: {str(e)}"
