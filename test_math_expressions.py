#!/usr/bin/env python3
"""
Przykład użycia zmodernizowanego modułu do obsługi równań matematycznych
"""

from modules.utils.math_expressions import is_math_expression, handle_math_expression

# Przetestuj proste wyrażenia arytmetyczne
expressions = [
    "1+1",
    "3*4",
    "5-2",
    "10/2"
]

for expr in expressions:
    print(f"\nTestowanie wyrażenia: '{expr}'")
    print(f"Czy to wyrażenie matematyczne? {is_math_expression(expr)}")
    
    result = handle_math_expression(expr)
    print(f"Wygenerowany kod:\n{result['code']}")
    print(f"Wyjaśnienie:\n{result['explanation']}")

# Przetestuj bardziej złożone wyrażenia
complex_expressions = [
    "2√(x³+1) - log₂(x+3)",
    "sin²(2x) + cos²(2x)",
    "2√(x³+1) - log₂(x+3) = (sin²(2x) + cos²(2x))·(3x²-5)/(2x+7) + 2/3·∛(x²-4)"
]

for expr in complex_expressions:
    print(f"\nTestowanie wyrażenia: '{expr}'")
    print(f"Czy to wyrażenie matematyczne? {is_math_expression(expr)}")
    
    result = handle_math_expression(expr)
    print(f"Wygenerowany kod:\n{result['code']}")
    print(f"Wyjaśnienie:\n{result['explanation']}")
