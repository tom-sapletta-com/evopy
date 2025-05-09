#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Geometry - Rozszerzenie matematyczne dla modułu text2python.
Obsługuje obliczenia geometryczne (koło, trójkąt, kwadrat, prostokąt, itp.).
"""

import re
import math
from typing import Dict, Any, List, Optional, Tuple, Union

# Słownik wzorców dla różnych figur geometrycznych
GEOMETRIC_PATTERNS = {
    "circle": {
        "patterns": [
            r'(koł[ao]|okrąg).*?promie[ńn]\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'(koł[ao]|okrąg).*?średnic[ay]\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'(koł[ao]|okrąg).*?obwód\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'(koł[ao]|okrąg).*?pole\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'pole\s+koła\s+o\s+promieniu\s+(\d+(?:\.\d+)?)',
            r'obwód\s+koła\s+o\s+promieniu\s+(\d+(?:\.\d+)?)',
            r'pole\s+koła\s+o\s+średnicy\s+(\d+(?:\.\d+)?)',
            r'obwód\s+koła\s+o\s+średnicy\s+(\d+(?:\.\d+)?)'
        ],
        "properties": ["radius", "diameter", "circumference", "area"]
    },
    "square": {
        "patterns": [
            r'kwadrat.*?bok\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'kwadrat.*?pole\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'kwadrat.*?obwód\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'pole\s+kwadratu\s+o\s+boku\s+(\d+(?:\.\d+)?)',
            r'obwód\s+kwadratu\s+o\s+boku\s+(\d+(?:\.\d+)?)'
        ],
        "properties": ["side", "area", "perimeter"]
    },
    "rectangle": {
        "patterns": [
            r'prostokąt.*?długość\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'prostokąt.*?szerokość\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'prostokąt.*?pole\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'prostokąt.*?obwód\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'pole\s+prostokąta\s+o\s+bokach\s+(\d+(?:\.\d+)?)\s+i\s+(\d+(?:\.\d+)?)',
            r'obwód\s+prostokąta\s+o\s+bokach\s+(\d+(?:\.\d+)?)\s+i\s+(\d+(?:\.\d+)?)'
        ],
        "properties": ["length", "width", "area", "perimeter"]
    },
    "triangle": {
        "patterns": [
            r'trójkąt.*?bok[iau]\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'trójkąt.*?pole\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'trójkąt.*?obwód\s*[=:]?\s*(\d+(?:\.\d+)?)',
            r'pole\s+trójkąta\s+o\s+bokach\s+(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*(?:i|,)\s*(\d+(?:\.\d+)?)',
            r'obwód\s+trójkąta\s+o\s+bokach\s+(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*(?:i|,)\s*(\d+(?:\.\d+)?)'
        ],
        "properties": ["sides", "area", "perimeter"]
    }
}

def identify_query(query: str) -> bool:
    """
    Sprawdza, czy zapytanie dotyczy obliczeń geometrycznych
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        bool: True jeśli zapytanie dotyczy geometrii, False w przeciwnym przypadku
    """
    query = query.lower()
    
    # Sprawdź ogólne słowa kluczowe związane z geometrią
    geometry_keywords = ["koło", "okrąg", "kwadrat", "prostokąt", "trójkąt", 
                        "sześcian", "kula", "walec", "stożek", "promień", 
                        "średnica", "bok", "pole", "obwód", "objętość"]
    
    if any(keyword in query for keyword in geometry_keywords):
        return True
    
    # Sprawdź szczegółowe wzorce dla różnych figur
    for shape, data in GEOMETRIC_PATTERNS.items():
        for pattern in data["patterns"]:
            if re.search(pattern, query, re.IGNORECASE):
                return True
    
    return False

def extract_parameters(query: str) -> Dict[str, Any]:
    """
    Wyodrębnia parametry z zapytania geometrycznego
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        Dict[str, Any]: Słownik z parametrami
    """
    query = query.lower()
    params = {
        "shape": None,
        "operation": None,
        "values": {}
    }
    
    # Określ rodzaj figury
    if any(keyword in query for keyword in ["koło", "okrąg"]):
        params["shape"] = "circle"
    elif "kwadrat" in query:
        params["shape"] = "square"
    elif "prostokąt" in query:
        params["shape"] = "rectangle"
    elif "trójkąt" in query:
        params["shape"] = "triangle"
    
    # Określ rodzaj operacji
    if "pole" in query:
        params["operation"] = "area"
    elif any(keyword in query for keyword in ["obwód", "obwodu"]):
        params["operation"] = "perimeter"
    elif "objętość" in query:
        params["operation"] = "volume"
    
    # Wyodrębnij wartości dla danej figury
    if params["shape"] == "circle":
        # Promień
        radius_match = re.search(r'promie[ńn]\s*[=:]?\s*(\d+(?:\.\d+)?)', query)
        if radius_match:
            params["values"]["radius"] = float(radius_match.group(1))
        
        # Średnica
        diameter_match = re.search(r'średnic[ay]\s*[=:]?\s*(\d+(?:\.\d+)?)', query)
        if diameter_match:
            params["values"]["diameter"] = float(diameter_match.group(1))
            if "radius" not in params["values"]:
                params["values"]["radius"] = params["values"]["diameter"] / 2
    
    elif params["shape"] == "square":
        # Bok
        side_match = re.search(r'bok\s*[=:]?\s*(\d+(?:\.\d+)?)', query)
        if side_match:
            params["values"]["side"] = float(side_match.group(1))
    
    elif params["shape"] == "rectangle":
        # Długość i szerokość
        length_match = re.search(r'długość\s*[=:]?\s*(\d+(?:\.\d+)?)', query)
        width_match = re.search(r'szerokość\s*[=:]?\s*(\d+(?:\.\d+)?)', query)
        
        if length_match:
            params["values"]["length"] = float(length_match.group(1))
        
        if width_match:
            params["values"]["width"] = float(width_match.group(1))
        
        # Sprawdź wzorzec "o bokach X i Y"
        sides_match = re.search(r'bokach\s+(\d+(?:\.\d+)?)\s+i\s+(\d+(?:\.\d+)?)', query)
        if sides_match:
            params["values"]["length"] = float(sides_match.group(1))
            params["values"]["width"] = float(sides_match.group(2))
    
    elif params["shape"] == "triangle":
        # Boki trójkąta
        sides_match = re.search(r'bokach\s+(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*(?:i|,)\s*(\d+(?:\.\d+)?)', query)
        if sides_match:
            params["values"]["a"] = float(sides_match.group(1))
            params["values"]["b"] = float(sides_match.group(2))
            params["values"]["c"] = float(sides_match.group(3))
    
    return params

def generate_code(query: str) -> Dict[str, Any]:
    """
    Generuje kod Python dla zapytania geometrycznego
    
    Args:
        query: Zapytanie użytkownika
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    # Wyodrębnij parametry z zapytania
    params = extract_parameters(query)
    
    if not params["shape"]:
        return {
            "success": False,
            "code": "",
            "error": "Nie udało się określić rodzaju figury geometrycznej"
        }
    
    # Generuj kod w zależności od figury i operacji
    if params["shape"] == "circle":
        return _generate_circle_code(params)
    elif params["shape"] == "square":
        return _generate_square_code(params)
    elif params["shape"] == "rectangle":
        return _generate_rectangle_code(params)
    elif params["shape"] == "triangle":
        return _generate_triangle_code(params)
    
    return {
        "success": False,
        "code": "",
        "error": f"Nie zaimplementowano obsługi dla figury {params['shape']}"
    }

