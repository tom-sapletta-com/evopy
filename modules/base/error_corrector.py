#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System inteligentnej korekcji błędów w generowanym kodzie dla Evopy
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ErrorCorrector')

class ErrorCorrector:
    """System inteligentnej korekcji błędów w generowanym kodzie"""
    
    # Typowe błędy i ich korekcje
    COMMON_ERRORS = {
        # Błędy składniowe
        r'SyntaxError: invalid syntax': {
            "patterns": [
                (r'```(.*?)```', r'\1'),  # Usuń znaczniki markdown
                (r'print\((.*?),\s*\)', r'print(\1)'),  # Napraw nadmiarowe przecinki
                (r'([\'"])([\'"])', r'\1\2')  # Napraw puste stringi
            ],
            "priority": 1
        },
        # Błędy importu
        r'ImportError: No module named': {
            "patterns": [],
            "extra_imports": [
                "import requests",
                "import numpy as np",
                "import matplotlib.pyplot as plt",
                "from pathlib import Path"
            ],
            "priority": 2
        },
        # Poprawianie typowych pułapek
        r'name \'e2\' is not defined': {
            "patterns": [
                (r'except.*?as e2:', r'except Exception as error:'),
                (r'e2', r'error')
            ],
            "priority": 1
        },
        # Błędy indeksowania
        r'IndexError: list index out of range': {
            "patterns": [
                (r'(\w+)\[(\d+)\]', r'\1[\2] if len(\1) > \2 else None')
            ],
            "priority": 1
        },
        # Błędy klucza
        r'KeyError:': {
            "patterns": [
                (r'(\w+)\[([\'"].*?[\'"])\]', r'\1.get(\2)')
            ],
            "priority": 1
        },
        # Błędy dzielenia przez zero
        r'ZeroDivisionError:': {
            "patterns": [
                (r'(\w+)\s*\/\s*(\w+)', r'\1 / \2 if \2 != 0 else 0')
            ],
            "priority": 1
        },
        # Błędy typu
        r'TypeError: can\'t multiply sequence by non-int': {
            "patterns": [
                (r'(\w+)\s*\*\s*(\w+)', r'int(\1) * \2')
            ],
            "priority": 1
        }
    }
    
    @classmethod
    def correct_code(cls, code: str, error_message: str) -> Tuple[str, List[str]]:
        """
        Koryguje kod na podstawie komunikatu o błędzie
        
        Args:
            code: Kod do skorygowania
            error_message: Komunikat o błędzie
            
        Returns:
            Tuple[str, List[str]]: (skorygowany_kod, zastosowane_korekcje)
        """
        corrected_code = code
        applied_corrections = []
        
        # Znajdź pasujące wzorce błędów
        for error_pattern, correction_info in cls.COMMON_ERRORS.items():
            if re.search(error_pattern, error_message):
                # Zastosuj wzorce korekcji
                for pattern, replacement in correction_info.get("patterns", []):
                    new_code = re.sub(pattern, replacement, corrected_code)
                    if new_code != corrected_code:
                        corrected_code = new_code
                        applied_corrections.append(f"Zastosowano korekcję: {pattern} -> {replacement}")
                
                # Dodaj brakujące importy jeśli potrzeba
                for import_stmt in correction_info.get("extra_imports", []):
                    if import_stmt not in corrected_code:
                        import_section = cls._find_import_section(corrected_code)
                        if import_section == 0:
                            # Dodaj na początku
                            corrected_code = import_stmt + "\n" + corrected_code
                        else:
                            # Dodaj po ostatnim imporcie
                            lines = corrected_code.split('\n')
                            lines.insert(import_section, import_stmt)
                            corrected_code = '\n'.join(lines)
                        applied_corrections.append(f"Dodano import: {import_stmt}")
        
        return corrected_code, applied_corrections
    
    @staticmethod
    def _find_import_section(code: str) -> int:
        """
        Znajduje ostatnią linię z instrukcją import
        
        Args:
            code: Kod do przeszukania
            
        Returns:
            int: Numer linii ostatniego importu
        """
        lines = code.split('\n')
        last_import_line = 0
        
        for i, line in enumerate(lines):
            if re.match(r'import\s+', line) or re.match(r'from\s+.*\s+import\s+', line):
                last_import_line = i + 1
        
        return last_import_line
    
    @classmethod
    def analyze_error(cls, error_message: str) -> Dict[str, Any]:
        """
        Analizuje błąd i sugeruje rozwiązania
        
        Args:
            error_message: Komunikat o błędzie
            
        Returns:
            Dict[str, Any]: Analiza błędu
        """
        analysis = {
            "error_type": "Unknown",
            "possible_causes": [],
            "suggested_solutions": []
        }
        
        # Określ typ błędu
        error_types = [
            ("SyntaxError", r'SyntaxError'),
            ("ImportError", r'ImportError'),
            ("NameError", r'NameError'),
            ("TypeError", r'TypeError'),
            ("ValueError", r'ValueError'),
            ("IndexError", r'IndexError'),
            ("KeyError", r'KeyError'),
            ("AttributeError", r'AttributeError'),
            ("ZeroDivisionError", r'ZeroDivisionError'),
            ("FileNotFoundError", r'FileNotFoundError'),
            ("PermissionError", r'PermissionError'),
            ("RuntimeError", r'RuntimeError')
        ]
        
        for error_type, pattern in error_types:
            if re.search(pattern, error_message):
                analysis["error_type"] = error_type
                break
        
        # Dodaj typowe przyczyny i rozwiązania dla różnych typów błędów
        if analysis["error_type"] == "SyntaxError":
            analysis["possible_causes"] = [
                "Brakujący nawias",
                "Niepoprawne wcięcie",
                "Brakujący dwukropek po instrukcji warunkowej lub pętli",
                "Niepoprawne użycie operatorów"
            ]
            analysis["suggested_solutions"] = [
                "Sprawdź nawiasy - każdy nawias otwierający musi mieć odpowiadający nawias zamykający",
                "Sprawdź wcięcia - Python używa wcięć do określania bloków kodu",
                "Upewnij się, że po instrukcjach if, for, while, def, class jest dwukropek",
                "Sprawdź operatory - upewnij się, że używasz ich poprawnie"
            ]
        elif analysis["error_type"] == "ImportError":
            analysis["possible_causes"] = [
                "Brakujący moduł",
                "Niepoprawna nazwa modułu",
                "Moduł nie jest zainstalowany"
            ]
            analysis["suggested_solutions"] = [
                "Sprawdź nazwę importowanego modułu",
                "Zainstaluj brakujący moduł: pip install <nazwa_modułu>",
                "Sprawdź ścieżkę do modułu"
            ]
        elif analysis["error_type"] == "NameError":
            analysis["possible_causes"] = [
                "Użycie niezdefiniowanej zmiennej",
                "Literówka w nazwie zmiennej",
                "Zmienna zdefiniowana w innym zakresie"
            ]
            analysis["suggested_solutions"] = [
                "Zdefiniuj zmienną przed jej użyciem",
                "Sprawdź pisownię nazwy zmiennej",
                "Upewnij się, że zmienna jest dostępna w bieżącym zakresie"
            ]
        
        return analysis
    
    @classmethod
    def extract_error_location(cls, error_message: str) -> Optional[Tuple[str, int]]:
        """
        Wyodrębnia lokalizację błędu z komunikatu
        
        Args:
            error_message: Komunikat o błędzie
            
        Returns:
            Optional[Tuple[str, int]]: (nazwa_pliku, numer_linii) lub None
        """
        # Wzorzec dla typowego komunikatu o błędzie w Pythonie
        pattern = r'File "([^"]+)", line (\d+)'
        match = re.search(pattern, error_message)
        
        if match:
            file_name = match.group(1)
            line_number = int(match.group(2))
            return file_name, line_number
        
        return None


