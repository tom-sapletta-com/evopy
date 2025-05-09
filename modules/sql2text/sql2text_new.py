#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł SQL2TEXT wykorzystujący nową architekturę bazową

Moduł konwertuje zapytania SQL na opisy w języku naturalnym.
"""

import os
import sys
import json
import logging
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj klasy bazowe
from modules.base import BaseText2XModule, ErrorCorrector

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class SQL2Text(BaseText2XModule):
    """Klasa do konwersji zapytań SQL na opis tekstowy"""
    
    def initialize(self) -> None:
        """Inicjalizacja specyficzna dla modułu SQL2TEXT"""
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "codellama:7b-code",
            "dependencies": [],
            "temperature": 0.2,
            "max_tokens": 2000,
            "output_dir": None
        }
        
        # Aktualizacja konfiguracji
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Ładowanie konfiguracji z pliku
        self.load_config()
        
        # Inicjalizacja katalogu wyjściowego
        self.output_dir = self.config.get("output_dir")
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        self.logger.info(f"Moduł SQL2TEXT zainicjalizowany z modelem: {self.config['model']}")
    
    def ensure_model_available(self) -> bool:
        """Sprawdza, czy model jest dostępny"""
        try:
            # Sprawdź, czy Ollama jest zainstalowane i czy model jest dostępny
            cmd = ["ollama", "list"]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Błąd podczas sprawdzania dostępności modelu: {stderr}")
                return False
            
            # Sprawdź, czy model jest na liście
            return self.config["model"] in stdout
            
        except Exception as e:
            self.logger.error(f"Błąd podczas sprawdzania dostępności modelu: {e}")
            return False
    
    def process(self, sql_code: str, **kwargs) -> Dict[str, Any]:
        """Przetwarza zapytanie SQL na opis w języku naturalnym"""
        # Parametry przetwarzania
        model = kwargs.get('model', self.config['model'])
        temperature = kwargs.get('temperature', self.config['temperature'])
        max_tokens = kwargs.get('max_tokens', self.config['max_tokens'])
        detail_level = kwargs.get('detail_level', 'standard')  # standard, basic, detailed
        
        self.logger.info(f"Przetwarzanie SQL na tekst: {sql_code[:50]}...")
        
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "description": "",
                    "error": f"Model {model} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w wyjaśnianiu zapytań SQL.
Twoim zadaniem jest wygenerowanie dokładnego opisu w języku naturalnym, który wyjaśnia co robi podane zapytanie SQL.
Opis powinien być szczegółowy, ale zrozumiały dla osoby nieznającej szczegółów technicznych SQL.
Wyjaśnij cel zapytania, jakie dane pobiera lub modyfikuje, oraz jakie operacje wykonuje na tych danych."""
            
            # Dostosuj prompt w zależności od poziomu szczegółowości
            if detail_level == 'basic':
                system_prompt += "\nSkup się na podstawowym celu zapytania, bez wchodzenia w szczegóły techniczne."
            elif detail_level == 'detailed':
                system_prompt += "\nPodaj szczegółowe wyjaśnienie, w tym analizę klauzul, złączeń, filtrów i innych elementów zapytania."
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nWyjaśnij, co robi następujące zapytanie SQL:\n```sql\n{sql_code}\n```"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", model,
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Błąd podczas generowania opisu: {stderr}")
                return {
                    "success": False,
                    "description": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij opis z odpowiedzi
            description = stdout.strip()
            
            # Zapisz opis do pliku, jeśli podano katalog wyjściowy
            if self.output_dir:
                # Utwórz nazwę pliku na podstawie pierwszych słów zapytania SQL
                filename = sql_code.strip().lower().replace(" ", "_")[:30]
                filename = re.sub(r'[^a-z0-9_]', '', filename)
                filename = f"{filename}_{hash(sql_code) % 10000}.txt"
                
                # Zapisz opis do pliku
                file_path = os.path.join(self.output_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(description)
                
                self.logger.info(f"Opis SQL zapisany do pliku: {file_path}")
            
            return {
                "success": True,
                "description": description,
                "error": "",
                "analysis": "Opis wygenerowany pomyślnie",
                "model": model,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "detail_level": detail_level
                }
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas konwersji SQL na tekst: {e}")
            return {
                "success": False,
                "description": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def analyze_sql_query(self, sql_code: str) -> Dict[str, Any]:
        """Analizuje zapytanie SQL i zwraca jego strukturę i potencjalne problemy"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "analysis": "",
                    "error": f"Model {self.config['model']} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w analizie zapytań SQL.
Twoim zadaniem jest przeanalizowanie podanego zapytania SQL i zwrócenie:
1. Struktury zapytania (główne klauzule, tabele, warunki)
2. Potencjalnych problemów wydajnościowych
3. Sugestii optymalizacji
4. Oceny złożoności zapytania

Odpowiedź powinna być szczegółowa i techniczna."""
            
            prompt = f"Przeanalizuj następujące zapytanie SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.config["model"],
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Błąd podczas analizy zapytania: {stderr}")
                return {
                    "success": False,
                    "analysis": "",
                    "error": stderr
                }
            
            # Wyodrębnij analizę z odpowiedzi
            analysis = stdout.strip()
            
            return {
                "success": True,
                "analysis": analysis,
                "error": ""
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas analizy zapytania: {e}")
            return {
                "success": False,
                "analysis": "",
                "error": str(e)
            }
    
    def generate_example_data(self, sql_code: str) -> Dict[str, Any]:
        """Generuje przykładowe dane, które pasują do zapytania SQL"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "example_data": "",
                    "error": f"Model {self.config['model']} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w SQL i generowaniu danych testowych.
Twoim zadaniem jest wygenerowanie przykładowych danych, które pasują do podanego zapytania SQL.
Wygeneruj:
1. Definicje tabel (CREATE TABLE) z odpowiednimi typami danych
2. Przykładowe dane (INSERT INTO) dla każdej tabeli
3. Wynik zapytania na tych danych

Dane powinny być realistyczne i sensowne w kontekście zapytania."""
            
            prompt = f"Wygeneruj przykładowe dane dla następującego zapytania SQL:\n\n```sql\n{sql_code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.config["model"],
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.logger.error(f"Błąd podczas generowania przykładowych danych: {stderr}")
                return {
                    "success": False,
                    "example_data": "",
                    "error": stderr
                }
            
            # Wyodrębnij przykładowe dane z odpowiedzi
            example_data = stdout.strip()
            
            return {
                "success": True,
                "example_data": example_data,
                "error": ""
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania przykładowych danych: {e}")
            return {
                "success": False,
                "example_data": "",
                "error": str(e)
            }
    
    def validate_input(self, text: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Walidacja specyficzna dla modułu SQL2TEXT"""
        is_valid, error = super().validate_input(text, **kwargs)
        
        if not is_valid:
            return is_valid, error
        
        # Dodatkowa walidacja specyficzna dla SQL2TEXT
        if len(text) < 10:
            return False, "Zapytanie SQL jest zbyt krótkie (minimum 10 znaków)"
        
        # Sprawdź, czy tekst wygląda jak zapytanie SQL
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'FROM', 'WHERE', 'JOIN']
        has_sql_keyword = any(keyword in text.upper() for keyword in sql_keywords)
        
        if not has_sql_keyword:
            return False, "Tekst nie wygląda na zapytanie SQL (brak kluczowych słów SQL)"
        
        return True, None


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji modułu
    sql2text = SQL2Text()
    
    # Przykładowe zapytanie SQL
    sql_query = """
    SELECT u.username, COUNT(c.id) as comment_count
    FROM users u
    JOIN comments c ON u.id = c.user_id
    JOIN posts p ON c.post_id = p.id
    WHERE p.created_at >= DATE('now', '-1 month')
    GROUP BY u.id
    HAVING COUNT(c.id) >= 5
    ORDER BY comment_count DESC;
    """
    
    # Przetwarzanie zapytania SQL
    result = sql2text.execute(sql_query, detail_level='detailed')
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Jeśli generowanie powiodło się, przeprowadź analizę i wygeneruj przykładowe dane
    if result.get("success"):
        # Analiza zapytania
        analysis = sql2text.analyze_sql_query(sql_query)
        print("\nAnaliza zapytania:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
        
        # Generowanie przykładowych danych
        example_data = sql2text.generate_example_data(sql_query)
        print("\nPrzykładowe dane:")
        print(json.dumps(example_data, indent=2, ensure_ascii=False))
