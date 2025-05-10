#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test integracyjny dla DockerSandbox i modułu text2python
Sprawdza poprawność uruchamiania kodu w Dockerze i generowania linków
"""

import os
import sys
import json
import uuid
import tempfile
import logging
from pathlib import Path
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test-docker-integration')

# Dodaj główny katalog projektu do ścieżki importów
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Importuj potrzebne moduły
from docker_sandbox import DockerSandbox, check_docker_available

# Sprawdź, czy moduł text2python jest dostępny
try:
    from modules.text2python.text2python import Text2Python
    text2python_available = True
except ImportError:
    logger.warning("Moduł text2python nie jest dostępny")
    text2python_available = False

# Sprawdź, czy moduł docker_tasks_store jest dostępny
try:
    from modules.docker_tasks_store import register_docker_container, get_docker_task
    docker_tasks_available = True
except ImportError:
    logger.warning("Moduł docker_tasks_store nie jest dostępny")
    docker_tasks_available = False

def test_docker_sandbox():
    """Test podstawowej funkcjonalności DockerSandbox"""
    print("\n=== Test podstawowej funkcjonalności DockerSandbox ===")
    
    # Sprawdź dostępność Dockera
    docker_available, docker_message = check_docker_available()
    print(f"Docker dostępny: {docker_available}, komunikat: {docker_message}")
    
    if not docker_available:
        print("Docker nie jest dostępny, pomijanie testów")
        return False
    
    # Utwórz katalog tymczasowy dla piaskownicy
    sandbox_dir = Path(tempfile.gettempdir()) / "evopy_sandbox_test"
    os.makedirs(sandbox_dir, exist_ok=True)
    
    print(f"Katalog piaskownicy: {sandbox_dir}")
    
    # Utwórz piaskownicę
    sandbox = DockerSandbox(base_dir=sandbox_dir)
    
    print(f"Utworzono piaskownicę: {sandbox.sandbox_id}")
    
    # Przygotuj prosty kod do testów
    test_code = """
def execute():
    import platform
    import os
    import sys
    
    result = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "current_dir": os.getcwd(),
        "files": os.listdir(),
        "calculation": 2 + 2
    }
    
    return result
