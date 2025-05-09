#!/usr/bin/env python3
"""
Dependency Manager - Moduł do automatycznego zarządzania zależnościami kodu

Ten moduł analizuje kod Python, wykrywa brakujące zależności i automatycznie je dodaje.
Wykorzystuje statyczną analizę kodu oraz dynamiczne wykrywanie importów.
"""

import os
import re
import ast
import sys
import importlib
import logging
import subprocess
from typing import List, Set, Dict, Any, Optional, Tuple

logger = logging.getLogger("evo-assistant.dependency-manager")

# Lista standardowych modułów Python
STANDARD_MODULES = set(sys.builtin_module_names)
try:
    # Dodaj wszystkie moduły z biblioteki standardowej
    import pkgutil
    STANDARD_MODULES.update({module.name for module in pkgutil.iter_modules()
                            if not module.name.startswith('_')})
except Exception as e:
    logger.warning(f"Nie można załadować pełnej listy modułów standardowych: {e}")

# Dodaj ręcznie najczęściej używane moduły
COMMON_MODULES = {
    'time', 'datetime', 'os', 'sys', 're', 'json', 'math', 'random',
    'collections', 'itertools', 'functools', 'pathlib', 'shutil',
    'subprocess', 'threading', 'multiprocessing', 'urllib', 'http',
    'socket', 'email', 'csv', 'xml', 'html', 'sqlite3', 'logging',
    'argparse', 'configparser', 'uuid', 'hashlib', 'base64', 'pickle',
    'numpy', 'pandas', 'matplotlib', 'requests', 'bs4', 'flask', 'django',
    'sqlalchemy', 'tensorflow', 'torch', 'sklearn', 'scipy'
}

class DependencyManager:
    """Klasa do zarządzania zależnościami kodu Python"""
    
    def __init__(self):
        """Inicjalizacja menedżera zależności"""
        self.known_modules = STANDARD_MODULES.union(COMMON_MODULES)
    
    def analyze_code(self, code: str) -> Set[str]:
        """
        Analizuje kod Python i wykrywa używane moduły
        
        Args:
            code: Kod Python do analizy
            
        Returns:
            Set[str]: Zbiór używanych modułów
        """
        used_modules = set()
        
        # Metoda 1: Analiza statyczna za pomocą AST
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Sprawdź bezpośrednie importy (import x)
                if isinstance(node, ast.Import):
                    for name in node.names:
                        used_modules.add(name.name.split('.')[0])
                
                # Sprawdź importy z (from x import y)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    used_modules.add(node.module.split('.')[0])
                
                # Sprawdź użycie modułów (x.function())
                elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    used_modules.add(node.value.id)
        except SyntaxError:
            logger.warning("Nie można przeprowadzić analizy AST - błąd składni")
        
        # Metoda 2: Analiza za pomocą wyrażeń regularnych
        # Znajdź wszystkie potencjalne nazwy modułów używane w kodzie
        potential_modules = set(re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\.', code))
        
        # Usuń zmienne lokalne (przybliżenie)
        local_vars = set(re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=', code))
        potential_modules -= local_vars
        
        # Dodaj znalezione moduły
        used_modules.update(potential_modules)
        
        # Filtruj tylko znane moduły
        return used_modules.intersection(self.known_modules)
    
    def generate_imports(self, modules: Set[str]) -> str:
        """
        Generuje kod importów dla podanych modułów
        
        Args:
            modules: Zbiór modułów do zaimportowania
            
        Returns:
            str: Kod z instrukcjami import
        """
        imports = []
        for module in sorted(modules):
            imports.append(f"import {module}")
        
        return "\n".join(imports)
    
    def fix_missing_imports(self, code: str) -> str:
        """
        Naprawia brakujące importy w kodzie
        
        Args:
            code: Kod Python do naprawy
            
        Returns:
            str: Kod z dodanymi importami
        """
        # Znajdź już istniejące importy
        existing_imports = set()
        import_lines = re.findall(r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)', code, re.MULTILINE)
        from_import_lines = re.findall(r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*)', code, re.MULTILINE)
        
        existing_imports.update(import_lines)
        existing_imports.update(from_import_lines)
        
        # Znajdź używane moduły
        used_modules = self.analyze_code(code)
        
        # Znajdź brakujące importy
        missing_modules = used_modules - existing_imports
        
        if not missing_modules:
            return code
        
        # Generuj kod importów
        import_code = self.generate_imports(missing_modules)
        
        # Dodaj importy na początku kodu
        # Znajdź pierwsze linie z docstring lub komentarzami
        lines = code.split('\n')
        insert_position = 0
        
        # Pomiń docstring jeśli istnieje
        if len(lines) > 0 and lines[0].startswith('"""'):
            for i, line in enumerate(lines[1:], 1):
                if line.endswith('"""'):
                    insert_position = i + 1
                    break
        
        # Pomiń komentarze na początku
        while insert_position < len(lines) and lines[insert_position].startswith('#'):
            insert_position += 1
        
        # Pomiń istniejące importy
        while insert_position < len(lines) and (
            lines[insert_position].startswith('import ') or 
            lines[insert_position].startswith('from ') or
            lines[insert_position].strip() == ''
        ):
            insert_position += 1
        
        # Dodaj pustą linię po importach jeśli nie ma
        if insert_position > 0 and lines[insert_position-1].strip() != '':
            import_code += '\n'
        
        # Wstaw importy
        lines.insert(insert_position, import_code)
        
        logger.info(f"Dodano brakujące importy: {', '.join(missing_modules)}")
        
        return '\n'.join(lines)
    
    def ensure_dependencies(self, code: str) -> str:
        """
        Upewnia się, że wszystkie zależności są dostępne i dodaje brakujące importy
        
        Args:
            code: Kod Python do analizy i naprawy
            
        Returns:
            str: Naprawiony kod z wszystkimi potrzebnymi importami
        """
        # Napraw brakujące importy
        fixed_code = self.fix_missing_imports(code)
        
        return fixed_code


# Funkcja pomocnicza do użycia w innych modułach
def fix_code_dependencies(code: str) -> str:
    """
    Naprawia brakujące zależności w kodzie
    
    Args:
        code: Kod Python do naprawy
        
    Returns:
        str: Naprawiony kod
    """
    manager = DependencyManager()
    return manager.ensure_dependencies(code)
