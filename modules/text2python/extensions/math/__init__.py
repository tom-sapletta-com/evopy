#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rozszerzenie matematyczne dla modułu text2python.
Obsługuje podstawowe operacje matematyczne, geometryczne i równania.
"""

import re
from typing import Dict, Any, List, Optional, Union

# Importuj funkcje z modułu geometrii
from .geometry import identify_query as identify_geometry_query
from .geometry import generate_code as generate_geometry_code

# Słowa kluczowe dla zapytań matematycznych
MATH_KEYWORDS = [
    'matematyka', 'oblicz', 'policz', 'wylicz', 'suma', 'różnica', 'iloczyn', 'iloraz',
    'dodawanie', 'odejmowanie', 'mnożenie', 'dzielenie', 'potęga', 'pierwiastek',
    'logarytm', 'sinus', 'cosinus', 'tangens', 'cotangens', 'funkcja', 'równanie',
    'układ równań', 'nierówność', 'całka', 'pochodna', 'granica', 'ciąg', 'szereg',
    'macierz', 'wektor', 'liczba', 'procent', 'statystyka', 'prawdopodobieństwo',
    'kombinatoryka', 'permutacja', 'kombinacja', 'silnia', 'NWD', 'NWW'
]

# Wzorce regularne dla prostych operacji arytmetycznych
ARITHMETIC_PATTERN = re.compile(r'^\s*(\d+(?:\.\d+)?\s*[+\-*/]\s*\d+(?:\.\d+)?)\s*$')

def identify_query(query: str) -> bool:
    """
    Sprawdza, czy zapytanie dotyczy matematyki
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        bool: True jeśli zapytanie dotyczy matematyki, False w przeciwnym przypadku
    """
    # Sprawdź czy zapytanie dotyczy geometrii
    if identify_geometry_query(query):
        return True
    
    # Sprawdź czy zapytanie zawiera słowa kluczowe matematyczne
    if any(keyword in query.lower() for keyword in MATH_KEYWORDS):
        return True
    
    # Sprawdź czy zapytanie jest prostym działaniem arytmetycznym
    if ARITHMETIC_PATTERN.match(query):
        return True
    
    return False

def generate_code(query: str) -> Dict[str, Any]:
    """
    Generuje kod Python dla zapytania matematycznego
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    # Sprawdź czy zapytanie dotyczy geometrii
    if identify_geometry_query(query):
        return generate_geometry_code(query)
    
    # Sprawdź czy zapytanie jest prostym działaniem arytmetycznym
    arithmetic_match = ARITHMETIC_PATTERN.match(query)
    if arithmetic_match:
        expression = arithmetic_match.group(1)
        code = f"def execute():\n    return {expression}"
        return {
            "success": True,
            "code": code,
            "explanation": f"Ten kod oblicza wynik działania arytmetycznego: {expression}",
            "analysis": "Kod jest poprawny i zgodny z intencją."
        }
    
    # Domyślna odpowiedź, jeśli nie znaleziono pasującego generatora
    return {
        "success": False,
        "code": "",
        "error": "Nie znaleziono odpowiedniego generatora kodu dla tego zapytania matematycznego"
    }

# Upewnij się, że funkcje są dostępne na poziomie modułu
__all__ = ['identify_query', 'generate_code']
