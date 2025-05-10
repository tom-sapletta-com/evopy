#!/usr/bin/env python3
"""
Docker Sandbox - Moduł do bezpiecznego uruchamiania kodu w kontenerach Docker

Ten moduł zapewnia bezpieczne środowisko do uruchamiania kodu Python
generowanego na podstawie żądań użytkownika.
"""

import os
import uuid
import json
import time
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Sprawdź, czy moduł docker_tasks_store jest dostępny
try:
    from modules.docker_tasks_store import register_docker_container
    docker_tasks_available = True
except ImportError:
    docker_tasks_available = False
    print("Moduł docker_tasks_store nie jest dostępny. Kontenery Docker nie będą rejestrowane w interfejsie webowym.")
    # Pusta funkcja zastępcza
    def register_docker_container(*args, **kwargs):
        return {}

# Import menedżera zależności
from dependency_manager import fix_code_dependencies

logger = logging.getLogger("evo-assistant.docker-sandbox")


def check_docker_available() -> Tuple[bool, str]:
    """
    Sprawdza, czy Docker jest dostępny i działa poprawnie
    
    Returns:
        Tuple[bool, str]: (czy_dostępny, komunikat)
    """
    try:
        # Sprawdź, czy komenda docker jest dostępna
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, f"Docker nie jest dostępny: {result.stderr}"
        
        # Sprawdź, czy możemy uruchomić kontener
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return False, f"Docker nie działa poprawnie: {result.stderr}"
        
        return True, "Docker jest dostępny i działa poprawnie"
    except FileNotFoundError:
        return False, "Komenda docker nie została znaleziona"
    except subprocess.TimeoutExpired:
        return False, "Timeout podczas sprawdzania dostępności Dockera"
    except Exception as e:
        return False, f"Błąd podczas sprawdzania dostępności Dockera: {e}"


