#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test modułu DockerSandbox
"""

import os
import sys
import tempfile
from pathlib import Path

# Dodaj główny katalog projektu do ścieżki importów
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Importuj DockerSandbox
from docker_sandbox import DockerSandbox, check_docker_available

def test_docker_sandbox():
    """Test modułu DockerSandbox"""
    print("Sprawdzanie dostępności Dockera...")
    docker_available, docker_message = check_docker_available()
    print(f"Docker dostępny: {docker_available}, komunikat: {docker_message}")
    
    if not docker_available:
        print("Docker nie jest dostępny, pomijanie testów")
        return
    
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
    
    # Wyczyść piaskownicę
    print("\nCzyszczenie piaskownicy...")
    cleanup_result = sandbox.cleanup()
    print(f"Wynik czyszczenia: {cleanup_result}")

if __name__ == "__main__":
    test_docker_sandbox()
