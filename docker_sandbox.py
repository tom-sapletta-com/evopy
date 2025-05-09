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

# Import menedżera zależności
from dependency_manager import fix_code_dependencies

logger = logging.getLogger("evo-assistant.docker-sandbox")

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
            except Exception as e2:
                result["error"] = f"Po próbie automatycznego importu: {str(e2)}"
                result["traceback"] = traceback.format_exc()
        else:
            result["error"] = f"Brakujący moduł: {module_name}. Nie można go automatycznie zaimportować."
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
                    return {
                        "success": False,
                        "output": stdout,
                        "error": stderr,
                        "execution_time": self.timeout
                    }
                
                # Parsuj wynik JSON
                try:
                    result = json.loads(stdout)
                    return result
                except json.JSONDecodeError:
                    return {
                        "success": True,
                        "output": stdout,
                        "error": "",
                        "execution_time": 0
                    }
                
            except subprocess.TimeoutExpired:
                # Zabij kontener jeśli przekroczył limit czasu
                subprocess.run(["docker", "kill", container_name], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
                
                logger.warning(f"Kod przekroczył limit czasu ({self.timeout}s)")
                return {
                    "success": False,
                    "output": "",
                    "error": f"Kod przekroczył limit czasu ({self.timeout}s)",
                    "execution_time": self.timeout
                }
                
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania kodu: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"Błąd piaskownicy: {str(e)}",
                "execution_time": 0
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
            # Usuń katalog piaskownicy
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
            logger.info(f"Wyczyszczono piaskownicę: {self.sandbox_id}")
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia piaskownicy: {e}")
