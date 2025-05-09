#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bazowa klasa testowa dla modułów konwersji
"""

import pytest
import importlib.util
import os
from pathlib import Path

class BaseConverterTest:
    """Bazowa klasa testowa dla modułów konwersji"""
    
    # Nazwa modułu do testowania (nadpisywana w klasach potomnych)
    module_name = None
    
    # Przykładowe dane wejściowe i oczekiwane wyjścia (nadpisywane w klasach potomnych)
    test_cases = []
    
    @pytest.fixture
    def converter(self):
        """Tworzy instancję konwertera do testów"""
        if not self.module_name:
            pytest.skip("Nie podano nazwy modułu")
            
        # Ścieżka do modułu
        module_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "modules" / self.module_name
        module_file = module_dir / f"{self.module_name}.py"
        
        if not module_file.exists():
            pytest.skip(f"Moduł {self.module_name} nie istnieje")
        
        # Dynamiczne importowanie modułu
        spec = importlib.util.spec_from_file_location(self.module_name, module_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Zakładamy, że każdy moduł ma klasę o tej samej nazwie co moduł
        # np. text2python.py ma klasę Text2Python
        class_name = ''.join(word.capitalize() for word in self.module_name.split('2'))
        converter_class = getattr(module, class_name)
        
        # Inicjalizacja konwertera
        return converter_class()
    
    def test_converter_initialization(self, converter):
        """Test inicjalizacji konwertera"""
        assert converter is not None, f"Nie udało się zainicjalizować konwertera {self.module_name}"
    
    def test_convert_method_exists(self, converter):
        """Test czy metoda convert istnieje"""
        assert hasattr(converter, "convert"), f"Konwerter {self.module_name} nie ma metody convert"
        assert callable(getattr(converter, "convert")), f"Atrybut convert konwertera {self.module_name} nie jest metodą"
    
    @pytest.mark.parametrize("input_text,expected_output", [])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji dla różnych przypadków testowych"""
        result = converter.convert(input_text)
        assert result is not None, "Wynik konwersji jest None"
        
        # Sprawdź czy wynik zawiera oczekiwane elementy
        # Możemy sprawdzać częściową zgodność, ponieważ modele mogą generować różne odpowiedzi
        if expected_output:
            assert any(expected in result for expected in expected_output.split('\n') if expected.strip()), \
                f"Wynik konwersji nie zawiera oczekiwanych elementów. Otrzymano: {result}"
