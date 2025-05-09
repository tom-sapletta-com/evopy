#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usługa API dla modułu text2docker
"""

import os
import sys
import json
import logging
from pathlib import Path

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj dekorator API
from modules.utils.api_decorator import create_api_service

# Importuj moduł text2docker
from modules.text2docker import Text2Docker

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('docker_api')

# Tworzenie usługi API
docker_api = create_api_service(
    name="docker_api",
    description="API do konwersji tekstu na polecenia Docker",
    port=5003
)

# Inicjalizacja konwertera text2docker
text2docker = Text2Docker()

@docker_api.endpoint('/convert', methods=['POST', 'GET'])
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

@docker_api.endpoint('/validate', methods=['POST', 'GET'])
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

@docker_api.endpoint('/run', methods=['POST'])
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
    url = docker_api.start()
    print(f"Usługa API uruchomiona pod adresem: {url}")
    
    # Utrzymuj działanie skryptu
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Zatrzymywanie usługi API...")
        docker_api.stop()
