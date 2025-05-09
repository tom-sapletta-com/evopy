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

def register_docker_container(task_id, container_id, code, output, is_service=False, service_url=None, service_name=None, user_prompt=None, agent_explanation=None):
    """Rejestruje kontener Docker dla zadania"""
    DOCKER_TASKS[task_id] = {
        "container_id": container_id,
        "timestamp": datetime.now().isoformat(),
        "code": code,
        "output": output,
        "is_service": is_service,
        "service_url": service_url,
        "service_name": service_name,
        "user_prompt": user_prompt,
        "agent_explanation": agent_explanation
    }
    
    # Jeśli to serwis webowy, dodaj go również do słownika serwisów
    if is_service and service_url:
        web_services[task_id] = {
            "container_id": container_id,
            "timestamp": datetime.now().isoformat(),
            "service_url": service_url,
            "service_name": service_name or f"Service {task_id[:8]}"
        }
    
    # Zapisz zadania do pliku
    save_tasks()
    
    logger.info(f"Zarejestrowano kontener {container_id} dla zadania {task_id}")
    return DOCKER_TASKS[task_id]

def get_docker_task(task_id):
    """Pobiera informacje o zadaniu Docker"""
    return DOCKER_TASKS.get(task_id, {})

def get_all_docker_tasks():
    """Pobiera wszystkie zadania Docker"""
    return DOCKER_TASKS

def get_all_web_services():
    """Pobiera wszystkie serwisy webowe"""
    return web_services

# Wczytaj zadania przy importowaniu modułu
load_tasks()
