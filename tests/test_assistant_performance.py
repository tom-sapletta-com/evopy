#!/usr/bin/env python3
"""
Test Assistant Performance - Testy wydajności asystenta evopy

Ten moduł zawiera testy wydajności asystenta evopy dla różnych zadań,
które powinien umieć wykonać junior programista.
"""

import os
import sys
import json
import time
import uuid
import logging
import requests
import subprocess
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime

# Dodaj katalog główny projektu do ścieżki importu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modułów projektu
from modules.text2python.text2python import Text2Python
from docker_sandbox import DockerSandbox

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_performance.log")
    ]
)
logger = logging.getLogger("evopy-tests")

# Stałe
TEST_DIR = Path(__file__).parent
SANDBOX_DIR = Path.home() / ".evo-assistant" / "sandbox"
CODE_DIR = Path.home() / ".evo-assistant" / "code"
RESULTS_DIR = TEST_DIR / "results"

# Upewnij się, że katalogi istnieją
for directory in [SANDBOX_DIR, CODE_DIR, RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)

class AssistantTester:
    """Klasa do testowania wydajności asystenta evopy"""
    
    def __init__(self, model_name: str = "deepseek-coder:instruct-6.7b"):
        """
        Inicjalizacja testera asystenta
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
        """
        self.model_name = model_name
        self.text2python = Text2Python(model_name=model_name, code_dir=CODE_DIR)
        self.results = {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
    
    def run_tests(self, test_cases: List[Dict[str, Any]]):
        """
        Uruchamia testy wydajności dla podanych przypadków testowych
        
        Args:
            test_cases: Lista przypadków testowych
        """
        logger.info(f"Rozpoczynanie testów wydajności dla modelu {self.model_name}")
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Test {i}/{len(test_cases)}: {test_case['name']}")
            
            result = self.run_test_case(test_case)
            self.results["tests"].append(result)
            
            # Zapisz wyniki po każdym teście
            self.save_results()
            
            # Krótka przerwa między testami
            time.sleep(1)
        
        logger.info("Testy zakończone")
        self.analyze_results()
    
    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Uruchamia pojedynczy przypadek testowy
        
        Args:
            test_case: Przypadek testowy
            
        Returns:
            Dict: Wynik testu
        """
        prompt = test_case["prompt"]
        expected_output = test_case.get("expected_output", None)
        category = test_case.get("category", "Inne")
        
        # Inicjalizacja wyniku testu
        test_result = {
            "name": test_case["name"],
            "prompt": prompt,
            "category": category,
            "expected_output": expected_output,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "code_generation": {
                "success": False,
                "time_taken": 0,
                "code": ""
            },
            "code_execution": {
                "success": False,
                "time_taken": 0,
                "output": "",
                "error": ""
            }
        }
        
        try:
            # Pomiar czasu generowania kodu
            start_time = time.time()
            code_result = self.text2python.generate_code(prompt)
            generation_time = time.time() - start_time
            
            test_result["code_generation"]["time_taken"] = generation_time
            test_result["code_generation"]["success"] = code_result["success"]
            
            if code_result["success"]:
                test_result["code_generation"]["code"] = code_result["code"]
                
                # Uruchomienie kodu w piaskownicy Docker
                start_time = time.time()
                sandbox = DockerSandbox(base_dir=SANDBOX_DIR, timeout=30)
                execution_result = sandbox.run(code_result["code"])
                execution_time = time.time() - start_time
                
                test_result["code_execution"]["time_taken"] = execution_time
                test_result["code_execution"]["success"] = execution_result["success"]
                test_result["code_execution"]["output"] = execution_result["output"]
                test_result["code_execution"]["error"] = execution_result.get("error", "")
                
                # Sprawdzenie oczekiwanego wyniku
                if expected_output is not None:
                    if self._check_output(execution_result["output"], expected_output):
                        test_result["success"] = True
                else:
                    # Jeśli nie podano oczekiwanego wyniku, uznajemy test za udany jeśli kod się wykonał
                    test_result["success"] = execution_result["success"]
                
                # Wyczyść piaskownicę
                sandbox.cleanup()
            
        except Exception as e:
            logger.error(f"Błąd podczas testu {test_case['name']}: {e}")
            test_result["error"] = str(e)
        
        return test_result
    
    def _check_output(self, actual_output: str, expected_output: str) -> bool:
        """
        Sprawdza czy faktyczny wynik odpowiada oczekiwanemu
        
        Args:
            actual_output: Faktyczny wynik
            expected_output: Oczekiwany wynik
            
        Returns:
            bool: True jeśli wyniki są zgodne, False w przeciwnym razie
        """
        # Normalizacja wyników
        actual = actual_output.strip().lower()
        expected = expected_output.strip().lower()
        
        # Sprawdzenie dokładnej zgodności
        if actual == expected:
            return True
        
        # Sprawdzenie czy oczekiwany wynik zawiera się w faktycznym
        if expected in actual:
            return True
        
        # Można dodać bardziej zaawansowane metody porównywania
        
        return False
    
    def save_results(self):
        """Zapisuje wyniki testów do pliku JSON"""
        filename = RESULTS_DIR / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Wyniki zapisane do {filename}")
    
    def analyze_results(self):
        """Analizuje wyniki testów i generuje raport"""
        tests = self.results["tests"]
        
        # Statystyki ogólne
        total_tests = len(tests)
        successful_tests = sum(1 for test in tests if test["success"])
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Czasy generowania kodu
        generation_times = [test["code_generation"]["time_taken"] for test in tests 
                           if test["code_generation"]["success"]]
        
        # Czasy wykonania kodu
        execution_times = [test["code_execution"]["time_taken"] for test in tests 
                          if test["code_execution"]["success"]]
        
        # Statystyki według kategorii
        categories = {}
        for test in tests:
            category = test["category"]
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "successful": 0,
                    "generation_times": [],
                    "execution_times": []
                }
            
            categories[category]["total"] += 1
            if test["success"]:
                categories[category]["successful"] += 1
            
            if test["code_generation"]["success"]:
                categories[category]["generation_times"].append(test["code_generation"]["time_taken"])
            
            if test["code_execution"]["success"]:
                categories[category]["execution_times"].append(test["code_execution"]["time_taken"])
        
        # Generowanie raportu
        report = {
            "model": self.model_name,
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": success_rate,
            "average_generation_time": statistics.mean(generation_times) if generation_times else 0,
            "average_execution_time": statistics.mean(execution_times) if execution_times else 0,
            "categories": {}
        }
        
        for category, stats in categories.items():
            success_rate = stats["successful"] / stats["total"] if stats["total"] > 0 else 0
            report["categories"][category] = {
                "total": stats["total"],
                "successful": stats["successful"],
                "success_rate": success_rate,
                "average_generation_time": statistics.mean(stats["generation_times"]) if stats["generation_times"] else 0,
                "average_execution_time": statistics.mean(stats["execution_times"]) if stats["execution_times"] else 0
            }
        
        # Zapisz raport
        report_file = RESULTS_DIR / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Raport zapisany do {report_file}")
        
        # Wyświetl podsumowanie
        print(f"\nPodsumowanie testów dla modelu {self.model_name}:")
        print(f"Liczba testów: {total_tests}")
        print(f"Udane testy: {successful_tests} ({success_rate:.2%})")
        print(f"Średni czas generowania kodu: {report['average_generation_time']:.2f}s")
        print(f"Średni czas wykonania kodu: {report['average_execution_time']:.2f}s")
        print("\nWyniki według kategorii:")
        for category, stats in report["categories"].items():
            print(f"  {category}: {stats['successful']}/{stats['total']} ({stats['success_rate']:.2%})")


# Przykładowe przypadki testowe dla umiejętności junior programisty
def get_test_cases() -> List[Dict[str, Any]]:
    """
    Zwraca listę przypadków testowych dla umiejętności junior programisty
    
    Returns:
        List[Dict[str, Any]]: Lista przypadków testowych
    """
    return [
        # Podstawy programowania
        {
            "name": "Obliczanie silni",
            "prompt": "Napisz funkcję, która oblicza silnię liczby n.",
            "expected_output": "120",  # dla n=5
            "category": "Podstawy programowania"
        },
        {
            "name": "Sprawdzanie liczby pierwszej",
            "prompt": "Napisz funkcję, która sprawdza czy podana liczba jest liczbą pierwszą.",
            "expected_output": "True",  # dla n=17
            "category": "Podstawy programowania"
        },
        {
            "name": "Ciąg Fibonacciego",
            "prompt": "Napisz funkcję, która generuje n-ty wyraz ciągu Fibonacciego.",
            "expected_output": "55",  # dla n=10
            "category": "Podstawy programowania"
        },
        
        # Struktury danych
        {
            "name": "Odwracanie listy",
            "prompt": "Napisz funkcję, która odwraca listę bez użycia wbudowanych funkcji.",
            "expected_output": "[5, 4, 3, 2, 1]",  # dla [1, 2, 3, 4, 5]
            "category": "Struktury danych"
        },
        {
            "name": "Znajdowanie duplikatów",
            "prompt": "Napisz funkcję, która znajduje duplikaty w liście.",
            "expected_output": "[2, 3]",  # dla [1, 2, 2, 3, 3, 4, 5]
            "category": "Struktury danych"
        },
        {
            "name": "Łączenie słowników",
            "prompt": "Napisz funkcję, która łączy dwa słowniki, sumując wartości dla tych samych kluczy.",
            "expected_output": "{'a': 3, 'b': 5, 'c': 7, 'd': 4}",  # dla {'a': 1, 'b': 2, 'c': 3} i {'a': 2, 'b': 3, 'c': 4, 'd': 4}
            "category": "Struktury danych"
        },
        
        # Programowanie obiektowe
        {
            "name": "Klasa Prostokąt",
            "prompt": "Napisz klasę Prostokąt z metodami do obliczania pola i obwodu.",
            "expected_output": "Pole: 15, Obwód: 16",  # dla prostokąta 3x5
            "category": "Programowanie obiektowe"
        },
        {
            "name": "Dziedziczenie",
            "prompt": "Napisz klasę bazową Kształt i klasę pochodną Koło z metodą do obliczania pola.",
            "expected_output": "78.5",  # dla koła o promieniu 5
            "category": "Programowanie obiektowe"
        },
        {
            "name": "Przeciążanie operatorów",
            "prompt": "Napisz klasę Wektor2D z przeciążonymi operatorami dodawania i mnożenia przez skalar.",
            "expected_output": "Wektor(5, 7)",  # dla Wektor(2, 3) + Wektor(3, 4)
            "category": "Programowanie obiektowe"
        },
        
        # Algorytmy
        {
            "name": "Sortowanie bąbelkowe",
            "prompt": "Zaimplementuj algorytm sortowania bąbelkowego.",
            "expected_output": "[1, 2, 3, 4, 5]",  # dla [5, 3, 1, 4, 2]
            "category": "Algorytmy"
        },
        {
            "name": "Wyszukiwanie binarne",
            "prompt": "Zaimplementuj algorytm wyszukiwania binarnego.",
            "expected_output": "3",  # indeks liczby 4 w posortowanej liście [1, 2, 3, 4, 5]
            "category": "Algorytmy"
        },
        {
            "name": "Algorytm Euklidesa",
            "prompt": "Zaimplementuj algorytm Euklidesa do znajdowania największego wspólnego dzielnika.",
            "expected_output": "6",  # dla 24 i 18
            "category": "Algorytmy"
        },
        
        # Przetwarzanie tekstu
        {
            "name": "Liczenie słów",
            "prompt": "Napisz funkcję, która liczy wystąpienia słów w tekście.",
            "expected_output": "{'ala': 2, 'ma': 2, 'kota': 1, 'i': 1, 'psa': 1}",  # dla "Ala ma kota i Ala ma psa"
            "category": "Przetwarzanie tekstu"
        },
        {
            "name": "Palindrom",
            "prompt": "Napisz funkcję, która sprawdza czy podany tekst jest palindromem.",
            "expected_output": "True",  # dla "kajak"
            "category": "Przetwarzanie tekstu"
        },
        {
            "name": "Anagramy",
            "prompt": "Napisz funkcję, która sprawdza czy dwa słowa są anagramami.",
            "expected_output": "True",  # dla "listen" i "silent"
            "category": "Przetwarzanie tekstu"
        },
        
        # Obsługa plików
        {
            "name": "Zapis do pliku",
            "prompt": "Napisz funkcję, która zapisuje listę liczb do pliku CSV.",
            "category": "Obsługa plików"
        },
        {
            "name": "Odczyt z pliku",
            "prompt": "Napisz funkcję, która odczytuje plik tekstowy i zwraca liczbę linii, słów i znaków.",
            "category": "Obsługa plików"
        },
        {
            "name": "Parsowanie JSON",
            "prompt": "Napisz funkcję, która parsuje plik JSON i zwraca wartość dla podanego klucza.",
            "category": "Obsługa plików"
        },
        
        # Wyrażenia regularne
        {
            "name": "Walidacja adresu email",
            "prompt": "Napisz funkcję, która sprawdza czy podany ciąg znaków jest poprawnym adresem email.",
            "expected_output": "True",  # dla "test@example.com"
            "category": "Wyrażenia regularne"
        },
        {
            "name": "Ekstrakcja numerów telefonów",
            "prompt": "Napisz funkcję, która znajduje wszystkie numery telefonów w tekście.",
            "expected_output": "['123-456-789', '987-654-321']",  # dla "Kontakt: 123-456-789 lub 987-654-321"
            "category": "Wyrażenia regularne"
        },
        {
            "name": "Zamiana formatowania",
            "prompt": "Napisz funkcję, która zamienia daty w formacie DD/MM/YYYY na YYYY-MM-DD.",
            "expected_output": "2023-05-15",  # dla "15/05/2023"
            "category": "Wyrażenia regularne"
        },
        
        # Zadania złożone
        {
            "name": "Kalkulator",
            "prompt": "Napisz prosty kalkulator, który obsługuje dodawanie, odejmowanie, mnożenie i dzielenie.",
            "expected_output": "15.0",  # dla "5 * 3"
            "category": "Zadania złożone"
        },
        {
            "name": "Gra w zgadywanie liczby",
            "prompt": "Napisz prostą grę w zgadywanie liczby wylosowanej przez komputer.",
            "category": "Zadania złożone"
        },
        {
            "name": "Konwerter jednostek",
            "prompt": "Napisz konwerter jednostek, który obsługuje konwersje między różnymi jednostkami długości.",
            "expected_output": "100.0",  # dla konwersji 1 m na cm
            "category": "Zadania złożone"
        }
    ]


def main():
    """Funkcja główna"""
    # Sprawdź czy Ollama jest uruchomiona
    try:
        subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Ollama nie jest uruchomiona. Uruchom Ollama przed rozpoczęciem testów.")
        sys.exit(1)
    
    # Pobierz przypadki testowe
    test_cases = get_test_cases()
    
    # Uruchom testy
    tester = AssistantTester(model_name="deepseek-coder:instruct-6.7b")
    tester.run_tests(test_cases)


if __name__ == "__main__":
    main()