"""
    
    # Uruchom kod w piaskownicy
    print("Uruchamianie kodu w piaskownicy...")
    result = sandbox.run(test_code)
    
    # Wyświetl wynik
    print("\nWynik wykonania kodu:")
    for key, value in result.items():
        print(f"- {key}: {value}")
    
    # Sprawdź, czy wynik zawiera oczekiwane klucze
    success = result.get("success", False)
    container_name = result.get("container_name", "")
    sandbox_id = result.get("sandbox_id", "")
    
    if not success:
        print(f"BŁĄD: Wykonanie kodu nie powiodło się: {result.get('error', 'Nieznany błąd')}")
        return False
    
    if not container_name:
        print("BŁĄD: Brak nazwy kontenera w wyniku")
        return False
    
    if not sandbox_id:
        print("BŁĄD: Brak ID piaskownicy w wyniku")
        return False
    
    print(f"Kontener Docker: {container_name}")
    print(f"ID piaskownicy: {sandbox_id}")
    
    # Wyczyść piaskownicę
    print("\nCzyszczenie piaskownicy...")
    cleanup_result = sandbox.cleanup()
    print(f"Wynik czyszczenia: {cleanup_result}")
    
    return True

def test_text2python_docker_integration():
    """Test integracji modułu text2python z DockerSandbox"""
    if not text2python_available:
        print("\n=== Test integracji text2python z DockerSandbox POMINIĘTY (moduł niedostępny) ===")
        return False
    
    print("\n=== Test integracji text2python z DockerSandbox ===")
    
    # Inicjalizuj moduł text2python
    t2p = Text2Python()
    
    # Przygotuj zapytanie testowe
    test_query = "Oblicz pole prostokąta o długości a = 10 i szerokości b = 5"
    
    # Wygeneruj kod Python
    print(f"Generowanie kodu dla zapytania: {test_query}")
    result = t2p.process(test_query)
    
    if not result.get("success", False):
        print(f"BŁĄD: Generowanie kodu nie powiodło się: {result.get('error', 'Nieznany błąd')}")
        return False
    
    # Pobierz wygenerowany kod
    code = result.get("code", "")
    
    if not code:
        print("BŁĄD: Brak wygenerowanego kodu")
        return False
    
    print(f"\nWygenerowany kod:\n{code}")
    
    # Wykonaj kod w piaskownicy Docker
    print("\nWykonywanie kodu w piaskownicy Docker...")
    execution_result = t2p.execute_code(code, use_sandbox=True)
    
    # Wyświetl wynik
    print("\nWynik wykonania kodu:")
    for key, value in execution_result.items():
        print(f"- {key}: {value}")
    
    # Sprawdź, czy wynik zawiera oczekiwane klucze
    success = execution_result.get("success", False)
    container_name = execution_result.get("container_name", "")
    sandbox_id = execution_result.get("sandbox_id", "")
    
    if not success:
        print(f"BŁĄD: Wykonanie kodu nie powiodło się: {execution_result.get('error', 'Nieznany błąd')}")
        return False
    
    if not container_name:
        print("BŁĄD: Brak nazwy kontenera w wyniku")
        return False
    
    if not sandbox_id:
        print("BŁĄD: Brak ID piaskownicy w wyniku")
        return False
    
    print(f"Kontener Docker: {container_name}")
    print(f"ID piaskownicy: {sandbox_id}")
    
    return True

def test_docker_tasks_integration():
    """Test integracji z modułem docker_tasks_store"""
    if not docker_tasks_available:
        print("\n=== Test integracji z docker_tasks_store POMINIĘTY (moduł niedostępny) ===")
        return False
    
    print("\n=== Test integracji z docker_tasks_store ===")
    
    # Utwórz unikalne ID zadania
    task_id = str(uuid.uuid4())
    container_id = f"test-container-{task_id[:8]}"
    
    # Przygotuj testowy kod i wynik
    test_code = "def execute():\n    return 2 + 2"
    test_output = {"success": True, "output": "4", "error": "", "execution_time": 0.1}
    
    # Zarejestruj kontener Docker
    print(f"Rejestrowanie kontenera Docker dla zadania {task_id}...")
    register_docker_container(
        task_id=task_id,
        container_id=container_id,
        code=test_code,
        output=test_output,
        is_service=False,
        service_url=None,
        service_name=None,
        user_prompt="Testowe zapytanie",
        agent_explanation="Testowe wyjaśnienie",
        container_exists=True
    )
    
    # Pobierz informacje o zadaniu
    task_info = get_docker_task(task_id)
    
    if not task_info:
        print(f"BŁĄD: Nie można pobrać informacji o zadaniu {task_id}")
        return False
    
    print("\nInformacje o zadaniu:")
    for key, value in task_info.items():
        if key not in ["code", "output"]:  # Pomiń duże pola dla czytelności
            print(f"- {key}: {value}")
    
    # Sprawdź, czy informacje o zadaniu zawierają oczekiwane klucze
    if task_info.get("container_id") != container_id:
        print(f"BŁĄD: Niepoprawne ID kontenera: {task_info.get('container_id')} != {container_id}")
        return False
    
    # Sprawdź, czy link do kontenera jest poprawny
    container_link = task_info.get("container_link", "")
    expected_link = f"/docker/{task_id}"
    
    if container_link != expected_link:
        print(f"BŁĄD: Niepoprawny link do kontenera: {container_link} != {expected_link}")
        return False
    
    print(f"Link do kontenera: {container_link}")
    
    return True

def test_docker_link_generation():
    """Test generowania linków do kontenerów Docker"""
    print("\n=== Test generowania linków do kontenerów Docker ===")
    
    # Utwórz katalog tymczasowy dla piaskownicy
    sandbox_dir = Path(tempfile.gettempdir()) / "evopy_sandbox_test"
    os.makedirs(sandbox_dir, exist_ok=True)
    
    # Utwórz piaskownicę
    sandbox = DockerSandbox(base_dir=sandbox_dir)
    
    # Przygotuj prosty kod do testów
    test_code = """
