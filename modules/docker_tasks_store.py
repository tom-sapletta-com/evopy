#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do przechowywania informacji o zadaniach Docker.
Zapewnia trwałe przechowywanie zadań między uruchomieniami serwera.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Konfiguracja logowania
logger = logging.getLogger('docker-tasks-store')

# Ścieżka do pliku z zadaniami Docker
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULES_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TASKS_FILE = os.path.join(DATA_DIR, 'docker_tasks.json')

# Upewnij się, że plik istnieje
if not os.path.exists(TASKS_FILE):
    with open(TASKS_FILE, 'w') as f:
        json.dump({'docker_tasks': {}, 'web_services': {}, 'updated_at': datetime.now().isoformat()}, f, indent=2)

# Logowanie ścieżek dla debugowania
logger.info(f"PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"DATA_DIR: {DATA_DIR}")
logger.info(f"TASKS_FILE: {TASKS_FILE}")

# Utwórz katalog danych, jeśli nie istnieje
os.makedirs(DATA_DIR, exist_ok=True)

# Globalny słownik zadań Docker
DOCKER_TASKS = {}
docker_tasks = DOCKER_TASKS  # Alias dla kompatybilności
web_services = {}

def load_tasks():
    """Wczytuje zadania Docker z pliku"""
    global DOCKER_TASKS, web_services
    
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r') as f:
                data = json.load(f)
                DOCKER_TASKS = data.get('docker_tasks', {})
                web_services = data.get('web_services', {})
                
                # Aktualizuj alias
                global docker_tasks
                docker_tasks = DOCKER_TASKS
                
                logger.info(f"Wczytano {len(DOCKER_TASKS)} zadań Docker z pliku")
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania zadań Docker: {e}")
    else:
        logger.info("Plik z zadaniami Docker nie istnieje, tworzenie nowego")
        save_tasks()

def save_tasks():
    """Zapisuje zadania Docker do pliku"""
    try:
        with open(TASKS_FILE, 'w') as f:
            data = {
                'docker_tasks': DOCKER_TASKS,
                'web_services': web_services,
                'updated_at': datetime.now().isoformat()
            }
            json.dump(data, f, indent=2)
        logger.info(f"Zapisano {len(DOCKER_TASKS)} zadań Docker do pliku")
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania zadań Docker: {e}")

def register_docker_container(task_id, container_id, code, output, is_service=False, service_url=None, service_name=None, user_prompt=None, agent_explanation=None, container_exists=True):
    """Rejestruje kontener Docker dla zadania
    
    Args:
        task_id: ID zadania Docker
        container_id: ID kontenera Docker
        code: Kod Python, który został uruchomiony
        output: Wynik wykonania kodu
        is_service: Czy to jest serwis webowy
        service_url: URL serwisu (tylko dla is_service=True)
        service_name: Nazwa serwisu (tylko dla is_service=True)
        user_prompt: Zapytanie użytkownika, które doprowadziło do wygenerowania kodu
        agent_explanation: Wyjaśnienie asystenta dotyczące wygenerowanego kodu
        container_exists: Czy kontener nadal istnieje w systemie
    
    Returns:
        Dict: Informacje o zarejestrowanym zadaniu Docker
    """
    # Generuj linki do kontenera Docker
    container_link = f"/docker/{task_id}"
    web_interface_url = f"http://localhost:5000/docker/{task_id}"
    continue_url = f"http://localhost:5000/docker/{task_id}/continue"
    continue_info = f"Możesz kontynuować konwersację pod adresem: {web_interface_url}"
    
    DOCKER_TASKS[task_id] = {
        "container_id": container_id,
        "timestamp": datetime.now().isoformat(),
        "code": code,
        "output": output,
        "is_service": is_service,
        "service_url": service_url,
        "service_name": service_name,
        "user_prompt": user_prompt,
        "agent_explanation": agent_explanation,
        "container_exists": container_exists,
        "container_link": container_link,
        "web_interface_url": web_interface_url
    }
    
    # Jeśli to serwis webowy, dodaj go również do słownika serwisów niezależnie od tego, czy kontener istnieje
    if is_service and service_url:
        web_services[task_id] = {
            "container_id": container_id,
            "timestamp": datetime.now().isoformat(),
            "service_url": service_url,
            "service_name": service_name or f"Serwis {task_id[:8]}",
            "status": "running" if container_exists else "stopped",
            "container_link": container_link,
            "web_interface_url": web_interface_url
        }
    
    # Zapisz zadania do pliku
    save_tasks()
    
    logger.info(f"Zarejestrowano kontener {container_id} dla zadania {task_id}")
    return DOCKER_TASKS[task_id]

def get_docker_task(task_id):
    """Pobiera informacje o zadaniu Docker"""
    logger.info(f"Próba pobrania zadania Docker o ID: {task_id}")
    logger.info(f"Typ ID zadania: {type(task_id)}, Długość: {len(task_id) if task_id else 0}")
    logger.info(f"Dostępne klucze w DOCKER_TASKS: {list(DOCKER_TASKS.keys())}")
    
    # Spróbuj znaleźć zadanie bezpośrednio
    task = DOCKER_TASKS.get(task_id)
    
    if task:
        logger.info(f"Zadanie Docker {task_id} znalezione bezpośrednio")
    else:
        # Spróbuj znaleźć zadanie przez porównanie stringów
        logger.info(f"Zadanie Docker {task_id} nie znalezione bezpośrednio, próba porównania stringów")
        for key in DOCKER_TASKS.keys():
            if str(key) == str(task_id):
                task = DOCKER_TASKS[key]
                logger.info(f"Zadanie Docker znalezione przez porównanie stringów: {key}")
                break
    
    logger.info(f"Wynik pobierania zadania Docker {task_id}: {'znaleziono' if task else 'nie znaleziono'}")
    return task

def get_all_docker_tasks():
    """Pobiera wszystkie zadania Docker"""
    return DOCKER_TASKS

def get_all_web_services():
    """Pobiera wszystkie serwisy webowe"""
    return web_services

# Wczytaj zadania przy importowaniu modułu
load_tasks()
