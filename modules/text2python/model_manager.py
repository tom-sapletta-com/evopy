#!/usr/bin/env python3
"""
Model Manager - Moduł do zarządzania modelami LLM dla Evopy

Ten moduł zapewnia funkcje do zarządzania modelami LLM, w tym:
- Sprawdzanie dostępności modeli z timeoutem
- Strategia fallbacku modeli
- Zarządzanie procesami uruchamiania modeli

Copyright 2025 Tom Sapletta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import json
import logging
import subprocess
import platform
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("evo-assistant.model-manager")

# Wykrywanie platformy
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_FEDORA = IS_LINUX and os.path.exists("/etc/fedora-release")
IS_MACOS = platform.system() == "Darwin"

# Definicje modeli
DEFAULT_MODELS = [
    {
        "id": "llama",
        "name": "llama3",
        "description": "Llama 3 (Meta AI)",
        "context_window": 8192,
        "priority": 1
    },
    {
        "id": "deepsek",
        "name": "deepseek-coder",
        "description": "DeepSeek Coder",
        "context_window": 16384,
        "priority": 2
    },
    {
        "id": "phi",
        "name": "phi3",
        "description": "Phi-3 (Microsoft)",
        "context_window": 4096,
        "priority": 3
    },
    {
        "id": "mistral",
        "name": "mistral",
        "description": "Mistral AI",
        "context_window": 8192,
        "priority": 4
    },
    {
        "id": "bielik",
        "name": "bielik",
        "description": "Bielik (Polish LLM)",
        "context_window": 4096,
        "priority": 5
    }
]

def get_available_models() -> List[Dict[str, Any]]:
    """
    Zwraca listę dostępnych modeli LLM z timeoutem
    
    Returns:
        List[Dict]: Lista modeli z ich konfiguracją
    """
    # Pobierz modele z konfiguracji
    models = DEFAULT_MODELS.copy()
    
    # Sprawdź dostępność modeli w Ollama
    available_models = check_ollama_models(timeout=5)
    
    # Oznacz modele jako dostępne
    for model in models:
        model["available"] = model["name"] in available_models
    
    return models

def check_ollama_models(timeout: int = 5) -> List[str]:
    """
    Sprawdza dostępne modele w Ollama z timeoutem
    
    Args:
        timeout: Limit czasu w sekundach
        
    Returns:
        List[str]: Lista dostępnych modeli
    """
    try:
        # Dostosuj komendę do systemu operacyjnego
        ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"
        
        # Uruchom komendę z timeoutem
        result = subprocess.run(
            [ollama_cmd, "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            logger.warning(f"Błąd podczas sprawdzania modeli Ollama: {result.stderr}")
            return []
        
        # Pobierz listę dostępnych modeli
        available_models_raw = result.stdout.strip().split('\n')[1:] if result.stdout.strip() else []
        available_models = []
        
        # Przetwórz listę dostępnych modeli
        for model_line in available_models_raw:
            if not model_line.strip():
                continue
            model_parts = model_line.split()
            if len(model_parts) > 0:
                model_name = model_parts[0].split(':')[0]
                available_models.append(model_name)
        
        return available_models
    
    except subprocess.TimeoutExpired:
        logger.warning(f"Przekroczono limit czasu ({timeout}s) podczas sprawdzania modeli Ollama")
        return []
    except Exception as e:
        logger.error(f"Błąd podczas sprawdzania modeli Ollama: {str(e)}")
        return []

def get_model_config(model_id: str = None) -> Dict[str, Any]:
    """
    Zwraca konfigurację wybranego modelu lub aktywnego modelu
    
    Args:
        model_id: Identyfikator modelu (opcjonalnie)
        
    Returns:
        Dict: Konfiguracja modelu
    """
    # Pobierz wszystkie modele
    models = get_available_models()
    
    # Jeśli podano model_id, znajdź go na liście
    if model_id:
        for model in models:
            if model["id"] == model_id:
                return model
    
    # Jeśli nie podano model_id lub nie znaleziono modelu, użyj pierwszego dostępnego
    for model in sorted(models, key=lambda x: x.get("priority", 999)):
        if model.get("available", False):
            return model
    
    # Jeśli żaden model nie jest dostępny, użyj pierwszego z listy
    return models[0]

def pull_model(model_name: str, timeout: int = 60) -> bool:
    """
    Pobiera model z Ollama z timeoutem
    
    Args:
        model_name: Nazwa modelu do pobrania
        timeout: Limit czasu w sekundach
        
    Returns:
        bool: True jeśli model został pobrany, False w przeciwnym przypadku
    """
    # Specjalna obsługa dla modelu Bielik, który nie jest dostępny w publicznym repozytorium Ollama
    if model_name.lower() == "bielik":
        logger.warning(f"Model {model_name} nie jest dostępny w publicznym repozytorium Ollama.")
        logger.info("Bielik to polski model językowy, który wymaga ręcznej instalacji.")
        logger.info("Instrukcje instalacji: https://github.com/bielik-project/bielik")
        return False
        
    try:
        # Dostosuj komendę do systemu operacyjnego
        ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"
        
        # Uruchom komendę z timeoutem
        logger.info(f"Pobieranie modelu {model_name}...")
        result = subprocess.run(
            [ollama_cmd, "pull", model_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            # Sprawdź, czy błąd dotyczy braku pliku manifestu (częsty błąd dla nieistniejących modeli)
            if "file does not exist" in result.stderr or "manifest" in result.stderr:
                logger.error(f"Model {model_name} nie istnieje w repozytorium Ollama.")
                logger.info(f"Dostępne modele to: llama3, mistral, deepseek-coder, phi3")
            else:
                logger.error(f"Błąd podczas pobierania modelu {model_name}: {result.stderr}")
            return False
        
        logger.info(f"Model {model_name} został pomyślnie pobrany")
        return True
    
    except subprocess.TimeoutExpired:
        logger.error(f"Przekroczono limit czasu ({timeout}s) podczas pobierania modelu {model_name}")
        return False
    except Exception as e:
        logger.error(f"Błąd podczas pobierania modelu {model_name}: {str(e)}")
        return False

def find_best_available_model(preferred_models: List[str] = None) -> Optional[str]:
    """
    Znajduje najlepszy dostępny model z listy preferowanych
    
    Args:
        preferred_models: Lista preferowanych modeli w kolejności priorytetów
        
    Returns:
        Optional[str]: Nazwa najlepszego dostępnego modelu lub None
    """
    if preferred_models is None:
        # Domyślna lista preferowanych modeli
        preferred_models = ["llama3", "deepseek-coder", "phi3", "mistral", "bielik"]
    
    # Pobierz dostępne modele
    available_models = check_ollama_models(timeout=5)
    
    # Znajdź pierwszy dostępny model z listy preferowanych
    for model in preferred_models:
        if model in available_models:
            return model
    
    return None

def run_model_with_timeout(
    model_name: str,
    prompt: str,
    timeout: int = 30,
    system_prompt: str = None
) -> Tuple[int, str, str]:
    """
    Uruchamia model LLM z timeoutem
    
    Args:
        model_name: Nazwa modelu do uruchomienia
        prompt: Zapytanie do modelu
        timeout: Limit czasu w sekundach
        system_prompt: Systemowy prompt (opcjonalnie)
        
    Returns:
        Tuple[int, str, str]: Kod wyjścia, stdout, stderr
    """
    try:
        # Dostosuj komendę do systemu operacyjnego
        ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"
        
        # Przygotuj komendę
        cmd = [ollama_cmd, "run", model_name]
        
        # Dodaj system prompt jeśli podano
        if system_prompt:
            combined_prompt = f"{system_prompt}\n\n{prompt}"
        else:
            combined_prompt = prompt
        
        # Uruchom komendę z timeoutem
        logger.info(f"Uruchamianie modelu {model_name} z timeoutem {timeout}s...")
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Przekaż prompt do stdin i odczytaj wynik z timeoutem
        stdout, stderr = process.communicate(input=combined_prompt, timeout=timeout)
        
        return process.returncode, stdout, stderr
    
    except subprocess.TimeoutExpired:
        # Zabij proces jeśli przekroczono limit czasu
        process.kill()
        logger.error(f"Przekroczono limit czasu ({timeout}s) podczas uruchamiania modelu {model_name}")
        return 1, "", f"Przekroczono limit czasu ({timeout}s)"
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania modelu {model_name}: {str(e)}")
        return 1, "", str(e)

# Przykład użycia
if __name__ == "__main__":
    print("=== Dostępne modele ===")
    models = get_available_models()
    for model in models:
        status = "✓" if model.get("available", False) else "✗"
        print(f"{status} {model['id']} ({model['name']}): {model['description']}")
    
    print("\n=== Najlepszy dostępny model ===")
    best_model = find_best_available_model()
    print(f"Najlepszy dostępny model: {best_model}")
    
    if best_model:
        print("\n=== Test modelu ===")
        returncode, stdout, stderr = run_model_with_timeout(
            model_name=best_model,
            prompt="Wyświetl aktualną datę i godzinę w Pythonie",
            timeout=10
        )
        
        print(f"Kod wyjścia: {returncode}")
        print(f"Wynik:\n{stdout}")
        
        if stderr:
            print(f"Błąd:\n{stderr}")
