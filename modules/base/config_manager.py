#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Menedżer konfiguracji dla modułów TEXT2X w Evopy
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Set

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('ConfigManager')

class ConfigManager:
    """Menedżer konfiguracji dla wszystkich modułów"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Inicjalizacja menedżera konfiguracji
        
        Args:
            config_path: Ścieżka do pliku głównej konfiguracji (opcjonalna)
        """
        self.config_path = config_path or Path.home() / ".evopy" / "config" / "config.json"
        self.config_dir = self.config_path.parent
        
        # Utwórz katalog konfiguracji, jeśli nie istnieje
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Główna konfiguracja
        self.config = self._load_config()
        
        # Konfiguracje modułów
        self.module_configs: Dict[str, Dict[str, Any]] = {}
        
        # Załaduj konfiguracje wszystkich modułów
        self._load_all_module_configs()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Ładuje główną konfigurację z pliku
        
        Returns:
            Dict[str, Any]: Załadowana konfiguracja
        """
        if not self.config_path.exists():
            logger.info(f"Plik konfiguracyjny {self.config_path} nie istnieje, tworzenie domyślnej konfiguracji")
            default_config = {
                "version": "1.0.0",
                "modules": {},
                "global": {
                    "log_level": "INFO",
                    "api_enabled": True,
                    "api_port": 5000,
                    "sandbox_enabled": True
                }
            }
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            logger.info(f"Konfiguracja załadowana z {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
            return {
                "version": "1.0.0",
                "modules": {},
                "global": {
                    "log_level": "INFO",
                    "api_enabled": True,
                    "api_port": 5000,
                    "sandbox_enabled": True
                }
            }
    
    def _save_config(self, config: Dict[str, Any]) -> bool:
        """
        Zapisuje główną konfigurację do pliku
        
        Args:
            config: Konfiguracja do zapisania
            
        Returns:
            bool: Czy zapis się powiódł
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Konfiguracja zapisana do {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania konfiguracji: {e}")
            return False
    
    def _load_all_module_configs(self) -> None:
        """Ładuje konfiguracje wszystkich modułów"""
        for config_file in self.config_dir.glob("*.json"):
            if config_file.name == "config.json":
                continue
            
            module_name = config_file.stem
            
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    module_config = json.load(f)
                
                self.module_configs[module_name] = module_config
                logger.info(f"Konfiguracja modułu {module_name} załadowana z {config_file}")
            except Exception as e:
                logger.error(f"Błąd podczas ładowania konfiguracji modułu {module_name}: {e}")
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Pobiera konfigurację dla konkretnego modułu
        
        Args:
            module_name: Nazwa modułu
            
        Returns:
            Dict[str, Any]: Konfiguracja modułu
        """
        # Jeśli konfiguracja modułu nie jest załadowana, spróbuj ją załadować
        if module_name not in self.module_configs:
            module_config_path = self.config_dir / f"{module_name.lower()}.json"
            
            if module_config_path.exists():
                try:
                    with open(module_config_path, "r", encoding="utf-8") as f:
                        self.module_configs[module_name] = json.load(f)
                    
                    logger.info(f"Konfiguracja modułu {module_name} załadowana z {module_config_path}")
                except Exception as e:
                    logger.error(f"Błąd podczas ładowania konfiguracji modułu {module_name}: {e}")
                    self.module_configs[module_name] = {}
            else:
                # Jeśli plik konfiguracyjny nie istnieje, utwórz domyślną konfigurację
                logger.info(f"Plik konfiguracyjny modułu {module_name} nie istnieje, tworzenie domyślnej konfiguracji")
                self.module_configs[module_name] = {}
                
                # Sprawdź, czy moduł ma konfigurację w głównym pliku konfiguracyjnym
                if "modules" in self.config and module_name in self.config["modules"]:
                    self.module_configs[module_name] = self.config["modules"][module_name]
        
        # Połącz konfigurację modułu z globalnymi ustawieniami
        config = self.module_configs.get(module_name, {}).copy()
        
        # Dodaj globalne ustawienia, jeśli nie są nadpisane w konfiguracji modułu
        if "global" in self.config:
            for key, value in self.config["global"].items():
                if key not in config:
                    config[key] = value
        
        return config
    
    def update_module_config(self, module_name: str, config: Dict[str, Any]) -> bool:
        """
        Aktualizuje konfigurację modułu
        
        Args:
            module_name: Nazwa modułu
            config: Nowa konfiguracja
            
        Returns:
            bool: Czy aktualizacja się powiodła
        """
        # Aktualizuj konfigurację w pamięci
        self.module_configs[module_name] = config
        
        # Aktualizuj konfigurację w głównym pliku konfiguracyjnym
        if "modules" not in self.config:
            self.config["modules"] = {}
        
        self.config["modules"][module_name] = config
        
        # Zapisz konfigurację do pliku
        module_config_path = self.config_dir / f"{module_name.lower()}.json"
        
        try:
            with open(module_config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Konfiguracja modułu {module_name} zapisana do {module_config_path}")
            
            # Zapisz również główną konfigurację
            self._save_config(self.config)
            
            return True
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania konfiguracji modułu {module_name}: {e}")
            return False
    
    def get_available_modules(self) -> List[str]:
        """
        Pobiera listę dostępnych modułów
        
        Returns:
            List[str]: Lista nazw dostępnych modułów
        """
        modules = set()
        
        # Dodaj moduły z plików konfiguracyjnych
        for config_file in self.config_dir.glob("*.json"):
            if config_file.name == "config.json":
                continue
            
            modules.add(config_file.stem)
        
        # Dodaj moduły z głównej konfiguracji
        if "modules" in self.config:
            for module_name in self.config["modules"]:
                modules.add(module_name)
        
        return sorted(list(modules))
    
    def get_global_config(self) -> Dict[str, Any]:
        """
        Pobiera globalną konfigurację
        
        Returns:
            Dict[str, Any]: Globalna konfiguracja
        """
        return self.config.get("global", {})
    
    def update_global_config(self, config: Dict[str, Any]) -> bool:
        """
        Aktualizuje globalną konfigurację
        
        Args:
            config: Nowa konfiguracja
            
        Returns:
            bool: Czy aktualizacja się powiodła
        """
        self.config["global"] = config
        return self._save_config(self.config)
    
    def reset_module_config(self, module_name: str) -> bool:
        """
        Resetuje konfigurację modułu do domyślnych wartości
        
        Args:
            module_name: Nazwa modułu
            
        Returns:
            bool: Czy reset się powiódł
        """
        # Usuń konfigurację z pamięci
        if module_name in self.module_configs:
            del self.module_configs[module_name]
        
        # Usuń konfigurację z głównego pliku konfiguracyjnego
        if "modules" in self.config and module_name in self.config["modules"]:
            del self.config["modules"][module_name]
        
        # Usuń plik konfiguracyjny modułu
        module_config_path = self.config_dir / f"{module_name.lower()}.json"
        
        if module_config_path.exists():
            try:
                module_config_path.unlink()
                logger.info(f"Plik konfiguracyjny modułu {module_name} usunięty")
            except Exception as e:
                logger.error(f"Błąd podczas usuwania pliku konfiguracyjnego modułu {module_name}: {e}")
                return False
        
        # Zapisz główną konfigurację
        return self._save_config(self.config)
    
    def get_module_dependencies(self, module_name: str) -> Set[str]:
        """
        Pobiera zależności modułu
        
        Args:
            module_name: Nazwa modułu
            
        Returns:
            Set[str]: Zbiór zależności
        """
        config = self.get_module_config(module_name)
        return set(config.get("dependencies", []))
    
    def add_module_dependency(self, module_name: str, dependency: str) -> bool:
        """
        Dodaje zależność do modułu
        
        Args:
            module_name: Nazwa modułu
            dependency: Nazwa zależności
            
        Returns:
            bool: Czy dodanie się powiodło
        """
        config = self.get_module_config(module_name)
        
        if "dependencies" not in config:
            config["dependencies"] = []
        
        if dependency not in config["dependencies"]:
            config["dependencies"].append(dependency)
        
        return self.update_module_config(module_name, config)
    
    def remove_module_dependency(self, module_name: str, dependency: str) -> bool:
        """
        Usuwa zależność z modułu
        
        Args:
            module_name: Nazwa modułu
            dependency: Nazwa zależności
            
        Returns:
            bool: Czy usunięcie się powiodło
        """
        config = self.get_module_config(module_name)
        
        if "dependencies" in config and dependency in config["dependencies"]:
            config["dependencies"].remove(dependency)
        
        return self.update_module_config(module_name, config)


# Przykład użycia
if __name__ == "__main__":
    # Tworzenie instancji menedżera konfiguracji
    config_manager = ConfigManager()
    
    # Pobieranie globalnej konfiguracji
    global_config = config_manager.get_global_config()
    print("Globalna konfiguracja:", global_config)
    
    # Pobieranie konfiguracji modułu
    module_config = config_manager.get_module_config("text2python")
    print("Konfiguracja modułu text2python:", module_config)
    
    # Aktualizacja konfiguracji modułu
    module_config["model"] = "llama3"
    module_config["max_tokens"] = 2000
    config_manager.update_module_config("text2python", module_config)
    
    # Pobieranie listy dostępnych modułów
    available_modules = config_manager.get_available_modules()
    print("Dostępne moduły:", available_modules)
    
    # Dodanie zależności do modułu
    config_manager.add_module_dependency("text2python", "numpy")
    
    # Pobieranie zależności modułu
    dependencies = config_manager.get_module_dependencies("text2python")
    print("Zależności modułu text2python:", dependencies)
