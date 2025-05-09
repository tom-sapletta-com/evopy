#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł konwersji tekstu na kod Python z automatycznym uruchamianiem w Dockerze
"""

import os
import sys
import logging
import json
import time
from pathlib import Path

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('text2python_docker')

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduły
try:
    from ollama_api import OllamaAPI
    from docker_sandbox import DockerSandbox
    from modules.text2python import Text2Python
except ImportError as e:
    logger.error(f"Błąd importu: {e}")
    raise

class Text2PythonDocker:
    """Klasa konwertująca tekst na kod Python i uruchamiająca go w Dockerze"""
    
    def __init__(self, model="llama3", docker_image="python:3.9-slim", timeout=30):
        """
        Inicjalizacja konwertera text2python_docker
        
        Args:
            model (str): Nazwa modelu do generowania kodu Python
            docker_image (str): Obraz Docker do uruchamiania kodu Python
            timeout (int): Limit czasu wykonania kodu w sekundach
        """
        self.model = model
        self.docker_image = docker_image
        self.timeout = timeout
        
        # Inicjalizacja konwertera text2python
        self.text2python = Text2Python(model=model)
        
        # Inicjalizacja piaskownicy Docker
        self.sandbox = DockerSandbox(
            base_dir=Path(os.path.expanduser("~/.evopy/sandbox")),
            docker_image=docker_image,
            timeout=timeout
        )
        
        logger.info(f"Zainicjalizowano konwerter text2python_docker z modelem {model} i obrazem Docker {docker_image}")
    
    def convert(self, text, auto_run=True):
        """
        Konwertuje tekst na kod Python i opcjonalnie uruchamia go w Dockerze
        
        Args:
            text (str): Tekst do konwersji
            auto_run (bool): Czy automatycznie uruchomić kod w Dockerze
            
        Returns:
            dict: Wynik konwersji i wykonania kodu
        """
        if not text:
            return {
                "code": "# Nie podano tekstu do konwersji",
                "success": False,
                "output": "",
                "error": "Nie podano tekstu do konwersji",
                "execution_time": 0
            }
        
        try:
            # Konwertuj tekst na kod Python
            logger.info("Konwersja tekstu na kod Python...")
            python_code = self.text2python.convert(text)
            
            if not python_code or python_code.strip() == "":
                return {
                    "code": "# Nie udało się wygenerować kodu Python",
                    "success": False,
                    "output": "",
                    "error": "Nie udało się wygenerować kodu Python",
                    "execution_time": 0
                }
            
            # Jeśli auto_run=True, uruchom kod w Dockerze
            if auto_run:
                logger.info("Automatyczne uruchamianie kodu w Dockerze...")
                execution_result = self.run_code(python_code)
                
                return {
                    "code": python_code,
                    "success": execution_result["success"],
                    "output": execution_result["output"],
                    "error": execution_result["error"],
                    "execution_time": execution_result["execution_time"]
                }
            else:
                return {
                    "code": python_code,
                    "success": None,
                    "output": "",
                    "error": "",
                    "execution_time": 0
                }
        except Exception as e:
            logger.error(f"Błąd podczas konwersji lub wykonania: {e}")
            return {
                "code": f"# Błąd: {str(e)}",
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }
    
    def run_code(self, code):
        """
        Uruchamia kod Python w Dockerze
        
        Args:
            code (str): Kod Python do uruchomienia
            
        Returns:
            dict: Wynik wykonania kodu
        """
        if not code:
            return {
                "success": False,
                "output": "",
                "error": "Nie podano kodu do wykonania",
                "execution_time": 0
            }
        
        try:
            # Przygotuj kod do wykonania
            executable_code = self._prepare_code(code)
            
            # Uruchom kod w piaskownicy Docker
            logger.info("Uruchamianie kodu w piaskownicy Docker...")
            start_time = time.time()
            result = self.sandbox.run(executable_code)
            execution_time = time.time() - start_time
            
            # Dodaj czas wykonania do wyniku
            result["execution_time"] = execution_time
            
            return result
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania kodu: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }
        finally:
            # Zawsze wyczyść piaskownicę po wykonaniu
            self.sandbox.cleanup()
    
    def _prepare_code(self, code):
        """
        Przygotowuje kod Python do wykonania w Dockerze
        
        Args:
            code (str): Kod Python do przygotowania
            
        Returns:
            str: Przygotowany kod Python
        """
        # Sprawdź czy kod zawiera funkcję execute
        if "def execute(" not in code:
            # Jeśli nie, dodaj funkcję execute i wywołanie
            prepared_code = code.strip()
            
            # Dodaj funkcję execute, która uruchomi kod
            prepared_code += """

# Funkcja execute dodana automatycznie przez text2python_docker
def execute():
    # Uruchom kod powyżej i zwróć wynik
    try:
        # Sprawdź czy zdefiniowano zmienne lub funkcje, które można zwrócić
        local_vars = locals()
        # Filtruj zmienne, które nie są funkcjami wbudowanymi, modułami itp.
        result_vars = {k: v for k, v in local_vars.items() 
                      if not k.startswith('__') and k != 'execute'}
        
        if result_vars:
            return list(result_vars.values())[-1]  # Zwróć ostatnią zdefiniowaną zmienną
        else:
            return None
    except Exception as e:
        return f"Błąd wykonania: {str(e)}"

# Wywołaj funkcję execute i wyświetl wynik
result = execute()
if result is not None:
    print(result)
"""
        else:
            # Jeśli kod już zawiera funkcję execute, dodaj tylko wywołanie
            prepared_code = code.strip()
            
            if "execute()" not in prepared_code:
                prepared_code += """

# Wywołaj funkcję execute i wyświetl wynik
result = execute()
if result is not None:
    print(result)
"""
        
        return prepared_code
    
    def explain_code(self, code):
        """
        Generuje wyjaśnienie kodu Python
        
        Args:
            code (str): Kod Python do wyjaśnienia
            
        Returns:
            str: Wyjaśnienie kodu
        """
        return self.text2python.explain_code(code)
    
    def cleanup(self):
        """Czyści zasoby używane przez konwerter"""
        if hasattr(self, 'sandbox'):
            self.sandbox.cleanup()
