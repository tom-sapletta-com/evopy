#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ExtensionManager - Komponent odpowiedzialny za zarządzanie rozszerzeniami
dla modułu text2python.
"""

import os
import sys
import importlib
import logging
import inspect
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Type, Union

class ExtensionManager:
    """
    Klasa odpowiedzialna za zarządzanie rozszerzeniami dla modułu text2python.
    Automatycznie wykrywa i ładuje rozszerzenia z katalogu extensions/.
    """
    
    def __init__(self, extensions_dir: Optional[str] = None, config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja menedżera rozszerzeń
        
        Args:
            extensions_dir: Ścieżka do katalogu z rozszerzeniami (opcjonalna)
            config: Dodatkowa konfiguracja
        """
        self.logger = logging.getLogger('ExtensionManager')
        self.config = config or {}
        
        # Ustal ścieżkę do katalogu z rozszerzeniami
        if extensions_dir:
            self.extensions_dir = Path(extensions_dir)
        else:
            # Domyślnie katalog extensions/ w katalogu modułu text2python
            self.extensions_dir = Path(__file__).parent.parent / "extensions"
        
        # Słownik załadowanych rozszerzeń
        self.extensions: Dict[str, Any] = {}
        
        # Słownik funkcji identyfikujących zapytania dla rozszerzeń
        self.identify_functions: Dict[str, Callable] = {}
        
        # Słownik funkcji generujących kod dla rozszerzeń
        self.generate_functions: Dict[str, Callable] = {}
        
        # Załaduj rozszerzenia
        self._load_extensions()
    
    def _load_extensions(self) -> None:
        """
        Ładuje wszystkie dostępne rozszerzenia z katalogu extensions/
        """
        self.logger.info(f"Ładowanie rozszerzeń z katalogu: {self.extensions_dir}")
        
        # Sprawdź czy katalog istnieje
        if not self.extensions_dir.exists():
            self.logger.warning(f"Katalog rozszerzeń {self.extensions_dir} nie istnieje")
            os.makedirs(self.extensions_dir, exist_ok=True)
            return
        
        # Dodaj katalog rozszerzeń do ścieżki Pythona
        if str(self.extensions_dir) not in sys.path:
            sys.path.insert(0, str(self.extensions_dir))
        
        # Przeszukaj katalog rozszerzeń
        for item in self.extensions_dir.iterdir():
            # Pomiń pliki ukryte i katalogi __pycache__
            if item.name.startswith('.') or item.name == '__pycache__':
                continue
            
            # Jeśli to katalog, sprawdź czy zawiera plik __init__.py
            if item.is_dir():
                init_file = item / "__init__.py"
                if not init_file.exists():
                    continue
                
                # Załaduj rozszerzenie jako pakiet
                extension_name = item.name
                try:
                    extension_module = importlib.import_module(extension_name)
                    self._register_extension(extension_name, extension_module)
                except Exception as e:
                    self.logger.error(f"Błąd podczas ładowania rozszerzenia {extension_name}: {e}")
            
            # Jeśli to plik Python, załaduj jako moduł
            elif item.suffix == '.py' and item.name != '__init__.py':
                extension_name = item.stem
                try:
                    extension_module = importlib.import_module(extension_name)
                    self._register_extension(extension_name, extension_module)
                except Exception as e:
                    self.logger.error(f"Błąd podczas ładowania rozszerzenia {extension_name}: {e}")
        
        self.logger.info(f"Załadowano {len(self.extensions)} rozszerzeń")
    
    def _register_extension(self, name: str, module: Any) -> None:
        """
        Rejestruje rozszerzenie
        
        Args:
            name: Nazwa rozszerzenia
            module: Moduł rozszerzenia
        """
        # Sprawdź czy moduł zawiera wymagane funkcje
        has_identify = hasattr(module, 'identify_query')
        has_generate = hasattr(module, 'generate_code')
        
        if not (has_identify and has_generate):
            self.logger.warning(f"Rozszerzenie {name} nie zawiera wymaganych funkcji identify_query i generate_code")
            return
        
        # Zarejestruj rozszerzenie
        self.extensions[name] = module
        self.identify_functions[name] = getattr(module, 'identify_query')
        self.generate_functions[name] = getattr(module, 'generate_code')
        
        self.logger.info(f"Zarejestrowano rozszerzenie: {name}")
    
    def identify_extension_for_query(self, query: str) -> Optional[str]:
        """
        Identyfikuje rozszerzenie, które może obsłużyć dane zapytanie
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            Optional[str]: Nazwa rozszerzenia lub None, jeśli żadne nie pasuje
        """
        for name, identify_func in self.identify_functions.items():
            try:
                if identify_func(query):
                    self.logger.info(f"Zapytanie '{query[:30]}...' zostanie obsłużone przez rozszerzenie {name}")
                    return name
            except Exception as e:
                self.logger.error(f"Błąd podczas identyfikacji zapytania przez rozszerzenie {name}: {e}")
        
        return None
    
    def generate_code_with_extension(self, extension_name: str, query: str) -> Dict[str, Any]:
        """
        Generuje kod przy użyciu określonego rozszerzenia
        
        Args:
            extension_name: Nazwa rozszerzenia
            query: Zapytanie użytkownika
            
        Returns:
            Dict[str, Any]: Wygenerowany kod i metadane
        """
        if extension_name not in self.generate_functions:
            self.logger.error(f"Rozszerzenie {extension_name} nie istnieje")
            return {
                "success": False,
                "code": "",
                "error": f"Rozszerzenie {extension_name} nie istnieje"
            }
        
        try:
            generate_func = self.generate_functions[extension_name]
            result = generate_func(query)
            
            # Dodaj informację o rozszerzeniu
            if isinstance(result, dict):
                result["extension"] = extension_name
            
            return result
        except Exception as e:
            self.logger.error(f"Błąd podczas generowania kodu przez rozszerzenie {extension_name}: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e),
                "extension": extension_name
            }
    
    def get_extension_info(self, extension_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Zwraca informacje o rozszerzeniach
        
        Args:
            extension_name: Nazwa rozszerzenia (opcjonalna)
            
        Returns:
            Dict[str, Any]: Informacje o rozszerzeniach
        """
        if extension_name:
            if extension_name not in self.extensions:
                return {"error": f"Rozszerzenie {extension_name} nie istnieje"}
            
            module = self.extensions[extension_name]
            return {
                "name": extension_name,
                "docstring": module.__doc__ or "Brak dokumentacji",
                "functions": [f for f in dir(module) if callable(getattr(module, f)) and not f.startswith('_')]
            }
        
        # Zwróć informacje o wszystkich rozszerzeniach
        return {
            "extensions_count": len(self.extensions),
            "extensions": [
                {
                    "name": name,
                    "docstring": module.__doc__ or "Brak dokumentacji"
                }
                for name, module in self.extensions.items()
            ]
        }
    
    def reload_extensions(self) -> None:
        """
        Przeładowuje wszystkie rozszerzenia
        """
        self.logger.info("Przeładowywanie rozszerzeń...")
        
        # Wyczyść słowniki
        self.extensions.clear()
        self.identify_functions.clear()
        self.generate_functions.clear()
        
        # Załaduj rozszerzenia ponownie
        self._load_extensions()
