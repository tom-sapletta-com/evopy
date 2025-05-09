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
logger = logging.getLogger('python2text')


class Python2Text:
    """Klasa do konwersji kodu Python na opis tekstowy"""
    
    def __init__(self, model_name="codellama:7b-code", code_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            code_dir: Katalog z kodem (opcjonalny)
        """
        self.model_name = model_name
        self.code_dir = code_dir
        logger.info(f"Inicjalizacja Python2Text z modelem {model_name}")
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
    
    def python_to_text(self, python_code: str) -> Dict[str, Any]:
        """Konwertuje kod Python na opis w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "description": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie opisu dla kodu Python...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w wyjaśnianiu kodu Python.
Twoim zadaniem jest wygenerowanie dokładnego opisu w języku naturalnym, który wyjaśnia co robi podany kod Python.
Opis powinien być szczegółowy, ale zrozumiały dla osoby nieznającej szczegółów technicznych.
Wyjaśnij cel kodu, jego działanie krok po kroku oraz potencjalne zastosowania."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nWyjaśnij, co robi następujący kod Python:\n```python\n{python_code}\n```"
            
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
                logger.error(f"Błąd podczas generowania opisu: {stderr}")
                return {
                    "success": False,
                    "description": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij opis z odpowiedzi
            description = stdout.strip()
            
            return {
                "success": True,
                "description": description,
                "error": "",
                "analysis": "Opis wygenerowany pomyślnie"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji kodu Python na tekst: {e}")
            return {
                "success": False,
                "description": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def analyze_code(self, python_code: str) -> Dict[str, Any]:
        """Analizuje kod Python i zwraca jego strukturę i potencjalne problemy"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "analysis": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w analizie kodu Python.
Twoim zadaniem jest przeanalizowanie podanego kodu Python i zwrócenie:
1. Struktury kodu (główne funkcje, klasy, metody)
2. Potencjalnych problemów lub błędów
3. Sugestii optymalizacji lub poprawy
4. Oceny jakości kodu (czytelność, zgodność z PEP 8)

Odpowiedź powinna być szczegółowa i techniczna."""
            
            prompt = f"Przeanalizuj następujący kod Python:\n\n```python\n{python_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Analizowanie kodu Python...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas analizy kodu: {stderr}")
                return {
                    "success": False,
                    "analysis": "",
                    "error": stderr
                }
            
            return {
                "success": True,
                "analysis": stdout.strip(),
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas analizy kodu Python: {e}")
            return {
                "success": False,
                "analysis": "",
                "error": str(e)
            }
    
    def generate_docstring(self, python_code: str, style: str = "google") -> Dict[str, Any]:
        """Generuje docstring dla kodu Python w określonym stylu
        
        Args:
            python_code: Kod Python do analizy
            style: Styl docstring (google, numpy, sphinx)
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "docstring": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = f"""Jesteś ekspertem w tworzeniu dokumentacji kodu Python.
Twoim zadaniem jest wygenerowanie docstring w stylu {style} dla podanego kodu Python.
Docstring powinien zawierać:
1. Krótki opis funkcji/klasy/metody
2. Opis parametrów
3. Opis wartości zwracanej
4. Przykłady użycia (opcjonalnie)
5. Informacje o wyjątkach (jeśli są rzucane)

Zwróć tylko sam docstring, bez kodu."""
            
            prompt = f"Wygeneruj docstring dla następującego kodu Python:\n\n```python\n{python_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie docstring dla kodu Python...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania docstring: {stderr}")
                return {
                    "success": False,
                    "docstring": "",
                    "error": stderr
                }
            
            # Wyodrębnij docstring z odpowiedzi
            docstring = stdout.strip()
            
            # Usuń potencjalne znaczniki kodu
            docstring = re.sub(r'^```python\n|^```\n|\n```$', '', docstring, flags=re.MULTILINE)
            
            return {
                "success": True,
                "docstring": docstring,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania docstring: {e}")
            return {
                "success": False,
                "docstring": "",
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Python2Text(model={self.model_name})"
