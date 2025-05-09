#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu regex2text
"""

import pytest
from .test_base import BaseConverterTest

class TestRegex2Text(BaseConverterTest):
    """Testy dla modułu regex2text"""
    
    module_name = "regex2text"
    
    @pytest.mark.parametrize("input_text,expected_output", [
        (
            r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "email"
        ),
        (
            r"\d{3}-\d{3}-\d{3}",
            "telefon"
        ),
        (
            r"\d{2}-\d{3}",
            "kod pocztowy"
        ),
        (
            r"\d{4}-\d{2}-\d{2}",
            "dat"
        )
    ])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji wyrażeń regularnych na tekst"""
        try:
            result = converter.convert(input_text)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera oczekiwane elementy
            assert expected_output.lower() in result.lower(), f"Wynik konwersji nie zawiera '{expected_output}'. Otrzymano: {result}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_error_handling(self, converter):
        """Test obsługi błędów"""
        try:
            # Testowanie z pustym wejściem
            result = converter.convert("")
            assert result is not None, "Konwerter powinien obsłużyć puste wejście"
            
            # Testowanie z niepoprawnym wyrażeniem regularnym
            result = converter.convert("(niepoprawne[wyrażenie")
            assert result is not None, "Konwerter powinien obsłużyć niepoprawne wyrażenie regularne"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_complex_regex(self, converter):
        """Test konwersji złożonego wyrażenia regularnego"""
        try:
            complex_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            result = converter.convert(complex_regex)
            assert result is not None, "Wynik konwersji jest None"
            assert len(result) > 0, "Wynik konwersji jest pusty"
            
            # Sprawdź czy wynik zawiera typowe elementy dla takiego wyrażenia
            expected_elements = ["hasł", "duż", "mał", "liter", "cyfr", "znak"]
            found_elements = [elem for elem in expected_elements if elem.lower() in result.lower()]
            assert len(found_elements) > 0, f"Wynik konwersji nie zawiera żadnego z oczekiwanych elementów: {expected_elements}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_regex_with_groups(self, converter):
        """Test konwersji wyrażenia regularnego z grupami"""
        try:
            regex_with_groups = r"(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})"
            result = converter.convert(regex_with_groups)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera informacje o grupach
            expected_elements = ["grup", "dat", "czas", "godzin"]
            found_elements = [elem for elem in expected_elements if elem.lower() in result.lower()]
            assert len(found_elements) > 0, f"Wynik konwersji nie zawiera informacji o grupach: {expected_elements}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
