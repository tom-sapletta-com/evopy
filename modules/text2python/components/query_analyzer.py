#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QueryAnalyzer - Komponent odpowiedzialny za analizę zapytań użytkownika
i określanie ich typu, złożoności oraz intencji.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

class QueryAnalyzer:
    """
    Klasa odpowiedzialna za analizę zapytań użytkownika i określanie
    ich typu, złożoności oraz intencji.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja analizatora zapytań
        
        Args:
            config: Dodatkowa konfiguracja
        """
        self.config = config or {}
        self.logger = logging.getLogger('QueryAnalyzer')
        
        # Definicje typów zapytań
        self.query_types = {
            "arithmetic": r'^\s*(\d+\s*[+\-*/]\s*\d+)\s*$',
            "math_function": r'(sin|cos|tan|log|sqrt|pow|exp)\s*\(.*?\)',
            "geometric": r'(koło|okrąg|trójkąt|kwadrat|prostokąt|sześcian|kula|walec|stożek)',
            "equation": r'(równanie|rozwiąż|oblicz|znajdź|wyznacz).*(x|y|z)',
            "data_processing": r'(dane|csv|excel|plik|tabela|dataframe)',
            "api_request": r'(api|http|request|get|post|url)',
            "file_operation": r'(plik|odczytaj|zapisz|otwórz|zamknij)',
            "general_programming": r'(funkcja|klasa|metoda|obiekt|lista|słownik|pętla)'
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analizuje zapytanie użytkownika
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            Dict[str, Any]: Wynik analizy zapytania
        """
        self.logger.info(f"Analizowanie zapytania: '{query}'")
        
        # Inicjalizacja wyniku analizy
        analysis = {
            "query": query,
            "query_type": "unknown",
            "complexity": self._calculate_complexity(query),
            "keywords": self._extract_keywords(query),
            "is_valid": True,
            "is_math_expression": False,
            "requires_external_data": False,
            "requires_visualization": False
        }
        
        # Sprawdź czy zapytanie jest puste lub zawiera tylko znaki specjalne
        if not query or query.strip() == "" or all(not c.isalnum() for c in query):
            analysis["is_valid"] = False
            return analysis
        
        # Określ typ zapytania
        for query_type, pattern in self.query_types.items():
            if re.search(pattern, query, re.IGNORECASE):
                analysis["query_type"] = query_type
                break
        
        # Sprawdź czy zapytanie jest wyrażeniem matematycznym
        if analysis["query_type"] in ["arithmetic", "math_function", "equation"]:
            analysis["is_math_expression"] = True
        
        # Sprawdź czy zapytanie wymaga danych zewnętrznych
        if any(keyword in query.lower() for keyword in ["dane", "plik", "api", "url", "http", "csv", "excel"]):
            analysis["requires_external_data"] = True
        
        # Sprawdź czy zapytanie wymaga wizualizacji
        if any(keyword in query.lower() for keyword in ["wykres", "diagram", "wizualizacja", "narysuj", "pokaż", "plot"]):
            analysis["requires_visualization"] = True
        
        return analysis
    
    def _calculate_complexity(self, text: str) -> float:
        """
        Oblicza złożoność zapytania na podstawie różnych metryk
        
        Args:
            text: Tekst zapytania
            
        Returns:
            float: Wartość złożoności od 0.0 do 1.0
        """
        # Prosta heurystyka złożoności oparta na długości, liczbie słów kluczowych i strukturze
        complexity = 0.0
        
        # Długość tekstu (0.0-0.3)
        length_score = min(len(text) / 500.0, 1.0) * 0.3
        complexity += length_score
        
        # Liczba słów kluczowych technicznych (0.0-0.4)
        tech_keywords = ['plik', 'dane', 'oblicz', 'algorytm', 'funkcja', 'klasa', 'obiekt',
                         'lista', 'słownik', 'iteracja', 'rekurencja', 'sortowanie', 'filtrowanie',
                         'API', 'baza danych', 'HTTP', 'JSON', 'XML', 'CSV', 'SQL', 'wykres',
                         'analiza', 'statystyka', 'uczenie maszynowe', 'AI', 'sieć neuronowa']
        
        keyword_count = sum(1 for keyword in tech_keywords if keyword.lower() in text.lower())
        keyword_score = min(keyword_count / 10.0, 1.0) * 0.4
        complexity += keyword_score
        
        # Złożoność strukturalna (0.0-0.3) - liczba zdań, przecinków, nawiasów
        structure_indicators = len(re.findall(r'[.!?]', text)) + len(re.findall(r',', text)) + len(
            re.findall(r'[()]', text))
        structure_score = min(structure_indicators / 20.0, 1.0) * 0.3
        complexity += structure_score
        
        return round(complexity, 2)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Wyodrębnia słowa kluczowe z tekstu
        
        Args:
            text: Tekst do analizy
            
        Returns:
            List[str]: Lista słów kluczowych
        """
        # Usuń znaki interpunkcyjne i zamień na małe litery
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Podziel na słowa
        words = text.split()
        
        # Usuń słowa stop (krótkie, powszechne słowa)
        stop_words = ['i', 'w', 'na', 'z', 'do', 'dla', 'jest', 'są', 'to', 'a', 'o', 'że', 'by']
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Zwróć unikalne słowa kluczowe
        return list(set(keywords))