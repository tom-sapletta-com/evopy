#!/usr/bin/env python3
"""
Resource Manager - Moduł do zarządzania zasobami systemowymi

Ten moduł odpowiada za wykrywanie dostępnych zasobów sprzętowych
i dostosowywanie parametrów wykonania (np. timeout) w zależności od nich.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Próba importu psutil, jeśli nie jest dostępny, używamy wartości domyślnych
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger("evo-assistant.resource-manager")

# Ścieżka do pliku .env
ENV_PATH = Path(__file__).parents[2] / "config" / ".env"

def load_config():
    """
    Ładuje konfigurację z pliku .env
    
    Returns:
        dict: Słownik z konfiguracją
    """
    # Załaduj zmienne środowiskowe
    load_dotenv(ENV_PATH)
    
    config = {
        "default_timeout": int(os.getenv("DEFAULT_TIMEOUT", 60)),
        "max_timeout": int(os.getenv("MAX_TIMEOUT", 120)),
        "min_timeout": int(os.getenv("MIN_TIMEOUT", 30)),
        "auto_adjust": os.getenv("AUTO_ADJUST_TIMEOUT", "true").lower() == "true",
        "cpu_weight": float(os.getenv("CPU_WEIGHT", 0.6)),
        "memory_weight": float(os.getenv("MEMORY_WEIGHT", 0.4))
    }
    
    return config

def get_system_resources():
    """
    Pobiera informacje o dostępnych zasobach systemowych
    
    Returns:
        dict: Słownik z informacjami o zasobach
    """
    if not PSUTIL_AVAILABLE:
        logger.warning("Moduł psutil nie jest dostępny. Używanie domyślnych wartości.")
        return {
            "cpu_count": 4,
            "cpu_usage": 50.0,
            "memory_total_gb": 8.0,
            "memory_available_gb": 4.0,
            "memory_usage_percent": 50.0
        }
    
    try:
        # Pobierz informacje o CPU
        cpu_count = psutil.cpu_count(logical=True)
        cpu_usage = psutil.cpu_percent(interval=0.5)
        
        # Pobierz informacje o pamięci
        memory = psutil.virtual_memory()
        memory_total_gb = memory.total / (1024 ** 3)  # Konwersja na GB
        memory_available_gb = memory.available / (1024 ** 3)  # Konwersja na GB
        memory_usage_percent = memory.percent
        
        return {
            "cpu_count": cpu_count,
            "cpu_usage": cpu_usage,
            "memory_total_gb": memory_total_gb,
            "memory_available_gb": memory_available_gb,
            "memory_usage_percent": memory_usage_percent
        }
    except Exception as e:
        logger.error(f"Błąd podczas pobierania informacji o zasobach: {str(e)}")
        # W przypadku błędu zwróć domyślne wartości
        return {
            "cpu_count": 4,
            "cpu_usage": 50.0,
            "memory_total_gb": 8.0,
            "memory_available_gb": 4.0,
            "memory_usage_percent": 50.0
        }

def calculate_timeout():
    """
    Oblicza optymalny timeout na podstawie dostępnych zasobów
    
    Returns:
        int: Timeout w sekundach
    """
    config = load_config()
    
    # Jeśli automatyczne dostosowanie jest wyłączone, zwróć domyślny timeout
    if not config["auto_adjust"]:
        return config["default_timeout"]
    
    # Pobierz informacje o zasobach
    resources = get_system_resources()
    
    # Oblicz współczynnik dostępności CPU (im niższe użycie, tym lepiej)
    cpu_factor = 1.0 - (resources["cpu_usage"] / 100.0)
    
    # Oblicz współczynnik dostępności pamięci (im więcej wolnej pamięci, tym lepiej)
    memory_factor = 1.0 - (resources["memory_usage_percent"] / 100.0)
    
    # Oblicz ogólny współczynnik dostępności zasobów (ważona suma)
    resource_factor = (
        config["cpu_weight"] * cpu_factor + 
        config["memory_weight"] * memory_factor
    )
    
    # Oblicz timeout na podstawie współczynnika dostępności zasobów
    # Im więcej zasobów, tym dłuższy timeout (do maksymalnej wartości)
    timeout_range = config["max_timeout"] - config["min_timeout"]
    adjusted_timeout = config["min_timeout"] + int(timeout_range * resource_factor)
    
    # Ogranicz timeout do zdefiniowanych limitów
    timeout = max(config["min_timeout"], min(adjusted_timeout, config["max_timeout"]))
    
    logger.info(f"Dostosowano timeout do zasobów systemowych: {timeout}s (CPU: {resources['cpu_usage']}%, RAM: {resources['memory_usage_percent']}%)")
    
    return timeout

def get_adjusted_timeout():
    """
    Zwraca dostosowany timeout z uwzględnieniem zasobów systemowych
    
    Returns:
        int: Timeout w sekundach
    """
    try:
        return calculate_timeout()
    except Exception as e:
        logger.error(f"Błąd podczas obliczania timeout'u: {str(e)}")
        # W przypadku błędu zwróć domyślną wartość
        return load_config()["default_timeout"]

if __name__ == "__main__":
    # Konfiguracja logowania
    logging.basicConfig(level=logging.INFO)
    
    # Wyświetl informacje o zasobach i obliczony timeout
    resources = get_system_resources()
    timeout = get_adjusted_timeout()
    
    print(f"Dostępne zasoby:")
    print(f"  CPU: {resources['cpu_count']} rdzeni, użycie: {resources['cpu_usage']}%")
    print(f"  RAM: {resources['memory_total_gb']:.1f} GB, dostępne: {resources['memory_available_gb']:.1f} GB ({resources['memory_usage_percent']}% użyte)")
    print(f"Obliczony timeout: {timeout}s")
