#!/usr/bin/env python3
"""
Test podstawowych zapytań dla Evopy

Ten skrypt testuje trzy podstawowe typy zapytań do Evopy:
1. Proste zapytanie tekstowe
2. Zapytanie wymagające konwersji na kod Python
3. Zapytanie wymagające konwersji i weryfikacji intencji

Skrypt sprawdza, czy system poprawnie konwertuje zapytania na kod Python,
generuje wyjaśnienia i przeprowadza analizę logiczną kodu.
"""

import os
import sys
import json
import time
import logging
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Import modułów oceny jakości i wydajności kodu
from code_quality import evaluate_code_quality, evaluate_explanation_clarity
from code_efficiency import analyze_code_efficiency, integrate_with_dependency_manager

# Dodaj katalog główny do ścieżki, aby zaimportować moduły Evopy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importuj moduł resource_manager do dostosowywania timeout'u
from modules.utils.resource_manager import get_adjusted_timeout

# Importuj moduły Evopy
from modules.text2python import Text2Python

def setup_logging():
    """Konfiguracja logowania"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("test_queries.log")
        ]
    )
    return logging.getLogger("evopy-tests")

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("evopy-tests")

# Zapytania testowe
TEST_QUERIES = [
    {
        "name": "Proste zapytanie tekstowe",
        "query": "Wyświetl aktualną datę i godzinę",
        "expected_contains": ["datetime"]
    },
    {
        "name": "Zapytanie matematyczne",
        "query": "Oblicz sumę liczb od 1 do 100",
        "expected_contains": ["sum", "range"]
    },
    {
        "name": "Zapytanie z przetwarzaniem tekstu",
        "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
        "expected_contains": ["vowels"]
    }
]

def run_tests(model_name="llama3", timeout=None, test_case=None):
    """
    Uruchamia testy dla podanego modelu z timeoutem
    
    Args:
        model_name: Nazwa modelu do testowania
        timeout: Limit czasu w sekundach dla każdego testu (opcjonalnie, jeśli None, zostanie dostosowany automatycznie)
        test_case: Opcjonalny konkretny przypadek testowy do uruchomienia
        
    Returns:
        Dict: Słownik z wynikami testów
    """
    # Konfiguracja loggera
    setup_logging()
    
    # Jeśli timeout nie został podany, dostosuj go automatycznie do zasobów sprzętowych
    if timeout is None:
        timeout = get_adjusted_timeout()
        logger.info(f"Automatycznie dostosowano timeout do zasobów sprzętowych: {timeout}s")
    
    # Informacja o rozpoczęciu testów
    logger.info(f"Rozpoczynam testy z modelem {model_name} (timeout: {timeout}s)")
    
    # Sprawdzenie dostępności Ollama przed próbą użycia modelu
    # Importujemy funkcję check_ollama_running z model_manager
    from modules.text2python.model_manager import check_ollama_running
    
    if not check_ollama_running(timeout=5):
        logger.error("Serwer Ollama nie jest uruchomiony. Uruchom go przed rozpoczęciem testów.")
        logger.info("Możesz uruchomić Ollama poleceniem: ollama serve")
        return {
            "model_name": model_name,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "details": [],
            "error": "Serwer Ollama nie jest uruchomiony"
        }
    
    # Inicjalizacja Text2Python z podanym modelem
    try:
        text2python = Text2Python(model_name=model_name)
        # Zapisujemy timeout jako atrybut do późniejszego wykorzystania
        text2python.timeout = timeout
    except Exception as e:
        logger.error(f"Błąd podczas inicjalizacji Text2Python: {str(e)}")
        return {
            "model_name": model_name,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "details": [],
            "error": f"Błąd inicjalizacji: {str(e)}"
        }
    
    # Sprawdź dostępność modelu
    logger.info(f"Sprawdzanie dostępności modelu {model_name}...")
    model_available = text2python.ensure_model_available()
    
    if not model_available:
        # Nie przerywaj testów, jeśli model_manager już dokonał fallbacku do innego modelu
        if text2python.model_name != model_name:
            logger.warning(f"Kontynuuję testy z modelem zastępczym: {text2python.model_name}")
        else:
            logger.error(f"Model {model_name} nie jest dostępny i nie znaleziono modelu zastępczego")
            return {
                "model_id": model_name,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "details": [],
                "error": "Model niedostępny"
            }
    
    # Przygotowanie słownika przypadków testowych z listy TEST_QUERIES
    test_cases = {query['name']: query for query in TEST_QUERIES}
    
    # Informacja o liczbie testów
    total_tests = len(test_cases) if not test_case else 1
    logger.info(f"Liczba testów do wykonania: {total_tests}")
    
    # Uruchom testy
    if test_case:
        # Uruchom tylko konkretny test
        if test_case in test_cases:
            run_test_case(text2python, test_case, test_cases[test_case])
        else:
            logger.error(f"Nieznany przypadek testowy: {test_case}")
            logger.info(f"Dostępne przypadki testowe: {', '.join(test_cases.keys())}")
    else:
        # Uruchom wszystkie testy
        successful_tests = 0
        test_results = []
        
        for case_name, case_data in test_cases.items():
            # Uruchom test i pobierz szczegółowe wyniki
            test_result = run_test_case(text2python, case_name, case_data)
            test_results.append(test_result)
            
            # Zliczaj udane testy
            if test_result["status"] == "PASSED":
                successful_tests += 1
        
        # Podsumowanie testów
        logger.info(f"Podsumowanie testów: {successful_tests}/{total_tests} zakończonych sukcesem")
        if successful_tests < total_tests:
            logger.warning(f"Nie wszystkie testy zakończyły się sukcesem. Sprawdź logi po szczegóły.")
        
        # Przygotuj wyniki do zwrócenia
        results = {
            "model_name": model_name,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "total_tests": total_tests,
            "passed_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "tests": test_results  # Dodajemy szczegółowe wyniki testów
        }
        
        return results


def run_test_case(text2python, case_name, case_data):
    """
    Uruchamia pojedynczy przypadek testowy
    
    Args:
        text2python: Instancja Text2Python
        case_name: Nazwa przypadku testowego
        case_data: Dane przypadku testowego
    
    Returns:
        dict: Słownik z informacjami o wyniku testu
    """
    logger.info(f"Testowanie przypadku: {case_name}")
    
    # Pobierz dane przypadku testowego
    query = case_data["query"]
    expected_output = case_data.get("expected_output", None)
    expected_contains = case_data.get("expected_contains", [])
    
    try:
        # Ustaw timeout dla generowania kodu
        start_time = time.time()
        
        # Analizuj zapytanie
        logger.info(f"Analizowanie zapytania: '{query}'")
        
        # Generuj kod Python na podstawie zapytania z określonym timeoutem
        result = text2python.generate_code(query, timeout=text2python.timeout)
        
        # Zmierz czas wykonania
        execution_time = time.time() - start_time
        logger.info(f"Czas generowania kodu: {execution_time:.2f}s")
        
        # Sprawdź, czy kod został wygenerowany
        if not result or "code" not in result:
            logger.error(f"Nie wygenerowano kodu dla zapytania: {query}")
            return False
        
        code = result.get("code", "")
        explanation = result.get("explanation", "")
        
        # Sprawdź, czy kod zawiera oczekiwane elementy
        if expected_contains:
            all_contains = True
            missing_elements = []
            
            for expected in expected_contains:
                if expected not in code:
                    all_contains = False
                    missing_elements.append(expected)
            
            if not all_contains:
                logger.error(f"Brakujące elementy w kodzie: {', '.join(missing_elements)}")
                logger.debug(f"Wygenerowany kod:\n{code}")
                return False
        
        # Sprawdź oczekiwany wynik, jeśli został podany
        if expected_output is not None:
            # Tutaj można dodać wykonanie kodu i sprawdzenie wyniku
            # Używając dependency_manager i docker_sandbox
            pass
        
        # Integracja z systemem autonaprawy zależności
        logger.info("Integracja z systemem autonaprawy zależności...")
        fixed_code, efficiency_metrics = integrate_with_dependency_manager(code)
        
        # Jeśli kod został zmieniony, zaktualizuj go
        if fixed_code != code:
            logger.info("Kod został poprawiony przez system autonaprawy zależności")
            code = fixed_code
        
        # Ocena jakości kodu i wyjaśnień
        logger.info("Ocena jakości kodu i wyjaśnień...")
        quality_metrics = evaluate_code_quality(code, explanation)
        
        # Obliczenie liczby linii kodu
        code_lines = len(code.strip().split('\n'))
        
        logger.info(f"Test {case_name} zakończony sukcesem (czas: {execution_time:.2f}s)")
        return {
            "name": case_name,
            "status": "PASSED",
            "reason": f"Test zakończony sukcesem (czas: {execution_time:.2f}s)",
            "execution_time": execution_time,
            "code": code,
            "explanation": explanation,
            "code_lines": code_lines,
            "quality_metrics": {
                "documentation_quality": quality_metrics["documentation_quality"],
                "code_readability": quality_metrics["code_readability"],
                "explanation_clarity": quality_metrics["explanation_clarity"],
                "maintainability_index": quality_metrics["maintainability_index"],
                "overall_quality_score": quality_metrics["overall_quality_score"]
            },
            "efficiency_metrics": {
                "time_complexity": efficiency_metrics["time_complexity"],
                "time_complexity_score": efficiency_metrics["time_complexity_score"],
                "space_complexity": efficiency_metrics["space_complexity"],
                "space_complexity_score": efficiency_metrics["space_complexity_score"],
                "code_size_efficiency": efficiency_metrics["code_size_efficiency"],
                "overall_efficiency_score": efficiency_metrics["overall_efficiency_score"]
            }
        }
        
    except subprocess.TimeoutExpired:
        error_msg = f"Przekroczono limit czasu podczas generowania kodu dla zapytania: {query}"
        logger.error(error_msg)
        return {
            "name": case_name,
            "status": "FAILED",
            "reason": error_msg,
            "execution_time": time.time() - start_time
        }
    except Exception as e:
        error_msg = f"Błąd podczas testowania przypadku {case_name}: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Szczegóły błędu:", exc_info=True)
        return {
            "name": case_name,
            "status": "FAILED",
            "reason": error_msg,
            "execution_time": time.time() - start_time
        }

def save_results(results: Dict[str, Any], output_path: str = None) -> None:
    """
    Zapisuje wyniki testów do pliku JSON
    
    Args:
        results: Wyniki testów
        output_path: Ścieżka do pliku wyjściowego (opcjonalnie)
    """
    if output_path is None:
        output_path = Path(__file__).parent / "test_results.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Wyniki testów zapisane do: {output_path}")

def main():
    """
    Główna funkcja uruchamiająca testy
    """
    # Parsowanie argumentów wiersza poleceń
    parser = argparse.ArgumentParser(description="Testy podstawowych zapytań dla Evopy")
    parser.add_argument("--model", type=str, help="Identyfikator modelu do testowania (deepsek, llama, bielik)")
    parser.add_argument("--timeout", type=int, default=30, help="Limit czasu dla każdego testu w sekundach (domyślnie: 30)")
    args = parser.parse_args()
    
    print("\n=== Uruchamianie testów podstawowych zapytań ===\n")
    
    # Utwórz katalog na wyniki testów
    results_dir = Path("test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Uruchom testy z wybranym modelem i timeoutem
    results = run_tests(model_name=args.model, timeout=args.timeout)
    
    # Zapisz wyniki
    output_path = results_dir / f"test_results_{results['model_name']}_{results['timestamp']}.json"
    save_results(results, output_path)
    
    # Wyświetl podsumowanie
    print("\n=== Podsumowanie testów ===\n")
    print(f"Model: {results['model_name']}")
    print(f"Przeprowadzono {results['total_tests']} testów")
    print(f"Zaliczone: {results['passed_tests']}")
    print(f"Niezaliczone: {results['failed_tests']}")
    
    for detail in results["tests"]:
        status_symbol = "✓" if detail["status"] == "PASSED" else "✗"
        print(f"{status_symbol} {detail['name']}: {detail['reason']}")
    
    # Zwróć kod wyjścia
    return 0 if results['failed_tests'] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
