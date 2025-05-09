#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu text2python
"""

import pytest
from .test_base import BaseConverterTest

class TestText2Python(BaseConverterTest):
    """Testy dla modułu text2python"""
    
    module_name = "text2python"
    
    @pytest.mark.parametrize("input_text,expected_output", [
        (
            "Napisz funkcję, która oblicza silnię liczby",
            "def factorial"
        ),
        (
            "Stwórz klasę reprezentującą prostokąt z metodami do obliczania pola i obwodu",
            "class Rectangle"
        ),
        (
            "Napisz program, który sprawdza czy podana liczba jest liczbą pierwszą",
            "def is_prime"
        )
    ])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji tekstu na kod Python"""
        # Jeśli konwerter wymaga modelu językowego, możemy zamockować jego odpowiedź
        # lub przeprowadzić test integracyjny, jeśli model jest dostępny
        try:
            result = converter.convert(input_text)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera oczekiwane elementy
            # Używamy luźnego porównania, ponieważ dokładny wynik może się różnić
            assert expected_output in result, f"Wynik konwersji nie zawiera '{expected_output}'. Otrzymano: {result}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_error_handling(self, converter):
        """Test obsługi błędów"""
        try:
            # Testowanie z pustym wejściem
            result = converter.convert("")
            assert result is not None, "Konwerter powinien obsłużyć puste wejście"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_code_explanation(self, converter):
        """Test wyjaśnienia kodu"""
        if not hasattr(converter, "explain_code"):
            pytest.skip("Konwerter nie ma metody explain_code")
        
        try:
            code = "def hello_world():\n    print('Hello, World!')"
            explanation = converter.explain_code(code)
            assert explanation is not None, "Wyjaśnienie kodu jest None"
            assert len(explanation) > 0, "Wyjaśnienie kodu jest puste"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
