#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł TEXT2PYTHON wykorzystujący nową architekturę bazową
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj klasy bazowe
from modules.base import BaseText2XModule, ConfigManager, ErrorCorrector

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class Text2Python(BaseText2XModule):
    """Klasa do konwersji tekstu na kod Python"""
    
    def initialize(self) -> None:
        """Inicjalizacja specyficzna dla modułu TEXT2PYTHON"""
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "llama3",
            "dependencies": ["numpy", "pandas", "matplotlib"],
            "max_tokens": 1000,
            "temperature": 0.7,
            "use_sandbox": True,
            "sandbox_type": "docker"
        }
        
        # Aktualizacja konfiguracji
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Ładowanie konfiguracji z pliku
        self.load_config()
        
        # Inicjalizacja menedżera konfiguracji
        self.config_manager = ConfigManager()
        
        # Załaduj konfigurację modułu z centralnego menedżera
        module_config = self.config_manager.get_module_config("text2python")
        self.config.update(module_config)
        
        self.logger.info(f"Moduł TEXT2PYTHON zainicjalizowany z modelem: {self.config['model']}")
    
    def process(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Przetwarza tekst na kod Python
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict[str, Any]: Wygenerowany kod Python
        """
        self.logger.info(f"Przetwarzanie tekstu: {text[:50]}...")
        
        # Parametry przetwarzania
        model = kwargs.get('model', self.config['model'])
        temperature = kwargs.get('temperature', self.config['temperature'])
        max_tokens = kwargs.get('max_tokens', self.config['max_tokens'])
        
        # W rzeczywistej implementacji tutaj byłoby wywołanie modelu LLM
        # Dla przykładu generujemy prosty kod na podstawie tekstu
        
        # Przykładowa implementacja
        if "suma" in text.lower() or "dodaj" in text.lower() or "dodawanie" in text.lower():
            code = """
def suma(a, b):
    \"\"\"
    Funkcja sumująca dwie liczby
    
    Args:
        a: Pierwsza liczba
        b: Druga liczba
        
    Returns:
        Suma a i b
    \"\"\"
    return a + b

# Przykładowe użycie
if __name__ == "__main__":
    liczba1 = 5
    liczba2 = 3
    wynik = suma(liczba1, liczba2)
    print(f"Suma {liczba1} i {liczba2} wynosi: {wynik}")
"""
        elif "lista" in text.lower() or "tablica" in text.lower() or "array" in text.lower():
            code = """
def operacje_na_liscie(lista):
    \"\"\"
    Funkcja wykonująca podstawowe operacje na liście
    
    Args:
        lista: Lista do przetworzenia
        
    Returns:
        Słownik z wynikami operacji
    \"\"\"
    if not lista:
        return {"error": "Lista jest pusta"}
    
    return {
        "suma": sum(lista),
        "średnia": sum(lista) / len(lista),
        "minimum": min(lista),
        "maksimum": max(lista),
        "liczba_elementów": len(lista)
    }

# Przykładowe użycie
if __name__ == "__main__":
    moja_lista = [1, 2, 3, 4, 5]
    wyniki = operacje_na_liscie(moja_lista)
    
    for operacja, wynik in wyniki.items():
        print(f"{operacja}: {wynik}")
"""
        elif "plik" in text.lower() or "file" in text.lower() or "odczyt" in text.lower() or "zapis" in text.lower():
            code = """
import os
from pathlib import Path

def operacje_na_pliku(nazwa_pliku, tryb="odczyt", dane=None):
    \"\"\"
    Funkcja wykonująca operacje na pliku
    
    Args:
        nazwa_pliku: Nazwa pliku
        tryb: Tryb operacji ("odczyt", "zapis", "dopisanie")
        dane: Dane do zapisania (tylko dla trybów "zapis" i "dopisanie")
        
    Returns:
        Zawartość pliku (dla trybu "odczyt") lub status operacji
    \"\"\"
    try:
        if tryb == "odczyt":
            with open(nazwa_pliku, "r", encoding="utf-8") as f:
                return f.read()
        elif tryb == "zapis":
            with open(nazwa_pliku, "w", encoding="utf-8") as f:
                f.write(dane)
            return {"status": "success", "message": f"Zapisano dane do pliku {nazwa_pliku}"}
        elif tryb == "dopisanie":
            with open(nazwa_pliku, "a", encoding="utf-8") as f:
                f.write(dane)
            return {"status": "success", "message": f"Dopisano dane do pliku {nazwa_pliku}"}
        else:
            return {"status": "error", "message": f"Nieznany tryb: {tryb}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Przykładowe użycie
if __name__ == "__main__":
    # Ścieżka do pliku
    plik = Path("przyklad.txt")
    
    # Zapis do pliku
    operacje_na_pliku(plik, "zapis", "To jest przykładowy tekst.\\n")
    
    # Dopisanie do pliku
    operacje_na_pliku(plik, "dopisanie", "To jest druga linia tekstu.\\n")
    
    # Odczyt z pliku
    zawartosc = operacje_na_pliku(plik, "odczyt")
    print(f"Zawartość pliku:\\n{zawartosc}")
"""
        elif "klasa" in text.lower() or "class" in text.lower() or "obiekt" in text.lower():
            code = """
class Osoba:
    \"\"\"
    Klasa reprezentująca osobę
    \"\"\"
    
    def __init__(self, imie, nazwisko, wiek=None):
        \"\"\"
        Inicjalizacja osoby
        
        Args:
            imie: Imię osoby
            nazwisko: Nazwisko osoby
            wiek: Wiek osoby (opcjonalny)
        \"\"\"
        self.imie = imie
        self.nazwisko = nazwisko
        self.wiek = wiek
    
    def przedstaw_sie(self):
        \"\"\"
        Metoda przedstawiająca osobę
        
        Returns:
            Tekst przedstawiający osobę
        \"\"\"
        if self.wiek:
            return f"Nazywam się {self.imie} {self.nazwisko}, mam {self.wiek} lat."
        else:
            return f"Nazywam się {self.imie} {self.nazwisko}."
    
    def urodziny(self):
        \"\"\"
        Metoda zwiększająca wiek osoby o 1
        
        Returns:
            Nowy wiek osoby
        \"\"\"
        if self.wiek is not None:
            self.wiek += 1
            return self.wiek
        else:
            return None

# Przykładowe użycie
if __name__ == "__main__":
    osoba1 = Osoba("Jan", "Kowalski", 30)
    osoba2 = Osoba("Anna", "Nowak")
    
    print(osoba1.przedstaw_sie())
    print(osoba2.przedstaw_sie())
    
    osoba1.urodziny()
    print(f"{osoba1.imie} ma teraz {osoba1.wiek} lat.")
"""
        else:
            code = f"""
def main():
    \"\"\"
    Główna funkcja programu
    \"\"\"
    print("Przetwarzanie tekstu: {text}")
    return "Wykonano"

# Wywołanie głównej funkcji
if __name__ == "__main__":
    wynik = main()
    print(wynik)
"""
        
        return {
            "success": True,
            "code": code,
            "language": "python",
            "query": text,
            "model": model,
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        }
    
    def execute_code(self, code: str, use_sandbox: bool = None) -> Dict[str, Any]:
        """
        Wykonuje wygenerowany kod Python
        
        Args:
            code: Kod do wykonania
            use_sandbox: Czy użyć piaskownicy (opcjonalne)
            
        Returns:
            Dict[str, Any]: Wynik wykonania kodu
        """
        if use_sandbox is None:
            use_sandbox = self.config.get('use_sandbox', True)
        
        self.logger.info(f"Wykonywanie kodu (use_sandbox={use_sandbox})...")
        
        if use_sandbox:
            # W rzeczywistej implementacji tutaj byłoby wywołanie piaskownicy
            # Dla przykładu zwracamy symulowany wynik
            return {
                "success": True,
                "output": "Symulowany wynik wykonania kodu w piaskownicy",
                "execution_time": 0.5
            }
        else:
            # Wykonanie kodu bezpośrednio (niebezpieczne!)
            try:
                import tempfile
                import subprocess
                
                # Zapisz kod do tymczasowego pliku
                with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                # Wykonaj kod
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Usuń tymczasowy plik
                os.unlink(temp_file)
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "execution_time": 0.5  # Symulowany czas wykonania
                }
            except Exception as e:
                self.logger.error(f"Błąd podczas wykonywania kodu: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def correct_code(self, code: str, error_message: str) -> Dict[str, Any]:
        """
        Koryguje kod na podstawie komunikatu o błędzie
        
        Args:
            code: Kod do skorygowania
            error_message: Komunikat o błędzie
            
        Returns:
            Dict[str, Any]: Skorygowany kod i zastosowane korekcje
        """
        self.logger.info(f"Korygowanie kodu na podstawie błędu: {error_message[:50]}...")
        
        # Użyj systemu korekcji błędów
        corrected_code, corrections = ErrorCorrector.correct_code(code, error_message)
        
        # Analiza błędu
        error_analysis = ErrorCorrector.analyze_error(error_message)
        
        return {
            "success": True,
            "original_code": code,
            "corrected_code": corrected_code,
            "corrections": corrections,
            "error_analysis": error_analysis
        }


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji modułu
    text2python = Text2Python()
    
    # Przetwarzanie tekstu
    query = "Napisz funkcję, która sumuje dwie liczby"
    result = text2python.execute(query)
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Wykonanie wygenerowanego kodu
    if result["success"]:
        code = result["result"]["code"]
        execution_result = text2python.execute_code(code, use_sandbox=True)
        print("\nWynik wykonania kodu:")
        print(json.dumps(execution_result, indent=2, ensure_ascii=False))
        
        # Przykład korekcji kodu z błędem
        code_with_error = """
def divide(a, b):
    return a / b

result = divide(10, 0)
print(result)
"""
        error_message = "ZeroDivisionError: division by zero"
        correction_result = text2python.correct_code(code_with_error, error_message)
        print("\nWynik korekcji kodu:")
        print(json.dumps(correction_result, indent=2, ensure_ascii=False))
