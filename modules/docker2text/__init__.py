#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji poleceń Docker na tekst
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
logger = logging.getLogger('docker2text')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł ollama_api
try:
    from ollama_api import OllamaAPI
except ImportError:
    logger.error("Nie można zaimportować modułu ollama_api. Upewnij się, że jest zainstalowany.")
    OllamaAPI = None

class Docker2Text:
    """Klasa konwertująca polecenia Docker na tekst"""
    
    def __init__(self, model="llama3"):
        """Inicjalizacja konwertera docker2text"""
        self.model = model
        self.ollama_api = OllamaAPI() if OllamaAPI else None
        
        # Sprawdź dostępność modelu
        if self.ollama_api:
            logger.info(f"Sprawdzanie dostępności modelu {model}...")
            if self.ollama_api.check_model_exists(model):
                logger.info(f"Model {model} jest dostępny")
            else:
                logger.warning(f"Model {model} nie jest dostępny. Spróbuj pobrać go za pomocą 'ollama pull {model}'")
    
    def convert(self, docker_command):
        """
        Konwertuje polecenie Docker na opis tekstowy
        
        Args:
            docker_command (str): Polecenie Docker do konwersji
            
        Returns:
            str: Opis tekstowy polecenia Docker
        """
        if not docker_command:
            return "Nie podano polecenia Docker do konwersji"
        
        if not self.ollama_api:
            return "Błąd: Moduł ollama_api nie jest dostępny"
        
        # Przygotuj prompt dla modelu
        prompt = f"""Opisz poniższe polecenie Docker w języku naturalnym. 
Wyjaśnij co robi to polecenie, jakie są jego parametry i jaki będzie efekt jego wykonania.
Opisz to w sposób zrozumiały dla osoby, która nie zna Dockera.

Polecenie Docker:
{docker_command}

Opis:
"""
        
        try:
            # Generuj opis za pomocą modelu
            logger.info("Generowanie opisu polecenia Docker...")
            response = self.ollama_api.generate(self.model, prompt)
            
            return response.strip()
        except Exception as e:
            logger.error(f"Błąd podczas generowania opisu: {e}")
            return f"Błąd: {str(e)}"
    
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
    
    def get_command_structure(self, command):
        """
        Analizuje strukturę polecenia Docker
        
        Args:
            command (str): Polecenie Docker do analizy
            
        Returns:
            dict: Struktura polecenia Docker
        """
        if not command or not self.validate_command(command):
            return {"valid": False}
        
        parts = command.split()
        
        # Podstawowa struktura
        structure = {
            "valid": True,
            "base_command": parts[0],  # docker
            "subcommand": parts[1] if len(parts) > 1 else "",
            "options": [],
            "arguments": []
        }
        
        # Analizuj opcje i argumenty
        i = 2
        while i < len(parts):
            if parts[i].startswith('-'):
                # To jest opcja
                option = {"name": parts[i], "value": None}
                
                # Sprawdź czy opcja ma wartość
                if i + 1 < len(parts) and not parts[i + 1].startswith('-'):
                    option["value"] = parts[i + 1]
                    i += 2
                else:
                    i += 1
                
                structure["options"].append(option)
            else:
                # To jest argument
                structure["arguments"].append(parts[i])
                i += 1
        
        return structure
    
    def get_command_help(self, command_structure):
        """
        Pobiera pomoc dla polecenia Docker
        
        Args:
            command_structure (dict): Struktura polecenia Docker
            
        Returns:
            str: Pomoc dla polecenia Docker
        """
        if not command_structure or not command_structure.get("valid", False):
            return "Niepoprawne polecenie Docker"
        
        # Przygotuj polecenie pomocy
        help_command = f"docker {command_structure['subcommand']} --help"
        
        try:
            # Wykonaj polecenie pomocy
            result = subprocess.run(help_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Błąd: {result.stderr}"
        except Exception as e:
            logger.error(f"Błąd podczas pobierania pomocy: {e}")
            return f"Błąd: {str(e)}"
