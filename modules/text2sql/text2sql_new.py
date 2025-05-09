#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł TEXT2SQL wykorzystujący nową architekturę bazową

Moduł konwertuje opisy w języku naturalnym na zapytania SQL.
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

class Text2SQL(BaseText2XModule):
    """Klasa do konwersji tekstu na zapytania SQL"""
    
    def initialize(self) -> None:
        """Inicjalizacja specyficzna dla modułu TEXT2SQL"""
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "codellama:7b-code",
            "dependencies": [],
            "temperature": 0.2,
            "max_tokens": 2000,
            "sql_dir": None
        }
        
        # Aktualizacja konfiguracji
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Ładowanie konfiguracji z pliku
        self.load_config()
        
        # Inicjalizacja katalogu SQL
        self.sql_dir = self.config.get("sql_dir")
        if self.sql_dir:
            os.makedirs(self.sql_dir, exist_ok=True)
        
        self.logger.info(f"Moduł TEXT2SQL zainicjalizowany z modelem: {self.config['model']}")
    
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
    
    def process(self, text: str, **kwargs) -> Dict[str, Any]:
        """Przetwarza tekst na zapytanie SQL"""
        # Parametry przetwarzania
        model = kwargs.get('model', self.config['model'])
        temperature = kwargs.get('temperature', self.config['temperature'])
        max_tokens = kwargs.get('max_tokens', self.config['max_tokens'])
        db_schema = kwargs.get('db_schema', "")
        
        self.logger.info(f"Przetwarzanie tekstu na SQL: {text[:50]}...")
        
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {model} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na zapytania SQL.
Twoim zadaniem jest wygenerowanie zapytania SQL, które realizuje opisane zadanie.
Generuj tylko kod SQL, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Zapewnij, że zapytanie jest poprawne składniowo i realizuje dokładnie to, o co prosi użytkownik."""
            
            # Dodaj informacje o schemacie bazy danych, jeśli zostały podane
            if db_schema:
                system_prompt += f"\n\nPracujesz z następującym schematem bazy danych:\n{db_schema}"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\nUtwórz zapytanie SQL, które realizuje następujące zadanie:\n{text}\n\nKod SQL:"
            
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
                self.logger.error(f"Błąd podczas generowania kodu SQL: {stderr}")
                return {
                    "success": False,
                    "code": "",
                    "error": stderr,
                    "analysis": "Błąd generowania"
                }
            
            # Wyodrębnij kod SQL z odpowiedzi
            code = stdout.strip()
            
            # Jeśli kod jest otoczony znacznikami ```sql i ```, usuń je
            code = re.sub(r'^```sql\n|^```\n|\n```$', '', code, flags=re.MULTILINE)
            
            # Zapisz zapytanie SQL do pliku, jeśli podano katalog SQL
            if self.sql_dir:
                # Utwórz nazwę pliku na podstawie pierwszych słów zapytania
                filename = text.lower().replace(" ", "_")[:30]
                filename = re.sub(r'[^a-z0-9_]', '', filename)
                filename = f"{filename}_{hash(text) % 10000}.sql"
                
                # Zapisz zapytanie do pliku
                file_path = os.path.join(self.sql_dir, filename)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(code)
                
                self.logger.info(f"Zapytanie SQL zapisane do pliku: {file_path}")
            
            return {
                "success": True,
                "code": code,
                "error": "",
                "analysis": "Kod SQL wygenerowany pomyślnie",
                "model": model,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas konwersji tekstu na SQL: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "analysis": "Wyjątek podczas generowania"
            }
    
    def explain_sql(self, sql_code: str) -> Dict[str, Any]:
        """Generuje wyjaśnienie zapytania SQL w języku naturalnym"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "explanation": "",
                    "error": f"Model {self.config['model']} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu zapytań SQL. Twoim zadaniem jest wyjaśnienie działania podanego kodu SQL w prosty i zrozumiały sposób. Wyjaśnienie powinno być szczegółowe, ale zrozumiałe dla osoby bez głębokiej znajomości SQL.'
            
            prompt = f"Wyjaśnij działanie następującego zapytania SQL:\n\n```sql\n{sql_code}\n```"
            
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
                self.logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return {
                    "success": False,
                    "explanation": "",
                    "error": stderr
                }
            
            # Wyodrębnij wyjaśnienie z odpowiedzi
            explanation = stdout.strip()
            
            return {
                "success": True,
                "explanation": explanation,
                "error": ""
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return {
                "success": False,
                "explanation": "",
                "error": str(e)
            }
    
    def optimize_sql(self, sql_code: str) -> Dict[str, Any]:
        """Optymalizuje zapytanie SQL"""
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return {
                    "success": False,
                    "optimized_code": "",
                    "error": f"Model {self.config['model']} nie jest dostępny"
                }
            
            # Przygotuj zapytanie do modelu
            system_prompt = """Jesteś ekspertem w optymalizacji zapytań SQL.
Twoim zadaniem jest optymalizacja podanego zapytania SQL, aby działało szybciej i efektywniej.
Zaproponuj zoptymalizowane zapytanie, które zwraca dokładnie te same wyniki, ale jest bardziej wydajne.
Wyjaśnij również, jakie optymalizacje zostały wprowadzone i dlaczego są one korzystne."""
            
            prompt = f"Zoptymalizuj następujące zapytanie SQL:\n\n```sql\n{sql_code}\n```"
            
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
                self.logger.error(f"Błąd podczas optymalizacji zapytania: {stderr}")
                return {
                    "success": False,
                    "optimized_code": "",
                    "explanation": "",
                    "error": stderr
                }
            
            # Wyodrębnij zoptymalizowany kod i wyjaśnienie z odpowiedzi
            response = stdout.strip()
            
            # Spróbuj wyodrębnić kod SQL z odpowiedzi
            sql_match = re.search(r'```sql\n(.*?)\n```', response, re.DOTALL)
            if sql_match:
                optimized_code = sql_match.group(1).strip()
                explanation = re.sub(r'```sql\n.*?\n```', '', response, flags=re.DOTALL).strip()
            else:
                # Jeśli nie znaleziono kodu w znacznikach, spróbuj heurystycznie
                lines = response.split('\n')
                code_lines = []
                explanation_lines = []
                in_code = False
                
                for line in lines:
                    if line.strip().upper().startswith(('SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'WITH')):
                        in_code = True
                        code_lines.append(line)
                    elif in_code and line.strip() and not line.strip().startswith(('--', '#', '/*')):
                        code_lines.append(line)
                    else:
                        in_code = False
                        explanation_lines.append(line)
                
                optimized_code = '\n'.join(code_lines).strip()
                explanation = '\n'.join(explanation_lines).strip()
            
            return {
                "success": True,
                "optimized_code": optimized_code,
                "explanation": explanation,
                "error": ""
            }
            
        except Exception as e:
            self.logger.error(f"Błąd podczas optymalizacji zapytania: {e}")
            return {
                "success": False,
                "optimized_code": "",
                "explanation": "",
                "error": str(e)
            }
    
    def validate_input(self, text: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Walidacja specyficzna dla modułu TEXT2SQL"""
        is_valid, error = super().validate_input(text, **kwargs)
        
        if not is_valid:
            return is_valid, error
        
        # Dodatkowa walidacja specyficzna dla TEXT2SQL
        if len(text) < 10:
            return False, "Opis zapytania jest zbyt krótki (minimum 10 znaków)"
        
        return True, None


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji modułu
    text2sql = Text2SQL()
    
    # Przykładowy schemat bazy danych
    db_schema = """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE posts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    
    CREATE TABLE comments (
        id INTEGER PRIMARY KEY,
        post_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (post_id) REFERENCES posts(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """
    
    # Przetwarzanie tekstu
    query = "Znajdź wszystkich użytkowników, którzy napisali co najmniej 5 komentarzy do postów utworzonych w ciągu ostatniego miesiąca"
    result = text2sql.execute(query, db_schema=db_schema)
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Jeśli generowanie powiodło się, wyjaśnij i optymalizuj zapytanie
    if result.get("success") and "code" in result.get("result", {}):
        sql_code = result["result"]["code"]
        
        # Wyjaśnienie zapytania
        explanation = text2sql.explain_sql(sql_code)
        print("\nWyjaśnienie zapytania:")
        print(json.dumps(explanation, indent=2, ensure_ascii=False))
        
        # Optymalizacja zapytania
        optimization = text2sql.optimize_sql(sql_code)
        print("\nOptymalizacja zapytania:")
        print(json.dumps(optimization, indent=2, ensure_ascii=False))