def _generate_circle_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generuje kod dla obliczeń związanych z kołem
    
    Args:
        params: Parametry koła
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    values = params["values"]
    operation = params["operation"]
    
    # Sprawdź czy mamy promień
    if "radius" not in values:
        return {
            "success": False,
            "code": "",
            "error": "Brak promienia koła"
        }
    
    radius = values["radius"]
    
    if operation == "area":
        code = f"def execute(radius={radius}):\n    \"\"\"Oblicza pole koła o podanym promieniu.\"\"\"\n    import math\n    area = math.pi * radius ** 2\n    return area"
        
        explanation = f"Funkcja oblicza pole koła o promieniu {radius} jednostek. Używa wzoru π * r², gdzie π to stała matematyczna, a r to promień koła."
    
    elif operation == "perimeter" or operation is None:  # Domyślnie obliczamy obwód
        code = f"def execute(radius={radius}):\n    \"\"\"Oblicza obwód koła o podanym promieniu.\"\"\"\n    import math\n    circumference = 2 * math.pi * radius\n    return circumference"
        
        explanation = f"Funkcja oblicza obwód koła o promieniu {radius} jednostek. Używa wzoru 2 * π * r, gdzie π to stała matematyczna, a r to promień koła."
    
    else:
        return {
            "success": False,
            "code": "",
            "error": f"Nieznana operacja dla koła: {operation}"
        }
    
    return {
        "success": True,
        "code": code,
        "explanation": explanation,
        "shape": "circle",
        "operation": operation,
        "parameters": values
    }

