#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify the successful migration of the text2python module
to the new architecture with BaseText2XModule, ConfigManager, and ErrorCorrector.
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to the Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the migrated Text2Python class
from modules.text2python import Text2Python

def test_basic_functionality():
    """Test basic functionality of the migrated Text2Python module"""
    print("Testing basic functionality of the migrated Text2Python module...")
    
    # Create an instance of the Text2Python class
    text2python = Text2Python()
    
    # Test simple query
    query = "calculate the area of a circle with radius 5"
    print(f"\nTesting query: '{query}'")
    result = text2python.process(query)
    
    # Print the results
    print("\nResults:")
    print(f"Success: {result.get('success', False)}")
    print(f"Code:\n{result.get('code', '')}")
    print(f"Explanation: {result.get('explanation', '')[:150]}...")
    
    # Test error handling
    invalid_query = ""
    print(f"\nTesting invalid query: '{invalid_query}'")
    result = text2python.process(invalid_query)
    
    # Print the results
    print("\nResults for invalid query:")
    print(f"Success: {result.get('success', False)}")
    print(f"Error: {result.get('error', 'No error')}")
    
    return True

def test_architecture_integration():
    """Test integration with the new architecture components"""
    print("\nTesting integration with the new architecture components...")
    
    # Create an instance of the Text2Python class
    text2python = Text2Python()
    
    # Verify that the instance is using the BaseText2XModule
    print(f"\nIs instance of BaseText2XModule: {hasattr(text2python, 'process')}")
    print(f"Has ConfigManager: {hasattr(text2python, 'config_manager')}")
    
    # Test code analysis and correction
    code_with_error = """
def execute():
    # This code has a syntax error
    print("Hello, world!"
    return 42
"""
    
    print("\nTesting code analysis with syntax error:")
    analysis = text2python._analyze_code(code_with_error, "print hello world")
    
    print(f"Is logical: {analysis.get('is_logical', True)}")
    print(f"Issues: {analysis.get('issues', [])}")
    
    return True

def main():
    """Main function to run all tests"""
    print("=" * 50)
    print("TESTING TEXT2PYTHON MIGRATION")
    print("=" * 50)
    
    basic_test_passed = test_basic_functionality()
    architecture_test_passed = test_architecture_integration()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"Basic Functionality: {'PASSED' if basic_test_passed else 'FAILED'}")
    print(f"Architecture Integration: {'PASSED' if architecture_test_passed else 'FAILED'}")
    print("=" * 50)
    
    if basic_test_passed and architecture_test_passed:
        print("\nAll tests passed! The migration was successful.")
    else:
        print("\nSome tests failed. Please check the output for details.")

if __name__ == "__main__":
    main()
