#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify the math extension functionality.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the math extension directly
try:
    from modules.text2python.extensions.math import identify_query, generate_code
    print("Successfully imported math extension functions directly!")
    print(f"identify_query function: {identify_query}")
    print(f"generate_code function: {generate_code}")
    
    # Test the identify_query function
    test_query = "oblicz pole koła o promieniu 5"
    result = identify_query(test_query)
    print(f"identify_query result for '{test_query}': {result}")
    
    # Test the generate_code function
    if result:
        code_result = generate_code(test_query)
        print(f"generate_code result: {code_result}")
except ImportError as e:
    print(f"Failed to import math extension directly: {e}")

# Try alternative import approaches
print("\nTrying alternative import approaches:")

# Approach 1: Import the module
try:
    import modules.text2python.extensions.math as math_ext
    print("Successfully imported math extension as a module!")
    print(f"Module attributes: {dir(math_ext)}")
    
    if hasattr(math_ext, 'identify_query') and hasattr(math_ext, 'generate_code'):
        print("Module has both required functions!")
except ImportError as e:
    print(f"Failed to import math extension as a module: {e}")

# Approach 2: Import using importlib
import importlib
print("\nTrying importlib approach:")
try:
    math_module = importlib.import_module('modules.text2python.extensions.math')
    print(f"Successfully imported using importlib: {math_module}")
    print(f"Module attributes: {dir(math_module)}")
    
    if hasattr(math_module, 'identify_query') and hasattr(math_module, 'generate_code'):
        print("Module has both required functions!")
except ImportError as e:
    print(f"Failed to import using importlib: {e}")

# Print Python path for debugging
print("\nPython path:")
for p in sys.path:
    print(f"  {p}")
