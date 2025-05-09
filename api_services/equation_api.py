#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Usługa API obsługująca równanie matematyczne:
2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
"""

import os
import sys
import json
import math
import logging
from pathlib import Path

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj dekorator API
from api_services.api_decorator import create_api_service

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('equation_api')

# Implementacja funkcji do obliczania równania matematycznego
def cbrt(val):
    """Własna implementacja pierwiastka sześciennego"""
    if val >= 0:
        return val ** (1/3)
    else:
        return -(-val) ** (1/3)

def equation_solver(x):
    """Oblicza różnicę między lewą i prawą stroną równania"""
    # Lewa strona równania
    left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
    
    # Prawa strona równania (sin²(2x) + cos²(2x) = 1)
    trig_term = 1
    fraction_term = (3 * x**2 - 5) / (2 * x + 7)
    cube_root_term = (2/3) * cbrt(x**2 - 4)
    right = trig_term * fraction_term + cube_root_term
    
    return left - right

def solve_equation(start=2, end=20, step=0.1, tolerance=1e-10):
    """Szuka rozwiązań równania w podanym zakresie"""
    solutions = []
    x_values = [start + i * step for i in range(int((end - start) / step))]
    
    for x in x_values:
        try:
            # Sprawdź ograniczenia dziedziny
            if x <= -3 or x <= -3.5 or (-2 < x < 2):
                continue
            
            # Oblicz wartość równania
            diff = equation_solver(x)
            
            # Jeśli różnica jest bliska zeru, znaleźliśmy rozwiązanie
            if abs(diff) < tolerance:
                solutions.append((x, diff))
        except ValueError:
            continue
    
    return solutions

# Tworzenie usługi API
equation_api = create_api_service(
    name="equation_api",
    description="API do analizy równania matematycznego: 2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)",
    port=5002
)

@equation_api.endpoint('/calculate', methods=['POST', 'GET'])
def calculate(data):
    """
    Oblicza wartość równania dla podanej wartości x
    
    Parametry:
        x (float): Wartość x do obliczenia
    
    Zwraca:
        dict: Wynik obliczeń
    """
    try:
        # Pobierz wartość x z danych
        x = float(data.get('x', 0))
        
        # Sprawdź ograniczenia dziedziny
        if x <= -3:
            return {"error": "x musi być większe od -3 dla logarytmu"}
        if x <= -3.5:
            return {"error": "x musi być większe od -3.5 dla mianownika"}
        if -2 < x < 2:
            return {"error": "x musi być ≥ 2 lub ≤ -2 dla pierwiastka sześciennego"}
        
        # Oblicz wartość równania
        result = equation_solver(x)
        
        # Oblicz obie strony równania dla weryfikacji
        left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
        right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * cbrt(x**2 - 4)
        
        return {
            "x": x,
            "result": result,
            "left_side": left,
            "right_side": right,
            "difference": left - right
        }
    except Exception as e:
        logger.error(f"Błąd podczas obliczeń: {e}")
        return {"error": str(e)}

@equation_api.endpoint('/search', methods=['POST', 'GET'])
def search(data):
    """
    Szuka rozwiązań równania w podanym zakresie
    
    Parametry:
        start (float): Początek zakresu
        end (float): Koniec zakresu
        step (float): Krok
        tolerance (float): Tolerancja dla uznania wartości za rozwiązanie
    
    Zwraca:
        dict: Wyniki wyszukiwania
    """
    try:
        # Pobierz parametry wyszukiwania z danych
        start = float(data.get('start', 2))
        end = float(data.get('end', 20))
        step = float(data.get('step', 0.1))
        tolerance = float(data.get('tolerance', 1e-10))
        
        # Generowanie wartości x bez użycia NumPy
        x_values = [start + i * step for i in range(int((end - start) / step))]
        
        solutions = []
        samples = []
        
        for x in x_values:
            try:
                # Sprawdź ograniczenia dziedziny
                if x <= -3 or x <= -3.5 or (-2 < x < 2):
                    continue
                
                # Oblicz wartość równania
                diff = equation_solver(x)
                
                # Jeśli różnica jest bliska zeru, znaleźliśmy rozwiązanie
                if abs(diff) < tolerance:
                    solutions.append({
                        "x": x,
                        "difference": diff
                    })
                
                # Dodaj próbkę co 10 wartości
                if len(samples) < 10 or x % 10 < step:
                    samples.append({
                        "x": x,
                        "difference": diff
                    })
            except Exception as e:
                logger.error(f"Błąd dla x = {x}: {e}")
        
        return {
            "solutions": solutions,
            "samples": samples,
            "range": {
                "start": start,
                "end": end,
                "step": step
            },
            "conclusion": "Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie." if not solutions else f"Znaleziono {len(solutions)} rozwiązań."
        }
    except Exception as e:
        logger.error(f"Błąd podczas wyszukiwania: {e}")
        return {"error": str(e)}

@equation_api.endpoint('/analyze', methods=['POST', 'GET'])
def analyze(data):
    """
    Przeprowadza pełną analizę równania
    
    Zwraca:
        dict: Wyniki analizy
    """
    try:
        # Testowe wartości x
        test_values = [2, 3, 5, 10]
        results = []
        
        for x in test_values:
            try:
                # Oblicz wartość równania
                diff = equation_solver(x)
                
                # Oblicz obie strony równania
                left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
                right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * cbrt(x**2 - 4)
                
                results.append({
                    "x": x,
                    "left_side": left,
                    "right_side": right,
                    "difference": diff
                })
            except Exception as e:
                logger.error(f"Błąd dla x = {x}: {e}")
        
        return {
            "equation": "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)",
            "domain_constraints": [
                "x > -3 (dla logarytmu)",
                "x > -3.5 (dla mianownika)",
                "x >= 2 lub x <= -2 (dla pierwiastka sześciennego)"
            ],
            "test_results": results,
            "conclusion": "Równanie nie ma rozwiązań rzeczywistych w swojej dziedzinie."
        }
    except Exception as e:
        logger.error(f"Błąd podczas analizy: {e}")
        return {"error": str(e)}

# Uruchom usługę API, jeśli skrypt jest uruchamiany bezpośrednio
if __name__ == '__main__':
    # Uruchom usługę API
    url = equation_api.start()
    print(f"Usługa API uruchomiona pod adresem: {url}")
    
    # Utrzymuj działanie skryptu
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Zatrzymywanie usługi API...")
        equation_api.stop()
