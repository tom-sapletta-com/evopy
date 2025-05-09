#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System rozpoznawania intencji i dopasowania modułu dla Evopy
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ModuleSelector')

class ModuleSelector:
    """Selektor odpowiedniego modułu na podstawie intencji zapytania"""
    
    # Wzorce dla różnych modułów
    MODULE_PATTERNS = {
        "TEXT2PYTHON": [
            r'(napisz|stwórz|generuj|utwórz).*kod.*python',
            r'(napisz|stwórz|generuj|utwórz).*skrypt',
            r'(napisz|stwórz|generuj|utwórz).*program',
            r'(napisz|stwórz|generuj|utwórz).*funkcj[eaę]',
            r'(napisz|stwórz|generuj|utwórz).*klas[eaę]',
            r'zaimplementuj',
            r'python'
        ],
        "TEXT2SQL": [
            r'(napisz|stwórz|generuj|utwórz).*zapytanie.*sql',
            r'(napisz|stwórz|generuj|utwórz).*kwerend[eaę]',
            r'(napisz|stwórz|generuj|utwórz).*sql',
            r'baz[aey].*danych',
            r'sql',
            r'select.*from',
            r'insert.*into',
            r'update.*set',
            r'delete.*from'
        ],
        "TEXT2HTML": [
            r'(napisz|stwórz|generuj|utwórz).*html',
            r'(napisz|stwórz|generuj|utwórz).*stron[eaę]',
            r'(napisz|stwórz|generuj|utwórz).*szablon',
            r'html',
            r'strona.*internetowa',
            r'strona.*www'
        ],
        "TEXT2CSS": [
            r'(napisz|stwórz|generuj|utwórz).*css',
            r'(napisz|stwórz|generuj|utwórz).*styl',
            r'css',
            r'styl.*strony'
        ],
        "TEXT2JAVASCRIPT": [
            r'(napisz|stwórz|generuj|utwórz).*javascript',
            r'(napisz|stwórz|generuj|utwórz).*js',
            r'javascript',
            r'js',
            r'skrypt.*js'
        ],
        "TEXT2DOCKER": [
            r'(napisz|stwórz|generuj|utwórz).*dockerfile',
            r'(napisz|stwórz|generuj|utwórz).*docker-compose',
            r'(napisz|stwórz|generuj|utwórz).*kontener',
            r'docker',
            r'kontener'
        ],
        "TEXT2EMAIL": [
            r'(napisz|stwórz|generuj|utwórz).*email',
            r'(napisz|stwórz|generuj|utwórz).*mail',
            r'(napisz|stwórz|generuj|utwórz).*wiadomość',
            r'wyślij.*email',
            r'wyślij.*mail',
            r'wyślij.*wiadomość',
            r'email',
            r'mail'
        ],
        "TEXT2PRINT": [
            r'(wydrukuj|drukuj)',
            r'drukarka',
            r'wydruk'
        ],
        "TEXT2SPEECH": [
            r'(zamień|konwertuj|przekształć).*na mowę',
            r'(zamień|konwertuj|przekształć).*na głos',
            r'(przeczytaj|odczytaj).*na głos',
            r'powiedz',
            r'mów',
            r'synteza mowy'
        ],
        "TEXT2IMAGE": [
            r'(wygeneruj|stwórz|utwórz|narysuj).*obraz',
            r'(wygeneruj|stwórz|utwórz|narysuj).*obrazek',
            r'(wygeneruj|stwórz|utwórz|narysuj).*grafik[eaę]',
            r'(wygeneruj|stwórz|utwórz|narysuj).*zdjęcie',
            r'narysuj',
            r'obraz',
            r'grafika'
        ],
        "TEXT2MARKDOWN": [
            r'(napisz|stwórz|generuj|utwórz).*markdown',
            r'(napisz|stwórz|generuj|utwórz).*md',
            r'markdown',
            r'md'
        ],
        "TEXT2JSON": [
            r'(napisz|stwórz|generuj|utwórz).*json',
            r'json'
        ],
        "TEXT2XML": [
            r'(napisz|stwórz|generuj|utwórz).*xml',
            r'xml'
        ],
        "TEXT2YAML": [
            r'(napisz|stwórz|generuj|utwórz).*yaml',
            r'(napisz|stwórz|generuj|utwórz).*yml',
            r'yaml',
            r'yml'
        ],
        "TEXT2CSV": [
            r'(napisz|stwórz|generuj|utwórz).*csv',
            r'csv'
        ],
        "TEXT2PDF": [
            r'(napisz|stwórz|generuj|utwórz).*pdf',
            r'pdf'
        ],
        "TEXT2EXCEL": [
            r'(napisz|stwórz|generuj|utwórz).*excel',
            r'(napisz|stwórz|generuj|utwórz).*xlsx',
            r'excel',
            r'xlsx'
        ],
        "TEXT2BASH": [
            r'(napisz|stwórz|generuj|utwórz).*bash',
            r'(napisz|stwórz|generuj|utwórz).*skrypt.*bash',
            r'(napisz|stwórz|generuj|utwórz).*skrypt.*shell',
            r'bash',
            r'shell',
            r'skrypt.*bash',
            r'skrypt.*shell'
        ]
    }
    
    def __init__(self, custom_patterns: Optional[Dict[str, List[str]]] = None):
        """
        Inicjalizacja selektora modułów
        
        Args:
            custom_patterns: Niestandardowe wzorce dla modułów (opcjonalne)
        """
        self.patterns = self.MODULE_PATTERNS.copy()
        
        # Dodaj niestandardowe wzorce, jeśli zostały podane
        if custom_patterns:
            for module, patterns in custom_patterns.items():
                if module in self.patterns:
                    self.patterns[module].extend(patterns)
                else:
                    self.patterns[module] = patterns
    
    def detect_module(self, query: str) -> str:
        """
        Wykrywa odpowiedni moduł na podstawie zapytania
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            str: Nazwa wykrytego modułu
        """
        query_lower = query.lower()
        
        # Słownik do przechowywania liczby dopasowań dla każdego modułu
        module_scores: Dict[str, int] = {}
        
        for module, patterns in self.patterns.items():
            module_scores[module] = 0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    module_scores[module] += 1
        
        # Znajdź moduł z największą liczbą dopasowań
        best_module = max(module_scores.items(), key=lambda x: x[1])
        
        # Jeśli najlepszy moduł ma co najmniej jedno dopasowanie, zwróć go
        if best_module[1] > 0:
            logger.info(f"Wykryto moduł {best_module[0]} z {best_module[1]} dopasowaniami")
            return best_module[0]
        
        # Domyślny moduł
        logger.info("Nie wykryto żadnego modułu, używam domyślnego: TEXT2PYTHON")
        return "TEXT2PYTHON"
    
    def detect_module_with_confidence(self, query: str) -> Tuple[str, float]:
        """
        Wykrywa odpowiedni moduł na podstawie zapytania wraz z poziomem pewności
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            Tuple[str, float]: (nazwa_modułu, poziom_pewności)
        """
        query_lower = query.lower()
        
        # Słownik do przechowywania liczby dopasowań dla każdego modułu
        module_scores: Dict[str, int] = {}
        total_matches = 0
        
        for module, patterns in self.patterns.items():
            module_scores[module] = 0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    module_scores[module] += 1
                    total_matches += 1
        
        # Znajdź moduł z największą liczbą dopasowań
        if total_matches > 0:
            best_module = max(module_scores.items(), key=lambda x: x[1])
            confidence = best_module[1] / total_matches
            
            logger.info(f"Wykryto moduł {best_module[0]} z pewnością {confidence:.2f}")
            return best_module[0], confidence
        
        # Domyślny moduł
        logger.info("Nie wykryto żadnego modułu, używam domyślnego: TEXT2PYTHON")
        return "TEXT2PYTHON", 0.0
    
    def get_top_modules(self, query: str, top_n: int = 3) -> List[Tuple[str, int]]:
        """
        Zwraca listę najlepiej dopasowanych modułów
        
        Args:
            query: Zapytanie użytkownika
            top_n: Liczba najlepszych modułów do zwrócenia
            
        Returns:
            List[Tuple[str, int]]: Lista (nazwa_modułu, liczba_dopasowań)
        """
        query_lower = query.lower()
        
        # Słownik do przechowywania liczby dopasowań dla każdego modułu
        module_scores: Dict[str, int] = {}
        
        for module, patterns in self.patterns.items():
            module_scores[module] = 0
            
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    module_scores[module] += 1
        
        # Posortuj moduły według liczby dopasowań (malejąco)
        sorted_modules = sorted(module_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Zwróć top_n modułów
        return sorted_modules[:top_n]
    
    def add_pattern(self, module: str, pattern: str) -> None:
        """
        Dodaje nowy wzorzec dla modułu
        
        Args:
            module: Nazwa modułu
            pattern: Wzorzec do dodania
        """
        if module not in self.patterns:
            self.patterns[module] = []
        
        if pattern not in self.patterns[module]:
            self.patterns[module].append(pattern)
            logger.info(f"Dodano wzorzec '{pattern}' dla modułu {module}")
    
    def remove_pattern(self, module: str, pattern: str) -> bool:
        """
        Usuwa wzorzec dla modułu
        
        Args:
            module: Nazwa modułu
            pattern: Wzorzec do usunięcia
            
        Returns:
            bool: Czy usunięcie się powiodło
        """
        if module in self.patterns and pattern in self.patterns[module]:
            self.patterns[module].remove(pattern)
            logger.info(f"Usunięto wzorzec '{pattern}' dla modułu {module}")
            return True
        
        logger.warning(f"Wzorzec '{pattern}' nie istnieje dla modułu {module}")
        return False
    
    def get_patterns(self, module: str) -> List[str]:
        """
        Pobiera wzorce dla modułu
        
        Args:
            module: Nazwa modułu
            
        Returns:
            List[str]: Lista wzorców
        """
        return self.patterns.get(module, [])
    
    def get_all_modules(self) -> List[str]:
        """
        Pobiera listę wszystkich dostępnych modułów
        
        Returns:
            List[str]: Lista nazw modułów
        """
        return list(self.patterns.keys())


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji selektora modułów
    module_selector = ModuleSelector()
    
    # Przykładowe zapytania
    queries = [
        "Napisz funkcję w Pythonie, która oblicza silnię",
        "Stwórz zapytanie SQL, które wybiera wszystkie rekordy z tabeli users",
        "Wygeneruj stronę HTML z formularzem kontaktowym",
        "Napisz skrypt bash, który tworzy kopię zapasową plików",
        "Wyślij email z potwierdzeniem zamówienia",
        "Wygeneruj obrazek przedstawiający zachód słońca nad morzem",
        "Zamień ten tekst na mowę",
        "Utwórz plik JSON z danymi użytkowników"
    ]
    
    # Testowanie wykrywania modułów
    for query in queries:
        module = module_selector.detect_module(query)
        print(f"Zapytanie: '{query}'")
        print(f"Wykryty moduł: {module}")
        
        # Wykrywanie z poziomem pewności
        module, confidence = module_selector.detect_module_with_confidence(query)
        print(f"Pewność: {confidence:.2f}")
        
        # Najlepsze moduły
        top_modules = module_selector.get_top_modules(query, 3)
        print(f"Najlepsze moduły: {top_modules}")
        print()
    
    # Dodanie nowego wzorca
    module_selector.add_pattern("TEXT2PYTHON", r'algorytm')
    
    # Pobranie wzorców dla modułu
    python_patterns = module_selector.get_patterns("TEXT2PYTHON")
    print(f"Wzorce dla TEXT2PYTHON: {python_patterns}")
    
    # Pobranie wszystkich modułów
    all_modules = module_selector.get_all_modules()
    print(f"Wszystkie moduły: {all_modules}")
