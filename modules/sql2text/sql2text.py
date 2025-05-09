#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł SQL2TEXT - Konwersja zapytań SQL na opisy tekstowe

Ten plik jest wrapperem dla nowej implementacji w sql2text_new.py,
zapewniającym kompatybilność wsteczną z istniejącym API.
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj nową implementację
from modules.sql2text.sql2text_new import SQL2Text as SQL2TextNew

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
        # Inicjalizacja nowej implementacji
        config = {
            "model": model_name,
            "output_dir": sql_dir
        }
        self.impl = SQL2TextNew(config=config)
        self.model_name = model_name
        self.sql_dir = sql_dir
        logger.info(f"Inicjalizacja SQL2Text z modelem {model_name}")
        if sql_dir:
            logger.info(f"Katalog SQL: {sql_dir}")
    
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny"""
        return self.impl.ensure_model_available()
    
    def sql_to_text(self, sql_code: str) -> Dict[str, Any]:
        """Konwertuje zapytanie SQL na opis w języku naturalnym"""
        # Wywołaj metodę process z nowej implementacji
        return self.impl.process(sql_code)
    
    def analyze_sql_query(self, sql_code: str) -> Dict[str, Any]:
        """Analizuje zapytanie SQL i zwraca jego strukturę i potencjalne problemy"""
        # Wywołaj metodę analyze_sql_query z nowej implementacji
        return self.impl.analyze_sql_query(sql_code)
    
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
