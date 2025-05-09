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
logger = logging.getLogger('sql2text')


class SQL2Text:
    """Klasa do konwersji zapytań SQL na opis tekstowy"""
    
    def __init__(self, model_name="codellama:7b-code", sql_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            sql_dir: Katalog z zapytaniami SQL (opcjonalny)
        """
        self.model_name = model_name
        self.sql_dir = sql_dir
        logger.info(f"Inicjalizacja SQL2Text z modelem {model_name}")
        if sql_dir:
            logger.info(f"Katalog SQL: {sql_dir}")
        
    
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
    
    def sql_to_text(self, sql_code: str) -> Dict[str, Any]:
        """Konwertuje zapytanie SQL na opis w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "description": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie opisu dla zapytania SQL...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w wyjaśnianiu zapytań SQL.
Twoim zadaniem jest wygenerowanie dokładnego opisu w języku naturalnym, który wyjaśnia co robi podane zapytanie SQL.
Opis powinien być szczegółowy, ale zrozumiały dla osoby nieznającej szczegółów technicznych SQL.
Wyjaśnij cel zapytania, jakie dane pobiera lub modyfikuje, oraz jakie operacje wykonuje na tych danych."""
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nWyjaśnij, co robi następujące zapytanie SQL:\n```sql\n{sql_code}\n```"
            
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
            logger.error(f"Błąd podczas konwersji SQL na tekst: {e}")
            return {
                "success": False,
                "description": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def analyze_sql_query(self, sql_code: str) -> Dict[str, Any]:
        """Analizuje zapytanie SQL i zwraca jego strukturę i potencjalne problemy"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "analysis": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w analizie zapytań SQL.
Twoim zadaniem jest przeanalizowanie podanego zapytania SQL i zwrócenie:
1. Struktury zapytania (główne klauzule, tabele, warunki)
2. Potencjalnych problemów wydajnościowych
3. Sugestii optymalizacji
4. Oceny złożoności zapytania

Odpowiedź powinna być szczegółowa i techniczna."""
            
            prompt = f"Przeanalizuj następujące zapytanie SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Analizowanie zapytania SQL...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas analizy zapytania: {stderr}")
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
            logger.error(f"Błąd podczas analizy zapytania SQL: {e}")
            return {
                "success": False,
                "analysis": "",
                "error": str(e)
            }
    
    def generate_example_data(self, sql_code: str) -> Dict[str, Any]:
        """Generuje przykładowe dane, które pasują do zapytania SQL"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "example_data": "",
                    "error": f"Model {self.model_name} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w SQL i generowaniu danych testowych.
Twoim zadaniem jest przeanalizowanie podanego zapytania SQL i wygenerowanie:
1. Przykładowej struktury tabel, których dotyczy zapytanie (CREATE TABLE)
2. Przykładowych danych, które można umieścić w tych tabelach (INSERT INTO)
3. Przykładowy wynik zapytania na tych danych

Dane powinny być realistyczne i pasować do kontekstu zapytania."""
            
            prompt = f"Wygeneruj przykładowe dane dla następującego zapytania SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie przykładowych danych dla zapytania SQL...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania przykładowych danych: {stderr}")
                return {
                    "success": False,
                    "example_data": "",
                    "error": stderr
                }
            
            return {
                "success": True,
                "example_data": stdout.strip(),
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania przykładowych danych: {e}")
            return {
                "success": False,
                "example_data": "",
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"SQL2Text(model={self.model_name})"
