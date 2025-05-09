# Evopy Assistant Testing Framework

This directory contains a comprehensive testing framework for evaluating the performance and correctness of the Evopy Assistant modules, including both text2python and python2text conversions.

## Overview

The testing framework evaluates:
1. **Text2Python**: Converting natural language requests into Python code
2. **Python2Text**: Converting Python code into natural language descriptions
3. Executing the generated code in a secure Docker sandbox
4. Measuring performance metrics for different LLM models
5. Validating correctness of the generated outputs

## Components

### Directories
- `performance/`: Tests for measuring performance metrics of different models
- `correctness/`: Tests for validating the correctness of code generation and description
- `results/`: Directory where test results are stored

### Main Test Files
- `performance/performance_test.py`: Tests for measuring performance metrics
- `correctness/correctness_test.py`: Tests for validating correctness of conversions

## Test Categories

### Performance Tests
The performance testing framework evaluates:

- Execution time for text2python and python2text conversions
- Memory usage during conversions
- Token usage efficiency
- Success rate across different types of queries

### Correctness Tests
The correctness testing framework validates:

- **Text2Python**:
  - Basic functionality (simple function generation)
  - Error handling (try-except blocks)
  - Data processing (filtering, mapping)

- **Python2Text**:
  - Description accuracy for simple functions
  - Error handling explanation
  - Algorithm description quality

### Programming Skills Covered
- Basic Programming (loops, conditionals, functions)
- Data Structures (lists, dictionaries, sets)
- Object-Oriented Programming (classes, inheritance, encapsulation)
- Algorithms (sorting, searching, mathematical algorithms)
- Text Processing (string manipulation, regular expressions)
- File Handling (reading/writing files, parsing formats)
- Complex Tasks (combining multiple concepts)

## Requirements

- Python 3.8+
- Ollama running locally with one of the supported models:
  - DeepSeek model (`deepseek-coder:instruct-6.7b`)
  - Llama model (`llama3:8b`)
  - Bielik model (custom model)
- Docker installed and running (for secure code execution)
- Environment variables configured in `config/.env`
- Additional Python packages:
  - dotenv (for configuration management)
  - matplotlib (for reporting)
  - pandas (for data analysis)

## Usage

### Running All Tests

Use the main test script to run all tests with the default model (specified in `.env`):

```bash
./test.sh
```

### Running Tests with a Specific Model

```bash
./test.sh --model=llama
```

### Running Only Performance Tests

```bash
python tests/performance/performance_test.py --model=deepsek
```

### Running Only Correctness Tests

```bash
python tests/correctness/correctness_test.py --model=deepsek
```

### Testing All Available Models

```bash
python tests/performance/performance_test.py --all-models
python tests/correctness/correctness_test.py --all-models
```

### Testing Specific Conversion Direction

```bash
python tests/performance/performance_test.py --text2python  # Only test text2python
python tests/performance/performance_test.py --python2text  # Only test python2text
```

## Test Results

Test results are stored in the following locations:
- Performance test results: `tests/performance/results/`
- Correctness test results: `tests/correctness/results/`

Results are saved as JSON files with timestamps and model identifiers.

## Adding New Test Cases

### Adding Performance Tests

To add new performance test cases, modify the `PERFORMANCE_TESTS` list in `performance/performance_test.py`. Each test case should include:

- `name`: A descriptive name for the test
- `query`: The natural language request to be converted to code (for text2python)
- `code`: The Python code to be converted to description (for python2text)
- `expected_output`: The expected result (optional)

### Adding Correctness Tests

To add new correctness test cases, modify the `CORRECTNESS_TESTS` or `PYTHON2TEXT_TESTS` lists in `correctness/correctness_test.py`. Each test case should include:

- `name`: A descriptive name for the test
- `query` or `code`: The input for conversion
- `validation_criteria`: List of criteria to validate the output

## Interpreting Results

The test framework evaluates:

1. **Code Generation Success**: Whether the module successfully generated valid Python code
2. **Code Execution Success**: Whether the generated code executed without errors
3. **Output Correctness**: Whether the output matches the expected validation criteria
4. **Performance Metrics**: Time taken for code generation and execution, token usage

## Auto-Dependency Repair

The system includes automatic dependency repair functionality that:

1. Detects missing imports in generated code
2. Automatically adds required import statements
3. Handles dynamic imports during execution in the Docker sandbox

This feature ensures that code with missing imports like `time` or standard libraries will still execute correctly.
