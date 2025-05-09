#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Rozszerzenie matematyczne dla modułu text2python.
Obsługuje podstawowe operacje matematyczne, geometryczne i równania.
"""

from .geometry import identify_query as identify_geometry_query
from .geometry import generate_code as generate_geometry_code

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
    
    # Tutaj można dodać więcej sprawdzeń dla innych kategorii matematycznych
    
    return False

def generate_code(query: str) -> dict:
    """
    Generuje kod Python dla zapytania matematycznego
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        dict: Wygenerowany kod i metadane
    """
    # Sprawdź czy zapytanie dotyczy geometrii
    if identify_geometry_query(query):
        return generate_geometry_code(query)
    
    # Domyślna odpowiedź, jeśli nie znaleziono pasującego generatora
    return {
        "success": False,
        "code": "",
        "error": "Nie znaleziono odpowiedniego generatora kodu dla tego zapytania matematycznego"
    }
