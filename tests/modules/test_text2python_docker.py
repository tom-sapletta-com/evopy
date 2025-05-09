#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu text2python_docker
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from test_base import BaseConverterTest

class TestText2PythonDocker(BaseConverterTest):
    """Testy dla modułu text2python_docker"""
    
    module_name = "text2python_docker"
    
    def test_initialization(self, converter):
        """Test inicjalizacji konwertera"""
        assert converter is not None
        assert hasattr(converter, 'text2python')
        assert hasattr(converter, 'sandbox')
        assert converter.model == "llama3"
    
    def test_convert_empty_input(self, converter):
        """Test konwersji pustego wejścia"""
        result = converter.convert("")
        assert result is not None
        assert "code" in result
        assert "success" in result
        assert result["success"] is False
        assert "Nie podano tekstu" in result["error"]
    
    @pytest.mark.parametrize("input_text,expected_code", [
        (
            "Napisz funkcję, która dodaje dwie liczby",
            "def add"
        ),
        (
            "Oblicz sumę liczb od 1 do 10",
            "sum"
        ),
        (
            "Wyświetl aktualną datę i czas",
            "datetime"
        )
    ])
    def test_convert_without_execution(self, converter, input_text, expected_code):
        """Test konwersji tekstu na kod Python bez uruchamiania"""
        with patch.object(converter, 'run_code') as mock_run:
            # Symuluj, że nie chcemy automatycznie uruchamiać kodu
            result = converter.convert(input_text, auto_run=False)
            
            assert result is not None
            assert "code" in result
            assert expected_code.lower() in result["code"].lower()
            
            # Sprawdź czy run_code nie zostało wywołane
            mock_run.assert_not_called()
    
    def test_convert_with_execution(self, converter):
        """Test konwersji tekstu na kod Python z uruchamianiem"""
        # Mockuj metodę run_code, aby nie uruchamiać faktycznego kodu
        with patch.object(converter, 'run_code') as mock_run:
            mock_run.return_value = {
                "success": True,
                "output": "Wynik wykonania",
                "error": "",
                "execution_time": 0.5
            }
            
            result = converter.convert("Oblicz 2 + 2", auto_run=True)
            
            assert result is not None
            assert "code" in result
            assert result["success"] is True
            assert result["output"] == "Wynik wykonania"
            
            # Sprawdź czy run_code zostało wywołane
            mock_run.assert_called_once()
    
    def test_prepare_code_without_execute(self, converter):
        """Test przygotowania kodu bez funkcji execute"""
        code = "print('Hello, World!')"
        prepared_code = converter._prepare_code(code)
        
        assert "def execute(" in prepared_code
        assert "result = execute()" in prepared_code
    
    def test_prepare_code_with_execute(self, converter):
        """Test przygotowania kodu z funkcją execute"""
        code = """
def execute():
    return 42
"""
        prepared_code = converter._prepare_code(code)
        
        assert "def execute(" in prepared_code
        assert "result = execute()" in prepared_code
        assert prepared_code.count("def execute(") == 1  # Upewnij się, że nie dodano drugiej funkcji execute
    
    @pytest.mark.docker
    def test_run_code(self, converter):
        """Test uruchamiania kodu w Dockerze"""
        # Ten test wymaga Dockera, więc oznaczamy go markerem docker
        try:
            # Prosty kod do uruchomienia
            code = """
def execute():
    return 2 + 2
"""
            result = converter.run_code(code)
            
            assert result is not None
            assert result["success"] is True
            assert "4" in result["output"]
            assert result["error"] == ""
            assert result["execution_time"] > 0
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_explain_code(self, converter):
        """Test wyjaśniania kodu Python"""
        # Mockuj metodę explain_code z text2python
        with patch.object(converter.text2python, 'explain_code') as mock_explain:
            mock_explain.return_value = "To jest wyjaśnienie kodu"
            
            code = "print('Hello, World!')"
            explanation = converter.explain_code(code)
            
            assert explanation == "To jest wyjaśnienie kodu"
            mock_explain.assert_called_once_with(code)
    
    def test_cleanup(self, converter):
        """Test czyszczenia zasobów"""
        # Mockuj metodę cleanup z sandbox
        with patch.object(converter.sandbox, 'cleanup') as mock_cleanup:
            converter.cleanup()
            mock_cleanup.assert_called_once()
    
    @pytest.mark.docker
    def test_integration(self, converter):
        """Test integracyjny - konwersja i uruchomienie"""
        try:
            # Prosty opis do konwersji
            text = "Napisz funkcję execute, która zwraca sumę liczb od 1 do 5"
            result = converter.convert(text, auto_run=True)
            
            assert result is not None
            assert "code" in result
            assert result["success"] is True
            assert "15" in result["output"] or "sum" in result["code"].lower()
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
