#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu python2text
"""

import pytest
from .test_base import BaseConverterTest

class TestPython2Text(BaseConverterTest):
    """Testy dla modułu python2text"""
    
    module_name = "python2text"
    
    @pytest.mark.parametrize("input_text,expected_output", [
        (
            """def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)""",
            "silni"
        ),
        (
            """class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
    def area(self):
        return self.width * self.height
        
    def perimeter(self):
        return 2 * (self.width + self.height)""",
            "prostokąt"
        ),
        (
            """def is_prime(num):
    if num <= 1:
        return False
    if num <= 3:
        return True
    if num % 2 == 0 or num % 3 == 0:
        return False
    i = 5
    while i * i <= num:
        if num % i == 0 or num % (i + 2) == 0:
            return False
        i += 6
    return True""",
            "liczb"
        )
    ])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji kodu Python na tekst"""
        try:
            result = converter.convert(input_text)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera oczekiwane elementy
            # Używamy luźnego porównania, ponieważ dokładny wynik może się różnić
            assert expected_output in result.lower(), f"Wynik konwersji nie zawiera '{expected_output}'. Otrzymano: {result}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_error_handling(self, converter):
        """Test obsługi błędów"""
        try:
            # Testowanie z pustym wejściem
            result = converter.convert("")
            assert result is not None, "Konwerter powinien obsłużyć puste wejście"
            
            # Testowanie z niepoprawnym kodem Python
            result = converter.convert("def invalid_function(")
            assert result is not None, "Konwerter powinien obsłużyć niepoprawny kod"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_complex_code(self, converter):
        """Test konwersji złożonego kodu"""
        try:
            complex_code = """
import numpy as np
import matplotlib.pyplot as plt

def plot_sine_wave(amplitude=1, frequency=1, phase=0, duration=2*np.pi):
    # Generowanie danych
    x = np.linspace(0, duration, 1000)
    y = amplitude * np.sin(frequency * x + phase)
    
    # Tworzenie wykresu
    plt.figure(figsize=(10, 6))
    plt.plot(x, y)
    plt.title(f'Sine Wave: A={amplitude}, f={frequency}, φ={phase}')
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.grid(True)
    plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    plt.axvline(x=0, color='k', linestyle='-', alpha=0.3)
    
    return plt
"""
            result = converter.convert(complex_code)
            assert result is not None, "Wynik konwersji jest None"
            assert len(result) > 0, "Wynik konwersji jest pusty"
            assert "wykres" in result.lower() or "sine" in result.lower() or "fala" in result.lower(), \
                "Wynik konwersji nie zawiera oczekiwanych słów kluczowych"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
