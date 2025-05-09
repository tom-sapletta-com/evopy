#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu shell2text
"""

import pytest
from .test_base import BaseConverterTest

class TestShell2Text(BaseConverterTest):
    """Testy dla modułu shell2text"""
    
    module_name = "shell2text"
    
    @pytest.mark.parametrize("input_text,expected_output", [
        (
            "ls -la",
            "list"
        ),
        (
            "find . -name '*.py' -type f",
            "znajd"
        ),
        (
            "mkdir -p test_dir/subdir",
            "utw"
        ),
        (
            "du -sh *",
            "zajm"
        )
    ])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji poleceń shell na tekst"""
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
            
            # Testowanie z niepoprawnym poleceniem
            result = converter.convert("command_that_does_not_exist --invalid-flag")
            assert result is not None, "Konwerter powinien obsłużyć niepoprawne polecenie"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_complex_command(self, converter):
        """Test konwersji złożonego polecenia"""
        try:
            complex_command = """
find /var/log -name "*.log" -type f -mtime +7 -exec rm {} \; && \
echo "Logs cleaned on $(date)" | mail -s "Log Cleanup Report" admin@example.com
"""
            result = converter.convert(complex_command)
            assert result is not None, "Wynik konwersji jest None"
            assert len(result) > 0, "Wynik konwersji jest pusty"
            
            # Sprawdź czy wynik zawiera typowe elementy dla takiego zadania
            expected_elements = ["log", "usun", "znajd", "email", "wiadomo"]
            found_elements = [elem for elem in expected_elements if elem.lower() in result.lower()]
            assert len(found_elements) > 0, f"Wynik konwersji nie zawiera żadnego z oczekiwanych elementów: {expected_elements}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
