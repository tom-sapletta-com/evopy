#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moduł bazowy dla wszystkich modułów TEXT2X w Evopy
"""

from .text2x_base import BaseText2XModule
from .config_manager import ConfigManager
from .module_selector import ModuleSelector
from .error_corrector import ErrorCorrector

__all__ = [
    'BaseText2XModule',
    'ConfigManager',
    'ModuleSelector',
    'ErrorCorrector'
]
