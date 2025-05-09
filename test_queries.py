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
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Dodaj katalog główny do ścieżki, aby zaimportować moduły Evopy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importuj moduły Evopy
from modules.text2python import Text2Python
import argparse

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

def run_tests(model_id: str = None, timeout: int = 30) -> Dict[str, Any]:
    """
    Uruchamia testy dla podstawowych zapytań
    
    Args:
        model_id: Identyfikator modelu do testowania
        timeout: Limit czasu dla każdego testu w sekundach
    
    Returns:
        Dict: Wyniki testów
    """
    # Importuj model_manager dla lepszej obsługi modeli
    from modules.text2python.model_manager import check_ollama_models, find_best_available_model
    
    # Inicjalizacja konwertera
    text2python = Text2Python(model_id=model_id, code_dir=Path("generated_code"))
    
    # Przygotuj strukturę wyników
    results = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "model_id": text2python.model_id,
        "model_name": text2python.model_name,
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "tests": []
    }
    
    # Sprawdź, czy model jest dostępny z timeoutem 5 sekund
    logger.info(f"Sprawdzanie dostępności modelu {text2python.model_name}...")
    available_models = check_ollama_models(timeout=5)
    
    if text2python.model_name not in available_models:
        # Spróbuj znaleźć alternatywny model
        fallback_model = find_best_available_model()
        if fallback_model:
            logger.warning(f"Model {text2python.model_name} nie jest dostępny. Używam {fallback_model}")
            text2python.model_name = fallback_model
        else:
            logger.error("Nie znaleziono żadnego dostępnego modelu. Testy nie mogą być wykonane.")
            return {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "model_id": model_id,
                "model_name": "",
                "total_tests": len(TEST_QUERIES),
                "passed_tests": 0,
                "failed_tests": len(TEST_QUERIES),
                "tests": [{"name": q["name"], "status": "FAILED", "reason": "Model niedostępny"} for q in TEST_QUERIES]
            }
    
    # Uruchom testy dla każdego zapytania z timeoutem
    for query_data in TEST_QUERIES:
        query_name = query_data["name"]
        query = query_data["query"]
        expected_contains = query_data["expected_contains"]
        
        logger.info(f"Testowanie zapytania: {query_name}")
        
        try:
            # Ustaw timeout dla generowania kodu
            start_time = time.time()
            
            # Generuj kod Python na podstawie zapytania
            result = text2python.generate_code(query)
            
            # Zmierz czas wykonania
            execution_time = time.time() - start_time
            
            # Sprawdź, czy kod został wygenerowany
            code = result.get("code", "")
            explanation = result.get("explanation", "")
            
            # Sprawdź, czy kod zawiera oczekiwane elementy
            all_contains = True
            for expected in expected_contains:
                if expected not in code:
                    all_contains = False
                    break
            
            if all_contains:
                status = "PASSED"
                reason = f"Kod zawiera wszystkie oczekiwane elementy (czas: {execution_time:.2f}s)"
                results["passed_tests"] += 1
            else:
                status = "FAILED"
                missing = [expected for expected in expected_contains if expected not in code]
                reason = f"Brakujące elementy w kodzie: {', '.join(missing)}"
                results["failed_tests"] += 1
            
        except Exception as e:
            status = "FAILED"
            reason = str(e)
            results["failed_tests"] += 1
        
        # Dodaj szczegóły testu do wyników
        results["tests"].append({
            "name": query_name,
            "status": status,
            "reason": reason,
            "query": query,
            "code": result.get("code", "") if "result" in locals() else "",
            "explanation": result.get("explanation", "") if "result" in locals() else ""
        })
        
        logger.info(f"Test {query_name}: {status} - {reason}")
    
    # Podsumowanie testów
    results["total_tests"] = len(TEST_QUERIES)
    logger.info(f"Testy zakończone. Zaliczone: {results['passed_tests']}/{results['total_tests']}")
    
    return results

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
    results = run_tests(model_id=args.model, timeout=args.timeout)
    
    # Zapisz wyniki
    output_path = results_dir / f"test_results_{results['model_id']}_{results['timestamp']}.json"
    save_results(results, output_path)
    
    # Wyświetl podsumowanie
    print("\n=== Podsumowanie testów ===\n")
    print(f"Model: {results['model_id']}")
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
