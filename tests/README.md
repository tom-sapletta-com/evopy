# Evopy Assistant Testing Framework

This directory contains a comprehensive testing framework for evaluating the performance of the Evopy Assistant on various programming tasks that a junior programmer should be able to handle.

## Overview

The testing framework evaluates the assistant's ability to:
1. Convert natural language requests into Python code
2. Execute the generated code in a secure Docker sandbox
3. Produce correct results for various programming tasks

## Components

- `test_assistant_performance.py`: The main testing module that evaluates the assistant's performance
- `run_performance_tests.py`: A script to run tests and generate detailed reports with visualizations

## Test Categories

The framework includes test cases covering various programming skills:

- Basic Programming (loops, conditionals, functions)
- Data Structures (lists, dictionaries, sets)
- Object-Oriented Programming (classes, inheritance, encapsulation)
- Algorithms (sorting, searching, mathematical algorithms)
- Text Processing (string manipulation, regular expressions)
- File Handling (reading/writing files, parsing formats)
- Complex Tasks (combining multiple concepts)

## Requirements

- Python 3.8+
- Ollama running locally with the DeepSeek model (`deepseek-coder:instruct-6.7b`)
- Docker installed and running
- Additional Python packages for reporting:
  - matplotlib
  - pandas

## Usage

### Running Basic Tests

```bash
python test_assistant_performance.py
```

This will run all test cases and generate a basic JSON report.

### Running Advanced Tests with Reporting

```bash
python run_performance_tests.py --generate-report
```

This will run all tests and generate a detailed HTML report with visualizations.

### Running Tests for Specific Categories

```bash
python run_performance_tests.py --categories "Podstawy programowania" "Algorytmy"
```

### Comparing Multiple Models

```bash
python run_performance_tests.py --model "deepseek-coder:instruct-6.7b" --compare-models "llama3:8b" "codellama:7b"
```

Note: You need to run tests for each model separately before comparing them.

## Test Results

Test results are stored in the `results` directory as JSON files. Detailed reports and visualizations are stored in the `reports` directory.

## Adding New Test Cases

To add new test cases, modify the `get_test_cases()` function in `test_assistant_performance.py`. Each test case should include:

- `name`: A descriptive name for the test
- `prompt`: The natural language request to be converted to code
- `expected_output`: The expected result (optional)
- `category`: The category of the test

## Interpreting Results

The test framework evaluates:

1. **Code Generation Success**: Whether the assistant successfully generated valid Python code
2. **Code Execution Success**: Whether the generated code executed without errors
3. **Output Correctness**: Whether the output matches the expected result (if specified)
4. **Performance Metrics**: Time taken for code generation and execution

## Example Report

The HTML report includes:
- Overall success rate
- Performance by category
- Detailed test results with generated code and outputs
- Visualizations of performance metrics
