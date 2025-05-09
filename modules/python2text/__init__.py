"""
Python2Text - Moduł do konwersji kodu Python na opis w języku naturalnym

Ten moduł wykorzystuje modele językowe do konwersji kodu Python
na opis funkcjonalności w języku naturalnym.
"""

from .python2text import Python2Text, get_available_models, get_model_config

__all__ = ['Python2Text', 'get_available_models', 'get_model_config']
