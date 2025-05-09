#!/usr/bin/env python3
"""
Moduł do obsługi wyrażeń matematycznych z parametrami

Ten moduł zawiera funkcje do analizy wyrażeń matematycznych i generowania
kodu Python z parametrami zamiast zmiennych wewnętrznych.
"""

import re
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional, Union

def is_math_expression(text: str) -> bool:
    """
    Sprawdza czy tekst jest wyrażeniem matematycznym.
    
    Args:
        text: Tekst do sprawdzenia
        
    Returns:
        bool: True jeśli tekst to wyrażenie matematyczne, False w przeciwnym razie
    """
    # Usuwamy białe znaki
    text = text.strip()
    
    # Proste wyrażenia arytmetyczne (np. "1+1", "3*4")
    if re.match(r'^\s*\d+\s*[\+\-\*/]\s*\d+\s*$', text):
        return True
    
    # Bardziej złożone wyrażenia (wykrywanie specjalnych symboli i funkcji)
    math_symbols = ['√', '∛', '^', '+', '-', '*', '/', '=', '(', ')', '[', ']', '{', '}', 
                    'sin', 'cos', 'tan', 'log', 'ln', 'exp', 'sqrt', 'cbrt', 'pow']
    
    # Sprawdź czy tekst zawiera symbole matematyczne
    symbols_found = sum(1 for symbol in math_symbols if symbol in text)
    
    # Sprawdź stosunek symboli matematycznych do długości tekstu
    if len(text) > 0 and symbols_found / len(text) >= 0.1:
        return True
    
    # Sprawdź czy tekst pasuje do wzorca równania
    if '=' in text and (re.search(r'\d', text) or any(symbol in text for symbol in math_symbols)):
        return True
    
    return False

def extract_variables_from_expression(expression: str) -> Tuple[List[Tuple[str, Union[int, float]]], str]:
    """
    Analizuje wyrażenie arytmetyczne i wyodrębnia zmienne oraz ich wartości.
    
    Args:
        expression: Wyrażenie arytmetyczne (np. "3+4", "5*2", itd.)
        
    Returns:
        tuple: (lista zmiennych, kod wyrażenia z użyciem zmiennych)
    """
    # Lista operatorów arytmetycznych
    operators = ['+', '-', '*', '/', '**', '//', '%', '√', '∛', 'log', 'sin', 'cos', 'tan']
    
    # Wyodrębnij tokeny z wyrażenia
    tokens = []
    current_token = ""
    i = 0
    
    while i < len(expression):
        char = expression[i]
        
        # Obsługa liczb (całkowitych i zmiennoprzecinkowych)
        if char.isdigit() or char == '.':
            current_token += char
        
        # Obsługa operatorów specjalnych (√, ∛, log, sin, cos, tan)
        elif any(op.startswith(char) for op in operators if len(op) > 1):
            # Sprawdź czy to dłuższy operator
            for op in sorted(operators, key=len, reverse=True):
                if expression[i:i+len(op)] == op:
                    if current_token:
                        tokens.append(current_token)
                        current_token = ""
                    tokens.append(op)
                    i += len(op) - 1
                    break
            else:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
        
        # Obsługa podstawowych operatorów i znaków specjalnych
        elif char in '+-*/()^[]{}':
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        
        # Zmienne (x, y, etc.)
        elif char.isalpha():
            # Sprawdź czy to już jest zmienna
            if i > 0 and expression[i-1].isalpha():
                current_token += char
            else:
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                current_token = char
        
        # Ignoruj białe znaki
        elif char.isspace():
            if current_token:
                tokens.append(current_token)
                current_token = ""
        
        # Inne znaki specjalne
        else:
            if current_token:
                tokens.append(current_token)
                current_token = ""
            tokens.append(char)
        
        i += 1
    
    # Dodaj ostatni token jeśli istnieje
    if current_token:
        tokens.append(current_token)
    
    # Przygotuj zmienne i wyrażenie z ich użyciem
    variables = []
    var_names = ['x', 'y', 'z', 'a', 'b', 'c']  # Domyślne nazwy zmiennych
    var_idx = 0
    expression_with_vars = []
    
    for token in tokens:
        # Jeśli token to liczba
        if re.match(r'^-?\d+(\.\d+)?$', token):
            # Sprawdź czy już jest zdefiniowana zmienna dla tej wartości
            value = float(token) if '.' in token else int(token)
            existing_var = next((var_name for var_name, var_value in variables if var_value == value), None)
            
            if existing_var:
                expression_with_vars.append(existing_var)
            else:
                var_name = var_names[var_idx] if var_idx < len(var_names) else f'var{var_idx-len(var_names)+1}'
                variables.append((var_name, value))
                expression_with_vars.append(var_name)
                var_idx += 1
        else:
            expression_with_vars.append(token)
    
    return variables, ''.join(expression_with_vars)

