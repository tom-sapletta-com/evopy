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
import logging
from pathlib import Path
from typing import Dict, Any, List

# Dodaj katalog główny do ścieżki, aby zaimportować moduły Evopy
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importuj moduły Evopy
from text2python import Text2Python

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

def run_tests() -> Dict[str, Any]:
    """
    Uruchamia testy dla podstawowych zapytań
    
    Returns:
        Dict: Wyniki testów
    """
    results = {
        "total": len(TEST_QUERIES),
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Inicjalizacja konwertera tekst-na-Python
    text2python = Text2Python(model_name="llama3")
    
    # Sprawdź, czy model jest dostępny
    if not text2python.ensure_model_available():
        logger.error("Model llama3 nie jest dostępny. Testy nie mogą być wykonane.")
        return {
            "total": len(TEST_QUERIES),
            "passed": 0,
            "failed": len(TEST_QUERIES),
            "details": [{"name": q["name"], "status": "FAILED", "reason": "Model niedostępny"} for q in TEST_QUERIES]
        }
    
    # Uruchom testy dla każdego zapytania
    for query_data in TEST_QUERIES:
        query_name = query_data["name"]
        query = query_data["query"]
        expected_contains = query_data["expected_contains"]
        
        logger.info(f"Testowanie zapytania: {query_name}")
        
        try:
            # Generuj kod Python na podstawie zapytania
            result = text2python.generate_code(query)
            
            # Sprawdź, czy kod został wygenerowany
            if not result.get("code"):
                raise Exception("Nie wygenerowano kodu Python")
            
            # Sprawdź, czy wyjaśnienie zostało wygenerowane
            if not result.get("explanation"):
                raise Exception("Nie wygenerowano wyjaśnienia kodu")
            
            # Sprawdź, czy analiza została wygenerowana
            if not result.get("analysis"):
                raise Exception("Nie wygenerowano analizy logicznej kodu")
            
            # Sprawdź, czy kod zawiera oczekiwane elementy
            code = result["code"]
            all_contains = all(expected in code for expected in expected_contains)
            
            if all_contains:
                status = "PASSED"
                reason = "Kod zawiera wszystkie oczekiwane elementy"
                results["passed"] += 1
            else:
                status = "FAILED"
                missing = [expected for expected in expected_contains if expected not in code]
                reason = f"Kod nie zawiera oczekiwanych elementów: {', '.join(missing)}"
                results["failed"] += 1
            
        except Exception as e:
            status = "FAILED"
            reason = str(e)
            results["failed"] += 1
        
        # Dodaj szczegóły testu do wyników
        results["details"].append({
            "name": query_name,
            "status": status,
            "reason": reason,
            "query": query,
            "code": result.get("code", "") if "result" in locals() else "",
            "explanation": result.get("explanation", "") if "result" in locals() else ""
        })
        
        logger.info(f"Test {query_name}: {status} - {reason}")
    
    # Podsumowanie testów
    logger.info(f"Testy zakończone. Zaliczone: {results['passed']}/{results['total']}")
    
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
    logger.info("Rozpoczynanie testów podstawowych zapytań dla Evopy")
    
    # Uruchom testy
    results = run_tests()
    
    # Zapisz wyniki
    save_results(results)
    
    # Wyświetl podsumowanie
    print("\n" + "="*50)
    print(f"PODSUMOWANIE TESTÓW: {results['passed']}/{results['total']} zaliczonych")
    print("="*50)
    
    for detail in results["details"]:
        status_symbol = "✓" if detail["status"] == "PASSED" else "✗"
        print(f"{status_symbol} {detail['name']}: {detail['reason']}")
    
    # Zwróć kod wyjścia
    return 0 if results["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
