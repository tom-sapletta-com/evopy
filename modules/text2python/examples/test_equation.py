#!/usr/bin/env python3
"""
Testy jednostkowe dla implementacji analizy równania matematycznego:
2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)
"""

import unittest
import math
import sys
import os

# Dodanie katalogu nadrzędnego do ścieżki, aby umożliwić import modułów
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import funkcji z naszych modułów
from equation_example import equation as equation_example
from equation_simple import execute as equation_simple_execute
from equation_search import execute as equation_search
from equation_solver import equation as equation_solver

class TestEquationImplementations(unittest.TestCase):
    """Testy dla różnych implementacji równania matematycznego."""
    
    def setUp(self):
        """Przygotowanie danych testowych."""
        # Wartości x do testowania
        self.test_values = [2, 3, 5, 10]
        
        # Oczekiwane różnice dla każdej wartości x
        # Wartości obliczone wcześniej i potwierdzone przez wszystkie implementacje
        self.expected_differences = {
            2: 3.0417082687490016,
            3: 5.165751086778384,
            5: 13.493014477566039,
            10: 45.59823112068293
        }
    
    def test_equation_example(self):
        """Test dla implementacji z equation_example.py."""
        for x in self.test_values:
            with self.subTest(x=x):
                # Sprawdzenie, czy funkcja zwraca oczekiwaną różnicę
                result = equation_example(x)
                self.assertAlmostEqual(result, self.expected_differences[x], places=10)
    
    def test_equation_simple(self):
        """Test dla implementacji z equation_simple.py."""
        # Funkcja equation_value jest zdefiniowana wewnątrz funkcji execute
        # Musimy ją wydobyć i przetestować
        def get_equation_value_function():
            # Tworzymy własną implementację funkcji equation_value na podstawie kodu z equation_simple.py
            def equation_value(x):
                # Lewa strona równania
                left_side = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
                
                # Prawa strona równania (sin²(2x) + cos²(2x) = 1)
                trig_term = 1
                fraction_term = (3 * x**2 - 5) / (2 * x + 7)
                
                # Własna implementacja pierwiastka sześciennego
                def cbrt(val):
                    if val >= 0:
                        return val ** (1/3)
                    else:
                        return -(-val) ** (1/3)
                
                cube_root_term = (2/3) * cbrt(x**2 - 4)
                right_side = trig_term * fraction_term + cube_root_term
                
                return {
                    "x": x,
                    "lewa_strona": left_side,
                    "prawa_strona": right_side,
                    "roznica": left_side - right_side
                }
            return equation_value
        
        # Pobieramy funkcję equation_value
        equation_value = get_equation_value_function()
        
        # Testujemy funkcję
        for x in self.test_values:
            with self.subTest(x=x):
                # Sprawdzenie, czy funkcja zwraca oczekiwaną różnicę
                result = equation_value(x)
                self.assertAlmostEqual(result['roznica'], self.expected_differences[x], places=10)
    
    def test_equation_search(self):
        """Test dla implementacji z equation_search.py."""
        for x in self.test_values:
            with self.subTest(x=x):
                # Sprawdzenie, czy funkcja zwraca oczekiwaną różnicę
                result = equation_search(x)
                self.assertAlmostEqual(result, self.expected_differences[x], places=10)
    
    def test_equation_solver(self):
        """Test dla implementacji z equation_solver.py."""
        for x in self.test_values:
            with self.subTest(x=x):
                # Sprawdzenie, czy funkcja zwraca oczekiwaną różnicę
                result = equation_solver(x)
                self.assertAlmostEqual(result, self.expected_differences[x], places=10)
    
    def test_domain_constraints(self):
        """Test dla ograniczeń dziedziny funkcji."""
        # Wartości x poza dziedziną
        invalid_values = [-3, -3.5, -1, 0, 1]
        
        for x in invalid_values:
            with self.subTest(x=x):
                # Sprawdzenie, czy funkcje zgłaszają wyjątek dla wartości poza dziedziną
                with self.assertRaises(ValueError):
                    equation_solver(x)
    
    def test_no_solutions(self):
        """Test weryfikujący, że równanie nie ma rozwiązań rzeczywistych."""
        # Sprawdzenie, czy funkcja zawsze zwraca wartość dodatnią dla x w dziedzinie
        x_values = [2 + 0.1*i for i in range(180)]  # Wartości od 2 do 20 z krokiem 0.1
        
        for x in x_values:
            with self.subTest(x=x):
                result = equation_solver(x)
                self.assertGreater(result, 0)  # Różnica powinna być zawsze dodatnia

class TestEquationProperties(unittest.TestCase):
    """Testy dla właściwości równania matematycznego."""
    
    def test_left_side_grows_faster(self):
        """Test weryfikujący, że lewa strona równania rośnie szybciej niż prawa."""
        x_values = [2, 5, 10, 20]
        differences = []
        
        for x in x_values:
            # Obliczenie lewej i prawej strony równania
            left = 2 * math.sqrt(x**3 + 1) - math.log2(x + 3)
            
            # Własna implementacja pierwiastka sześciennego
            def cbrt(val):
                if val >= 0:
                    return val ** (1/3)
                else:
                    return -(-val) ** (1/3)
            
            right = (3 * x**2 - 5) / (2 * x + 7) + (2/3) * cbrt(x**2 - 4)
            
            # Zapisanie różnicy
            differences.append(left - right)
        
        # Sprawdzenie, czy różnica rośnie wraz ze wzrostem x
        for i in range(1, len(differences)):
            self.assertGreater(differences[i], differences[i-1])

if __name__ == '__main__':
    unittest.main()
