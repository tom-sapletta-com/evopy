#!/usr/bin/env python3
"""
Evopy - Cross-Platform CLI for Evopy Testing System
===================================================
This script provides a cross-platform interface for running Evopy tests and generating reports.
It works on Linux (including Fedora), Windows, and macOS.

Usage:
    python evopy.py [command] [options]

Commands:
    test    - Run tests for a single model
    report  - Generate a comparison report for multiple models
    cleanup - Clean intermediate files

Copyright 2025 Tom Sapletta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import json
import glob
import argparse
import subprocess
import platform
import datetime
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_FEDORA = IS_LINUX and os.path.exists("/etc/fedora-release")
IS_MACOS = platform.system() == "Darwin"

# Directory setup
SCRIPT_DIR = Path(__file__).parent.absolute()
CONFIG_DIR = SCRIPT_DIR / "config"
TESTS_DIR = SCRIPT_DIR / "tests"
RESULTS_DIR = SCRIPT_DIR / "test_results"
REPORTS_DIR = SCRIPT_DIR / "reports"
GENERATED_CODE_DIR = SCRIPT_DIR / "generated_code"

# Ensure directories exist
RESULTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
GENERATED_CODE_DIR.mkdir(exist_ok=True)

# ANSI colors for terminal output (Windows-compatible)
if IS_WINDOWS:
    # Enable ANSI colors on Windows
    os.system("")

BLUE = '\033[0;34m' if not IS_WINDOWS or os.environ.get('TERM') else ''
GREEN = '\033[0;32m' if not IS_WINDOWS or os.environ.get('TERM') else ''
YELLOW = '\033[0;33m' if not IS_WINDOWS or os.environ.get('TERM') else ''
RED = '\033[0;31m' if not IS_WINDOWS or os.environ.get('TERM') else ''
CYAN = '\033[0;36m' if not IS_WINDOWS or os.environ.get('TERM') else ''
BOLD = '\033[1m' if not IS_WINDOWS or os.environ.get('TERM') else ''
NC = '\033[0m' if not IS_WINDOWS or os.environ.get('TERM') else ''  # No Color

def print_color(color: str, message: str, bold: bool = False) -> None:
    """Print colored text that works across platforms."""
    if bold:
        print(f"{BOLD}{color}{message}{NC}")
    else:
        print(f"{color}{message}{NC}")

def run_command(cmd: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=cwd
        )
        stdout, stderr = process.communicate()
        return process.returncode, stdout, stderr
    except Exception as e:
        return 1, "", str(e)

def get_python_command() -> str:
    """Get the appropriate Python command for the current environment."""
    # Check for virtual environment
    venv_path = SCRIPT_DIR / ".venv" / "bin" / "python"
    if venv_path.exists():
        return str(venv_path)
    
    venv_path = SCRIPT_DIR / "venv" / "bin" / "python"
    if venv_path.exists():
        return str(venv_path)
    
    # Windows virtual environment
    venv_path_win = SCRIPT_DIR / ".venv" / "Scripts" / "python.exe"
    if IS_WINDOWS and venv_path_win.exists():
        return str(venv_path_win)
    
    venv_path_win = SCRIPT_DIR / "venv" / "Scripts" / "python.exe"
    if IS_WINDOWS and venv_path_win.exists():
        return str(venv_path_win)
    
    # Use system Python
    if shutil.which("python3"):
        return "python3"
    
    return "python"

def get_available_models() -> List[str]:
    """Get list of available models from Ollama."""
    print_color(BLUE, "Checking available Ollama models...")
    
    # Default models to test
    default_models = ["llama", "phi", "llama32", "bielik", "deepsek", "qwen", "mistral"]
    
    # Check if Ollama is installed
    ollama_cmd = "ollama.exe" if IS_WINDOWS else "ollama"
    if not shutil.which(ollama_cmd):
        print_color(YELLOW, "Ollama not found. Using default model list.")
        return default_models
    
    # Get available models from Ollama
    cmd = [ollama_cmd, "list"]
    exit_code, stdout, stderr = run_command(cmd)
    
    if exit_code != 0:
        print_color(YELLOW, f"Failed to get models from Ollama: {stderr}")
        return default_models
    
    # Parse Ollama output to get model names
    available_models = []
    for line in stdout.splitlines()[1:]:  # Skip header line
        if line.strip():
            model_name = line.split()[0].split(':')[0]
            if model_name not in available_models:
                available_models.append(model_name)
    
    # Add custom models that might not be in Ollama
    for model in ["bielik", "deepsek"]:
        if model not in available_models:
            available_models.append(model)
    
    # Filter to only include models from the default list
    filtered_models = [model for model in default_models if model in available_models]
    
    if not filtered_models:
        print_color(YELLOW, "No models found in Ollama. Using default list.")
        return default_models
    
    return filtered_models

def cleanup_files() -> None:
    """Clean up intermediate files."""
    print_color(GREEN, "=== Cleaning up intermediate files ===", bold=True)
    
    # Clean JSON result files
    for pattern in ["tests/performance/results/*.json", "tests/correctness/results/*.json", "test_results/*.json"]:
        path = SCRIPT_DIR / pattern
        for file in glob.glob(str(path)):
            try:
                os.remove(file)
                print(f"Removed: {file}")
            except Exception as e:
                print(f"Failed to remove {file}: {e}")
    
    # Clean generated code
    for file in GENERATED_CODE_DIR.glob("*"):
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Failed to remove {file}: {e}")
    
    # Clean Python files with hashes
    hash_pattern = f"{SCRIPT_DIR}/**/*_[a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9][a-f0-9]*.py"
    for file in glob.glob(hash_pattern, recursive=True):
        try:
            os.remove(file)
            print(f"Removed: {file}")
        except Exception as e:
            print(f"Failed to remove {file}: {e}")
    
    print_color(GREEN, "=== Cleanup complete ===", bold=True)

def run_tests_for_model(model: str) -> Dict[str, Any]:
    """Run tests for a specific model and return results."""
    print_color(GREEN, f"=== Running tests for model: {model} ===", bold=True)
    python_cmd = get_python_command()
    results = {}
    
    # Run basic query tests
    print_color(BLUE, "1. Basic query tests:")
    cmd = [python_cmd, str(SCRIPT_DIR / "test_queries.py"), f"--model={model}"]
    queries_code, queries_stdout, queries_stderr = run_command(cmd)
    results["queries_result"] = queries_code
    
    # Run correctness tests
    print_color(BLUE, "2. Correctness tests:")
    cmd = [python_cmd, str(TESTS_DIR / "correctness" / "correctness_test.py"), f"--model={model}"]
    correctness_code, correctness_stdout, correctness_stderr = run_command(cmd)
    results["correctness_result"] = correctness_code
    
    # Run performance tests
    print_color(BLUE, "3. Performance tests:")
    cmd = [python_cmd, str(TESTS_DIR / "performance" / "performance_test.py"), f"--model={model}"]
    performance_code, performance_stdout, performance_stderr = run_command(cmd)
    results["performance_result"] = performance_code
    
    # Summary
    print_color(CYAN, f"=== Summary for model: {model} ===", bold=True)
    if queries_code == 0 and correctness_code == 0 and performance_code == 0:
        print_color(GREEN, "✓ All tests completed successfully")
    else:
        print_color(RED, "✗ Some tests failed")
        print_color(BLUE, f"Basic queries: {GREEN + 'OK' if queries_code == 0 else RED + 'ERROR'}")
        print_color(BLUE, f"Correctness: {GREEN + 'OK' if correctness_code == 0 else RED + 'ERROR'}")
        print_color(BLUE, f"Performance: {GREEN + 'OK' if performance_code == 0 else RED + 'ERROR'}")
    
    # Save results to file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = REPORTS_DIR / f"results_{model}_{timestamp}.json"
    results_data = {
        "model": model,
        "timestamp": timestamp,
        "queries_result": queries_code,
        "correctness_result": correctness_code,
        "performance_result": performance_code
    }
    
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=4)
    
    print_color(BLUE, f"Results saved to: {results_file}")
    return results_data

def generate_report(models: List[str]) -> str:
    """Generate a comparison report for multiple models."""
    print_color(GREEN, "=== Generating comparison report ===", bold=True)
    
    # Use the generate_report.py script if it exists
    report_script = SCRIPT_DIR / "generate_report.py"
    if report_script.exists():
        python_cmd = get_python_command()
        models_arg = ",".join(models)
        cmd = [python_cmd, str(report_script), f"--models={models_arg}"]
        exit_code, stdout, stderr = run_command(cmd)
        
        if exit_code == 0:
            # Extract report path from output
            for line in stdout.splitlines():
                if "comparison_report_" in line and ".md" in line:
                    report_path = line.split()[-1]
                    return report_path
    
    # Fallback to built-in report generation
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = REPORTS_DIR / f"comparison_report_{timestamp}.md"
    
    with open(report_file, 'w') as f:
        # Header
        f.write(f"# Evopy Model Comparison Report\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary table
        f.write("## Summary\n\n")
        f.write("| Model | Basic Queries | Correctness | Performance | Total Score |\n")
        f.write("|-------|--------------|-------------|-------------|-------------|\n")
        
        for model in models:
            # Find latest results for this model
            result_files = list(REPORTS_DIR.glob(f"results_{model}_*.json"))
            if not result_files:
                f.write(f"| {model} | ? | ? | ? | 0/3 |\n")
                continue
            
            latest_result = max(result_files, key=os.path.getctime)
            with open(latest_result) as res_file:
                results = json.load(res_file)
            
            queries_ok = "✅" if results["queries_result"] == 0 else "❌"
            correctness_ok = "✅" if results["correctness_result"] == 0 else "❌"
            performance_ok = "✅" if results["performance_result"] == 0 else "❌"
            
            total_score = sum(1 for r in [results["queries_result"], results["correctness_result"], 
                                         results["performance_result"]] if r == 0)
            
            f.write(f"| {model} | {queries_ok} | {correctness_ok} | {performance_ok} | {total_score}/3 |\n")
    
    # Update the latest report link
    update_latest_report_link(str(report_file))
    
    print_color(GREEN, f"Report generated: {report_file}")
    return str(report_file)

def update_latest_report_link(report_path: str) -> None:
    """Create or update a symbolic link to the latest report."""
    latest_link = REPORTS_DIR / "comparison_report_latest.md"
    report_file = Path(report_path)
    
    # Create relative path for the link
    rel_path = os.path.basename(report_path)
    
    try:
        # Remove existing link if it exists
        if latest_link.exists():
            latest_link.unlink()
        
        # Create new link
        if IS_WINDOWS:
            # Windows often requires admin privileges for symlinks, so copy instead
            shutil.copy2(report_path, latest_link)
        else:
            # Create symbolic link on Unix systems
            latest_link.symlink_to(rel_path)
        
        print_color(GREEN, f"Updated latest report link: {latest_link}")
    except Exception as e:
        print_color(RED, f"Failed to update latest report link: {e}")

def command_test(args: argparse.Namespace) -> None:
    """Run the test command."""
    if args.cleanup:
        cleanup_files()
    
    if args.model:
        model = args.model
        run_tests_for_model(model)
    else:
        # Interactive model selection
        models = get_available_models()
        print_color(YELLOW, "Available models:")
        for i, model in enumerate(models):
            print(f"{i+1}) {CYAN}{model}{NC}")
        
        choice = input(f"\n{YELLOW}Select a model (1-{len(models)}): {NC}")
        try:
            index = int(choice) - 1
            if 0 <= index < len(models):
                run_tests_for_model(models[index])
            else:
                print_color(RED, "Invalid selection.")
        except ValueError:
            print_color(RED, "Invalid input. Please enter a number.")

def command_report(args: argparse.Namespace) -> None:
    """Run the report command."""
    if args.cleanup:
        cleanup_files()
    
    # Get available models
    available_models = get_available_models()
    
    if args.all:
        # Test all models
        results = {}
        for model in available_models:
            results[model] = run_tests_for_model(model)
        
        # Generate report
        report_path = generate_report(available_models)
        print_color(GREEN, f"Comparison report available at: {report_path}")
    else:
        # Interactive model selection
        print_color(YELLOW, "Available models:")
        for i, model in enumerate(available_models):
            print(f"{i+1}) {CYAN}{model}{NC}")
        print(f"{len(available_models)+1}) {CYAN}All models{NC}")
        
        choice = input(f"\n{YELLOW}Select models to test (comma-separated, e.g., 1,3,5 or 'all'): {NC}")
        
        if choice.lower() == 'all':
            selected_models = available_models
        else:
            selected_models = []
            try:
                for idx in choice.split(','):
                    index = int(idx.strip()) - 1
                    if index == len(available_models):
                        # "All models" option selected
                        selected_models = available_models
                        break
                    elif 0 <= index < len(available_models):
                        selected_models.append(available_models[index])
            except ValueError:
                print_color(RED, "Invalid input. Please enter numbers separated by commas.")
                return
        
        if not selected_models:
            print_color(RED, "No models selected.")
            return
        
        # Run tests for selected models
        results = {}
        for model in selected_models:
            results[model] = run_tests_for_model(model)
        
        # Generate report
        report_path = generate_report(selected_models)
        print_color(GREEN, f"Comparison report available at: {report_path}")

def command_cleanup(args: argparse.Namespace) -> None:
    """Run the cleanup command."""
    cleanup_files()

def main() -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Evopy - Cross-Platform CLI for Evopy Testing System")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests for a single model")
    test_parser.add_argument("--model", help="Model to test")
    test_parser.add_argument("--cleanup", action="store_true", help="Clean up intermediate files before testing")
    
    # Report command
    report_parser = subparsers.add_parser("report", help="Generate a comparison report for multiple models")
    report_parser.add_argument("--all", action="store_true", help="Test all available models")
    report_parser.add_argument("--cleanup", action="store_true", help="Clean up intermediate files before testing")
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clean intermediate files")
    
    args = parser.parse_args()
    
    if args.command == "test":
        command_test(args)
    elif args.command == "report":
        command_report(args)
    elif args.command == "cleanup":
        command_cleanup(args)
    else:
        # No command specified, show help
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