class DockerSandbox:
    """Klasa do zarządzania piaskownicami Docker dla kodu użytkownika"""

    def __init__(self, base_dir: Path, docker_image: str = "python:3.9-slim", timeout: int = 30):
        """
        Inicjalizacja piaskownicy Docker

        Args:
            base_dir: Katalog bazowy dla plików piaskownicy
            docker_image: Obraz Docker do użycia
            timeout: Limit czasu wykonania w sekundach
        """
        self.base_dir = base_dir
        self.docker_image = docker_image
        self.timeout = timeout
        self.container_id = None
        self.sandbox_id = str(uuid.uuid4())
        self.sandbox_dir = base_dir / self.sandbox_id

        # Utwórz katalog dla piaskownicy
        os.makedirs(self.sandbox_dir, exist_ok=True)

    def prepare_code(self, code: str, filename: str = "user_code.py") -> Path:
        """
        Przygotowuje kod do wykonania w piaskownicy

        Args:
            code: Kod Python do wykonania
            filename: Nazwa pliku dla kodu

        Returns:
            Path: Ścieżka do pliku z kodem
        """
        # Napraw brakujące zależności w kodzie użytkownika
        code = fix_code_dependencies(code)

        code_file = self.sandbox_dir / filename

        # Dodaj wrapper do przechwytywania wyjścia i błędów
        wrapped_code = f"""
import sys
import traceback
import json
import time
import importlib

# Funkcja do dynamicznego importowania modułów
def import_module_safe(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Funkcja do automatycznego importowania modułów
def auto_import():
    # Lista standardowych modułów do automatycznego importu w razie potrzeby
    auto_import_modules = [
        'time', 'datetime', 'os', 'sys', 're', 'json', 'math', 'random',
        'collections', 'itertools', 'functools', 'pathlib', 'shutil',
        'subprocess', 'threading', 'multiprocessing', 'urllib', 'http',
        'socket', 'email', 'csv', 'xml', 'html', 'sqlite3', 'logging'
    ]

    # Importuj wszystkie moduły z listy
    for module_name in auto_import_modules:
        if module_name not in globals():
            imported_module = import_module_safe(module_name)
            if imported_module:
                globals()[module_name] = imported_module

# Automatycznie zaimportuj standardowe moduły
auto_import()

# Przechwytywanie wyjścia
class OutputCapture:
    def __init__(self):
        self.output = []

    def write(self, text):
        self.output.append(text)

    def flush(self):
        pass

# Zapisz oryginalne strumienie
original_stdout = sys.stdout
original_stderr = sys.stderr

# Zastąp strumienie
stdout_capture = OutputCapture()
stderr_capture = OutputCapture()
sys.stdout = stdout_capture
sys.stderr = stderr_capture

# Wykonaj kod użytkownika
result = {{
    "success": False,
    "output": "",
    "error": "",
    "execution_time": 0
}}

try:
    start_time = time.time()

    # Kod użytkownika
{chr(10).join(['    ' + line for line in code.split(chr(10))])}

    execution_time = time.time() - start_time
    result["success"] = True
    result["execution_time"] = execution_time
except ImportError as e:
    # Próba automatycznego importu brakującego modułu
    missing_module = str(e).split("'")
    if len(missing_module) >= 2:
        module_name = missing_module[1]
        # Próba importu
        imported = import_module_safe(module_name)
        if imported:
            # Dodaj moduł do globals i spróbuj ponownie
            globals()[module_name] = imported
            try:
                # Ponowna próba wykonania kodu
                start_time = time.time()

                # Kod użytkownika
{chr(10).join(['                ' + line for line in code.split(chr(10))])}

                execution_time = time.time() - start_time
                result["success"] = True
                result["execution_time"] = execution_time
            except Exception as import_retry_error:
                result["error"] = f"Po próbie automatycznego importu: {{str(import_retry_error)}}"
                result["traceback"] = traceback.format_exc()
        else:
            result["error"] = f"Brakujący moduł: {{module_name}}. Nie można go automatycznie zaimportować."
            result["traceback"] = traceback.format_exc()
    else:
        result["error"] = str(e)
        result["traceback"] = traceback.format_exc()
except Exception as e:
    result["error"] = str(e)
    result["traceback"] = traceback.format_exc()

# Przywróć oryginalne strumienie
sys.stdout = original_stdout
sys.stderr = original_stderr

# Zapisz wyniki
result["output"] = "".join(stdout_capture.output)
result["error_output"] = "".join(stderr_capture.output)

# Zapisz wynik do pliku
with open("result.json", "w") as f:
    json.dump(result, f)

print(json.dumps(result))
"""

        with open(code_file, "w") as f:
            f.write(wrapped_code)

        return code_file

    def run(self, code: str) -> Dict[str, Any]:
        """
        Uruchamia kod w piaskownicy Docker

        Args:
            code: Kod Python do wykonania

        Returns:
            Dict: Wynik wykonania kodu
        """
        # Sprawdź, czy Docker jest dostępny
        docker_available, docker_message = check_docker_available()
        if not docker_available:
            logger.error(f"Docker nie jest dostępny: {docker_message}")
            return {
                "success": False,
                "error": f"Docker nie jest dostępny: {docker_message}",
                "output": "",
                "execution_time": 0
            }
        
        try:
            # Przygotuj kod
            code_file = self.prepare_code(code)

            # Utwórz kontener Docker
            container_name = f"evopy-sandbox-{self.sandbox_id}"

            # Uruchom kontener
            cmd = [
                "docker", "run",
                "--name", container_name,
                "--rm",  # Usuń kontener po zakończeniu
                "-v", f"{self.sandbox_dir}:/app",
                "-w", "/app",
                "--network", "none",  # Brak dostępu do sieci
                "--memory", "512m",  # Limit pamięci
                "--cpus", "0.5",  # Limit CPU
                self.docker_image,
                "python", "/app/user_code.py"
            ]

            logger.info(f"Uruchamianie kodu w piaskownicy: {container_name}")

            # Uruchom z limitem czasu
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            try:
                stdout, stderr = process.communicate(timeout=self.timeout)

                # Sprawdź wynik
                if process.returncode != 0:
                    logger.warning(f"Kod zakończył się z błędem: {stderr}")
                    result = {
                        "success": False,
                        "output": stdout,
                        "error": stderr,
                        "execution_time": self.timeout,
                        "container_name": container_name,
                        "sandbox_id": self.sandbox_id
                    }
                    
                    # Zarejestruj kontener w module docker_tasks_store, jeśli jest dostępny
                    if docker_tasks_available:
                        try:
                            task_id = self.sandbox_id
                            register_docker_container(
                                task_id=task_id,
                                container_id=container_name,
                                code=code,
                                output=result,
                                is_service=False,
                                container_exists=True
                            )
                            # Dodaj link do kontenera w interfejsie webowym
                            result["container_link"] = f"/docker/{task_id}"
                            result["web_interface_url"] = "http://localhost:5000/docker/{}".format(task_id)
                            logger.info(f"Zarejestrowano kontener {container_name} w interfejsie webowym")
                        except Exception as e:
                            logger.warning(f"Nie można zarejestrować kontenera w interfejsie webowym: {e}")
                    
                    return result

                # Parsuj wynik JSON
                try:
                    result = json.loads(stdout)
                    # Dodaj informacje o kontenerze
                    result["container_name"] = container_name
                    result["sandbox_id"] = self.sandbox_id
                    
                    # Zarejestruj kontener w module docker_tasks_store, jeśli jest dostępny
                    if docker_tasks_available:
                        try:
                            task_id = self.sandbox_id
                            register_docker_container(
                                task_id=task_id,
                                container_id=container_name,
                                code=code,
                                output=result,
                                is_service=False,
                                container_exists=True
                            )
                            # Dodaj link do kontenera w interfejsie webowym
                            result["container_link"] = f"/docker/{task_id}"
                            result["web_interface_url"] = "http://localhost:5000/docker/{}".format(task_id)
                            logger.info(f"Zarejestrowano kontener {container_name} w interfejsie webowym")
                        except Exception as e:
                            logger.warning(f"Nie można zarejestrować kontenera w interfejsie webowym: {e}")
                    
                    return result
                except json.JSONDecodeError:
                    logger.warning(f"Nie można sparsować wyniku jako JSON: {stdout}")
                    result = {
                        "success": True,
                        "output": stdout,
                        "error": "",
                        "execution_time": 0.1,  # Przybliżony czas wykonania
                        "container_name": container_name,
                        "sandbox_id": self.sandbox_id
                    }
                    
                    # Zarejestruj kontener w module docker_tasks_store, jeśli jest dostępny
                    if docker_tasks_available:
                        try:
                            task_id = self.sandbox_id
                            register_docker_container(
                                task_id=task_id,
                                container_id=container_name,
                                code=code,
                                output=result,
                                is_service=False,
                                container_exists=True
                            )
                            # Dodaj link do kontenera w interfejsie webowym
                            result["container_link"] = f"/docker/{task_id}"
                            result["web_interface_url"] = "http://localhost:5000/docker/{}".format(task_id)
                            logger.info(f"Zarejestrowano kontener {container_name} w interfejsie webowym")
                        except Exception as e:
                            logger.warning(f"Nie można zarejestrować kontenera w interfejsie webowym: {e}")
                    
                    return result
            except subprocess.TimeoutExpired:
                # Zabij proces, jeśli przekroczył limit czasu
                process.kill()
                logger.warning(f"Kod przekroczył limit czasu wykonania: {self.timeout}s")
                
                # Spróbuj zatrzymać kontener, jeśli nadal działa
                try:
                    subprocess.run(["docker", "stop", container_name], timeout=5, capture_output=True)
                    logger.info(f"Zatrzymano kontener: {container_name}")
                except Exception as container_error:
                    logger.warning(f"Nie można zatrzymać kontenera: {container_error}")
                
                return {
                    "success": False,
                    "output": "",
                    "error": f"Kod przekroczył limit czasu wykonania: {self.timeout}s",
                    "execution_time": self.timeout,
                    "container_name": container_name,
                    "sandbox_id": self.sandbox_id,
                    "timeout": True
                }
        except FileNotFoundError as e:
            logger.error(f"Nie znaleziono pliku lub komendy: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Nie znaleziono pliku lub komendy: {e}",
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        except PermissionError as e:
            logger.error(f"Brak uprawnień: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Brak uprawnień do uruchomienia kontenera Docker: {e}",
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania kodu w piaskownicy: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "sandbox_id": self.sandbox_id
            }
        finally:
            # Spróbuj wyczyścić kontener
            try:
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except:
                pass

    def cleanup(self):
        """Czyści zasoby piaskownicy"""
        try:
            # Sprawdź, czy kontener nadal istnieje i zatrzymaj go
            if self.container_id:
                try:
                    subprocess.run(
                        ["docker", "stop", self.container_id],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=5
                    )
                    logger.info(f"Zatrzymano kontener: {self.container_id}")
                except Exception as e:
                    logger.warning(f"Nie można zatrzymać kontenera {self.container_id}: {e}")
            
            # Sprawdź, czy istnieją kontenery z nazwą zawierającą sandbox_id i zatrzymaj je
            try:
                container_name = f"evopy-sandbox-{self.sandbox_id}"
                subprocess.run(
                    ["docker", "stop", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                logger.info(f"Zatrzymano kontener: {container_name}")
            except Exception:
                # Ignoruj błędy - kontener może już nie istnieć
                pass
            
            # Usuń katalog piaskownicy
            if os.path.exists(self.sandbox_dir):
                shutil.rmtree(self.sandbox_dir, ignore_errors=True)
                logger.info(f"Wyczyszczono piaskownicę: {self.sandbox_id}")
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia piaskownicy: {e}")
        
        return {"success": True, "message": f"Wyczyszczono piaskownicę: {self.sandbox_id}"}