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
logger = logging.getLogger('text2sql')


class Text2SQL:
    """Klasa do konwersji tekstu na zapytania SQL"""
    
    def __init__(self, model_name="codellama:7b-code", sql_dir=None):
        """Inicjalizacja klasy
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
            sql_dir: Katalog z zapytaniami SQL (opcjonalny)
        """
        self.model_name = model_name
        self.sql_dir = sql_dir
        logger.info(f"Inicjalizacja Text2SQL z modelem {model_name}")
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
    
    def text_to_sql(self, prompt: str, db_schema: str = "") -> Dict[str, Any]:
        """Konwertuje opis w języku naturalnym na zapytanie SQL
        
        Args:
            prompt: Opis w języku naturalnym
            db_schema: Opcjonalny schemat bazy danych do uwzględnienia w generowaniu
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            logger.info(f"Generowanie zapytania SQL dla: {prompt}...")
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na zapytania SQL.
Twoim zadaniem jest wygenerowanie zapytania SQL, które realizuje opisane zadanie.
Generuj tylko kod SQL, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Zapewnij, że zapytanie jest poprawne składniowo i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Dodaj informacje o schemacie bazy danych, jeśli zostały podane
            if db_schema:
                system_prompt += f"\n\nPracujesz z następującym schematem bazy danych:\n{db_schema}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nUtwórz zapytanie SQL, które realizuje następujące zadanie:\n{prompt}\n\nKod SQL:"
            
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
                logger.error(f"Błąd podczas generowania kodu SQL: {stderr}")
                return {
                    "success": False,
                    "code": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij kod SQL z odpowiedzi
            code = stdout.strip()
            
            # Jeśli kod jest otoczony znacznikami ```sql i ```, usuń je
            code = re.sub(r'^```sql\n|^```\n|\n```$', '', code, flags=re.MULTILINE)
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod SQL wygenerowany pomyślnie"
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas konwersji tekstu na SQL: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def explain_sql(self, sql_code: str) -> str:
        """Generuje wyjaśnienie zapytania SQL w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.model_name} nie jest dostępny."
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu zapytań SQL. Twoim zadaniem jest wyjaśnienie działania podanego kodu SQL w prosty i zrozumiały sposób. Wyjaśnienie powinno być szczegółowe, ale zrozumiałe dla osoby bez głębokiej znajomości SQL.'
            
            prompt = f"Wyjaśnij działanie następującego zapytania SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Generowanie wyjaśnienia zapytania SQL...")
            
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
    
    def optimize_sql(self, sql_code: str) -> Dict[str, Any]:
        """Optymalizuje zapytanie SQL"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "optimized_code": "",
                    "explanation": f"Model {self.model_name} nie jest dostępny",
                    "error": "Problem z modelem"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w optymalizacji zapytań SQL.
Twoim zadaniem jest przeanalizowanie podanego zapytania SQL i zaproponowanie zoptymalizowanej wersji.
Zwróć zoptymalizowane zapytanie oraz wyjaśnienie wprowadzonych zmian i korzyści z optymalizacji.
Skup się na poprawie wydajności, czytelności i zgodności z najlepszymi praktykami SQL."""
            
            prompt = f"Zoptymalizuj następujące zapytanie SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            logger.info("Optymalizacja zapytania SQL...")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas optymalizacji zapytania: {stderr}")
                return {
                    "success": False,
                    "optimized_code": "",
                    "explanation": "",
                    "error": stderr
                }
            
            response = stdout.strip()
            
            # Próba wyodrębnienia zoptymalizowanego kodu SQL
            sql_pattern = re.compile(r'```sql\n(.*?)\n```', re.DOTALL)
            match = sql_pattern.search(response)
            
            if match:
                optimized_code = match.group(1).strip()
                # Usuń blok kodu z odpowiedzi, aby pozostało samo wyjaśnienie
                explanation = re.sub(r'```sql\n.*?\n```', '', response, flags=re.DOTALL).strip()
            else:
                # Jeśli nie znaleziono bloku kodu, spróbuj znaleźć ogólny blok kodu
                code_pattern = re.compile(r'```\n(.*?)\n```', re.DOTALL)
                match = code_pattern.search(response)
                if match:
                    optimized_code = match.group(1).strip()
                    explanation = re.sub(r'```\n.*?\n```', '', response, flags=re.DOTALL).strip()
                else:
                    # Jeśli nadal nie znaleziono, przyjmij całą odpowiedź jako kod
                    optimized_code = response
                    explanation = "Brak szczegółowego wyjaśnienia optymalizacji."
            
            return {
                "success": True,
                "optimized_code": optimized_code,
                "explanation": explanation,
                "error": ""
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas optymalizacji zapytania SQL: {e}")
            return {
                "success": False,
                "optimized_code": "",
                "explanation": "",
                "error": str(e)
            }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2SQL(model={self.model_name})"
