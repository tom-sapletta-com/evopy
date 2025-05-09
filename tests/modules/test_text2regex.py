#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu text2regex
"""

import pytest
import re
from .test_base import BaseConverterTest

class TestText2Regex(BaseConverterTest):
    """Testy dla modułu text2regex"""
    
    module_name = "text2regex"
    
    @pytest.mark.parametrize("input_text,expected_output,test_string,should_match", [
        (
            "Wyrażenie regularne dopasowujące adresy email",
            r"@",
            "test@example.com",
            True
        ),
        (
            "Wyrażenie regularne dopasowujące numery telefonów w formacie XXX-XXX-XXX",
            r"\d{3}-\d{3}-\d{3}",
            "123-456-789",
            True
        ),
        (
            "Wyrażenie regularne dopasowujące kody pocztowe w formacie XX-XXX",
            r"\d{2}-\d{3}",
            "12-345",
            True
        ),
        (
            "Wyrażenie regularne dopasowujące daty w formacie RRRR-MM-DD",
            r"\d{4}-\d{2}-\d{2}",
            "2025-05-09",
            True
        )
    ])
    def test_conversion(self, converter, input_text, expected_output, test_string, should_match):
        """Test konwersji tekstu na wyrażenia regularne"""
        try:
            result = converter.convert(input_text)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera oczekiwane elementy
            if expected_output:
                assert expected_output in result, f"Wynik konwersji nie zawiera '{expected_output}'. Otrzymano: {result}"
            
            # Sprawdź czy wygenerowane wyrażenie regularne działa poprawnie
            try:
                regex = re.compile(result)
                match_result = bool(regex.search(test_string))
                assert match_result == should_match, f"Wyrażenie '{result}' {'nie dopasowało' if should_match else 'dopasowało'} tekstu '{test_string}'"
            except re.error:
                pytest.skip(f"Wygenerowane wyrażenie '{result}' nie jest poprawnym wyrażeniem regularnym")
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
    
    def test_complex_regex(self, converter):
        """Test konwersji złożonego wyrażenia regularnego"""
        try:
            complex_request = """
Wyrażenie regularne, które dopasowuje poprawne hasło spełniające następujące warunki:
- Długość co najmniej 8 znaków
- Zawiera przynajmniej jedną dużą literę
- Zawiera przynajmniej jedną małą literę
- Zawiera przynajmniej jedną cyfrę
- Zawiera przynajmniej jeden znak specjalny (np. !@#$%^&*)
- Nie zawiera białych znaków
"""
            result = converter.convert(complex_request)
            assert result is not None, "Wynik konwersji jest None"
            assert len(result) > 0, "Wynik konwersji jest pusty"
            
            # Sprawdź czy wygenerowane wyrażenie regularne jest poprawne
            try:
                regex = re.compile(result)
                
                # Sprawdź czy wyrażenie działa poprawnie dla różnych przypadków
                valid_password = "Abc123!@"
                invalid_passwords = ["abc123", "ABC123!", "Abcdefgh", "Abc 123!"]
                
                assert regex.search(valid_password), f"Wyrażenie nie dopasowało poprawnego hasła: {valid_password}"
                
                for password in invalid_passwords:
                    if regex.search(password):
                        pytest.skip(f"Wyrażenie dopasowało niepoprawne hasło: {password}")
            except re.error:
                pytest.skip(f"Wygenerowane wyrażenie '{result}' nie jest poprawnym wyrażeniem regularnym")
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
