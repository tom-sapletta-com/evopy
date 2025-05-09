#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł TEXT2SQL - Konwersja tekstu na zapytania SQL

Ten plik jest wrapperem dla nowej implementacji w text2sql_new.py,
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
from modules.text2sql.text2sql_new import Text2SQL as Text2SQLNew

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
        # Inicjalizacja nowej implementacji
        config = {
            "model": model_name,
            "sql_dir": sql_dir
        }
        self.impl = Text2SQLNew(config=config)
        self.model_name = model_name
        self.sql_dir = sql_dir
        logger.info(f"Inicjalizacja Text2SQL z modelem {model_name}")
        if sql_dir:
            logger.info(f"Katalog SQL: {sql_dir}")
    
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny"""
        return self.impl.ensure_model_available()
    
    def text_to_sql(self, prompt: str, db_schema: str = "") -> Dict[str, Any]:
        """Konwertuje opis w języku naturalnym na zapytanie SQL
        
        Args:
            prompt: Opis w języku naturalnym
            db_schema: Opcjonalny schemat bazy danych do uwzględnienia w generowaniu
        """
        result = self.impl.process(prompt, db_schema=db_schema)
        return result
    
    def explain_sql(self, sql_code: str) -> str:
        """Generuje wyjaśnienie zapytania SQL w języku naturalnym"""
        # Wywołaj metodę explain_sql z nowej implementacji
        result = self.impl.explain_sql(sql_code)
        
        # Zachowaj kompatybilność wsteczną - stara metoda zwracała string, nowa zwraca słownik
        if isinstance(result, dict):
            if result.get("success", False):
                return result.get("explanation", "")
            else:
                return f"Błąd podczas generowania wyjaśnienia: {result.get('error', 'Nieznany błąd')}"
        
        return result
    
    def optimize_sql(self, sql_code: str) -> Dict[str, Any]:
        """Optymalizuje zapytanie SQL"""
        # Wywołaj metodę optimize_sql z nowej implementacji
        return self.impl.optimize_sql(sql_code)

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2SQL(model={self.model_name})"
