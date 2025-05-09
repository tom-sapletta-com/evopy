#!/usr/bin/env python3
"""
Testy wydajności dla modułów text2python i python2text

Ten skrypt testuje wydajność i poprawność różnych modeli LLM
w zadaniach konwersji tekstu na kod Python i kodu Python na tekst.
"""

import os
import sys
import json
import time
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
        logging.FileHandler(Path(__file__).parent / "performance_test.log")
    ]
)
logger = logging.getLogger("evopy-performance-tests")

# Katalogi dla wyników testów
RESULTS_DIR = Path(__file__).parent / "results"
CODE_DIR = RESULTS_DIR / "code"
DESCRIPTION_DIR = RESULTS_DIR / "descriptions"

# Utwórz katalogi dla wyników
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(CODE_DIR, exist_ok=True)
os.makedirs(DESCRIPTION_DIR, exist_ok=True)

# Zapytania testowe dla text2python
TEXT2PYTHON_TEST_QUERIES = [
    {
        "name": "Proste zapytanie tekstowe",
        "query": "Wyświetl aktualną datę i godzinę",
        "expected_contains": ["import datetime", "datetime.now()"]
    },
    {
        "name": "Zapytanie matematyczne",
        "query": "Oblicz sumę liczb od 1 do 100",
        "expected_contains": ["sum(range(1, 101))", "5050"]
    },
    {
        "name": "Zapytanie z przetwarzaniem tekstu",
        "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
        "expected_contains": ["re.findall", "aeiou", "oeiaa"]
    }
]

# Przykładowe kody dla python2text
PYTHON2TEXT_TEST_CODES = [
    {
        "name": "Prosty kod daty i czasu",
        "code": """
def execute():
    import datetime
    now = datetime.datetime.now()
    return f"Aktualna data i czas: {now.strftime('%Y-%m-%d %H:%M:%S')}"
""",
        "expected_contains": ["data", "czas", "datetime"]
    },
    {
        "name": "Kod matematyczny",
        "code": """
def execute():
    # Obliczanie sumy liczb od 1 do 100
    total = sum(range(1, 101))
    return f"Suma liczb od 1 do 100 wynosi: {total}"
""",
        "expected_contains": ["suma", "liczb", "1", "100"]
    },
    {
        "name": "Kod przetwarzania tekstu",
        "code": """
def execute():
    import re
    text = "Python jest wspaniały"
    vowels = re.findall(r'[aeiou]', text.lower())
    return f"Samogłoski w tekście '{text}': {', '.join(vowels)}"
""",
        "expected_contains": ["samogłoski", "tekst", "Python"]
    }
]

def test_text2python(model_name: str) -> Dict[str, Any]:
    """
    Testuje wydajność i poprawność modelu w konwersji tekstu na kod Python
    
    Args:
        model_name: Nazwa modelu do testowania
        
    Returns:
        Dict: Wyniki testów
    """
    logger.info(f"Testowanie modelu {model_name} w konwersji tekst -> Python...")
    
    results = {
        "model_name": model_name,
        "total_queries": len(TEXT2PYTHON_TEST_QUERIES),
        "passed": 0,
        "failed": 0,
        "total_time": 0,
        "avg_time": 0,
        "details": []
    }
    
    # Inicjalizacja konwertera text2python
    text2python = Text2Python(model_name=model_name, code_dir=CODE_DIR)
    
    # Sprawdź, czy model jest dostępny
    if not text2python.ensure_model_available():
        logger.error(f"Model {model_name} nie jest dostępny. Testy nie mogą być wykonane.")
        results["error"] = f"Model {model_name} nie jest dostępny"
        return results
    
    # Uruchom testy dla każdego zapytania
    start_time_total = time.time()
    
    for query_data in TEXT2PYTHON_TEST_QUERIES:
        query_name = query_data["name"]
        query = query_data["query"]
        expected_contains = query_data["expected_contains"]
        
        query_result = {
            "name": query_name,
            "query": query,
            "expected_contains": expected_contains,
            "status": "FAILED",
            "time": 0
        }
        
        logger.info(f"Testowanie zapytania: {query_name}")
        
        try:
            # Zmierz czas generowania kodu
            start_time = time.time()
            result = text2python.generate_code(query)
            end_time = time.time()
            execution_time = end_time - start_time
            
            query_result["time"] = execution_time
            query_result["code"] = result.get("code", "")
            query_result["explanation"] = result.get("explanation", "")
            
            # Sprawdź, czy kod został wygenerowany
            if not result.get("code"):
                query_result["reason"] = "Nie wygenerowano kodu Python"
                results["failed"] += 1
                results["details"].append(query_result)
                continue
            
            # Sprawdź, czy wyjaśnienie zostało wygenerowane
            if not result.get("explanation"):
                query_result["reason"] = "Nie wygenerowano wyjaśnienia kodu"
                results["failed"] += 1
                results["details"].append(query_result)
                continue
            
            # Sprawdź, czy kod zawiera oczekiwane elementy
            all_expected_found = True
            missing_elements = []
            
            for expected in expected_contains:
                if expected not in result["code"]:
                    all_expected_found = False
                    missing_elements.append(expected)
            
            if all_expected_found:
                query_result["status"] = "PASSED"
                results["passed"] += 1
            else:
                query_result["status"] = "FAILED"
                query_result["reason"] = f"Brakujące elementy: {', '.join(missing_elements)}"
                results["failed"] += 1
            
            results["details"].append(query_result)
            
        except Exception as e:
            logger.error(f"Błąd podczas testowania zapytania {query_name}: {e}")
            query_result["reason"] = str(e)
            results["failed"] += 1
            results["details"].append(query_result)
    
    end_time_total = time.time()
    total_time = end_time_total - start_time_total
    
    # Oblicz statystyki
    results["total_time"] = total_time
    if len(TEXT2PYTHON_TEST_QUERIES) > 0:
        results["avg_time"] = total_time / len(TEXT2PYTHON_TEST_QUERIES)
    
    return results

