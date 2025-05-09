#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Union

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('text2python')


class Text2Python:
    """Klasa do konwersji tekstu na kod Python"""
    
    def __init__(self, model_name="codellama:7b-code", code_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            code_dir: Katalog z kodem (opcjonalny)
        """
        self.model_name = model_name
        self.code_dir = code_dir
        logger.info(f"Inicjalizacja Text2Python z modelem {model_name}")
        if code_dir:
            logger.info(f"Katalog kodu: {code_dir}")
        
    
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny"""
        try:
            # Sprawdź, czy Ollama jest zainstalowane i czy model jest dostępny
            cmd = ["ollama", "list"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas sprawdzania dostępności modelu: {stderr}")
                return False
            
            # Sprawdź, czy model jest na liście
            return self.model_name in stdout
            
        except Exception as e:
            logger.error(f"Błąd podczas sprawdzania dostępności modelu: {e}")
            return False
    
    def text_to_python(self, prompt: str) -> Dict[str, Any]:
        """Konwertuje opis w języku naturalnym na kod Python"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie kodu dla zapytania: {prompt}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania kodu: {stderr}")
                return {
                    "success": False,
                    "code": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij kod Python z odpowiedzi
            code = stdout.strip()
            
            # Jeśli kod jest otoczony znacznikami ```python i ```, usuń je
            code = re.sub(r'^```python\n|^```\n|\n```$', '', code, flags=re.MULTILINE)
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod wygenerowany pomyślnie"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na kod: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def explain_code(self, code: str) -> str:
        """Generuje wyjaśnienie kodu w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.model_name} nie jest dostępny."
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu kodu Python. Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób. Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku.'
            
            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie wyjaśnienia kodu...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"
            
            return stdout.strip()
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Python(model={self.model_name})"
