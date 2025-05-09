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
            "requires_visualization": False,
            "variables": self._extract_variables(query),
            "has_variables": False
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
        
        # Dodatkowe sprawdzenie dla zmiennych w zapytaniach o obliczenia geometryczne
        if "pole" in query.lower() and ("prostokąta" in query.lower() or "prostokat" in query.lower()):
            # Szukaj zmiennych a i b w kontekście prostokąta
            if "długości" in query.lower() and "szerokości" in query.lower():
                a_match = re.search(r'długości\s+([a-zA-Z])\s*=\s*(\d+)', query, re.IGNORECASE)
                b_match = re.search(r'szerokości\s+([a-zA-Z])\s*=\s*(\d+)', query, re.IGNORECASE)
                
                if a_match and b_match:
                    a_name, a_value = a_match.groups()
                    b_name, b_value = b_match.groups()
                    
                    # Dodaj zmienne do analizy
                    analysis["variables"][a_name] = {
                        "type": "numeric",
                        "value": int(a_value),
                        "position": a_match.start(),
                        "raw_match": a_match.group(0)
                    }
                    
                    analysis["variables"][b_name] = {
                        "type": "numeric",
                        "value": int(b_value),
                        "position": b_match.start(),
                        "raw_match": b_match.group(0)
                    }
                    
                    analysis["has_variables"] = True
        
        # Oznacz, czy zapytanie zawiera zmienne
        if analysis["variables"]:
            analysis["has_variables"] = True
        
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
        
    def _extract_variables(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Wyodrębnia zmienne z zapytania użytkownika
        
        Args:
            text: Zapytanie użytkownika
            
        Returns:
            Dict[str, Dict[str, Any]]: Słownik zidentyfikowanych zmiennych z ich właściwościami
        """
        variables = {}
        
        # Wzorce do wykrywania zmiennych
        patterns = [
            # Wzorzec dla zmiennej z przypisaniem wartości (np. "x = 5" lub "x równa się 5")
            (r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|równa się|wynosi|jest równe|jest równy|jest równa)[\s]*([\d.]+)', 'numeric'),
            
            # Wzorzec dla zmiennych w kontekście polskim (np. "o długości a = 10")
            (r'o[\s]+(?:długości|szerokości|wartości|promieniu|wysokości|głębokości)[\s]+([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|równej|równym|równa)[\s]*([\d.]+)', 'numeric'),
            
            # Wzorzec dla zmiennych w kontekście polskim (np. "długość a = 10")
            (r'(?:długość|szerokość|wartość|promień|wysokość|głębokość)[\s]+([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|równa|wynosi)[\s]*([\d.]+)', 'numeric'),
            
            # Wzorzec dla zmiennych w kontekście polskim bez słowa kluczowego (np. "a = 10 i b = 5")
            (r'\b([a-zA-Z_][a-zA-Z0-9_]*)[\s]*=[\s]*(\d+(?:\.\d+)?)[\s]*(?:i|oraz|,)[\s]*([a-zA-Z_][a-zA-Z0-9_]*)[\s]*=[\s]*(\d+(?:\.\d+)?)', 'numeric_pair'),
            
            # Dodatkowy wzorzec dla zmiennych w kontekście polskim (np. "a równa się 10 i b równa się 5")
            (r'\b([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:równa się|wynosi|jest równe|jest równy|jest równa)[\s]*(\d+(?:\.\d+)?)', 'numeric'),
            
            # Wzorzec dla zmiennej z przypisaniem tekstu (np. "nazwa = 'Jan'" lub "tekst to 'Hello'")
            (r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|to|jest|równa się)[\s]*[\'\"](.*?)[\'\"](\s|$)', 'string'),
            
            # Wzorzec dla zmiennej z przypisaniem wartości logicznej (np. "flaga = True" lub "warunek to False")
            (r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|to|jest|równa się)[\s]*(prawda|fałsz|true|false)', 'boolean'),
            
            # Wzorzec dla zmiennej z przypisaniem listy (np. "lista = [1, 2, 3]" lub "liczby to [1, 2, 3]")
            (r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|to|jest|równa się)[\s]*\[([^\]]+)\]', 'list'),
            
            # Wzorzec dla zmiennej z przypisaniem słownika (np. "dane = {klucz: wartość}")
            (r'([a-zA-Z_][a-zA-Z0-9_]*)[\s]*(?:=|to|jest|równa się)[\s]*\{([^\}]+)\}', 'dict'),
            
            # Wzorzec dla zmiennych w równaniach (np. "2*x + 3*y = 10")
            (r'(?<![a-zA-Z0-9_])([a-zA-Z_][a-zA-Z0-9_]*)(?![a-zA-Z0-9_])', 'unknown')
        ]
        
        # Przeszukaj tekst w poszukiwaniu zmiennych według wzorów
        for pattern, var_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                var_name = match.group(1)
                
                # Pomiń słowa kluczowe języka Python
                if var_name.lower() in ['if', 'else', 'for', 'while', 'def', 'class', 'return', 'import', 'from', 'as', 'try', 'except', 'finally', 'with', 'in', 'is', 'not', 'and', 'or', 'true', 'false', 'none']:
                    continue
                
                # Jeśli zmienna już istnieje, nie nadpisuj jej
                if var_name in variables:
                    continue
                
                variable_info = {
                    "type": var_type,
                    "position": match.start(),
                    "raw_match": match.group(0)
                }
                
                # Dodaj wartość zmiennej, jeśli jest dostępna
                if var_type == 'numeric' and len(match.groups()) > 1:
                    try:
                        value = match.group(2)
                        if '.' in value:
                            variable_info["value"] = float(value)
                        else:
                            variable_info["value"] = int(value)
                    except (ValueError, IndexError):
                        pass
                elif var_type == 'numeric_pair' and len(match.groups()) > 3:
                    # Obsługa pary zmiennych (np. "a = 10 i b = 5")
                    try:
                        # Pierwsza zmienna
                        var1_name = match.group(1)
                        var1_value = match.group(2)
                        
                        # Druga zmienna
                        var2_name = match.group(3)
                        var2_value = match.group(4)
                        
                        # Dodaj pierwszą zmienną
                        if '.' in var1_value:
                            variable_info["value"] = float(var1_value)
                        else:
                            variable_info["value"] = int(var1_value)
                        
                        # Dodaj drugą zmienną do słownika zmiennych
                        var2_info = {
                            "type": "numeric",
                            "position": match.start(3),
                            "raw_match": match.group(0)
                        }
                        
                        if '.' in var2_value:
                            var2_info["value"] = float(var2_value)
                        else:
                            var2_info["value"] = int(var2_value)
                        
                        # Dodaj drugą zmienną do słownika zmiennych
                        variables[var2_name] = var2_info
                    except (ValueError, IndexError):
                        pass
                elif var_type == 'string' and len(match.groups()) > 1:
                    variable_info["value"] = match.group(2)
                elif var_type == 'boolean' and len(match.groups()) > 1:
                    bool_value = match.group(2).lower()
                    variable_info["value"] = bool_value in ['true', 'prawda']
                elif var_type == 'list' and len(match.groups()) > 1:
                    try:
                        # Próba interpretacji listy
                        items_str = match.group(2)
                        items = [item.strip() for item in items_str.split(',')]
                        variable_info["value"] = items
                    except (ValueError, IndexError):
                        pass
                elif var_type == 'dict' and len(match.groups()) > 1:
                    try:
                        # Próba interpretacji słownika
                        dict_str = match.group(2)
                        pairs = [pair.strip() for pair in dict_str.split(',')]
                        dict_items = {}
                        for pair in pairs:
                            if ':' in pair:
                                k, v = pair.split(':', 1)
                                dict_items[k.strip()] = v.strip()
                        variable_info["value"] = dict_items
                    except (ValueError, IndexError):
                        pass
                
                variables[var_name] = variable_info
        
        return variables