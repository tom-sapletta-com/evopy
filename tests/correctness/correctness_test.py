#!/usr/bin/env python3
"""
Testy poprawności dla modułów text2python i python2text

Ten skrypt testuje poprawność konwersji tekst-kod i kod-tekst
dla różnych modeli LLM, sprawdzając czy generowane wyniki
spełniają określone kryteria.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Dodaj katalog główny do ścieżki, aby zaimportować moduły Evopy
sys.path.append(str(Path(__file__).parents[2]))

# Importuj moduły Evopy
from modules.text2python import Text2Python, get_available_models as get_text2python_models
from modules.python2text import Python2Text, get_available_models as get_python2text_models

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).parent / "correctness_test.log")
    ]
)
logger = logging.getLogger("evopy-correctness-tests")

# Katalogi dla wyników testów
RESULTS_DIR = Path(__file__).parent / "results"
CODE_DIR = RESULTS_DIR / "code"
DESCRIPTION_DIR = RESULTS_DIR / "descriptions"

# Utwórz katalogi dla wyników
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(DESCRIPTION_DIR, exist_ok=True)

# Testy poprawności dla text2python
CORRECTNESS_TESTS = [
    {
        "name": "Test 1: Podstawowa funkcjonalność",
        "query": "Napisz funkcję, która oblicza sumę dwóch liczb",
        "validation_criteria": [
            {"type": "contains", "value": "def", "description": "Definicja funkcji"},
            {"type": "contains", "value": "return", "description": "Instrukcja return"},
            {"type": "execution", "expected_output_contains": "sum", "description": "Poprawne wykonanie"}
        ]
    },
    {
        "name": "Test 2: Obsługa błędów",
        "query": "Napisz funkcję, która dzieli dwie liczby z obsługą dzielenia przez zero",
        "validation_criteria": [
            {"type": "contains", "value": "try", "description": "Blok try"},
            {"type": "contains", "value": "except", "description": "Blok except"},
            {"type": "contains", "value": "ZeroDivision", "description": "Obsługa dzielenia przez zero"}
        ]
    },
    {
        "name": "Test 3: Przetwarzanie danych",
        "query": "Napisz funkcję, która filtruje listę liczb, pozostawiając tylko liczby parzyste",
        "validation_criteria": [
            {"type": "contains", "value": "filter", "description": "Użycie filter lub list comprehension"},
            {"type": "contains", "value": "% 2", "description": "Sprawdzenie parzystości"},
            {"type": "execution", "expected_output_contains": "list", "description": "Zwraca listę"}
        ]
    }
]

# Testy poprawności dla python2text
PYTHON2TEXT_TESTS = [
    {
        "name": "Test 1: Opis prostej funkcji",
        "code": """
def add_numbers(a, b):
    \"\"\"Dodaje dwie liczby i zwraca wynik.\"\"\"
    return a + b
""",
        "validation_criteria": [
            {"type": "contains", "value": "dodaje", "description": "Opis działania"},
            {"type": "contains", "value": "liczby", "description": "Opis parametrów"},
            {"type": "contains", "value": "zwraca", "description": "Opis wyniku"}
        ]
    },
    {
        "name": "Test 2: Opis funkcji z obsługą błędów",
        "code": """
def divide_numbers(a, b):
    \"\"\"Dzieli dwie liczby z obsługą dzielenia przez zero.\"\"\"
    try:
        return a / b
    except ZeroDivisionError:
        return "Nie można dzielić przez zero"
""",
        "validation_criteria": [
            {"type": "contains", "value": "dzieli", "description": "Opis działania"},
            {"type": "contains", "value": "zero", "description": "Wzmianka o dzieleniu przez zero"},
            {"type": "contains", "value": "błąd", "description": "Wzmianka o obsłudze błędu"}
        ]
    },
    {
        "name": "Test 3: Opis funkcji przetwarzającej dane",
        "code": """
def filter_even_numbers(numbers):
    \"\"\"Filtruje listę liczb, pozostawiając tylko liczby parzyste.\"\"\"
    return [num for num in numbers if num % 2 == 0]
