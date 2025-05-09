#!/usr/bin/env python3
"""
Test Complex Tasks - Testy złożonych zadań dla asystenta evopy

Ten moduł zawiera testy wydajności asystenta evopy dla bardziej złożonych zadań
programistycznych, które wymagają łączenia wielu koncepcji i umiejętności.
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Dodaj katalog główny projektu do ścieżki importu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modułów projektu
from modules.text2python.text2python import Text2Python
from docker_sandbox import DockerSandbox
from test_assistant_performance import AssistantTester

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_complex_tasks.log")
    ]
)
logger = logging.getLogger("evopy-complex-tests")

# Stałe
TEST_DIR = Path(__file__).parent
SANDBOX_DIR = Path.home() / ".evo-assistant" / "sandbox"
CODE_DIR = Path.home() / ".evo-assistant" / "code"
RESULTS_DIR = TEST_DIR / "results"
COMPLEX_RESULTS_DIR = RESULTS_DIR / "complex"

# Upewnij się, że katalogi istnieją
for directory in [SANDBOX_DIR, CODE_DIR, RESULTS_DIR, COMPLEX_RESULTS_DIR]:
    os.makedirs(directory, exist_ok=True)


def get_complex_test_cases() -> List[Dict[str, Any]]:
    """
    Zwraca listę złożonych przypadków testowych wymagających integracji wielu umiejętności
    
    Returns:
        List[Dict[str, Any]]: Lista złożonych przypadków testowych
    """
    return [
        # Analiza danych i wizualizacja
        {
            "name": "Analiza danych CSV",
            "prompt": """
            Napisz funkcję, która:
            1. Wczytuje dane z pliku CSV (utwórz przykładowe dane zawierające informacje o sprzedaży produktów)
            2. Analizuje dane, obliczając sumę sprzedaży według kategorii produktów
            3. Generuje wykres słupkowy pokazujący sprzedaż według kategorii
            4. Zapisuje wykres do pliku PNG
            5. Zwraca słownik z wynikami analizy
            """,
            "category": "Analiza danych"
        },
        
        # Aplikacja webowa
        {
            "name": "Prosta aplikacja Flask",
            "prompt": """
            Napisz prostą aplikację webową z użyciem Flask, która:
            1. Wyświetla formularz do dodawania zadań do listy TODO
            2. Zapisuje zadania w pamięci (nie potrzeba bazy danych)
            3. Wyświetla listę wszystkich zadań
            4. Umożliwia oznaczenie zadania jako wykonane
            5. Zwraca instancję aplikacji Flask gotową do uruchomienia
            """,
            "category": "Aplikacje webowe"
        },
        
        # Przetwarzanie API
        {
            "name": "Integracja z API",
            "prompt": """
            Napisz funkcję, która:
            1. Pobiera dane o pogodzie z API OpenWeatherMap (zasymuluj odpowiedź API)
            2. Przetwarza dane, wyodrębniając temperaturę, wilgotność i ciśnienie
            3. Konwertuje temperaturę z Kelwinów na stopnie Celsjusza
            4. Formatuje dane jako czytelny raport tekstowy
            5. Zwraca słownik zawierający przetworzone dane
            """,
            "category": "Integracja API"
        },
        
        # Automatyzacja i skrypty
        {
            "name": "Automatyzacja przetwarzania plików",
            "prompt": """
            Napisz funkcję, która:
            1. Skanuje podany katalog w poszukiwaniu plików tekstowych (utwórz przykładowe pliki)
            2. Dla każdego pliku zlicza liczbę słów, linii i znaków
            3. Tworzy nowy plik z raportem zawierającym statystyki dla każdego pliku
            4. Sortuje pliki według liczby słów od największej do najmniejszej
            5. Zwraca słownik z podsumowaniem operacji
            """,
            "category": "Automatyzacja"
        },
        
        # Gra komputerowa
        {
            "name": "Prosta gra tekstowa",
            "prompt": """
            Napisz prostą tekstową grę przygodową, która:
            1. Zawiera co najmniej 3 lokacje, które gracz może odwiedzić
            2. Umożliwia zbieranie przedmiotów i używanie ich
            3. Zawiera prostego przeciwnika, z którym gracz może walczyć
            4. Implementuje system punktów życia gracza
            5. Kończy się, gdy gracz dotrze do celu lub straci wszystkie punkty życia
            6. Zwraca funkcję play(), która rozpoczyna grę
            """,
            "category": "Gry"
        },
        
        # Przetwarzanie obrazów
        {
            "name": "Przetwarzanie obrazów",
            "prompt": """
            Napisz funkcję, która:
            1. Generuje prosty obraz (np. koło, kwadrat) używając biblioteki PIL/Pillow
            2. Stosuje kilka transformacji do obrazu (obrót, zmiana rozmiaru, filtr)
            3. Dodaje tekst do obrazu
            4. Zapisuje przetworzone obrazy do plików
            5. Zwraca ścieżki do utworzonych plików
            """,
            "category": "Przetwarzanie obrazów"
        },
        
        # Baza danych
        {
            "name": "Operacje na bazie danych SQLite",
            "prompt": """
            Napisz funkcję, która:
            1. Tworzy bazę danych SQLite w pamięci
            2. Definiuje tabelę 'pracownicy' z polami: id, imię, nazwisko, stanowisko, pensja
            3. Dodaje przykładowe dane (co najmniej 5 pracowników)
            4. Wykonuje zapytania: 
               - lista pracowników zarabiających powyżej średniej
               - liczba pracowników na każdym stanowisku
               - pracownik z najwyższą pensją
            5. Zwraca wyniki zapytań jako słownik
            """,
            "category": "Bazy danych"
        },
        
        # Wielowątkowość
        {
            "name": "Przetwarzanie równoległe",
            "prompt": """
            Napisz funkcję, która:
            1. Generuje listę 1000000 losowych liczb
            2. Implementuje równoległe obliczanie sumy, średniej, minimum i maksimum
            3. Używa puli wątków do przyspieszenia obliczeń
            4. Porównuje czas wykonania z wersją jednowątkową
            5. Zwraca wyniki obliczeń i porównanie czasów
            """,
            "category": "Wielowątkowość"
        },
        
        # Parsowanie i web scraping
        {
            "name": "Web scraping",
            "prompt": """
            Napisz funkcję, która:
            1. Parsuje przykładowy dokument HTML (utwórz przykładowy HTML imitujący stronę z artykułami)
            2. Wyodrębnia tytuły, autorów i daty publikacji artykułów
            3. Filtruje artykuły według słów kluczowych
            4. Sortuje artykuły według daty
            5. Zwraca listę przetworzonych artykułów jako słownik
            """,
            "category": "Web scraping"
        },
        
        # Algorytmy i struktury danych
        {
            "name": "Implementacja grafu i algorytmów",
            "prompt": """
            Napisz funkcję, która:
            1. Implementuje strukturę danych grafu (skierowanego, ważonego)
            2. Dodaje przykładowe wierzchołki i krawędzie reprezentujące sieć dróg między miastami
            3. Implementuje algorytm Dijkstry do znajdowania najkrótszej ścieżki
            4. Znajduje najkrótszą ścieżkę między dwoma wybranymi miastami
            5. Zwraca najkrótszą ścieżkę i jej długość
            """,
            "category": "Algorytmy"
        },
        
        # Przetwarzanie języka naturalnego
        {
            "name": "Analiza tekstu",
            "prompt": """
            Napisz funkcję, która:
            1. Analizuje podany tekst (utwórz przykładowy długi tekst)
            2. Oblicza częstotliwość występowania słów
            3. Identyfikuje najczęściej występujące n-gramy (pary słów)
            4. Oblicza czytelność tekstu używając indeksu Flesch-Kincaid
            5. Zwraca słownik z wynikami analizy
            """,
            "category": "NLP"
        },
        
        # Aplikacja desktopowa
        {
            "name": "Prosta aplikacja desktopowa",
            "prompt": """
            Napisz prostą aplikację desktopową z interfejsem graficznym, która:
            1. Wyświetla okno z przyciskami i polem tekstowym
            2. Umożliwia użytkownikowi wprowadzenie tekstu
            3. Po kliknięciu przycisku wykonuje analizę tekstu (np. liczba słów, zdań)
            4. Wyświetla wyniki analizy
            5. Zwraca główną klasę aplikacji
            """,
            "category": "Aplikacje desktopowe"
        },
        
        # Sieć i protokoły
        {
            "name": "Klient-serwer TCP",
            "prompt": """
            Napisz funkcję, która:
            1. Implementuje prosty serwer TCP nasłuchujący na określonym porcie
            2. Implementuje klienta TCP łączącego się z serwerem
            3. Umożliwia wymianę wiadomości między klientem a serwerem
            4. Serwer przetwarza otrzymane wiadomości (np. odwraca tekst)
            5. Zwraca funkcje do uruchomienia serwera i klienta
            """,
            "category": "Sieci"
        },
        
        # Testowanie i TDD
        {
            "name": "Implementacja z testami jednostkowymi",
            "prompt": """
            Napisz funkcję, która:
            1. Implementuje klasę Kalkulator z metodami do podstawowych operacji matematycznych
            2. Implementuje testy jednostkowe dla każdej metody
            3. Używa asercji do weryfikacji poprawności wyników
            4. Obsługuje przypadki brzegowe i wyjątki
            5. Zwraca klasę Kalkulator i funkcję uruchamiającą testy
            """,
            "category": "Testowanie"
        },
        
        # Bezpieczeństwo
        {
            "name": "Szyfrowanie i bezpieczeństwo",
            "prompt": """
            Napisz funkcję, która:
            1. Implementuje prosty system logowania z hashowaniem haseł
            2. Umożliwia rejestrację nowych użytkowników
            3. Weryfikuje poświadczenia podczas logowania
            4. Implementuje mechanizm blokady konta po zbyt wielu nieudanych próbach
            5. Zwraca funkcje do rejestracji i logowania
            """,
            "category": "Bezpieczeństwo"
        }
    ]


class ComplexTaskTester(AssistantTester):
    """Klasa do testowania złożonych zadań dla asystenta evopy"""
    
    def __init__(self, model_name: str = "deepseek-coder:instruct-6.7b"):
        """
        Inicjalizacja testera złożonych zadań
        
        Args:
            model_name: Nazwa modelu Ollama do użycia
        """
        super().__init__(model_name)
        self.results["test_type"] = "complex_tasks"
    
    def save_results(self):
        """Zapisuje wyniki testów do pliku JSON"""
        filename = COMPLEX_RESULTS_DIR / f"complex_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.model_name.replace(':', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Wyniki zapisane do {filename}")


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
    test_cases = get_complex_test_cases()
    
    # Uruchom testy
    tester = ComplexTaskTester(model_name="deepseek-coder:instruct-6.7b")
    tester.run_tests(test_cases)


if __name__ == "__main__":
    main()
