#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Niestandardowe filtry dla szablonów Jinja2
"""

import os
from pathlib import Path

def basename(path):
    """
    Zwraca nazwę pliku z pełnej ścieżki
    
    Args:
        path (str): Pełna ścieżka do pliku
        
    Returns:
        str: Nazwa pliku
    """
    return os.path.basename(path)

def register_filters(app):
    """
    Rejestruje niestandardowe filtry dla aplikacji Flask
    
    Args:
        app: Aplikacja Flask
    """
    app.jinja_env.filters['basename'] = basename
