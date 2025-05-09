# Evopy Testing System Documentation

## Overview

The Evopy testing system provides comprehensive testing capabilities for both the `text2python` and `python2text` modules. It allows you to test different language models (LLMs) and compare their performance, accuracy, and capabilities.

## Available Scripts

### 1. `test.sh` - Single Model Testing

This script runs tests for a single model on all Evopy components.

#### Usage:

```bash
./test.sh [--model=MODEL_NAME]
```

#### Features:

- Interactive model selection at startup
- Automatic fallback to available models if the requested one isn't available
- Comprehensive testing of basic queries, correctness, and performance
- Detailed test results saved to the `test_results` directory

### 2. `report.sh` - Multi-Model Comparison

This script generates a comprehensive comparison report across multiple LLM models.

#### Usage:

```bash
./report.sh
```

#### Features:

- Tests multiple models in sequence
- Automatically detects available models in your Ollama installation
- Generates a markdown report comparing all tested models
- Creates a summary table showing success/failure for each test type
- Calculates performance metrics across models

## Generating Reports

To generate a comprehensive comparison report:

1. Run the report script:
   ```bash
   ./report.sh
   ```

2. Select which models to test:
   - Enter specific model numbers (e.g., `1 3 5`)
   - Enter `all` to test all available models
   - Select the "All models" option

3. Wait for all tests to complete. This may take some time depending on the number of models selected.

4. The report will be generated in the `reports` directory with a filename like `comparison_report_YYYYMMDD_HHMMSS.md`.

## Report Structure

The generated report includes:

1. **Summary Table**: A comparison table showing test results for all models:
   - Basic query tests (✅/❌)
   - Correctness tests (✅/❌)
   - Performance tests (✅/❌)
   - Total score for each model

2. **Detailed Results**: For each model, detailed test results including:
   - Execution times
   - Success rates
   - Specific test case results

## Troubleshooting

### Model Not Available

If a model isn't available in your Ollama installation:

1. The system will attempt to download it automatically
2. If download fails, it will fall back to an available model
3. You'll see warnings in the log about model availability

### Permission Issues

If you encounter permission issues with the `.env` file:

1. The script will notify you about the permission problem
2. Changes will only apply to the current session
3. To fix permanently, adjust permissions: `chmod u+w config/.env`

### Report Not Generated for All Models

If the report doesn't include all models:

1. **Availability**: Only models available in your Ollama installation will be tested
2. **Selection**: Ensure you've selected all desired models during the prompt
3. **Timeouts**: Long-running tests might time out; adjust the timeout in the script if needed

## Available Models

The system supports the following models:

1. **llama** - Llama 3 (default)
2. **phi** - Phi model
3. **llama32** - Llama 3.2
4. **bielik** - Bielik model
5. **deepsek** - DeepSeek Coder
6. **qwen** - Qwen model
7. **mistral** - Mistral model

Only models available in your Ollama installation will be listed for testing.

## Customizing Tests

To add new test cases or modify existing ones:

1. Edit `test_queries.py` for basic query tests
2. Edit files in `tests/correctness/` for correctness tests
3. Edit files in `tests/performance/` for performance tests

## Rendering and Viewing Reports

The reports are generated in Markdown format for easy viewing:

1. **Command Line**: Use tools like `mdless` or `glow` to view reports in the terminal:
   ```bash
   glow reports/comparison_report_YYYYMMDD_HHMMSS.md
   ```

2. **Web Browser**: Convert to HTML for better visualization:
   ```bash
   pandoc -s reports/comparison_report_YYYYMMDD_HHMMSS.md -o report.html
   ```

3. **IDE/Editor**: Open the markdown file in any markdown-supporting editor

## Best Practices

1. **Regular Testing**: Run reports periodically to track model improvements
2. **Model Comparison**: Test multiple models to find the best for your use case
3. **Test Case Coverage**: Ensure test cases cover your specific usage scenarios
4. **Performance Monitoring**: Track performance metrics over time to identify trends
