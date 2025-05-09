#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Konfiguracja testów dla projektu Evopy
"""

import os
import sys
import pytest
from pathlib import Path

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importy dla testów
import logging

# Konfiguracja logowania dla testów
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def test_data_dir():
    """Zwraca ścieżkę do katalogu z danymi testowymi"""
    return Path(__file__).parent / "test_data"

@pytest.fixture
def ensure_test_data_dir(test_data_dir):
    """Upewnia się, że katalog z danymi testowymi istnieje"""
    os.makedirs(test_data_dir, exist_ok=True)
    return test_data_dir
