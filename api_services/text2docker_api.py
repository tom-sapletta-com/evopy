#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usługa API dla modułu text2docker
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj dekorator API
from api_services.api_decorator import create_api_service

# Importuj moduł text2docker
try:
    from modules.text2docker import Text2Docker
except ImportError:
    # Jeśli nie można zaimportować modułu, utwórz zaślepkę
    class Text2Docker:
        def __init__(self, model="llama3"):
            self.model = model
        
        def convert(self, text):
            return f"docker run -it --rm ubuntu:latest bash -c 'echo \"{text}\"'"
        
        def validate_command(self, command):
            return command.startswith("docker")
        
        def run_command(self, command):
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                return {
                    "error": str(e)
                }

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2docker_api')

# Tworzenie usługi API
text2docker_api = create_api_service(
    name="text2docker_api",
    description="API do konwersji tekstu na polecenia Docker",
    port=5003
)

# Inicjalizacja konwertera text2docker
text2docker = Text2Docker()

@text2docker_api.endpoint('/convert', methods=['POST', 'GET'])
def convert(data):
    """
    Konwertuje tekst na polecenie Docker
    
    Parametry:
        text (str): Tekst do konwersji
    
    Zwraca:
        dict: Wynik konwersji
    """
    try:
        # Pobierz tekst z danych
        text = data.get('text', '')
        
        if not text:
            return {"error": "Nie podano tekstu do konwersji"}
        
        # Konwertuj tekst na polecenie Docker
        docker_command = text2docker.convert(text)
        
        return {
            "text": text,
            "docker_command": docker_command
        }
    except Exception as e:
        logger.error(f"Błąd podczas konwersji: {e}")
        return {"error": str(e)}

@text2docker_api.endpoint('/validate', methods=['POST', 'GET'])
def validate(data):
    """
    Sprawdza poprawność polecenia Docker
    
    Parametry:
        command (str): Polecenie Docker do sprawdzenia
    
    Zwraca:
        dict: Wynik walidacji
    """
    try:
        # Pobierz polecenie z danych
        command = data.get('command', '')
        
        if not command:
            return {"error": "Nie podano polecenia do sprawdzenia"}
        
        # Sprawdź poprawność polecenia Docker
        is_valid = text2docker.validate_command(command)
        
        return {
            "command": command,
            "is_valid": is_valid
        }
    except Exception as e:
        logger.error(f"Błąd podczas walidacji: {e}")
        return {"error": str(e)}

@text2docker_api.endpoint('/run', methods=['POST'])
def run(data):
    """
    Uruchamia polecenie Docker
    
    Parametry:
        command (str): Polecenie Docker do uruchomienia
    
    Zwraca:
        dict: Wynik uruchomienia
    """
    try:
        # Pobierz polecenie z danych
        command = data.get('command', '')
        
        if not command:
            return {"error": "Nie podano polecenia do uruchomienia"}
        
        # Sprawdź poprawność polecenia Docker
        is_valid = text2docker.validate_command(command)
        
        if not is_valid:
            return {"error": "Niepoprawne polecenie Docker"}
        
        # Uruchom polecenie Docker
        result = text2docker.run_command(command)
        
        return {
            "command": command,
            "result": result
        }
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania: {e}")
        return {"error": str(e)}

# Uruchom usługę API, jeśli skrypt jest uruchamiany bezpośrednio
if __name__ == '__main__':
    # Uruchom usługę API
    url = text2docker_api.start()
    print(f"Usługa API uruchomiona pod adresem: {url}")
    
    # Utrzymuj działanie skryptu
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Zatrzymywanie usługi API...")
        text2docker_api.stop()
