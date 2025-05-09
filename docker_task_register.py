#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł do bezpośredniego rejestrowania zadań Docker w serwerze modułów.
"""

import logging
import requests
import uuid

# Konfiguracja logowania
logger = logging.getLogger('docker-task-register')

def register_docker_task(task_id=None, container_id=None, code=None, output=None, is_service=False, service_url=None, service_name=None):
    """Rejestruje zadanie Docker bezpośrednio w serwerze modułów
    
    Args:
        task_id: ID zadania Docker (opcjonalne, jeśli nie podane, zostanie wygenerowane)
        container_id: ID kontenera Docker
        code: Kod Python, który został uruchomiony
        output: Wynik wykonania kodu
        is_service: Czy to jest serwis webowy
        service_url: URL serwisu (tylko dla is_service=True)
        service_name: Nazwa serwisu (tylko dla is_service=True)
        
    Returns:
        dict: Informacje o zarejestrowanym zadaniu Docker
    """
    if not task_id:
        task_id = str(uuid.uuid4())
    
    if not container_id:
        logger.error("Brak identyfikatora kontenera Docker")
        return {"success": False, "error": "Brak identyfikatora kontenera Docker"}
    
    try:
        # Przygotuj dane do wysłania
        data = {
            "task_id": task_id,
            "container_id": container_id,
            "code": code or "",
            "output": output or "",
            "is_service": "true" if is_service else "false"
        }
        
        # Dodaj informacje o serwisie, jeśli to serwis webowy
        if is_service:
            if service_url:
                data["service_url"] = service_url
            if service_name:
                data["service_name"] = service_name
        
        # Wyślij żądanie do serwera modułów
        response = requests.post(
            "http://localhost:5000/docker/register",
            data=data,
            timeout=5  # 5-sekundowy timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Zadanie Docker {task_id} zostało zarejestrowane w serwerze modułów")
            return result
        else:
            logger.warning(f"Błąd podczas rejestrowania zadania Docker w serwerze modułów: {response.text}")
            return {"success": False, "error": response.text}
    except Exception as e:
        logger.error(f"Nie udało się zarejestrować zadania Docker w serwerze modułów: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    # Przykład użycia
    import sys
    if len(sys.argv) < 3:
        print("Użycie: python docker_task_register.py <container_id> <code>")
        sys.exit(1)
    
    container_id = sys.argv[1]
    code = sys.argv[2]
    
    result = register_docker_task(container_id=container_id, code=code)
    print(result)