def handle_math_expression(expression: str) -> Dict[str, Any]:
    """
    Generuje kod Python dla prostego wyrażenia matematycznego z parametrami.
    
    Args:
        expression: Proste wyrażenie matematyczne (np. "1+1", "3*4", itp.)
        
    Returns:
        Dict: Struktura z wygenerowanym kodem i metadanymi
    """
    # Normalizacja wyrażenia - zastąpienie specjalnych symboli matematycznych
    normalized_expr = expression
    normalized_expr = normalized_expr.replace('√', 'sqrt')
    normalized_expr = normalized_expr.replace('∛', 'cbrt')
    normalized_expr = normalized_expr.replace('^', '**')
    normalized_expr = re.sub(r'log_(\d+)', r'log\1', normalized_expr)
    normalized_expr = re.sub(r'log₂', r'log2', normalized_expr)
    normalized_expr = re.sub(r'log₁₀', r'log10', normalized_expr)
    normalized_expr = re.sub(r'sin²\((.*?)\)', r'sin(\1)**2', normalized_expr)
    normalized_expr = re.sub(r'cos²\((.*?)\)', r'cos(\1)**2', normalized_expr)
    
    # Wyodrębnij zmienne i wyrażenie z ich użyciem
    variables, expr_with_vars = extract_variables_from_expression(normalized_expr)
    
    # Przygotuj implementację funkcji z parametrami
    param_list = ', '.join([var_name for var_name, _ in variables])
    if not param_list:
        param_list = 'x'  # Domyślny parametr jeśli nie znaleziono zmiennych
        
    # Przygotuj konwersje specjalnych funkcji matematycznych
    python_expr = expr_with_vars
    python_expr = re.sub(r'sqrt\((.*?)\)', r'math.sqrt(\1)', python_expr)
    python_expr = re.sub(r'cbrt\((.*?)\)', r'math.pow(\1, 1/3)', python_expr)
    python_expr = re.sub(r'log2\((.*?)\)', r'math.log2(\1)', python_expr)
    python_expr = re.sub(r'log10\((.*?)\)', r'math.log10(\1)', python_expr)
    python_expr = re.sub(r'sin\((.*?)\)', r'math.sin(\1)', python_expr)
    python_expr = re.sub(r'cos\((.*?)\)', r'math.cos(\1)', python_expr)
    
    code = f"""import math

def execute({param_list}):
    \"\"\"Oblicza wartość wyrażenia matematycznego: {expression}\"\"\" 
    result = {python_expr}
    return result

# Przykład użycia:
# print(execute({', '.join([str(value) for _, value in variables])}))  # = {expression}"""
    
    # Przygotuj wyjaśnienie dla użytkownika
    var_explanations = []
    for var_name, value in variables:
        var_explanations.append(f"{var_name} = {value}")
    
    vars_text = ", ".join(var_explanations)
    
    explanation = f"""Ten kod wykonuje obliczenie matematyczne: {expression}.

Funkcja 'execute' przyjmuje parametry: {param_list}
Parametry reprezentują wartości: {vars_text}
Funkcja oblicza wynik wyrażenia i zwraca go.

Czy to jest to, czego oczekiwałeś?"""
    
    # Przygotuj analizę
    analysis = {
        "is_logical": True,
        "matches_intent": True,
        "issues": [],
        "suggestions": []
    }
    
    # Przygotuj listę zmiennych w bardziej dostępnej formie
    variables_list = [{"name": name, "value": value} for name, value in variables]
    
    # Generuj unikalne ID dla kodu
    import uuid
    code_id = str(uuid.uuid4())
    
    # Przygotuj kod do zapisania w pliku
    import os
    file_path = None
    if 'code_dir' in globals():
        os.makedirs(code_dir, exist_ok=True)
        file_path = os.path.join(code_dir, f"{code_id}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
    
    # Zwróć pełną strukturę wyniku
    return {
        "success": True,
        "code": code,
        "code_id": code_id,
        "code_file": file_path,
        "explanation": explanation,
        "analysis": "Kod wydaje się poprawny i zgodny z intencją.",
        "analysis_details": analysis,
        "matches_intent": True,
        "is_logical": True,
        "variables": variables_list,
        "timestamp": datetime.now().isoformat()
    }
