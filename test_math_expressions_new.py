#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test generowania kodu dla prostych wyrażeń matematycznych
"""

import os
import sys
import logging
from pathlib import Path

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test-math-expressions')

# Dodaj główny katalog projektu do ścieżki importów
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Importuj potrzebne moduły
from modules.text2python.components.code_generator import CodeGenerator

def test_simple_math_expressions():
    """Test generowania kodu dla prostych wyrażeń matematycznych"""
    print("\n=== Test generowania kodu dla prostych wyrażeń matematycznych ===")
    
    # Inicjalizuj generator kodu
    code_generator = CodeGenerator()
    
    # Lista testowych wyrażeń
    test_expressions = [
        "2+2",
        "5-3",
        "4*6",
        "10/2",
        "x+y",
        "a*b",
        "oblicz 2+2",
        "ile to 5-3"
    ]
    
    for expr in test_expressions:
        print(f"\nTestowanie wyrażenia: '{expr}'")
        
        # Generuj kod
        result = code_generator.generate_code(expr)
        
        if not result.get("success", False):
            print(f"BŁĄD: Generowanie kodu nie powiodło się: {result.get('error', 'Nieznany błąd')}")
            continue
        
        # Pobierz wygenerowany kod
        code = result.get("code", "")
        
        if not code:
            print("BŁĄD: Brak wygenerowanego kodu")
            continue
        
        print(f"Wygenerowany kod:\n{code}")
        
        # Sprawdź, czy kod zawiera funkcję execute z parametrami
        if "def execute(" not in code:
            print("BŁĄD: Kod nie zawiera funkcji execute")
            continue
        
        # Sprawdź, czy funkcja execute ma parametry
        if "def execute()" in code:
            print("BŁĄD: Funkcja execute nie ma parametrów")
            continue
        
        print("✓ Kod zawiera funkcję execute z parametrami")

def main():
    """Główna funkcja testowa"""
    print("=== Test generowania kodu dla prostych wyrażeń matematycznych ===")
    
    # Uruchom testy
    test_simple_math_expressions()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