""",
        "validation_criteria": [
            {"type": "contains", "value": "filtruje", "description": "Opis działania"},
            {"type": "contains", "value": "parzyste", "description": "Wzmianka o liczbach parzystych"},
            {"type": "contains", "value": "listę", "description": "Wzmianka o liście"}
        ]
    }
]

def execute_code(code: str) -> Dict[str, Any]:
    """
    Wykonuje kod Python i zwraca wynik
    
    Args:
        code: Kod Python do wykonania
        
    Returns:
        Dict: Wynik wykonania kodu
    """
    try:
        # Utwórz tymczasowy plik z kodem
        temp_file = CODE_DIR / f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Wykonaj kod
        result = {}
        exec_globals = {}
        exec(code, exec_globals)
        
        # Sprawdź, czy funkcja execute istnieje
        if "execute" in exec_globals:
            result["output"] = str(exec_globals["execute"]())
            result["success"] = True
        else:
            result["output"] = "Funkcja execute nie została zdefiniowana"
            result["success"] = False
        
        return result
    except Exception as e:
        return {
            "success": False,
            "output": "",
            "error": str(e)
        }

def validate_text2python_result(result: Dict[str, Any], criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sprawdza, czy wynik konwersji tekst -> Python spełnia kryteria
    
    Args:
        result: Wynik konwersji
        criteria: Lista kryteriów do sprawdzenia
        
    Returns:
        Dict: Wynik walidacji
    """
    validation_result = {
        "passed": True,
        "total_criteria": len(criteria),
        "passed_criteria": 0,
        "failed_criteria": 0,
        "details": []
    }
    
    code = result.get("code", "")
    
    for criterion in criteria:
        criterion_result = {
            "type": criterion["type"],
            "description": criterion["description"],
            "passed": False
        }
        
        if criterion["type"] == "contains":
            if criterion["value"] in code:
                criterion_result["passed"] = True
                validation_result["passed_criteria"] += 1
            else:
                criterion_result["passed"] = False
                validation_result["failed_criteria"] += 1
                validation_result["passed"] = False
        
        elif criterion["type"] == "execution":
            # Wykonaj kod
            execution_result = execute_code(code)
            
            if execution_result["success"]:
                if criterion["expected_output_contains"] in execution_result["output"]:
                    criterion_result["passed"] = True
                    validation_result["passed_criteria"] += 1
                else:
                    criterion_result["passed"] = False
                    criterion_result["reason"] = f"Oczekiwano '{criterion['expected_output_contains']}' w wyniku, otrzymano: '{execution_result['output']}'"
                    validation_result["failed_criteria"] += 1
                    validation_result["passed"] = False
            else:
                criterion_result["passed"] = False
                criterion_result["reason"] = f"Błąd wykonania: {execution_result.get('error', 'Nieznany błąd')}"
                validation_result["failed_criteria"] += 1
                validation_result["passed"] = False
        
        validation_result["details"].append(criterion_result)
    
    return validation_result

