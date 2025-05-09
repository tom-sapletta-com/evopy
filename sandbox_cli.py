#!/usr/bin/env python3
"""
Evopy Sandbox CLI
================

Command-line interface for the Evopy cross-platform sandbox.
This tool allows executing Python code in isolated Docker containers
with resource limitations and network isolation.

Usage:
    python sandbox_cli.py [options] <file>
    python sandbox_cli.py [options] -c <code>

Options:
    --public         Use public sandbox (with network access)
    --private        Use private sandbox (without network access) [default]
    --no-repair      Disable automatic dependency repair
    --timeout=<sec>  Set execution timeout in seconds [default: 30]
    --memory=<mb>    Set memory limit in MB [default: 512]
    -c, --code       Execute code from command line instead of file
    -i, --input      Read input from stdin
    -h, --help       Show this help message
"""

import os
import sys
import argparse
import platform
from pathlib import Path

# Add the parent directory to the path to import the sandbox module
sys.path.append(str(Path(__file__).parent.absolute()))

try:
    from sandbox import execute_code
except ImportError:
    print("Error: Could not import sandbox module.")
    print("Make sure you're running this script from the Evopy directory.")
    sys.exit(1)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Evopy Sandbox CLI")
    
    # Sandbox type
    sandbox_group = parser.add_mutually_exclusive_group()
    sandbox_group.add_argument("--public", action="store_true", help="Use public sandbox (with network access)")
    sandbox_group.add_argument("--private", action="store_true", help="Use private sandbox (without network access)")
    
    # Dependency repair
    parser.add_argument("--no-repair", action="store_true", help="Disable automatic dependency repair")
    
    # Resource limits
    parser.add_argument("--timeout", type=int, default=30, help="Set execution timeout in seconds")
    parser.add_argument("--memory", type=int, default=512, help="Set memory limit in MB")
    
    # Input source
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("-c", "--code", help="Execute code from command line")
    source_group.add_argument("file", nargs="?", help="Execute code from file")
    
    # Input data
    parser.add_argument("-i", "--input", action="store_true", help="Read input from stdin")
    
    return parser.parse_args()

def read_file(file_path):
    """Read code from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

def read_input():
    """Read input from stdin."""
    print("Enter input data (press Ctrl+D on Linux/macOS or Ctrl+Z on Windows to finish):")
    return sys.stdin.read()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Determine sandbox type
    sandbox_type = "public" if args.public else "private"
    
    # Get code to execute
    if args.code:
        code = args.code
    else:
        code = read_file(args.file)
    
    # Get input data if requested
    input_data = read_input() if args.input else None
    
    # Execute code
    result = execute_code(
        code=code,
        input_data=input_data,
        sandbox_type=sandbox_type,
        auto_repair=not args.no_repair
    )
    
    # Print results
    if result["stdout"]:
        print("=== Output ===")
        print(result["stdout"])
    
    if result["stderr"]:
        print("=== Error ===")
        print(result["stderr"])
    
    print(f"=== Exit Code: {result['exit_code']} ===")
    
    # Print repair info if available
    if result.get("repaired"):
        print("=== Dependency Repair ===")
        print("Code was automatically repaired to fix missing imports.")
    
    # Return exit code
    return result["exit_code"]

if __name__ == "__main__":
    sys.exit(main())
