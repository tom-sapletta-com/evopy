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
        self.logger.info(f"Ladowanie rozszerzeń z katalogu: {self.extensions_dir}")
        
        # Sprawdź czy katalog istnieje
        if not self.extensions_dir.exists():
            self.logger.warning(f"Katalog rozszerzeń {self.extensions_dir} nie istnieje")
            os.makedirs(self.extensions_dir, exist_ok=True)
            return
        
        # Dodaj katalog nadrzędny rozszerzeń do ścieżki Pythona
        parent_dir = str(self.extensions_dir.parent)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        # Dodaj katalog modules do ścieżki Pythona, jeśli nie jest już dodany
        modules_dir = str(Path(parent_dir).parent)
        if modules_dir not in sys.path:
            sys.path.insert(0, modules_dir)
        
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
                
                # Spróbuj różne sposoby importowania modułu
                extension_module = None
                extension_name = item.name
                
                # Metoda 1: Bezpośredni import
                try:
                    extension_module = importlib.import_module(extension_name)
                    self._register_extension(extension_name, extension_module)
                    continue
                except ImportError:
                    pass
                
                # Metoda 2: Import z przedrostkiem extensions
                try:
                    full_extension_name = f"extensions.{extension_name}"
                    extension_module = importlib.import_module(full_extension_name)
                    self._register_extension(extension_name, extension_module)
                    continue
                except ImportError:
                    pass
                
                # Metoda 3: Import z pełną ścieżką
                try:
                    full_path_name = f"modules.text2python.extensions.{extension_name}"
                    extension_module = importlib.import_module(full_path_name)
                    self._register_extension(extension_name, extension_module)
                    continue
                except ImportError as e:
                    self.logger.error(f"Błąd podczas ładowania rozszerzenia {extension_name}: {e}")
            
            # Jeśli to plik Python, załaduj jako moduł
            elif item.suffix == '.py' and item.name != '__init__.py':
                extension_name = item.stem
                
                # Spróbuj różne sposoby importowania modułu
                try:
                    extension_module = importlib.import_module(extension_name)
                    self._register_extension(extension_name, extension_module)
                except ImportError:
                    try:
                        full_extension_name = f"extensions.{extension_name}"
                        extension_module = importlib.import_module(full_extension_name)
                        self._register_extension(extension_name, extension_module)
                    except ImportError as e:
                        self.logger.error(f"Błąd podczas ładowania rozszerzenia {extension_name}: {e}")
        
        self.logger.info(f"Załadowano {len(self.extensions)} rozszerzeń")
    
    def _register_extension(self, name: str, module) -> None:
        """
        Rejestruje rozszerzenie w menedżerze
        
        Args:
            name: Nazwa rozszerzenia
            module: Moduł rozszerzenia
        """
        # Sprawdź czy moduł zawiera wymagane funkcje bezpośrednio
        has_identify = hasattr(module, 'identify_query')
        has_generate = hasattr(module, 'generate_code')
        
        # Jeśli funkcje nie są dostępne bezpośrednio, sprawdź czy są dostępne poprzez __dict__
        if not (has_identify and has_generate):
            if hasattr(module, '__dict__'):
                has_identify = 'identify_query' in module.__dict__
                has_generate = 'generate_code' in module.__dict__
        
        # Jeśli nadal nie znaleziono funkcji, sprawdź czy są dostępne jako atrybuty
        if not (has_identify and has_generate):
            try:
                # Próba bezpośredniego dostępu do funkcji
                identify_func = getattr(module, 'identify_query', None)
                generate_func = getattr(module, 'generate_code', None)
                has_identify = callable(identify_func)
                has_generate = callable(generate_func)
            except Exception:
                pass
        
        # Jeśli nadal nie znaleziono funkcji, wyświetl ostrzeżenie i zakończ
        if not (has_identify and has_generate):
            self.logger.warning(f"Rozszerzenie {name} nie zawiera wymaganych funkcji identify_query i generate_code")
            return
        
        # Dodaj rozszerzenie do listy
        self.extensions[name] = module
        self.logger.info(f"Zarejestrowano rozszerzenie: {name}")
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
