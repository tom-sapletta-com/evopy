#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł bazowy dla wszystkich modułów TEXT2X w Evopy
"""

import os
import sys
import json
import logging
import importlib
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List, Tuple

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

class BaseText2XModule(ABC):
    """Abstrakcyjna klasa bazowa dla wszystkich modułów TEXT2X"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja modułu TEXT2X
        
        Args:
            config: Konfiguracja modułu (opcjonalna)
        """
        self.config = config or {}
        self.logger = self._setup_logger()
        self.initialize()
        
    def _setup_logger(self) -> logging.Logger:
        """
        Konfiguruje logger dla modułu
        
        Returns:
            logging.Logger: Skonfigurowany logger
        """
        logger_name = self.__class__.__name__
        logger = logging.getLogger(logger_name)
        
        # Sprawdź, czy logger już ma handlery
        if not logger.handlers:
            # Dodaj handler dla konsoli
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(console_handler)
            
            # Dodaj handler dla pliku
            log_dir = Path.home() / ".evopy" / "logs"
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(log_dir / f"{logger_name.lower()}.log")
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
            ))
            logger.addHandler(file_handler)
        
        return logger
        
    def initialize(self) -> None:
        """
        Inicjalizacja specyficzna dla modułu
        
        Ta metoda może być nadpisana przez klasy pochodne
        """
        self.logger.info(f"Inicjalizacja modułu {self.__class__.__name__}")
    
    @abstractmethod
    def process(self, text: str, **kwargs) -> Any:
        """
        Główna metoda przetwarzająca tekst na docelową formę
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry specyficzne dla modułu
            
        Returns:
            Any: Wynik przetwarzania
        """
        raise NotImplementedError("Każdy moduł musi implementować metodę process")
    
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
        return True, None
    
    def format_output(self, result: Any) -> Dict[str, Any]:
        """
        Formatowanie wyniku
        
        Args:
            result: Wynik do sformatowania
            
        Returns:
            Dict[str, Any]: Sformatowany wynik
        """
        if isinstance(result, dict):
            return result
        
        return {
            "success": True,
            "result": result
        }
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Obsługa błędów specyficzna dla modułu
        
        Args:
            error: Wyjątek do obsługi
            
        Returns:
            Dict[str, Any]: Informacja o błędzie
        """
        self.logger.error(f"Błąd podczas przetwarzania: {error}", exc_info=True)
        
        return {
            "success": False,
            "error": str(error),
            "error_type": error.__class__.__name__
        }
    
    def check_dependencies(self) -> Tuple[bool, List[str]]:
        """
        Sprawdza, czy wszystkie zależności modułu są zainstalowane
        
        Returns:
            Tuple[bool, List[str]]: (czy_wszystkie_zainstalowane, lista_brakujących)
        """
        missing_dependencies = []
        required_dependencies = self.config.get("dependencies", [])
        
        for dependency in required_dependencies:
            try:
                importlib.import_module(dependency)
            except ImportError:
                missing_dependencies.append(dependency)
        
        return len(missing_dependencies) == 0, missing_dependencies
    
    def install_dependencies(self) -> bool:
        """
        Instaluje brakujące zależności
        
        Returns:
            bool: Czy instalacja się powiodła
        """
        import subprocess
        
        all_installed, missing = self.check_dependencies()
        
        if all_installed:
            self.logger.info("Wszystkie zależności są już zainstalowane")
            return True
        
        self.logger.info(f"Instalowanie brakujących zależności: {', '.join(missing)}")
        
        try:
            for dependency in missing:
                self.logger.info(f"Instalowanie {dependency}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])
            
            # Sprawdź ponownie
            all_installed, still_missing = self.check_dependencies()
            
            if all_installed:
                self.logger.info("Wszystkie zależności zostały zainstalowane")
                return True
            else:
                self.logger.error(f"Nie udało się zainstalować: {', '.join(still_missing)}")
                return False
        except Exception as e:
            self.logger.error(f"Błąd podczas instalacji zależności: {e}")
            return False
    
    def save_config(self) -> bool:
        """
        Zapisuje konfigurację modułu
        
        Returns:
            bool: Czy zapis się powiódł
        """
        config_dir = Path.home() / ".evopy" / "config"
        os.makedirs(config_dir, exist_ok=True)
        
        config_file = config_dir / f"{self.__class__.__name__.lower()}.json"
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Konfiguracja zapisana do {config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
            return False
    
    def load_config(self) -> bool:
        """
        Ładuje konfigurację modułu
        
        Returns:
            bool: Czy ładowanie się powiodło
        """
        config_file = Path.home() / ".evopy" / "config" / f"{self.__class__.__name__.lower()}.json"
        
        if not config_file.exists():
            self.logger.info(f"Plik konfiguracyjny {config_file} nie istnieje")
            return False
        
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self.config.update(json.load(f))
            
            self.logger.info(f"Konfiguracja załadowana z {config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
            return False
    
    def execute(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Wykonuje pełny proces przetwarzania tekstu
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry specyficzne dla modułu
            
        Returns:
            Dict[str, Any]: Wynik przetwarzania
        """
        try:
            # Walidacja wejścia
            is_valid, error_message = self.validate_input(text, **kwargs)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_message
                }
            
            # Sprawdź zależności
            all_installed, missing = self.check_dependencies()
            if not all_installed:
                return {
                    "success": False,
                    "error": f"Brakujące zależności: {', '.join(missing)}",
                    "missing_dependencies": missing
                }
            
            # Przetwarzanie
            self.logger.info(f"Przetwarzanie tekstu: {text[:50]}...")
            result = self.process(text, **kwargs)
            
            # Formatowanie wyniku
            return self.format_output(result)
        except Exception as e:
            return self.handle_error(e)


# Przykład implementacji konkretnego modułu TEXT2X
class Text2PythonExample(BaseText2XModule):
    """Przykładowa implementacja modułu TEXT2PYTHON"""
    
    def initialize(self) -> None:
        """Inicjalizacja specyficzna dla modułu TEXT2PYTHON"""
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "llama3",
            "dependencies": ["numpy", "pandas"],
            "max_tokens": 1000
        }
        
        # Aktualizacja konfiguracji
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Ładowanie konfiguracji z pliku
        self.load_config()
    
    def process(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Przetwarza tekst na kod Python
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict[str, Any]: Wygenerowany kod Python
        """
        # W rzeczywistej implementacji tutaj byłoby wywołanie modelu LLM
        # Dla przykładu zwracamy prosty kod
        self.logger.info(f"Generowanie kodu Python dla: {text[:50]}...")
        
        # Przykładowa implementacja
        if "suma" in text.lower():
            code = "def suma(a, b):\n    return a + b\n\nwynik = suma(5, 3)\nprint(wynik)"
        elif "lista" in text.lower():
            code = "lista = [1, 2, 3, 4, 5]\nprint(sum(lista))"
        else:
            code = f"print('Przetwarzanie tekstu: {text}')"
        
        return {
            "code": code,
            "language": "python",
            "query": text
        }
    
    def validate_input(self, text: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """Walidacja specyficzna dla modułu TEXT2PYTHON"""
        is_valid, error = super().validate_input(text, **kwargs)
        
        if not is_valid:
            return is_valid, error
        
        # Dodatkowa walidacja specyficzna dla TEXT2PYTHON
        if len(text) < 5:
            return False, "Tekst jest zbyt krótki (minimum 5 znaków)"
        
        return True, None


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji modułu
    text2python = Text2PythonExample()
    
    # Przetwarzanie tekstu
    result = text2python.execute("Napisz funkcję, która sumuje dwie liczby")
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
