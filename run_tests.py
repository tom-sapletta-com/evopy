#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skrypt do uruchamiania testów dla projektu Evopy
"""

import os
import sys
import argparse
import pytest
from pathlib import Path

def main():
    """Główna funkcja uruchamiająca testy"""
    parser = argparse.ArgumentParser(description="Uruchamianie testów dla projektu Evopy")
    parser.add_argument("--module", type=str, help="Nazwa modułu do testowania (np. text2python)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Szczegółowe wyniki testów")
    parser.add_argument("--collect-only", action="store_true", help="Tylko zbierz testy bez uruchamiania")
    parser.add_argument("--docker", action="store_true", help="Uruchom testy wymagające Dockera")
    args = parser.parse_args()
    
    # Katalog testów
    tests_dir = Path(__file__).parent / "tests"
    
    # Przygotuj argumenty dla pytest
    pytest_args = []
    
    # Dodaj poziom szczegółowości
    if args.verbose:
        pytest_args.append("-v")
    
    # Dodaj opcję zbierania testów
    if args.collect_only:
        pytest_args.append("--collect-only")
    
    # Jeśli nie uruchamiamy testów wymagających Dockera, pomijamy je
    if not args.docker:
        pytest_args.append("-k")
        pytest_args.append("not docker")
    
    # Jeśli podano konkretny moduł, testuj tylko ten moduł
    if args.module:
        module_path = tests_dir / "modules" / f"test_{args.module}.py"
        if module_path.exists():
            pytest_args.append(str(module_path))
        else:
            print(f"Błąd: Nie znaleziono testów dla modułu {args.module}")
            print(f"Ścieżka: {module_path}")
            return 1
    else:
        # W przeciwnym razie uruchom wszystkie testy
        pytest_args.append(str(tests_dir))
    
    # Uruchom testy
    return pytest.main(pytest_args)

if __name__ == "__main__":
    sys.exit(main())
