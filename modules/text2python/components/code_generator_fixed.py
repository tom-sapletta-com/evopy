#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CodeGenerator - Komponent odpowiedzialny za generowanie kodu Python
na podstawie opisu w języku naturalnym
"""

import re
import os
import sys
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Union, Tuple

class CodeGenerator:
    """
    Klasa odpowiedzialna za generowanie kodu Python na podstawie
    opisu w języku naturalnym.
    """
    
    def __init__(self, model_name: str = "llama3", config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja generatora kodu
        
        Args:
            model_name: Nazwa modelu językowego do użycia
            config: Dodatkowa konfiguracja
        """
        self.model_name = model_name
        self.config = config or {}
        self.logger = logging.getLogger('CodeGenerator')
    
    def generate_code(self, prompt: str, query_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generuje kod Python na podstawie opisu w języku naturalnym
        
        Args:
            prompt: Opis funkcjonalności w języku naturalnym
            query_analysis: Opcjonalny wynik analizy zapytania z QueryAnalyzer
            
        Returns:
            Dict[str, Any]: Wygenerowany kod i metadane
        """
        try:
            self.logger.info(f"Generowanie kodu dla zapytania: {prompt[:50]}...")
            
            # Przygotuj prompt dla modelu
            system_prompt = """Jesteś ekspertem w programowaniu w Pythonie. Twoim zadaniem jest wygenerowanie kodu Python na podstawie opisu.
Generuj tylko kod Python, bez dodatkowych wyjaśnień czy komentarzy poza kodem.
Kod powinien być zwięzły, czytelny i zgodny z dobrymi praktykami programowania w Pythonie.
Funkcja powinna być nazwana 'execute' i powinna przyjmować wszystkie potrzebne zmienne jako parametry wejściowe.
Przykład: 'def execute(a, b, c=5):' zamiast inicjalizować zmienne wewnątrz funkcji.

Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik.
Zawsze zwracaj wynik działania funkcji za pomocą instrukcji return."""

            # Dodaj informacje o zmiennych, jeśli są dostępne
            variables_info = ""
            self.detected_variables = []
            self.variable_values = {}
            self.variable_initializations = ""  # Zachowaj dla kompatybilności wstecznej
            
            # Wykrywanie prostych wyrażeń matematycznych (np. 2+2, x+y, itp.)
            math_expr_pattern = re.compile(r'^\s*([a-zA-Z0-9]+)\s*([+\-*/])\s*([a-zA-Z0-9]+)\s*$')
            math_match = math_expr_pattern.match(prompt)
            
            if math_match:
                left_operand, operator, right_operand = math_match.groups()
                
                # Sprawdź, czy operandy są liczbami czy zmiennymi
                left_is_var = not left_operand.isdigit()
                right_is_var = not right_operand.isdigit()
                
                if left_is_var or right_is_var:
                    # Jeśli którykolwiek operand jest zmienną, dodaj obie jako parametry
                    if left_is_var:
                        self.detected_variables.append(left_operand)
                        self.variable_values[left_operand] = 1  # Domyślna wartość
                    
                    if right_is_var:
                        self.detected_variables.append(right_operand)
                        self.variable_values[right_operand] = 1  # Domyślna wartość
                    
                    variables_info += f"\nW zapytaniu zidentyfikowano wyrażenie matematyczne, które wymaga zmiennych jako parametrów funkcji execute:\n"
                    for var in self.detected_variables:
                        variables_info += f"- {var}=1 (zmienna w wyrażeniu)\n"
                    
                    variables_info += f"\nUżyj tych zmiennych jako parametrów funkcji execute, np. def execute({', '.join([f'{v}=1' for v in self.detected_variables])}):"
                else:
                    # Nawet jeśli oba operandy są liczbami, traktuj je jako zmienne
                    self.detected_variables.extend(['x', 'y'])
                    self.variable_values['x'] = left_operand
                    self.variable_values['y'] = right_operand
                    
                    variables_info += f"\nZapytanie zawiera proste wyrażenie matematyczne. Zamiast hardcodować wynik, użyj zmiennych:\n"
                    variables_info += f"- x={left_operand} (pierwszy operand)\n"
                    variables_info += f"- y={right_operand} (drugi operand)\n"
                    variables_info += f"\nUżyj tych zmiennych jako parametrów funkcji execute, np. def execute(x={left_operand}, y={right_operand}):"
                    variables_info += f"\nNastępnie zwróć wynik operacji {operator} na tych zmiennych."
            
            # Automatyczne wykrywanie zmiennych dla zapytań o obliczenia geometryczne
            if "pole" in prompt.lower() and ("prostokąta" in prompt.lower() or "prostokat" in prompt.lower()):
                # Automatycznie dodaj zmienne a i b dla prostokąta
                if "długości" in prompt.lower() and "szerokości" in prompt.lower():
                    a_match = re.search(r'długości\s+([a-zA-Z])\s*=\s*(\d+)', prompt, re.IGNORECASE)
                    b_match = re.search(r'szerokości\s+([a-zA-Z])\s*=\s*(\d+)', prompt, re.IGNORECASE)
                    
                    if a_match and b_match:
                        a_name, a_value = a_match.groups()
                        b_name, b_value = b_match.groups()
                        
                        # Zapisz wykryte zmienne
                        self.detected_variables.extend([a_name, b_name])
                        self.variable_values[a_name] = a_value
                        self.variable_values[b_name] = b_value
                        
                        variables_info += f"\nW zapytaniu zidentyfikowano zmienne, które powinny być parametrami funkcji execute:\n"
                        variables_info += f"- {a_name}={a_value} (długość prostokąta)\n"
                        variables_info += f"- {b_name}={b_value} (szerokość prostokąta)\n"
                        variables_info += f"\nUżyj tych zmiennych jako parametrów funkcji execute, np. def execute({a_name}={a_value}, {b_name}={b_value}):"                        
                    else:
                        # Jeśli nie znaleziono konkretnych zmiennych, użyj domyślnych a=10, b=5
                        self.detected_variables.extend(['a', 'b'])
                        self.variable_values['a'] = 10
                        self.variable_values['b'] = 5
                        
                        variables_info += f"\nNależy użyć następujących zmiennych jako parametrów funkcji execute:\n"
                        variables_info += f"- a=10 (długość prostokąta)\n"
                        variables_info += f"- b=5 (szerokość prostokąta)\n"
                        variables_info += f"\nUżyj tych zmiennych jako parametrów funkcji execute, np. def execute(a=10, b=5):"
                else:
                    # Jeśli nie znaleziono słów kluczowych, użyj domyślnych a=10, b=5
                    self.detected_variables.extend(['a', 'b'])
                    self.variable_values['a'] = 10
                    self.variable_values['b'] = 5
                    
                    variables_info += f"\nNależy użyć następujących zmiennych jako parametrów funkcji execute:\n"
                    variables_info += f"- a=10 (długość prostokąta)\n"
                    variables_info += f"- b=5 (szerokość prostokąta)\n"
                    variables_info += f"\nUżyj tych zmiennych jako parametrów funkcji execute, np. def execute(a=10, b=5):"
            
            # Dodaj informacje o zmiennych do promptu
            if variables_info:
                system_prompt += variables_info
            
            # Użyj modelu do wygenerowania kodu
            if self.model_name == "llama3":
                # Użyj lokalnego modelu llama3
                code = self._generate_code_with_llama(system_prompt, prompt)
            else:
                # Domyślnie użyj prostego generatora kodu
                code = self._generate_simple_code(prompt)
            
            # Wyodrębnij kod Python z odpowiedzi modelu
            code = self._extract_code(code)
            
            # Owij kod w funkcję execute, jeśli jej nie zawiera
            if "def execute" not in code:
                code = self._wrap_in_execute_function(code, query_analysis)

            return {
                "success": True,
                "code": code,
                "raw_response": ""
            }

        except Exception as e:
            self.logger.error(f"Błąd podczas generowania kodu: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e)
            }
    
    def _extract_code(self, text: str) -> str:
        """
        Wyodrębnia kod Python z odpowiedzi modelu
        
        Args:
            text: Odpowiedź modelu
            
        Returns:
            str: Wyodrębniony kod Python
        """
        # Próba wyodrębnienia kodu z bloków kodu markdown
        code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
        
        if code_blocks:
            # Zwracamy tylko zawartość bloku kodu, bez znaczników markdown
            return code_blocks[0].strip()
        
        # Usunięcie wszystkich znaczników markdown z tekstu
        # Usuwamy linie zawierające tylko ```
        text = re.sub(r'^```(?:python)?\s*$|^```\s*$', '', text, flags=re.MULTILINE)
        
        # Jeśli nie znaleziono bloków kodu, zwróć całą odpowiedź po oczyszczeniu
        return text.strip()
    
    def _wrap_in_execute_function(self, code: str, query_analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        Owija kod w funkcję execute jeśli jej nie zawiera
        
        Args:
            code: Kod Python
            query_analysis: Opcjonalny wynik analizy zapytania z QueryAnalyzer
            
        Returns:
            str: Kod z funkcją execute
        """
        # Sprawdź czy kod już zawiera funkcję execute
        if "def execute" in code:
            # Jeśli kod już zawiera funkcję execute, ale nie ma inicjalizacji zmiennych,
            # dodaj inicjalizacje zmiennych na początku funkcji
            if hasattr(self, 'variable_initializations') and self.variable_initializations:
                # Znajdź pozycję po definicji funkcji execute
                execute_pos = code.find("def execute")
                body_start = code.find(":", execute_pos) + 1
                
                # Znajdź pierwszą linię kodu po definicji funkcji
                next_line_pos = code.find("\n", body_start) + 1
                
                # Wstaw inicjalizacje zmiennych po definicji funkcji
                if next_line_pos > 0:
                    # Jeśli funkcja zawiera docstring, znajdź koniec docstringa
                    if code[next_line_pos:].strip().startswith('"""'):
                        docstring_end = code.find('"""', next_line_pos + 3) + 3
                        next_line_pos = code.find("\n", docstring_end) + 1
                    
                    code = code[:next_line_pos] + self.variable_initializations + code[next_line_pos:]
            
            return code
        
        # Dodaj wcięcie do każdej linii kodu
        indented_code = "\n".join(["    " + line for line in code.split("\n")])
        
        # Sprawdź, czy kod zawiera proste wyrażenie matematyczne (np. 2+2, x+y)
        simple_math_expr = False
        
        if len(indented_code.strip().split('\n')) == 1:
            math_expr_pattern = re.compile(r'\s*return\s+([a-zA-Z0-9]+)\s*([+\-*/])\s*([a-zA-Z0-9]+)\s*')
            math_match = math_expr_pattern.search(indented_code)
            
            if math_match:
                simple_math_expr = True
                left_operand, operator, right_operand = math_match.groups()
                
                # Sprawdź, czy operandy są liczbami czy zmiennymi
                left_is_var = not left_operand.isdigit()
                right_is_var = not right_operand.isdigit()
                
                if not left_is_var and not right_is_var:
                    # Jeśli oba operandy są liczbami, traktuj je jako zmienne x i y
                    indented_code = f"    return x {operator} y"
        
        # Przygotuj parametry funkcji execute
        params_str = ""
        docstring = ""
        
        # Zbierz zmienne z wykrytych zmiennych
        if hasattr(self, 'detected_variables') and self.detected_variables:
            params = []
            for var_name in self.detected_variables:
                if var_name in self.variable_values:
                    params.append(f"{var_name}={self.variable_values[var_name]}")
                else:
                    params.append(var_name)
            
            if params:
                params_str = ", ".join(params)
                
                # Dodaj docstring z opisem parametrów
                param_docs = []
                for var_name in self.detected_variables:
                    var_value = self.variable_values.get(var_name, "")
                    if var_value:
                        param_docs.append(f"        {var_name} (float/int): Zmienna {var_name}, domyślnie {var_value}")
                    else:
                        param_docs.append(f"        {var_name} (float/int): Zmienna {var_name}")
                
                if param_docs:
                    docstring = f"""
    \"\"\"
    Funkcja wykonująca zadanie.
{chr(10).join(param_docs)}
    
    Returns:
        Wynik wykonania zadania.
    \"\"\"
"""
        
        # Jeśli nie wykryto zmiennych, a kod zawiera proste wyrażenie matematyczne,
        # dodaj parametry x i y
        if not params_str and simple_math_expr:
            if math_match:
                left_operand, operator, right_operand = math_match.groups()
                params_str = f"x={left_operand}, y={right_operand}"
                
                docstring = f"""
    \"\"\"
    Funkcja wykonująca zadanie.
        x (float/int): Pierwszy operand, domyślnie {left_operand}
        y (float/int): Drugi operand, domyślnie {right_operand}
    
    Returns:
        Wynik wykonania zadania.
    \"\"\"
"""
        
        # Jeśli nadal nie ma parametrów, a kod jest prostym wyrażeniem, dodaj x i y
        if not params_str and len(indented_code.strip().split('\n')) == 1:
            params_str = "x=1, y=1"
            
            docstring = """
    \"\"\"
    Funkcja wykonująca zadanie.
        x (float/int): Pierwszy operand
        y (float/int): Drugi operand
    
    Returns:
        Wynik wykonania zadania.
    \"\"\"
"""
        
        # Utwórz funkcję execute
        if params_str:
            result = f"def execute({params_str}):{docstring}{indented_code}"
        else:
            result = f"def execute():{docstring}{indented_code}"
        
        return result
    
    def _generate_code_with_llama(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generuje kod używając lokalnego modelu llama3
        
        Args:
            system_prompt: Prompt systemowy
            user_prompt: Zapytanie użytkownika
            
        Returns:
            str: Wygenerowany kod
        """
        # Tutaj można zaimplementować wywołanie lokalnego modelu llama3
        # Na potrzeby tego przykładu zwracamy prosty kod
        return f"""```python
def execute():
    # Kod wygenerowany na podstawie zapytania: {user_prompt}
    return 42
```"""
    
    def _generate_simple_code(self, prompt: str) -> str:
        """
        Prosty generator kodu dla celów testowych
        
        Args:
            prompt: Zapytanie użytkownika
            
        Returns:
            str: Wygenerowany kod
        """
        # Prosty generator kodu dla celów testowych
        return f"""def execute():
    # Kod wygenerowany na podstawie zapytania: {prompt}
    return 42"""
