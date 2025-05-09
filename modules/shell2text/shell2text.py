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
logger = logging.getLogger('shell2text')


class Shell2Text:
    """Klasa do konwersji poleceń powłoki (shell) na opis tekstowy"""
    
    def __init__(self, model_name="codellama:7b-code", shell_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            shell_dir: Katalog z skryptami shell (opcjonalny)
        """
        self.model_name = model_name
        self.shell_dir = shell_dir
        logger.info(f"Inicjalizacja Shell2Text z modelem {model_name}")
        if shell_dir:
            logger.info(f"Katalog skryptów: {shell_dir}")
        
    
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
    
    def shell_to_text(self, shell_code: str) -> Dict[str, Any]:
        """Konwertuje polecenia shell na opis w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "description": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie opisu dla kodu shell...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w wyjaśnianiu poleceń shell.
Twoim zadaniem jest wygenerowanie dokładnego opisu w języku naturalnym, który wyjaśnia co robi podany skrypt shell.
Opis powinien być szczegółowy, ale zrozumiały dla osoby nieznającej szczegółów technicznych.
Wyjaśnij cel skryptu, jego działanie krok po kroku oraz potencjalne zastosowania."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nWyjaśnij, co robi następujący skrypt shell:\n```bash\n{shell_code}\n```"
            
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
            logger.error(f"Błąd podczas konwersji poleceń shell na tekst: {e}")
            return {
                "success": False,
                "description": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def analyze_shell_script(self, shell_code: str) -> Dict[str, Any]:
        """Analizuje skrypt shell i zwraca jego strukturę i potencjalne problemy"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "analysis": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w analizie skryptów shell.
Twoim zadaniem jest przeanalizowanie podanego skryptu shell i zwrócenie:
1. Struktury skryptu (główne sekcje, funkcje)
2. Potencjalnych problemów lub błędów
3. Sugestii optymalizacji lub poprawy
4. Oceny bezpieczeństwa (potencjalne luki)

Odpowiedź powinna być szczegółowa i techniczna."""
            
            prompt = f"Przeanalizuj następujący skrypt shell:\n\n```bash\n{shell_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Analizowanie skryptu shell...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas analizy skryptu: {stderr}")
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
            logger.error(f"Błąd podczas analizy skryptu shell: {e}")
            return {
                "success": False,
                "analysis": "",
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Shell2Text(model={self.model_name})"
