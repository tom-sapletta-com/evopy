#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skrypt do ręcznego rejestrowania zadań Docker.
Używaj tego skryptu, aby dodać zadanie Docker do serwera modułów.
"""

import os
import sys
import json
import requests
from datetime import datetime

def register_task(task_id, container_id, code="print('Hello, World!')", output="Hello, World!", is_service=False):
    """Rejestruje zadanie Docker w serwerze modułów"""
    try:
        # Przygotuj dane do wysłania
        data = {
            "task_id": task_id,
            "container_id": container_id,
            "code": code,
            "output": output,
            "is_service": "true" if is_service else "false"
        }
        
        # Wyślij żądanie do serwera modułów
        response = requests.post(
            "http://localhost:5000/docker/register",
            data=data
        )
        
        if response.status_code == 200:
            print(f"Zadanie Docker {task_id} zostało zarejestrowane w serwerze modułów")
            print(f"URL zadania: http://localhost:5000/docker/{task_id}")
            return True
        else:
            print(f"Błąd podczas rejestrowania zadania Docker: {response.text}")
            return False
    except Exception as e:
        print(f"Nie udało się zarejestrować zadania Docker: {e}")
        return False

def register_task_directly(task_id, container_id, code="print('Hello, World!')", output="Hello, World!", is_service=False):
    """Rejestruje zadanie Docker bezpośrednio w pliku"""
    try:
        # Ścieżka do pliku z zadaniami Docker
        modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "modules")
        data_dir = os.path.join(modules_dir, "data")
        tasks_file = os.path.join(data_dir, "docker_tasks.json")
        
        # Utwórz katalog danych, jeśli nie istnieje
        os.makedirs(data_dir, exist_ok=True)
        
        # Wczytaj istniejące zadania
        tasks = {}
        web_services = {}
        if os.path.exists(tasks_file):
            try:
                with open(tasks_file, "r") as f:
                    data = json.load(f)
                    tasks = data.get("docker_tasks", {})
                    web_services = data.get("web_services", {})
            except Exception as e:
                print(f"Błąd podczas wczytywania zadań Docker: {e}")
        
        # Dodaj nowe zadanie
        tasks[task_id] = {
            "container_id": container_id,
            "timestamp": datetime.now().isoformat(),
            "code": code,
            "output": output,
            "is_service": is_service,
            "service_url": None,
            "service_name": None
        }
        
        # Zapisz zadania do pliku
        with open(tasks_file, "w") as f:
            data = {
                "docker_tasks": tasks,
                "web_services": web_services,
                "updated_at": datetime.now().isoformat()
            }
            json.dump(data, f, indent=2)
        
        print(f"Zadanie Docker {task_id} zostało zapisane do pliku")
        print(f"URL zadania: http://localhost:5000/docker/{task_id}")
        return True
    except Exception as e:
        print(f"Błąd podczas zapisywania zadania Docker do pliku: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Użycie: python register_task.py <task_id> <container_id> [<code>] [<output>] [<is_service>]")
        sys.exit(1)
    
    task_id = sys.argv[1]
    container_id = sys.argv[2]
    code = sys.argv[3] if len(sys.argv) > 3 else "print('Hello, World!')"
    output = sys.argv[4] if len(sys.argv) > 4 else "Hello, World!"
    is_service = sys.argv[5].lower() == "true" if len(sys.argv) > 5 else False
    
    # Spróbuj zarejestrować zadanie przez API
    if not register_task(task_id, container_id, code, output, is_service):
        # Jeśli nie udało się przez API, zarejestruj bezpośrednio w pliku
        register_task_directly(task_id, container_id, code, output, is_service)
