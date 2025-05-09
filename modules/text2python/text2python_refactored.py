#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text2Python - Moduł do konwersji tekstu na kod Python

Ten moduł wykorzystuje model językowy do konwersji żądań użytkownika
wyrażonych w języku naturalnym na funkcje Python.
Zaimplementowany zgodnie z nową architekturą bazową Evopy.
"""

import os
import sys
import json
import time
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj klasy bazowe
from modules.base import BaseText2XModule, ConfigManager

# Importuj komponenty
from modules.text2python.components import (
    CodeGenerator,
    CodeAnalyzer,
    QueryAnalyzer,
    ExtensionManager
)

class Text2Python(BaseText2XModule):
    """
    Klasa do konwersji tekstu na kod Python.
    
    Wykorzystuje architekturę komponentową do podziału odpowiedzialności:
    - CodeGenerator - generowanie kodu Python
    - CodeAnalyzer - analiza i wyjaśnianie kodu
    - QueryAnalyzer - analiza zapytań użytkownika
    - ExtensionManager - zarządzanie rozszerzeniami
    """
    
    def initialize(self) -> None:
        """
        Inicjalizacja specyficzna dla modułu TEXT2PYTHON
        """
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "llama3",
            "dependencies": ["numpy", "pandas", "matplotlib"],
            "max_tokens": 1000,
            "temperature": 0.7,
            "use_sandbox": True,
            "sandbox_type": "docker",
            "code_dir": None,
            "extensions_dir": str(Path(__file__).parent / "extensions")
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
        
        # Ustawienie katalogu dla wygenerowanego kodu
        self.code_dir = self.config.get("code_dir")
        if self.code_dir:
            self.code_dir = Path(self.code_dir)
            os.makedirs(self.code_dir, exist_ok=True)
        
        # Inicjalizacja komponentów
        self.logger.info("Inicjalizacja komponentów...")
        
        self.code_generator = CodeGenerator(
            model_name=self.config["model"],
            config=self.config
        )
        
        self.code_analyzer = CodeAnalyzer(
            model_name=self.config["model"],
            config=self.config
        )
        
        self.query_analyzer = QueryAnalyzer(
            config=self.config
        )
        
        self.extension_manager = ExtensionManager(
            extensions_dir=self.config["extensions_dir"],
            config=self.config
        )
        
        self.logger.info(f"Moduł TEXT2PYTHON zainicjalizowany z modelem: {self.config['model']}")
    
    def load_config(self) -> None:
        """
        Ładuje konfigurację modułu z pliku
        """
        config_path = Path.home() / ".evopy" / "config" / "text2python.json"
        
        if not config_path.exists():
            self.logger.info(f"Plik konfiguracyjny {config_path} nie istnieje")
            return
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.config.update(config)
            
            self.logger.info(f"Konfiguracja załadowana z {config_path}")
        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
    
    def process(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Przetwarza tekst na kod Python
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict[str, Any]: Wygenerowany kod Python
        """
        # Walidacja wejścia
        is_valid, error_message = self.validate_input(text, **kwargs)
        if not is_valid:
            return {
                "success": False,
                "code": "",
                "error": error_message
            }
        
        # Analiza zapytania
        query_analysis = self.query_analyzer.analyze_query(text)
        
        if not query_analysis["is_valid"]:
            return {
                "success": False,
                "code": "def execute():\n    return 'Proszę podać prawidłowe zapytanie'",
                "error": "Zapytanie jest puste lub zawiera tylko znaki specjalne",
                "analysis": "Nieprawidłowe zapytanie",
                "explanation": "Twoje zapytanie nie zawierało wystarczających informacji do wygenerowania kodu."
            }
        
        # Sprawdź czy zapytanie może być obsłużone przez rozszerzenie
        extension_name = self.extension_manager.identify_extension_for_query(text)
        
        if extension_name:
            self.logger.info(f"Zapytanie będzie obsłużone przez rozszerzenie: {extension_name}")
            result = self.extension_manager.generate_code_with_extension(extension_name, text)
            
            # Dodaj dodatkowe informacje do wyniku
            if result.get("success", False):
                # Dodaj wyjaśnienie kodu, jeśli nie zostało dostarczone przez rozszerzenie
                if "explanation" not in result:
                    result["explanation"] = self.code_analyzer.explain_code(result["code"])
                
                # Dodaj analizę kodu
                if "analysis" not in result:
                    analysis = self.code_analyzer.analyze_code(result["code"], text)
                    result["analysis"] = analysis
                
                # Dodaj identyfikator kodu i ścieżkę do pliku
                code_id = str(uuid.uuid4())
                result["code_id"] = code_id
                
                # Zapisz kod do pliku jeśli podano katalog
                if self.code_dir:
                    code_file = self.code_dir / f"{code_id}.py"
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(result["code"])
                    result["code_file"] = str(code_file)
            
            return result
        
        # Generowanie kodu przy użyciu generatora kodu
        generation_result = self.code_generator.generate_code(text)
        
        if not generation_result.get("success", False):
            return generation_result
        
        code = generation_result["code"]
        
        # Analiza wygenerowanego kodu
        analysis = self.code_analyzer.analyze_code(code, text)
        
        # Generowanie wyjaśnienia kodu
        explanation = self.code_analyzer.explain_code(code)
        
        # Zapisz kod do pliku jeśli podano katalog
        code_id = str(uuid.uuid4())
        code_file = None
        if self.code_dir:
            code_file = self.code_dir / f"{code_id}.py"
            with open(code_file, "w", encoding="utf-8") as f:
                f.write(code)
        
        # Utwórz podsumowanie analizy
        analysis_summary = ""
        if analysis.get("issues") and len(analysis["issues"]) > 0:
            analysis_summary = "Potencjalne problemy: " + ", ".join(analysis["issues"])
        elif not analysis.get("is_logical", True):
            analysis_summary = "Kod może zawierać błędy logiczne."
        elif not analysis.get("matches_intent", True):
            analysis_summary = "Kod może nie realizować dokładnie tego, o co prosiłeś."
        else:
            analysis_summary = "Kod wydaje się poprawny i zgodny z intencją."
        
        # Zwróć wyniki
        return {
            "success": True,
            "code": code,
            "code_id": code_id,
            "code_file": str(code_file) if code_file else None,
            "explanation": explanation,
            "analysis": analysis_summary,
            "analysis_details": analysis,
            "matches_intent": analysis.get("matches_intent", True),
            "is_logical": analysis.get("is_logical", True),
            "suggestions": analysis.get("suggestions", []),
            "query_type": query_analysis.get("query_type", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_input(self, text: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Walidacja danych wejściowych
        
        Args:
            text: Tekst wejściowy do walidacji
            **kwargs: Dodatkowe parametry do walidacji
            
        Returns:
            Tuple[bool, Optional[str]]: (czy_poprawne, komunikat_błędu)
        """
        if not text or not isinstance(text, str):
            return False, "Tekst wejściowy musi być niepustym ciągiem znaków"
            
        if len(text) < 3:
            return False, "Tekst jest zbyt krótki (minimum 3 znaki)"
            
        return True, None
    
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
            # W rzeczywistej implementacji tutaj byłoby wywołanie piaskownicy Docker
            try:
                from modules.docker_sandbox import DockerSandbox
                sandbox = DockerSandbox()
                return sandbox.run_code(code)
            except ImportError:
                self.logger.error("Nie można zaimportować modułu DockerSandbox")
                return {
                    "success": False,
                    "error": "Moduł DockerSandbox nie jest dostępny"
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
    
    def get_available_extensions(self) -> Dict[str, Any]:
        """
        Zwraca listę dostępnych rozszerzeń
        
        Returns:
            Dict[str, Any]: Informacje o dostępnych rozszerzeniach
        """
        return self.extension_manager.get_extension_info()
    
    def reload_extensions(self) -> None:
        """
        Przeładowuje wszystkie rozszerzenia
        """
        self.extension_manager.reload_extensions()
    
    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Python(model={self.config['model']})"


# Przykład użycia
if __name__ == "__main__":
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Tworzenie instancji modułu
    text2python = Text2Python()
    
    # Przetwarzanie tekstu
    query = "Napisz funkcję, która sumuje dwie liczby"
    result = text2python.process(query)
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Wykonanie wygenerowanego kodu
    if result["success"]:
        code = result["code"]
        execution_result = text2python.execute_code(code, use_sandbox=False)
        print("\nWynik wykonania kodu:")
        print(json.dumps(execution_result, indent=2, ensure_ascii=False))
