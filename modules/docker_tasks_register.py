#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do rejestrowania zadań Docker w serwerze modułów.
Zapewnia prosty interfejs do rejestrowania zadań Docker bez konieczności
bezpośredniego wywoływania żądań HTTP.
"""

import os
import json
import logging
import uuid
import requests
from pathlib import Path

# Konfiguracja logowania
logger = logging.getLogger('docker-tasks-register')

# Ścieżka do pliku z zadaniami Docker
MODULES_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(MODULES_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TASKS_FILE = os.path.join(DATA_DIR, 'docker_tasks.json')

# Logowanie ścieżek dla debugowania
logger.info(f"PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"DATA_DIR: {DATA_DIR}")
logger.info(f"TASKS_FILE: {TASKS_FILE}")

# Utwórz katalog danych, jeśli nie istnieje
os.makedirs(DATA_DIR, exist_ok=True)

def register_docker_task(container_id, code, output, is_service=False, service_url=None, service_name=None, user_prompt=None, agent_explanation=None):
    """Rejestruje zadanie Docker w serwerze modułów
    
    Args:
        container_id: ID kontenera Docker
        code: Kod Python, który został uruchomiony
        output: Wynik wykonania kodu
        is_service: Czy to jest serwis webowy
        service_url: URL serwisu (tylko dla is_service=True)
        service_name: Nazwa serwisu (tylko dla is_service=True)
        user_prompt: Zapytanie użytkownika, które doprowadziło do wygenerowania kodu
        agent_explanation: Wyjaśnienie asystenta dotyczące wygenerowanego kodu
        
    Returns:
        str: ID zadania Docker
    """
    # Generuj unikalny identyfikator zadania
    task_id = str(uuid.uuid4())
    
    try:
        # Najpierw zapisz zadanie do pliku na wypadek, gdyby serwer modułów był niedostępny
        save_task_to_file(task_id, container_id, code, output, is_service, service_url, service_name, user_prompt, agent_explanation)
        
        # Spróbuj zarejestrować zadanie w serwerze modułów
        try:
            # Przygotuj dane do wysłania
            data = {
                "container_id": container_id,
                "code": code,
                "output": output,
                "is_service": "true" if is_service else "false"
            }
            
            if is_service and service_url:
                data["service_url"] = service_url
                
            if is_service and service_name:
                data["service_name"] = service_name
                
            # Dodaj prompt użytkownika i wyjaśnienie agenta, jeśli są dostępne
            if user_prompt:
                data["user_prompt"] = user_prompt
                
            if agent_explanation:
                data["agent_explanation"] = agent_explanation
            
            # Wyślij żądanie do serwera modułów
            response = requests.post(
                "http://localhost:5000/docker/register",
                data=data
            )
            
            if response.status_code == 200:
                logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane w serwerze modułów")
            else:
                logger.warning(f"Błąd podczas rejestrowania zadania Docker w serwerze modułów: {response.text}")
        except Exception as e:
            logger.warning(f"Nie udało się zarejestrować zadania Docker w serwerze modułów: {e}")
    except Exception as e:
        logger.error(f"Błąd podczas rejestrowania zadania Docker: {e}")
    
    return task_id

def save_task_to_file(task_id, container_id, code, output, is_service=False, service_url=None, service_name=None, user_prompt=None, agent_explanation=None):
    """Zapisuje zadanie Docker do pliku
    
    Args:
        task_id: ID zadania Docker
        container_id: ID kontenera Docker
        code: Kod Python, który został uruchomiony
        output: Wynik wykonania kodu
        is_service: Czy to jest serwis webowy
        service_url: URL serwisu (tylko dla is_service=True)
        service_name: Nazwa serwisu (tylko dla is_service=True)
    """
    try:
        # Wczytaj istniejące zadania
        tasks = {}
        if os.path.exists(TASKS_FILE):
            try:
                with open(TASKS_FILE, 'r') as f:
                    data = json.load(f)
                    tasks = data.get('docker_tasks', {})
            except Exception as e:
                logger.error(f"Błąd podczas wczytywania zadań Docker: {e}")
        
        # Dodaj nowe zadanie
        import datetime
        tasks[task_id] = {
            "container_id": container_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "code": code,
            "output": output,
            "is_service": is_service,
            "service_url": service_url,
            "service_name": service_name,
            "user_prompt": user_prompt,
            "agent_explanation": agent_explanation
        }
        
        # Zapisz zadania do pliku
        with open(TASKS_FILE, 'w') as f:
            data = {
                'docker_tasks': tasks,
                'updated_at': datetime.datetime.now().isoformat()
            }
            json.dump(data, f, indent=2)
        
        logger.info(f"Zadanie Docker {task_id} zostało zapisane do pliku")
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania zadania Docker do pliku: {e}")
