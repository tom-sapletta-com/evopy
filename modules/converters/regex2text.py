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
logger = logging.getLogger('regex2text')


class Regex2Text:
    """Klasa do konwersji wyrażeń regularnych na opis tekstowy"""
    
    def __init__(self, model_name="codellama:7b-code", regex_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            regex_dir: Katalog z wyrażeniami regularnymi (opcjonalny)
        """
        self.model_name = model_name
        self.regex_dir = regex_dir
        logger.info(f"Inicjalizacja Regex2Text z modelem {model_name}")
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
    
    def regex_to_text(self, regex: str, flavor: str = "python") -> Dict[str, Any]:
        """Konwertuje wyrażenie regularne na opis w języku naturalnym
        
        Args:
            regex: Wyrażenie regularne
            flavor: Dialekt wyrażeń regularnych (python, pcre, javascript, itp.)
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "description": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie opisu dla wyrażenia regularnego: {regex}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = f"""Jesteś ekspertem w wyjaśnianiu wyrażeń regularnych.
Twoim zadaniem jest wygenerowanie dokładnego opisu w języku naturalnym, który wyjaśnia co robi podane wyrażenie regularne.
Wyrażenie regularne jest w dialekcie {flavor}.
Opis powinien być szczegółowy, ale zrozumiały dla osoby nieznającej szczegółów technicznych wyrażeń regularnych.
Wyjaśnij, jakie wzorce pasują do tego wyrażenia regularnego i podaj przykłady pasujących ciągów."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nWyjaśnij, co robi następujące wyrażenie regularne:\n{regex}"
            
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
            logger.error(f"Błąd podczas konwersji wyrażenia regularnego na tekst: {e}")
            return {
                "success": False,
                "description": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def analyze_regex(self, regex: str) -> Dict[str, Any]:
        """Analizuje wyrażenie regularne i zwraca jego strukturę i potencjalne problemy"""
        try:
            # Sprawdź, czy wyrażenie regularne jest poprawne składniowo
            try:
                re.compile(regex)
                valid = True
                syntax_error = ""
            except re.error as e:
                valid = False
                syntax_error = str(e)
                logger.warning(f"Niepoprawne wyrażenie regularne: {e}")
            
            # Jeśli wyrażenie jest niepoprawne, zwróć tylko informację o błędzie
            if not valid:
                return {
                    "success": False,
                    "valid": False,
                    "error": syntax_error,
                    "analysis": f"Wyrażenie regularne jest niepoprawne składniowo: {syntax_error}"
                }
            
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "valid": True,
                    "analysis": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w analizie wyrażeń regularnych.
Twoim zadaniem jest przeanalizowanie podanego wyrażenia regularnego i zwrócenie:
1. Szczegółowej analizy każdej części wyrażenia
2. Potencjalnych problemów wydajnościowych
3. Potencjalnych pułapek lub nieoczekiwanych zachowań
4. Sugestii optymalizacji

Odpowiedź powinna być szczegółowa i techniczna."""
            
            prompt = f"Przeanalizuj następujące wyrażenie regularne:\n\n{regex}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Analizowanie wyrażenia regularnego...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas analizy wyrażenia: {stderr}")
                return {
                    "success": False,
                    "valid": True,
                    "analysis": "",
                    "error": stderr
                }
            
            return {
                "success": True,
                "valid": True,
                "analysis": stdout.strip(),
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas analizy wyrażenia regularnego: {e}")
            return {
                "success": False,
                "valid": False,
                "analysis": "",
                "error": str(e)
            }
    
    def simplify_regex(self, regex: str) -> Dict[str, Any]:
        """Upraszcza złożone wyrażenie regularne"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "simplified_regex": "",
                    "explanation": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w optymalizacji wyrażeń regularnych.
Twoim zadaniem jest przeanalizowanie podanego wyrażenia regularnego i zaproponowanie uproszczonej wersji.
Zwróć uproszczone wyrażenie regularne oraz wyjaśnienie wprowadzonych zmian.
Uproszczone wyrażenie powinno być równoważne funkcjonalnie, ale bardziej czytelne i/lub wydajniejsze."""
            
            prompt = f"Uprość następujące wyrażenie regularne:\n\n{regex}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Upraszczanie wyrażenia regularnego...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas upraszczania wyrażenia: {stderr}")
                return {
                    "success": False,
                    "simplified_regex": "",
                    "explanation": "",
                    "error": stderr
                }
            
            response = stdout.strip()
            
            # Próba wyodrębnienia uproszczonego wyrażenia regularnego
            # Szukamy wzorca, który wygląda jak wyrażenie regularne
            regex_pattern = re.compile(r'`([^`]+)`|"([^"]+)"|\'([^\']+)\'|^([^\n]+)$', re.MULTILINE)
            matches = regex_pattern.findall(response)
            
            simplified_regex = ""
            for match in matches:
                # Wybierz pierwszą niepustą grupę
                for group in match:
                    if group and re.search(r'[\\[\](){}.*+?|^$]', group):
                        simplified_regex = group
                        break
                if simplified_regex:
                    break
            
            # Jeśli nie znaleziono wyrażenia, użyj pierwszej linii odpowiedzi
            if not simplified_regex:
                simplified_regex = response.split('\n')[0].strip()
            
            # Usuń uproszczone wyrażenie z odpowiedzi, aby pozostało samo wyjaśnienie
            explanation = re.sub(re.escape(simplified_regex), '', response, flags=re.IGNORECASE).strip()
            
            # Sprawdź, czy uproszczone wyrażenie jest poprawne składniowo
            try:
                re.compile(simplified_regex)
                valid = True
            except re.error:
                valid = False
                
            return {
                "success": True,
                "simplified_regex": simplified_regex,
                "explanation": explanation,
                "valid": valid,
                "error": "" if valid else "Uproszczone wyrażenie jest niepoprawne składniowo"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas upraszczania wyrażenia regularnego: {e}")
            return {
                "success": False,
                "simplified_regex": "",
                "explanation": "",
                "valid": False,
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Regex2Text(model={self.model_name})"