def execute():
    return {"message": "Test udany", "status": "OK"}
"""
    
    # Uruchom kod w piaskownicy
    result = sandbox.run(test_code)
    
    # Sprawdź, czy wynik zawiera oczekiwane klucze
    success = result.get("success", False)
    container_name = result.get("container_name", "")
    sandbox_id = result.get("sandbox_id", "")
    
    if not success:
        print(f"BŁĄD: Wykonanie kodu nie powiodło się: {result.get('error', 'Nieznany błąd')}")
        return False
    
    # Wygeneruj link do kontenera
    container_link = f"http://localhost:5000/docker/{sandbox_id}"
    print(f"Wygenerowany link do kontenera: {container_link}")
    
    # Sprawdź, czy link jest poprawny
    if not sandbox_id:
        print("BŁĄD: Brak ID piaskownicy w wyniku")
        return False
    
    # Wyczyść piaskownicę
    sandbox.cleanup()
    
    return True

def main():
    """Główna funkcja testowa"""
    print("=== Test integracyjny dla DockerSandbox i modułu text2python ===")
    print(f"Data i czas: {datetime.now().isoformat()}")
    print(f"Katalog projektu: {project_root}")
    
    # Uruchom testy
    results = {
        "docker_sandbox": test_docker_sandbox(),
        "text2python_integration": test_text2python_docker_integration(),
        "docker_tasks_integration": test_docker_tasks_integration(),
        "docker_link_generation": test_docker_link_generation()
    }
    
    # Wyświetl podsumowanie
    print("\n=== Podsumowanie testów ===")
    for test_name, result in results.items():
        status = "SUKCES" if result else "BŁĄD"
        print(f"{test_name}: {status}")
    
    # Sprawdź, czy wszystkie testy zakończyły się sukcesem
    all_success = all(results.values())
    
    if all_success:
        print("\nWszystkie testy zakończyły się sukcesem!")
    else:
        print("\nNiektóre testy zakończyły się błędem.")
        
        # Sugestie naprawy
        print("\n=== Sugestie naprawy ===")
        
        if not results["docker_sandbox"]:
            print("1. Sprawdź, czy Docker jest zainstalowany i działa poprawnie.")
            print("2. Upewnij się, że użytkownik ma uprawnienia do uruchamiania kontenerów Docker.")
            print("3. Sprawdź, czy obraz python:3.9-slim jest dostępny.")
        
        if not results["text2python_integration"]:
            print("1. Sprawdź, czy moduł text2python jest poprawnie zaimportowany.")
            print("2. Upewnij się, że metoda execute_code w klasie Text2Python poprawnie korzysta z DockerSandbox.")
            print("3. Sprawdź, czy ścieżki importu są poprawne.")
        
        if not results["docker_tasks_integration"]:
            print("1. Sprawdź, czy moduł docker_tasks_store jest poprawnie zaimportowany.")
            print("2. Upewnij się, że funkcja register_docker_container poprawnie zapisuje informacje o kontenerze.")
            print("3. Sprawdź, czy funkcja get_docker_task poprawnie pobiera informacje o kontenerze.")
        
        if not results["docker_link_generation"]:
            print("1. Sprawdź, czy ID piaskownicy jest poprawnie przekazywane do wyniku.")
            print("2. Upewnij się, że link do kontenera jest poprawnie generowany.")
            print("3. Sprawdź, czy interfejs webowy poprawnie obsługuje linki do kontenerów.")
    
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main())