# Przykład użycia
if __name__ == "__main__":
    # Przykładowy kod z błędem
    code_with_error = """
def calculate_average(numbers):
    total = 0
    for number in numbers:
        total += number
    return total / len(numbers)

# Przykładowe użycie
values = []
average = calculate_average(values)
print("Średnia:", average)
"""
    
    # Przykładowy komunikat o błędzie
    error_msg = "ZeroDivisionError: division by zero"
    
    # Korekta kodu
    corrected_code, corrections = ErrorCorrector.correct_code(code_with_error, error_msg)
    
    print("Oryginalny kod:")
    print(code_with_error)
    print("\nKomunikat o błędzie:")
    print(error_msg)
    print("\nSkorygowany kod:")
    print(corrected_code)
    print("\nZastosowane korekcje:")
    for correction in corrections:
        print(f"- {correction}")
    
    # Analiza błędu
    analysis = ErrorCorrector.analyze_error(error_msg)
    
    print("\nAnaliza błędu:")
    print(f"Typ błędu: {analysis['error_type']}")
    print("Możliwe przyczyny:")
    for cause in analysis["possible_causes"]:
        print(f"- {cause}")
    print("Sugerowane rozwiązania:")
    for solution in analysis["suggested_solutions"]:
        print(f"- {solution}")