def test_python2text(model_name: str) -> Dict[str, Any]:
    """
    Testuje wydajność i poprawność modelu w konwersji kodu Python na tekst
    
    Args:
        model_name: Nazwa modelu do testowania
        
    Returns:
        Dict: Wyniki testów
    """
    logger.info(f"Testowanie modelu {model_name} w konwersji Python -> tekst...")
    
    results = {
        "model_name": model_name,
        "total_codes": len(PYTHON2TEXT_TEST_CODES),
        "passed": 0,
        "failed": 0,
        "total_time": 0,
        "avg_time": 0,
        "details": []
    }
    
    # Inicjalizacja konwertera python2text
    python2text = Python2Text(model_name=model_name, output_dir=DESCRIPTION_DIR)
    
    # Sprawdź, czy model jest dostępny
    if not python2text.ensure_model_available():
        logger.error(f"Model {model_name} nie jest dostępny. Testy nie mogą być wykonane.")
        results["error"] = f"Model {model_name} nie jest dostępny"
        return results
    
    # Uruchom testy dla każdego kodu
    start_time_total = time.time()
    
    for code_data in PYTHON2TEXT_TEST_CODES:
        code_name = code_data["name"]
        code = code_data["code"]
        expected_contains = code_data["expected_contains"]
        
        code_result = {
            "name": code_name,
            "code_length": len(code),
            "expected_contains": expected_contains,
            "status": "FAILED",
            "time": 0
        }
        
        logger.info(f"Testowanie kodu: {code_name}")
        
        try:
            # Zmierz czas generowania opisu
            start_time = time.time()
            result = python2text.generate_description(code)
            end_time = time.time()
            execution_time = end_time - start_time
            
            code_result["time"] = execution_time
            code_result["description"] = result.get("description", "")
            
            # Sprawdź, czy opis został wygenerowany
            if not result.get("description"):
                code_result["reason"] = "Nie wygenerowano opisu"
                results["failed"] += 1
                results["details"].append(code_result)
                continue
            
            # Sprawdź, czy opis zawiera oczekiwane elementy
            all_expected_found = True
            missing_elements = []
            
            for expected in expected_contains:
                if expected.lower() not in result["description"].lower():
                    all_expected_found = False
                    missing_elements.append(expected)
            
            if all_expected_found:
                code_result["status"] = "PASSED"
                results["passed"] += 1
            else:
                code_result["status"] = "FAILED"
                code_result["reason"] = f"Brakujące elementy: {', '.join(missing_elements)}"
                results["failed"] += 1
            
            results["details"].append(code_result)
            
        except Exception as e:
            logger.error(f"Błąd podczas testowania kodu {code_name}: {e}")
            code_result["reason"] = str(e)
            results["failed"] += 1
            results["details"].append(code_result)
    
    end_time_total = time.time()
    total_time = end_time_total - start_time_total
    
    # Oblicz statystyki
    results["total_time"] = total_time
    if len(PYTHON2TEXT_TEST_CODES) > 0:
        results["avg_time"] = total_time / len(PYTHON2TEXT_TEST_CODES)
    
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
    filename = f"{test_type}_{model_name}_{timestamp}.json"
    file_path = RESULTS_DIR / filename
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Zapisano wyniki testów do pliku: {file_path}")
    
    return str(file_path)

def main():
    """
    Główna funkcja uruchamiająca testy wydajności
    """
    parser = argparse.ArgumentParser(description="Testy wydajności dla modułów text2python i python2text")
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
        logger.info(f"Rozpoczynanie testów dla modelu: {model_name}")
        
        if args.text2python:
            text2python_results = test_text2python(model_name)
            save_results(text2python_results, "text2python")
            
            # Wyświetl podsumowanie
            logger.info(f"Wyniki testów text2python dla modelu {model_name}:")
            logger.info(f"Zaliczone: {text2python_results['passed']}/{text2python_results['total_queries']}")
            logger.info(f"Całkowity czas: {text2python_results['total_time']:.2f}s")
            logger.info(f"Średni czas: {text2python_results['avg_time']:.2f}s")
        
        if args.python2text:
            python2text_results = test_python2text(model_name)
            save_results(python2text_results, "python2text")
            
            # Wyświetl podsumowanie
            logger.info(f"Wyniki testów python2text dla modelu {model_name}:")
            logger.info(f"Zaliczone: {python2text_results['passed']}/{python2text_results['total_codes']}")
            logger.info(f"Całkowity czas: {python2text_results['total_time']:.2f}s")
            logger.info(f"Średni czas: {python2text_results['avg_time']:.2f}s")
    
    logger.info("Testy wydajności zakończone")

if __name__ == "__main__":
    main()