def _generate_square_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generuje kod dla obliczeń związanych z kwadratem
    
    Args:
        params: Parametry kwadratu
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    values = params["values"]
    operation = params["operation"]
    
    # Sprawdź czy mamy bok
    if "side" not in values:
        return {
            "success": False,
            "code": "",
            "error": "Brak długości boku kwadratu"
        }
    
    side = values["side"]
    
    if operation == "area":
        code = f"def execute(side={side}):\n    \"\"\"Oblicza pole kwadratu o podanym boku.\"\"\"\n    area = side ** 2\n    return area"
        
        explanation = f"Funkcja oblicza pole kwadratu o boku {side} jednostek. Używa wzoru a², gdzie a to długość boku kwadratu."
    
    elif operation == "perimeter" or operation is None:  # Domyślnie obliczamy obwód
        code = f"def execute(side={side}):\n    \"\"\"Oblicza obwód kwadratu o podanym boku.\"\"\"\n    perimeter = 4 * side\n    return perimeter"
        
        explanation = f"Funkcja oblicza obwód kwadratu o boku {side} jednostek. Używa wzoru 4 * a, gdzie a to długość boku kwadratu."
    
    else:
        return {
            "success": False,
            "code": "",
            "error": f"Nieznana operacja dla kwadratu: {operation}"
        }
    
    return {
        "success": True,
        "code": code,
        "explanation": explanation,
        "shape": "square",
        "operation": operation,
        "parameters": values
    }

def _generate_rectangle_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generuje kod dla obliczeń związanych z prostokątem
    
    Args:
        params: Parametry prostokąta
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    values = params["values"]
    operation = params["operation"]
    
    # Sprawdź czy mamy długość i szerokość
    if "length" not in values or "width" not in values:
        return {
            "success": False,
            "code": "",
            "error": "Brak długości lub szerokości prostokąta"
        }
    
    length = values["length"]
    width = values["width"]
    
    if operation == "area":
        code = f"def execute(length={length}, width={width}):\n    \"\"\"Oblicza pole prostokąta o podanych wymiarach.\"\"\"\n    area = length * width\n    return area"
        
        explanation = f"Funkcja oblicza pole prostokąta o długości {length} jednostek i szerokości {width} jednostek. Używa wzoru a * b, gdzie a to długość, a b to szerokość prostokąta."
    
    elif operation == "perimeter" or operation is None:  # Domyślnie obliczamy obwód
        code = f"def execute(length={length}, width={width}):\n    \"\"\"Oblicza obwód prostokąta o podanych wymiarach.\"\"\"\n    perimeter = 2 * (length + width)\n    return perimeter"
        
        explanation = f"Funkcja oblicza obwód prostokąta o długości {length} jednostek i szerokości {width} jednostek. Używa wzoru 2 * (a + b), gdzie a to długość, a b to szerokość prostokąta."
    
    else:
        return {
            "success": False,
            "code": "",
            "error": f"Nieznana operacja dla prostokąta: {operation}"
        }
    
    return {
        "success": True,
        "code": code,
        "explanation": explanation,
        "shape": "rectangle",
        "operation": operation,
        "parameters": values
    }

def _generate_triangle_code(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generuje kod dla obliczeń związanych z trójkątem
    
    Args:
        params: Parametry trójkąta
        
    Returns:
        Dict[str, Any]: Wygenerowany kod i metadane
    """
    values = params["values"]
    operation = params["operation"]
    
    # Sprawdź czy mamy wszystkie boki
    if "a" not in values or "b" not in values or "c" not in values:
        return {
            "success": False,
            "code": "",
            "error": "Brak wszystkich boków trójkąta"
        }
    
    a = values["a"]
    b = values["b"]
    c = values["c"]
    
    if operation == "area":
        code = f"def execute(a={a}, b={b}, c={c}):\n    \"\"\"Oblicza pole trójkąta o podanych bokach (wzór Herona).\"\"\"\n    import math\n    # Sprawdź czy trójkąt istnieje\n    if a + b <= c or a + c <= b or b + c <= a:\n        return \"Trójkąt o podanych bokach nie istnieje\"\n    \n    # Półobwód\n    s = (a + b + c) / 2\n    \n    # Wzór Herona\n    area = math.sqrt(s * (s - a) * (s - b) * (s - c))\n    return area"
        
        explanation = f"Funkcja oblicza pole trójkąta o bokach {a}, {b} i {c} jednostek. Używa wzoru Herona: √(s * (s-a) * (s-b) * (s-c)), gdzie s to półobwód trójkąta."
    
    elif operation == "perimeter" or operation is None:  # Domyślnie obliczamy obwód
        code = f"def execute(a={a}, b={b}, c={c}):\n    \"\"\"Oblicza obwód trójkąta o podanych bokach.\"\"\"\n    # Sprawdź czy trójkąt istnieje\n    if a + b <= c or a + c <= b or b + c <= a:\n        return \"Trójkąt o podanych bokach nie istnieje\"\n    \n    perimeter = a + b + c\n    return perimeter"
        
        explanation = f"Funkcja oblicza obwód trójkąta o bokach {a}, {b} i {c} jednostek. Używa wzoru a + b + c, czyli sumy długości wszystkich boków."
    
    else:
        return {
            "success": False,
            "code": "",
            "error": f"Nieznana operacja dla trójkąta: {operation}"
        }
    
    return {
        "success": True,
        "code": code,
        "explanation": explanation,
        "shape": "triangle",
        "operation": operation,
        "parameters": values
    }