def validate_python2text_result(result: Dict[str, Any], criteria: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Sprawdza, czy wynik konwersji Python -> tekst spełnia kryteria
    
    Args:
        result: Wynik konwersji
        criteria: Lista kryteriów do sprawdzenia
        
    Returns:
        Dict: Wynik walidacji
    """
    validation_result = {
        "passed": True,
        "total_criteria": len(criteria),
        "passed_criteria": 0,
        "failed_criteria": 0,
        "details": []
    }
    
    description = result.get("description", "").lower()
    
    for criterion in criteria:
        criterion_result = {
            "type": criterion["type"],
            "description": criterion["description"],
            "passed": False
        }
        
        if criterion["type"] == "contains":
            if criterion["value"].lower() in description:
                criterion_result["passed"] = True
                validation_result["passed_criteria"] += 1
            else:
                criterion_result["passed"] = False
                validation_result["failed_criteria"] += 1
                validation_result["passed"] = False
        
        validation_result["details"].append(criterion_result)
    
    return validation_result

def test_text2python_correctness(model_name: str) -> Dict[str, Any]:
    """
    Testuje poprawność konwersji tekst -> Python dla danego modelu
    
    Args:
        model_name: Nazwa modelu do testowania
        
    Returns:
        Dict: Wyniki testów
    """
    logger.info(f"Testowanie poprawności konwersji tekst -> Python dla modelu {model_name}...")
    
    results = {
        "model_name": model_name,
        "total_tests": len(CORRECTNESS_TESTS),
        "passed": 0,
        "failed": 0,
        "timestamp": datetime.now().isoformat(),
        "details": []
    }
    
    # Inicjalizacja konwertera
    text2python = Text2Python(model_name=model_name, code_dir=CODE_DIR)
    
    # Sprawdź, czy model jest dostępny
    if not text2python.ensure_model_available():
        logger.error(f"Model {model_name} nie jest dostępny. Testy nie mogą być wykonane.")
        results["error"] = f"Model {model_name} nie jest dostępny"
        return results
    
    # Uruchom testy dla każdego przypadku
    for test_case in CORRECTNESS_TESTS:
        test_name = test_case["name"]
        query = test_case["query"]
        criteria = test_case["validation_criteria"]
        
        test_result = {
            "name": test_name,
            "query": query,
            "status": "FAILED"
        }
        
        logger.info(f"Testowanie przypadku: {test_name}")
        
        try:
            # Generuj kod
            generation_result = text2python.generate_code(query)
            
            # Waliduj wynik
            validation_result = validate_text2python_result(generation_result, criteria)
            
            test_result["code"] = generation_result.get("code", "")
            test_result["explanation"] = generation_result.get("explanation", "")
            test_result["validation"] = validation_result
            
            if validation_result["passed"]:
                test_result["status"] = "PASSED"
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(test_result)
            
        except Exception as e:
            logger.error(f"Błąd podczas testowania przypadku {test_name}: {e}")
            test_result["error"] = str(e)
            results["failed"] += 1
            results["details"].append(test_result)
    
    return results

def test_python2text_correctness(model_name: str) -> Dict[str, Any]:
    """
    Testuje poprawność konwersji Python -> tekst dla danego modelu
    
    Args:
        model_name: Nazwa modelu do testowania
        
    Returns:
        Dict: Wyniki testów
    """
    logger.info(f"Testowanie poprawności konwersji Python -> tekst dla modelu {model_name}...")
    
    results = {
        "model_name": model_name,
        "total_tests": len(PYTHON2TEXT_TESTS),
        "passed": 0,
        "failed": 0,
        "timestamp": datetime.now().isoformat(),
        "details": []
    }
    
    # Inicjalizacja konwertera
    python2text = Python2Text(model_name=model_name, output_dir=DESCRIPTION_DIR)
    
    # Sprawdź, czy model jest dostępny
    if not python2text.ensure_model_available():
        logger.error(f"Model {model_name} nie jest dostępny. Testy nie mogą być wykonane.")
        results["error"] = f"Model {model_name} nie jest dostępny"
        return results
    
    # Uruchom testy dla każdego przypadku
    for test_case in PYTHON2TEXT_TESTS:
        test_name = test_case["name"]
        code = test_case["code"]
        criteria = test_case["validation_criteria"]
        
        test_result = {
            "name": test_name,
            "code_length": len(code),
            "status": "FAILED"
        }
        
        logger.info(f"Testowanie przypadku: {test_name}")
        
        try:
            # Generuj opis
            generation_result = python2text.generate_description(code)
            
            # Waliduj wynik
            validation_result = validate_python2text_result(generation_result, criteria)
            
            test_result["description"] = generation_result.get("description", "")
            test_result["validation"] = validation_result
            
            if validation_result["passed"]:
                test_result["status"] = "PASSED"
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append(test_result)
            
        except Exception as e:
            logger.error(f"Błąd podczas testowania przypadku {test_name}: {e}")
            test_result["error"] = str(e)
            results["failed"] += 1
            results["details"].append(test_result)
    
    return results

def save_results(results: Dict[str, Any], test_type: str) -> str:
    """
    Zapisuje wyniki testów do pliku JSON
    
    Args:
        results: Wyniki testów
        test_type: Typ testu ("text2python" lub "python2text")
        
    Returns:
        str: Ścieżka do zapisanego pliku
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = results["model_name"]
    filename = f"{test_type}_correctness_{model_name}_{timestamp}.json"
    file_path = RESULTS_DIR / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Zapisano wyniki testów do pliku: {file_path}")
    
    return str(file_path)

def main():
    """
    Główna funkcja uruchamiająca testy poprawności
    """
    parser = argparse.ArgumentParser(description="Testy poprawności dla modułów text2python i python2text")
    parser.add_argument("--model", type=str, help="Identyfikator modelu do testowania (deepsek, llama, bielik)")
    parser.add_argument("--all-models", action="store_true", help="Testuj wszystkie dostępne modele")
    parser.add_argument("--text2python", action="store_true", help="Testuj tylko konwersję tekst -> Python")
    parser.add_argument("--python2text", action="store_true", help="Testuj tylko konwersję Python -> tekst")
    args = parser.parse_args()
    
    # Jeśli nie podano żadnych opcji, testuj wszystko
    if not args.text2python and not args.python2text:
        args.text2python = True
        args.python2text = True
    
    # Pobierz dostępne modele
    models = []
    if args.model:
        models = [args.model]
    elif args.all_models:
        models = [model["id"] for model in get_text2python_models()]
    else:
        # Domyślnie użyj modelu z .env
        models = ["deepsek"]
    
    # Uruchom testy dla każdego modelu
    for model_name in models:
        logger.info(f"Rozpoczynanie testów poprawności dla modelu: {model_name}")
        
        if args.text2python:
            text2python_results = test_text2python_correctness(model_name)
            save_results(text2python_results, "text2python")
            
            # Wyświetl podsumowanie
            logger.info(f"Wyniki testów poprawności text2python dla modelu {model_name}:")
            logger.info(f"Zaliczone: {text2python_results['passed']}/{text2python_results['total_tests']}")
        
        if args.python2text:
            python2text_results = test_python2text_correctness(model_name)
            save_results(python2text_results, "python2text")
            
            # Wyświetl podsumowanie
            logger.info(f"Wyniki testów poprawności python2text dla modelu {model_name}:")
            logger.info(f"Zaliczone: {python2text_results['passed']}/{python2text_results['total_tests']}")
    
    logger.info("Testy poprawności zakończone")

if __name__ == "__main__":
    main()
