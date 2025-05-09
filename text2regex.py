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
logger = logging.getLogger('text2regex')


class Text2Regex:
    """Klasa do konwersji tekstu na wyrażenia regularne"""
    
    def __init__(self, model_name="codellama:7b-code", regex_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            regex_dir: Katalog z wyrażeniami regularnymi (opcjonalny)
        """
        self.model_name = model_name
        self.regex_dir = regex_dir
        logger.info(f"Inicjalizacja Text2Regex z modelem {model_name}")
        if regex_dir:
            logger.info(f"Katalog regex: {regex_dir}")
        
    
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
    
    def text_to_regex(self, prompt: str, flavor: str = "python") -> Dict[str, Any]:
        """Konwertuje opis w języku naturalnym na wyrażenie regularne
        
        Args:
            prompt: Opis w języku naturalnym
            flavor: Dialekt wyrażeń regularnych (python, pcre, javascript, itp.)
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "regex": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie wyrażenia regularnego dla: {prompt}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = f"""Jesteś ekspertem w konwersji opisu w języku naturalnym na wyrażenia regularne.
Twoim zadaniem jest wygenerowanie wyrażenia regularnego, które realizuje opisane zadanie.
Generuj wyrażenie regularne w dialekcie {flavor}.
Zwróć samo wyrażenie regularne, bez dodatkowych wyjaśnień, cudzysłowów czy znaczników.
Zapewnij, że wyrażenie jest poprawne składniowo i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nUtwórz wyrażenie regularne, które realizuje następujące zadanie:\n{prompt}\n\nWyrażenie regularne:"
            
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
                logger.error(f"Błąd podczas generowania wyrażenia regularnego: {stderr}")
                return {
                    "success": False,
                    "regex": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij wyrażenie regularne z odpowiedzi
            regex = stdout.strip()
            
            # Usuń potencjalne znaczniki kodu lub cudzysłowy
            regex = re.sub(r'^```.*\n|^`|`$|^"|"$|^\'|\'$|\n```$', '', regex, flags=re.MULTILINE)
            regex = regex.strip()
            
            # Sprawdź, czy wyrażenie regularne jest poprawne składniowo
            try:
                re.compile(regex)
                valid = True
            except re.error as e:
                logger.warning(f"Wygenerowane wyrażenie regularne jest niepoprawne składniowo: {e}")
                valid = False
                
            return {
                "success": True,
                "regex": regex,
                "valid": valid,
                "error": "" if valid else "Niepoprawne wyrażenie regularne",
                "analysis": "Wyrażenie regularne wygenerowane pomyślnie" if valid else "Wyrażenie regularne niepoprawne składniowo"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na wyrażenie regularne: {e}")
            return {
                "success": False,
                "regex": "",
                "valid": False,
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def explain_regex(self, regex: str) -> str:
        """Generuje wyjaśnienie wyrażenia regularnego w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.model_name} nie jest dostępny."
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu wyrażeń regularnych. Twoim zadaniem jest wyjaśnienie działania podanego wyrażenia regularnego w prosty i zrozumiały sposób. Wyjaśnienie powinno być szczegółowe, ale zrozumiałe dla osoby bez głębokiej znajomości wyrażeń regularnych.'
            
            prompt = f"Wyjaśnij działanie następującego wyrażenia regularnego:\n\n{regex}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie wyjaśnienia wyrażenia regularnego...")
            
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
    
    def test_regex(self, regex: str, test_strings: List[str]) -> Dict[str, Any]:
        """Testuje wyrażenie regularne na liście ciągów testowych"""
        results = []
        valid = True
        error_message = ""
        
        try:
            # Sprawdź, czy wyrażenie regularne jest poprawne składniowo
            pattern = re.compile(regex)
            
            # Testuj na każdym ciągu testowym
            for test_str in test_strings:
                match = pattern.search(test_str)
                if match:
                    groups = match.groups() if match.groups() else []
                    results.append({
                        "string": test_str,
                        "match": True,
                        "full_match": match.group(0) == test_str,
                        "start": match.start(),
                        "end": match.end(),
                        "matched_text": match.group(0),
                        "groups": [g for g in groups]
                    })
                else:
                    results.append({
                        "string": test_str,
                        "match": False
                    })
                    
        except re.error as e:
            valid = False
            error_message = str(e)
            logger.error(f"Błąd w wyrażeniu regularnym: {e}")
        except Exception as e:
            valid = False
            error_message = str(e)
            logger.error(f"Błąd podczas testowania wyrażenia regularnego: {e}")
            
        return {
            "success": valid,
            "valid": valid,
            "error": error_message,
            "results": results
        }
    
    def generate_test_strings(self, regex: str, count: int = 5) -> Dict[str, Any]:
        """Generuje przykładowe ciągi pasujące do wyrażenia regularnego"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "examples": [],
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w wyrażeniach regularnych.
Twoim zadaniem jest wygenerowanie przykładowych ciągów znaków, które pasują do podanego wyrażenia regularnego.
Zwróć tylko przykładowe ciągi, każdy w nowej linii, bez dodatkowych wyjaśnień."""
            
            prompt = f"Wygeneruj {count} przykładowych ciągów znaków, które pasują do następującego wyrażenia regularnego:\n\n{regex}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie przykładowych ciągów dla wyrażenia regularnego...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania przykładowych ciągów: {stderr}")
                return {
                    "success": False,
                    "examples": [],
                    "error": stderr
                }
            
            # Podziel odpowiedź na linie i usuń puste linie
            examples = [line.strip() for line in stdout.strip().split('\n') if line.strip()]
            
            # Sprawdź, czy przykłady rzeczywiście pasują do wyrażenia regularnego
            try:
                pattern = re.compile(regex)
                matching_examples = []
                non_matching_examples = []
                
                for example in examples:
                    if pattern.search(example):
                        matching_examples.append(example)
                    else:
                        non_matching_examples.append(example)
                
                return {
                    "success": True,
                    "examples": matching_examples,
                    "non_matching": non_matching_examples,
                    "error": ""
                }
            except re.error as e:
                return {
                    "success": False,
                    "examples": [],
                    "error": f"Niepoprawne wyrażenie regularne: {e}"
                }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania przykładowych ciągów: {e}")
            return {
                "success": False,
                "examples": [],
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Regex(model={self.model_name})"
