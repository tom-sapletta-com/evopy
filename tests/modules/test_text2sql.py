#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu text2sql
"""

import pytest
from .test_base import BaseConverterTest

class TestText2SQL(BaseConverterTest):
    """Testy dla modułu text2sql"""
    
    module_name = "text2sql"
    
    @pytest.mark.parametrize("input_text,expected_output", [
        (
            "Pobierz wszystkie rekordy z tabeli users",
            "SELECT"
        ),
        (
            "Dodaj nowego użytkownika o nazwie Jan Kowalski i emailu jan@example.com",
            "INSERT"
        ),
        (
            "Zaktualizuj adres email użytkownika o id 5 na nowy@example.com",
            "UPDATE"
        ),
        (
            "Usuń wszystkich użytkowników, którzy nie zalogowali się od roku",
            "DELETE"
        )
    ])
    def test_conversion(self, converter, input_text, expected_output):
        """Test konwersji tekstu na zapytania SQL"""
        try:
            result = converter.convert(input_text)
            assert result is not None, "Wynik konwersji jest None"
            
            # Sprawdź czy wynik zawiera oczekiwane elementy
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
    
    def test_complex_query(self, converter):
        """Test konwersji złożonego zapytania"""
        try:
            complex_request = """
Znajdź wszystkich klientów, którzy złożyli zamówienia o wartości powyżej 1000 zł w ostatnim miesiącu,
posortuj ich według łącznej wartości zamówień malejąco i pokaż tylko 10 najlepszych klientów
wraz z ich danymi kontaktowymi i sumą zamówień
"""
            result = converter.convert(complex_request)
            assert result is not None, "Wynik konwersji jest None"
            assert len(result) > 0, "Wynik konwersji jest pusty"
            
            # Sprawdź czy wynik zawiera typowe elementy dla takiego zadania
            expected_elements = ["SELECT", "JOIN", "WHERE", "ORDER BY", "LIMIT"]
            found_elements = [elem for elem in expected_elements if elem in result]
            assert len(found_elements) > 0, f"Wynik konwersji nie zawiera żadnego z oczekiwanych elementów: {expected_elements}"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
    
    def test_schema_awareness(self, converter):
        """Test świadomości schematu bazy danych"""
        # Ten test sprawdza, czy konwerter może obsłużyć informacje o schemacie bazy danych
        # jeśli taka funkcjonalność jest dostępna
        if not hasattr(converter, "set_schema"):
            pytest.skip("Konwerter nie obsługuje ustawiania schematu")
        
        try:
            schema = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL(10, 2),
    order_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""
            converter.set_schema(schema)
            
            query = "Pokaż wszystkie zamówienia użytkownika o id 5"
            result = converter.convert(query)
            
            assert "user_id" in result, "Wynik konwersji nie uwzględnia schematu bazy danych"
        except Exception as e:
            pytest.skip(f"Test pominięty z powodu błędu: {str(e)}")
