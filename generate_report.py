#!/usr/bin/env python3
"""
Evopy Report Generator
======================
This script generates comparison reports for Evopy models in multiple formats:
- Markdown
- HTML
- PDF (landscape orientation)

Usage:
    python generate_report.py [--format=all|md|html|pdf] [--input=<results_dir>] [--output=<output_dir>]
"""

import os
import sys
import json
import glob
import argparse
import logging
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('evopy-report-generator')

# Default paths
SCRIPT_DIR = Path(__file__).parent.absolute()
TEST_RESULTS_DIR = SCRIPT_DIR / "test_results"
REPORTS_DIR = SCRIPT_DIR / "reports"
CORRECTNESS_RESULTS_DIR = SCRIPT_DIR / "tests" / "correctness" / "results"
PERFORMANCE_RESULTS_DIR = SCRIPT_DIR / "tests" / "performance" / "results"

# Ensure directories exist
TEST_RESULTS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

def check_dependencies() -> bool:
    """Check if required dependencies are installed."""
    dependencies = {
        "pandoc": "Pandoc is required for HTML and PDF conversion. Install with: sudo apt-get install pandoc",
        "wkhtmltopdf": "wkhtmltopdf is required for PDF generation. Install with: sudo apt-get install wkhtmltopdf"
    }
    
    missing = []
    for dep, message in dependencies.items():
        try:
            subprocess.run(["which", dep], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            missing.append(f"{dep}: {message}")
    
    if missing:
        logger.error("Missing dependencies:")
        for msg in missing:
            logger.error(f"  - {msg}")
        return False
    
    return True

def load_test_results(model_name: str) -> Dict[str, Any]:
    """Load the most recent test results for a specific model."""
    # Find the most recent results file for this model
    pattern = f"{TEST_RESULTS_DIR}/test_results_{model_name}_*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    
    default_results = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "model_name": model_name,
        "passed_tests": 0,
        "failed_tests": 0,
        "total_tests": 0,
        "test_results": []
    }
    
    if not files:
        logger.warning(f"No test results found for model: {model_name}")
        return default_results
    
    try:
        # Load the most recent file
        with open(files[0], 'r') as f:
            data = json.load(f)
            
        # Ensure all required keys exist
        for key in default_results.keys():
            if key not in data:
                data[key] = default_results[key]
                
        return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading test results for {model_name}: {e}")
        return default_results

def load_correctness_results(model_name: str) -> Tuple[int, int]:
    """Load correctness test results for a specific model."""
    # Look for text2python and python2text results
    t2p_pattern = f"{CORRECTNESS_RESULTS_DIR}/text2python_correctness_{model_name}_*.json"
    p2t_pattern = f"{CORRECTNESS_RESULTS_DIR}/python2text_correctness_{model_name}_*.json"
    
    t2p_files = sorted(glob.glob(t2p_pattern), reverse=True)
    p2t_files = sorted(glob.glob(p2t_pattern), reverse=True)
    
    passed = 0
    total = 0
    
    # Process text2python results
    if t2p_files:
        try:
            with open(t2p_files[0], 'r') as f:
                data = json.load(f)
                passed += data.get("passed_tests", 0)
                total += data.get("total_tests", 0)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading text2python correctness results for {model_name}: {e}")
    
    # Process python2text results
    if p2t_files:
        try:
            with open(p2t_files[0], 'r') as f:
                data = json.load(f)
                passed += data.get("passed_tests", 0)
                total += data.get("total_tests", 0)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading python2text correctness results for {model_name}: {e}")
    
    return passed, total

def load_performance_results(model_name: str) -> Dict[str, Any]:
    """Load performance test results for a specific model."""
    pattern = f"{PERFORMANCE_RESULTS_DIR}/performance_{model_name}_*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    
    default_results = {
        "avg_time": 0, 
        "tests": 0,
        "passed_tests": 0,
        "min_time": 0,
        "max_time": 0,
        "total_time": 0,
        # New metrics for enhanced reporting
        "code_efficiency_score": 0,     # Score 0-100 for code efficiency
        "memory_usage": 0,             # Average memory usage in MB
        "cpu_usage": 0,                # Average CPU usage percentage
        "execution_time_variance": 0,   # Variance in execution times
        "time_complexity": "N/A",       # Estimated time complexity
        "space_complexity": "N/A"       # Estimated space complexity
    }
    
    if not files:
        return default_results
    
    try:
        with open(files[0], 'r') as f:
            data = json.load(f)
            # Ensure required keys exist
            for key in default_results.keys():
                if key not in data:
                    data[key] = default_results[key]
            return data
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading performance results for {model_name}: {e}")
        return default_results

def calculate_text_to_code_accuracy(model_name: str) -> Dict[str, Any]:
    """Calculate accuracy metrics for text-to-code conversion.
    
    This function analyzes the quality of code generated from text prompts.
    
    Returns:
        Dict with the following metrics:
        - code_correctness_score: Overall score (0-100) for code correctness
        - syntax_error_rate: Percentage of code with syntax errors
        - semantic_error_rate: Percentage of code with semantic/logical errors
        - test_case_pass_rate: Percentage of code passing test cases
        - prompt_adherence_score: How well the code adheres to the prompt (0-100)
    """
    # Load basic test results
    basic_results = load_test_results(model_name)
    correctness_passed, correctness_total = load_correctness_results(model_name)
    
    # Default metrics
    metrics = {
        "code_correctness_score": 0,
        "syntax_error_rate": 0,
        "semantic_error_rate": 0,
        "test_case_pass_rate": 0,
        "prompt_adherence_score": 0
    }
    
    # Calculate metrics if we have data
    if basic_results["total_tests"] > 0:
        # Extract relevant data from test results
        syntax_errors = 0
        semantic_errors = 0
        test_passes = 0
        adherence_scores = []
        
        # Analyze test results for error types
        for test in basic_results.get("test_results", []):
            if "syntax_error" in test.get("reason", "").lower():
                syntax_errors += 1
            elif "semantic_error" in test.get("reason", "").lower() or "logic_error" in test.get("reason", "").lower():
                semantic_errors += 1
            
            if test.get("status") == "PASSED":
                test_passes += 1
                
            # If there's an adherence score in the test results
            if "adherence_score" in test:
                adherence_scores.append(test["adherence_score"])
        
        total_tests = basic_results["total_tests"]
        
        # Calculate rates
        metrics["syntax_error_rate"] = (syntax_errors / total_tests) * 100 if total_tests > 0 else 0
        metrics["semantic_error_rate"] = (semantic_errors / total_tests) * 100 if total_tests > 0 else 0
        metrics["test_case_pass_rate"] = (test_passes / total_tests) * 100 if total_tests > 0 else 0
        
        # Calculate overall correctness score (weighted average)
        # Lower error rates and higher test pass rates contribute to higher score
        metrics["code_correctness_score"] = (
            (100 - metrics["syntax_error_rate"]) * 0.3 +
            (100 - metrics["semantic_error_rate"]) * 0.3 +
            metrics["test_case_pass_rate"] * 0.4
        )
        
        # Calculate prompt adherence score if available
        if adherence_scores:
            metrics["prompt_adherence_score"] = sum(adherence_scores) / len(adherence_scores)
        else:
            # Estimate from correctness if not available
            metrics["prompt_adherence_score"] = metrics["code_correctness_score"] * 0.9
    
    return metrics

def analyze_code_efficiency(model_name: str) -> Dict[str, Any]:
    """Analyze and score code efficiency metrics.
    
    Returns:
        Dict with efficiency metrics including:
        - time_complexity_score: Score based on algorithmic efficiency (0-100)
        - space_complexity_score: Score based on memory usage efficiency (0-100)
        - code_size_efficiency: Ratio of functionality to code size (0-100)
        - resource_usage_score: Score based on CPU/memory utilization (0-100)
    """
    # Load performance results
    performance_results = load_performance_results(model_name)
    basic_results = load_test_results(model_name)
    
    # Default metrics
    metrics = {
        "time_complexity_score": 0,
        "space_complexity_score": 0,
        "code_size_efficiency": 0,
        "resource_usage_score": 0,
        "overall_efficiency_score": 0
    }
    
    # If we have performance data
    if performance_results.get("tests", 0) > 0:
        # Use existing efficiency score if available
        if "code_efficiency_score" in performance_results and performance_results["code_efficiency_score"] > 0:
            metrics["overall_efficiency_score"] = performance_results["code_efficiency_score"]
        else:
            # Estimate based on execution time
            avg_time = performance_results.get("avg_time", 0)
            if avg_time > 0:
                # Lower times get higher scores (inverse relationship)
                # Normalize to 0-100 scale (assuming 10s is very slow, 0.1s is very fast)
                time_score = max(0, min(100, 100 - (avg_time / 0.1 * 10)))
                metrics["time_complexity_score"] = time_score
            
            # Estimate space complexity from memory usage if available
            memory_usage = performance_results.get("memory_usage", 0)
            if memory_usage > 0:
                # Lower memory usage gets higher scores (inverse relationship)
                # Normalize to 0-100 scale (assuming 1000MB is very high, 10MB is very low)
                space_score = max(0, min(100, 100 - (memory_usage / 10 * 10)))
                metrics["space_complexity_score"] = space_score
            
            # Calculate code size efficiency if we have code lines data
            avg_code_lines = basic_results.get("avg_code_lines", 0)
            if avg_code_lines > 0:
                # Assume optimal code is between 5-50 lines
                # Too short might lack proper error handling, too long might be inefficient
                if avg_code_lines < 5:
                    code_size_score = avg_code_lines * 20  # 0-4 lines: 0-80 points
                elif avg_code_lines <= 50:
                    code_size_score = 100 - ((avg_code_lines - 5) / 45 * 20)  # 5-50 lines: 100-80 points
                else:
                    code_size_score = max(0, 80 - ((avg_code_lines - 50) / 50 * 40))  # >50 lines: 80-0 points
                
                metrics["code_size_efficiency"] = code_size_score
            
            # Calculate resource usage score if available
            cpu_usage = performance_results.get("cpu_usage", 0)
            if cpu_usage > 0:
                # Lower CPU usage gets higher scores
                resource_score = max(0, 100 - cpu_usage)
                metrics["resource_usage_score"] = resource_score
            
            # Calculate overall efficiency score (weighted average of available metrics)
            available_metrics = [score for score in [
                metrics["time_complexity_score"],
                metrics["space_complexity_score"],
                metrics["code_size_efficiency"],
                metrics["resource_usage_score"]
            ] if score > 0]
            
            if available_metrics:
                metrics["overall_efficiency_score"] = sum(available_metrics) / len(available_metrics)
    
    return metrics

def get_available_models() -> List[str]:
    """Get a list of all models that have test results."""
    # Get all test result files
    pattern = f"{TEST_RESULTS_DIR}/test_results_*_*.json"
    files = glob.glob(pattern)
    
    # Extract model IDs from filenames
    models = set()
    for file in files:
        filename = os.path.basename(file)
        parts = filename.split('_')
        if len(parts) >= 3:
            model_name = parts[2]  # Assuming format: test_results_MODEL_TIMESTAMP.json
            models.add(model_name)
    
    return sorted(list(models))

def evaluate_code_quality(model_name: str) -> Dict[str, Any]:
    """Evaluate code quality and documentation.
    
    Returns:
        Dict with quality metrics including:
        - documentation_quality: Score for comments and docstrings (0-100)
        - explanation_clarity: Score for the model's explanation clarity (0-100)
        - code_readability: Score for naming, structure, and formatting (0-100)
        - maintainability_index: Standard software engineering metric (0-100)
    """
    # Load basic test results
    basic_results = load_test_results(model_name)
    
    # Default metrics
    metrics = {
        "documentation_quality": 0,
        "explanation_clarity": 0,
        "code_readability": 0,
        "maintainability_index": 0,
        "overall_quality_score": 0
    }
    
    # Calculate metrics if we have data
    if basic_results["total_tests"] > 0:
        # Extract data from test results
        explanation_scores = []
        doc_scores = []
        readability_scores = []
        
        # Analyze test results for code samples and explanations
        for test in basic_results.get("test_results", []):
            code = test.get("code", "")
            explanation = test.get("explanation", "")
            
            # Evaluate documentation quality (comments and docstrings)
            if code:
                # Count docstrings and comments
                doc_lines = 0
                code_lines = code.count('\n') + 1
                
                # Simple heuristic: count lines with docstrings or comments
                for line in code.split('\n'):
                    if '"""' in line or "'''" in line or '#' in line:
                        doc_lines += 1
                
                # Calculate documentation ratio (capped at 40%)
                doc_ratio = min(0.4, doc_lines / max(1, code_lines))
                # Convert to 0-100 score (40% ratio = 100 score)
                doc_score = min(100, doc_ratio * 250)
                doc_scores.append(doc_score)
            
            # Evaluate explanation clarity
            if explanation:
                # Simple heuristics for explanation quality
                words = len(explanation.split())
                sentences = explanation.count('.') + explanation.count('!') + explanation.count('?')
                
                # Calculate average words per sentence (optimal is 15-20)
                words_per_sentence = words / max(1, sentences)
                if words_per_sentence < 5:
                    clarity_score = words_per_sentence * 10  # Too short: 0-50
                elif words_per_sentence <= 20:
                    clarity_score = 100 - abs(words_per_sentence - 15) * 2  # Optimal: 90-100
                else:
                    clarity_score = max(0, 100 - (words_per_sentence - 20) * 5)  # Too long: 0-100
                
                # Adjust based on explanation length (too short or too long is penalized)
                if words < 50:
                    clarity_score *= words / 50
                elif words > 300:
                    clarity_score *= max(0.5, 1 - (words - 300) / 700)
                
                explanation_scores.append(clarity_score)
            
            # Evaluate code readability
            if code:
                # Simple heuristics for readability
                # 1. Average line length (optimal is 40-60 chars)
                lines = [line for line in code.split('\n') if line.strip()]
                avg_line_length = sum(len(line) for line in lines) / max(1, len(lines))
                
                if avg_line_length < 20:
                    length_score = avg_line_length * 2.5  # Too short: 0-50
                elif avg_line_length <= 60:
                    length_score = 100 - abs(avg_line_length - 40) * 1.25  # Optimal: 75-100
                else:
                    length_score = max(0, 100 - (avg_line_length - 60) * 2.5)  # Too long: 0-100
                
                # 2. Indentation consistency
                indent_score = 100
                prev_indent = -1
                for line in lines:
                    if line.strip():
                        indent = len(line) - len(line.lstrip())
                        if prev_indent >= 0 and indent > prev_indent and (indent - prev_indent) % 4 != 0:
                            indent_score -= 10  # Penalize inconsistent indentation
                        prev_indent = indent
                
                readability_score = (length_score + indent_score) / 2
                readability_scores.append(readability_score)
        
        # Calculate average scores if we have data
        if doc_scores:
            metrics["documentation_quality"] = sum(doc_scores) / len(doc_scores)
        
        if explanation_scores:
            metrics["explanation_clarity"] = sum(explanation_scores) / len(explanation_scores)
        
        if readability_scores:
            metrics["code_readability"] = sum(readability_scores) / len(readability_scores)
        
        # Calculate maintainability index (simplified version)
        # Normally this would use cyclomatic complexity, Halstead volume, etc.
        # Here we estimate from our other metrics
        if doc_scores and readability_scores:
            metrics["maintainability_index"] = (
                metrics["documentation_quality"] * 0.4 +
                metrics["code_readability"] * 0.6
            )
        
        # Calculate overall quality score
        available_metrics = [score for score in [
            metrics["documentation_quality"],
            metrics["explanation_clarity"],
            metrics["code_readability"],
            metrics["maintainability_index"]
        ] if score > 0]
        
        if available_metrics:
            metrics["overall_quality_score"] = sum(available_metrics) / len(available_metrics)
    
    return metrics

def measure_user_intent_alignment(model_name: str) -> Dict[str, Any]:
    """Measure how well code aligns with user intent.
    
    Returns:
        Dict with intent alignment metrics including:
        - requirement_fulfillment: Score for meeting requirements (0-100)
        - edge_case_handling: Score for handling edge cases (0-100)
        - user_feedback_score: Score based on user feedback (0-100)
    """
    # Load basic test results
    basic_results = load_test_results(model_name)
    
    # Default metrics
    metrics = {
        "requirement_fulfillment": 0,
        "edge_case_handling": 0,
        "user_feedback_score": 0,
        "overall_intent_alignment": 0
    }
    
    # Calculate metrics if we have data
    if basic_results["total_tests"] > 0:
        # Use pass rate as a proxy for requirement fulfillment
        pass_rate = (basic_results["passed_tests"] / basic_results["total_tests"]) * 100
        metrics["requirement_fulfillment"] = pass_rate
        
        # Extract data from test results for edge case handling
        edge_case_scores = []
        feedback_scores = []
        
        for test in basic_results.get("test_results", []):
            # Check if test mentions edge cases
            if "edge_case" in test.get("name", "").lower() or "edge_case" in test.get("reason", "").lower():
                if test.get("status") == "PASSED":
                    edge_case_scores.append(100)
                else:
                    edge_case_scores.append(0)
            
            # Check if there's user feedback data
            if "user_feedback" in test:
                feedback_scores.append(test["user_feedback"])
        
        # Calculate edge case handling score if we have data
        if edge_case_scores:
            metrics["edge_case_handling"] = sum(edge_case_scores) / len(edge_case_scores)
        else:
            # Estimate from requirement fulfillment if no specific edge case tests
            metrics["edge_case_handling"] = pass_rate * 0.8  # Edge cases are harder, so scale down
        
        # Calculate user feedback score if we have data
        if feedback_scores:
            metrics["user_feedback_score"] = sum(feedback_scores) / len(feedback_scores)
        else:
            # Estimate from requirement fulfillment if no feedback data
            metrics["user_feedback_score"] = pass_rate * 0.9
        
        # Calculate overall intent alignment score (weighted average)
        metrics["overall_intent_alignment"] = (
            metrics["requirement_fulfillment"] * 0.5 +
            metrics["edge_case_handling"] * 0.3 +
            metrics["user_feedback_score"] * 0.2
        )
    
    return metrics

def load_historical_data(model_name: str, days: int = 30) -> List[Dict[str, Any]]:
    """Load historical performance data for trend analysis.
    
    Args:
        model_name: Name of the model to analyze
        days: Number of days of history to retrieve
    
    Returns:
        List of data points with timestamp and metrics
    """
    # Calculate cutoff date
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    cutoff_str = cutoff_date.strftime("%Y%m%d")
    
    # Find all historical result files for this model
    test_pattern = f"{TEST_RESULTS_DIR}/test_results_{model_name}_*.json"
    perf_pattern = f"{PERFORMANCE_RESULTS_DIR}/performance_{model_name}_*.json"
    
    test_files = sorted(glob.glob(test_pattern))
    perf_files = sorted(glob.glob(perf_pattern))
    
    # Extract timestamps and filter by cutoff date
    history = []
    
    # Process test result files
    for file in test_files:
        filename = os.path.basename(file)
        parts = filename.split('_')
        if len(parts) >= 4:
            timestamp = parts[3].split('.')[0]  # Extract timestamp from filename
            
            # Skip if before cutoff date
            if timestamp < cutoff_str:
                continue
            
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    
                    # Create history entry
                    entry = {
                        "timestamp": timestamp,
                        "passed_tests": data.get("passed_tests", 0),
                        "total_tests": data.get("total_tests", 0),
                        "pass_rate": (data.get("passed_tests", 0) / data.get("total_tests", 1)) * 100
                    }
                    
                    # Find matching performance file
                    matching_perf = next((p for p in perf_files if timestamp in p), None)
                    if matching_perf:
                        try:
                            with open(matching_perf, 'r') as pf:
                                perf_data = json.load(pf)
                                entry["avg_time"] = perf_data.get("avg_time", 0)
                                entry["code_efficiency_score"] = perf_data.get("code_efficiency_score", 0)
                        except (json.JSONDecodeError, IOError):
                            pass
                    
                    history.append(entry)
            except (json.JSONDecodeError, IOError):
                continue
    
    return sorted(history, key=lambda x: x["timestamp"])

def generate_markdown_report(models: List[str], output_file: str) -> str:
    """Generate a markdown report comparing all models."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building the markdown content
    md_content = f"""# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: {timestamp}

## Podsumowanie wyników

### Wyniki ogólne

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Średni czas (s) | Całkowity wynik |
|-------|--------------|-------------------|------------------|----------------|------------------|
"""
    
    # Add a row for each model
    for model in models:
        # Load test results
        basic_results = load_test_results(model)
        correctness_passed, correctness_total = load_correctness_results(model)
        performance_results = load_performance_results(model)
        
        # Calculate basic test metrics
        basic_passed = basic_results["passed_tests"]
        basic_total = basic_results["total_tests"]
        basic_percent = (basic_passed / basic_total * 100) if basic_total > 0 else 0
        basic_status = f"{basic_passed}/{basic_total} ({basic_percent:.1f}%)"
        
        # Calculate correctness test metrics
        correctness_percent = (correctness_passed / correctness_total * 100) if correctness_total > 0 else 0
        correctness_status = f"{correctness_passed}/{correctness_total} ({correctness_percent:.1f}%)"
        
        # Calculate performance test metrics
        perf_tests = performance_results.get("tests", 0)
        perf_passed = performance_results.get("passed_tests", 0)
        perf_percent = (perf_passed / perf_tests * 100) if perf_tests > 0 else 0
        perf_status = f"{perf_passed}/{perf_tests} ({perf_percent:.1f}%)"
        
        # Get average execution time
        avg_time = performance_results.get("avg_time", 0)
        
        # Calculate total score as a percentage
        total_passed = basic_passed + correctness_passed + perf_passed
        total_possible = basic_total + correctness_total + perf_tests
        total_percent = (total_passed / total_possible * 100) if total_possible > 0 else 0
        
        # Add row to table
        md_content += f"| {model} | {basic_status} | {correctness_status} | {perf_status} | {avg_time:.2f} | {total_passed}/{total_possible} ({total_percent:.1f}%) |\n"
    
    # Add new metrics tables
    md_content += "\n### Dokładność konwersji tekst-na-kod\n\n"
    md_content += "| Model | Poprawność kodu | Błędy składniowe | Błędy semantyczne | Zgodność z intencją |\n"
    md_content += "|-------|----------------|-----------------|-------------------|----------------------|\n"
    
    for model in models:
        # Get text-to-code accuracy metrics
        accuracy_metrics = calculate_text_to_code_accuracy(model)
        
        correctness = f"{accuracy_metrics['code_correctness_score']:.1f}%"
        syntax_errors = f"{accuracy_metrics['syntax_error_rate']:.1f}%"
        semantic_errors = f"{accuracy_metrics['semantic_error_rate']:.1f}%"
        adherence = f"{accuracy_metrics['prompt_adherence_score']:.1f}%"
        
        md_content += f"| {model} | {correctness} | {syntax_errors} | {semantic_errors} | {adherence} |\n"
    
    md_content += "\n### Wydajność generowanego kodu\n\n"
    md_content += "| Model | Złożoność czasowa | Złożoność pamięciowa | Efektywność rozmiaru | Wykorzystanie zasobów |\n"
    md_content += "|-------|-----------------|---------------------|---------------------|----------------------|\n"
    
    for model in models:
        # Get code efficiency metrics
        efficiency_metrics = analyze_code_efficiency(model)
        
        time_complexity = f"{efficiency_metrics['time_complexity_score']:.1f}%"
        space_complexity = f"{efficiency_metrics['space_complexity_score']:.1f}%"
        code_size = f"{efficiency_metrics['code_size_efficiency']:.1f}%"
        resource_usage = f"{efficiency_metrics['resource_usage_score']:.1f}%"
        
        md_content += f"| {model} | {time_complexity} | {space_complexity} | {code_size} | {resource_usage} |\n"
    
    md_content += "\n### Jakość wyjaśnień i kodu\n\n"
    md_content += "| Model | Jakość dokumentacji | Klarowność wyjaśnień | Czytelność kodu | Indeks utrzymywalności |\n"
    md_content += "|-------|---------------------|----------------------|----------------|------------------------|\n"
    
    for model in models:
        # Get code quality metrics
        quality_metrics = evaluate_code_quality(model)
        
        doc_quality = f"{quality_metrics['documentation_quality']:.1f}%"
        explanation = f"{quality_metrics['explanation_clarity']:.1f}%"
        readability = f"{quality_metrics['code_readability']:.1f}%"
        maintainability = f"{quality_metrics['maintainability_index']:.1f}%"
        
        md_content += f"| {model} | {doc_quality} | {explanation} | {readability} | {maintainability} |\n"
    
    md_content += "\n### Zgodność z intencjami użytkownika\n\n"
    md_content += "| Model | Spełnienie wymagań | Obsługa przypadków brzegowych | Ocena użytkownika | Ogólna zgodność |\n"
    md_content += "|-------|-------------------|-------------------------------|------------------|----------------|\n"
    
    for model in models:
        # Get user intent alignment metrics
        intent_metrics = measure_user_intent_alignment(model)
        
        requirements = f"{intent_metrics['requirement_fulfillment']:.1f}%"
        edge_cases = f"{intent_metrics['edge_case_handling']:.1f}%"
        user_feedback = f"{intent_metrics['user_feedback_score']:.1f}%"
        overall = f"{intent_metrics['overall_intent_alignment']:.1f}%"
        
        md_content += f"| {model} | {requirements} | {edge_cases} | {user_feedback} | {overall} |\n"
    
    # Generate chart data for visualization
    chart_data = {
        "models": [],
        "basic_test_scores": [],
        "correctness_scores": [],
        "performance_times": [],
        # New chart data for additional metrics
        "code_correctness": [],
        "explanation_quality": [],
        "code_efficiency": [],
        "user_alignment": []
    }
    
    for model in models:
        # Load test results
        basic_results = load_test_results(model)
        correctness_passed, correctness_total = load_correctness_results(model)
        performance_results = load_performance_results(model)
        
        # Get additional metrics
        accuracy_metrics = calculate_text_to_code_accuracy(model)
        efficiency_metrics = analyze_code_efficiency(model)
        quality_metrics = evaluate_code_quality(model)
        intent_metrics = measure_user_intent_alignment(model)
        
        # Calculate percentages
        basic_percent = (basic_results['passed_tests'] / basic_results['total_tests'] * 100) if basic_results['total_tests'] > 0 else 0
        correctness_percent = (correctness_passed / correctness_total * 100) if correctness_total > 0 else 0
        avg_time = performance_results.get('avg_time', 0)
        
        # Add to chart data
        chart_data["models"].append(model)
        chart_data["basic_test_scores"].append(basic_percent)
        chart_data["correctness_scores"].append(correctness_percent)
        chart_data["performance_times"].append(avg_time)
        
        # Add new metrics to chart data
        chart_data["code_correctness"].append(accuracy_metrics["code_correctness_score"])
        chart_data["explanation_quality"].append(quality_metrics["explanation_clarity"])
        chart_data["code_efficiency"].append(efficiency_metrics["overall_efficiency_score"])
        chart_data["user_alignment"].append(intent_metrics["overall_intent_alignment"])
    
    # Create chart HTML
    bar_chart_html = f"""
<div style="width: 80%; margin: 20px auto;">
    <canvas id="test-results-chart" class="evopy-chart" data-chart='{{
        "type": "bar",
        "data": {{
            "labels": {chart_data["models"]},
            "datasets": [
                {{
                    "label": "Testy zapytań (%)",
                    "data": {chart_data["basic_test_scores"]},
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }},
                {{
                    "label": "Testy poprawności (%)",
                    "data": {chart_data["correctness_scores"]},
                    "backgroundColor": "rgba(75, 192, 192, 0.5)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1
                }}
            ]
        }},
        "options": {{
            "scales": {{
                "y": {{
                    "beginAtZero": true,
                    "max": 100,
                    "title": {{
                        "display": true,
                        "text": "Procent sukcesu (%)"
                    }}
                }}
            }},
            "plugins": {{
                "title": {{
                    "display": true,
                    "text": "Porównanie wyników testów"
                }}
            }}
        }}
    }}'></canvas>
</div>
"""
    
    line_chart_html = f"""
<div style="width: 80%; margin: 20px auto;">
    <canvas id="performance-chart" class="evopy-chart" data-chart='{{
        "type": "line",
        "data": {{
            "labels": {chart_data["models"]},
            "datasets": [
                {{
                    "label": "Średni czas wykonania (s)",
                    "data": {chart_data["performance_times"]},
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 2,
                    "tension": 0.1
                }}
            ]
        }},
        "options": {{
            "scales": {{
                "y": {{
                    "beginAtZero": true,
                    "title": {{
                        "display": true,
                        "text": "Czas (sekundy)"
                    }}
                }}
            }},
            "plugins": {{
                "title": {{
                    "display": true,
                    "text": "Porównanie czasu wykonania"
                }}
            }}
        }}
    }}'></canvas>
</div>
"""
    
    # Add radar chart for comprehensive model comparison
    radar_chart_html = f"""
<div style="width: 80%; margin: 20px auto;">
    <canvas id="radar-chart" class="evopy-chart" data-chart='{{
        "type": "radar",
        "data": {{
            "labels": [
                "Poprawność kodu", 
                "Jakość wyjaśnień", 
                "Wydajność kodu", 
                "Zgodność z intencjami",
                "Testy podstawowe"
            ],
            "datasets": [
                {{
                    "label": "{chart_data['models'][0] if len(chart_data['models']) > 0 else 'Model 1'}",
                    "data": [
                        {chart_data['code_correctness'][0] if len(chart_data['code_correctness']) > 0 else 0},
                        {chart_data['explanation_quality'][0] if len(chart_data['explanation_quality']) > 0 else 0},
                        {chart_data['code_efficiency'][0] if len(chart_data['code_efficiency']) > 0 else 0},
                        {chart_data['user_alignment'][0] if len(chart_data['user_alignment']) > 0 else 0},
                        {chart_data['basic_test_scores'][0] if len(chart_data['basic_test_scores']) > 0 else 0}
                    ],
                    "fill": true,
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "pointBackgroundColor": "rgba(54, 162, 235, 1)",
                    "pointBorderColor": "#fff",
                    "pointHoverBackgroundColor": "#fff",
                    "pointHoverBorderColor": "rgba(54, 162, 235, 1)"
                }},
                {{
                    "label": "{chart_data['models'][1] if len(chart_data['models']) > 1 else 'Model 2'}",
                    "data": [
                        {chart_data['code_correctness'][1] if len(chart_data['code_correctness']) > 1 else 0},
                        {chart_data['explanation_quality'][1] if len(chart_data['explanation_quality']) > 1 else 0},
                        {chart_data['code_efficiency'][1] if len(chart_data['code_efficiency']) > 1 else 0},
                        {chart_data['user_alignment'][1] if len(chart_data['user_alignment']) > 1 else 0},
                        {chart_data['basic_test_scores'][1] if len(chart_data['basic_test_scores']) > 1 else 0}
                    ],
                    "fill": true,
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "pointBackgroundColor": "rgba(255, 99, 132, 1)",
                    "pointBorderColor": "#fff",
                    "pointHoverBackgroundColor": "#fff",
                    "pointHoverBorderColor": "rgba(255, 99, 132, 1)"
                }}
            ]
        }},
        "options": {{
            "elements": {{
                "line": {{
                    "borderWidth": 3
                }}
            }},
            "scales": {{
                "r": {{
                    "angleLines": {{
                        "display": true
                    }},
                    "suggestedMin": 0,
                    "suggestedMax": 100
                }}
            }},
            "plugins": {{
                "title": {{
                    "display": true,
                    "text": "Porównanie modeli w różnych kategoriach"
                }}
            }}
        }}
    }}'></canvas>
</div>
"""
    
    # Add visualization section
    md_content += "\n## Wizualizacja wyników\n\n"
    md_content += "### Wykresy porównawcze\n\n"
    md_content += radar_chart_html + "\n\n"
    md_content += bar_chart_html + "\n\n"
    md_content += line_chart_html + "\n\n"
    
    # Add trend analysis section
    md_content += "\n## Analiza trendów\n\n"
    md_content += "### Postępy w czasie\n\n"
    
    # Generate trend data for each model
    for model in models:
        history = load_historical_data(model, days=30)
        if history:
            md_content += f"#### Model: {model}\n\n"
            
            # Create trend indicators
            pass_rate_trend = []
            time_trend = []
            efficiency_trend = []
            
            for i in range(1, len(history)):
                # Pass rate trend
                prev_pass = history[i-1].get("pass_rate", 0)
                curr_pass = history[i].get("pass_rate", 0)
                if curr_pass > prev_pass:
                    pass_rate_trend.append("↑")
                elif curr_pass < prev_pass:
                    pass_rate_trend.append("↓")
                else:
                    pass_rate_trend.append("→")
                
                # Time trend (lower is better)
                prev_time = history[i-1].get("avg_time", 0)
                curr_time = history[i].get("avg_time", 0)
                if curr_time < prev_time and prev_time > 0:
                    time_trend.append("↑")
                elif curr_time > prev_time and prev_time > 0:
                    time_trend.append("↓")
                else:
                    time_trend.append("→")
                
                # Efficiency trend
                prev_eff = history[i-1].get("code_efficiency_score", 0)
                curr_eff = history[i].get("code_efficiency_score", 0)
                if curr_eff > prev_eff:
                    efficiency_trend.append("↑")
                elif curr_eff < prev_eff:
                    efficiency_trend.append("↓")
                else:
                    efficiency_trend.append("→")
            
            # Display trend indicators
            if pass_rate_trend:
                pass_trend_str = "".join(pass_rate_trend[-5:]) if len(pass_rate_trend) > 5 else "".join(pass_rate_trend)
                time_trend_str = "".join(time_trend[-5:]) if len(time_trend) > 5 else "".join(time_trend)
                eff_trend_str = "".join(efficiency_trend[-5:]) if len(efficiency_trend) > 5 else "".join(efficiency_trend)
                
                md_content += f"- **Poprawność kodu**: {pass_trend_str} (ostatnie {min(5, len(pass_rate_trend))} testów)\n"
                md_content += f"- **Czas wykonania**: {time_trend_str} (ostatnie {min(5, len(time_trend))} testów)\n"
                md_content += f"- **Wydajność kodu**: {eff_trend_str} (ostatnie {min(5, len(efficiency_trend))} testów)\n\n"
            else:
                md_content += "- Brak wystarczających danych historycznych do analizy trendów\n\n"
        else:
            md_content += f"#### Model: {model}\n\n"
            md_content += "- Brak danych historycznych\n\n"
    
    # Add detailed results section
    md_content += "\n## Szczegółowe wyniki testów\n\n"
    
    for model in models:
        md_content += f"### Model: {model}\n\n"
        
        # Basic test results
        basic_results = load_test_results(model)
        basic_passed = basic_results['passed_tests']
        basic_total = basic_results['total_tests']
        basic_percent = (basic_passed / basic_total * 100) if basic_total > 0 else 0
        
        md_content += f"#### Wyniki testów zapytań\n"
        md_content += f"- Zaliczone testy: {basic_passed}/{basic_total} ({basic_percent:.1f}%)\n"
        md_content += f"- Ilość wygenerowanego kodu: {basic_results.get('total_code_lines', 0)} linii\n"
        md_content += f"- Średnia ilość linii na zapytanie: {basic_results.get('avg_code_lines', 0):.1f}\n"
        
        if basic_results["test_results"]:
            md_content += "- Szczegóły testów:\n"
            for test in basic_results["test_results"]:
                status = "✅" if test["status"] == "PASSED" else "❌"
                code_lines = test.get("code_lines", 0)
                md_content += f"  - {status} {test['name']}: {test['reason']} ({code_lines} linii kodu)\n"
        
        # Correctness test results
        correctness_passed, correctness_total = load_correctness_results(model)
        correctness_percent = (correctness_passed / correctness_total * 100) if correctness_total > 0 else 0
        
        md_content += f"\n#### Wyniki testów poprawności\n"
        md_content += f"- Zaliczone testy: {correctness_passed}/{correctness_total} ({correctness_percent:.1f}%)\n"
        md_content += f"- Skuteczność kompilacji: {basic_results.get('compilation_success_rate', 0):.1f}%\n"
        md_content += f"- Skuteczność wykonania: {basic_results.get('execution_success_rate', 0):.1f}%\n"
        
        # Performance test results
        performance_results = load_performance_results(model)
        perf_tests = performance_results.get("tests", 0)
        perf_passed = performance_results.get("passed_tests", 0)
        perf_percent = (perf_passed / perf_tests * 100) if perf_tests > 0 else 0
        
        md_content += f"\n#### Wyniki testów wydajności\n"
        if perf_tests > 0:
            md_content += f"- Zaliczone testy: {perf_passed}/{perf_tests} ({perf_percent:.1f}%)\n"
            md_content += f"- Średni czas wykonania: {performance_results.get('avg_time', 0):.2f} s\n"
            md_content += f"- Najszybszy test: {performance_results.get('min_time', 0):.2f} s\n"
            md_content += f"- Najwolniejszy test: {performance_results.get('max_time', 0):.2f} s\n"
            md_content += f"- Całkowity czas wykonania: {performance_results.get('total_time', 0):.2f} s\n"
        else:
            md_content += "- Brak wyników testów wydajności\n"
        
        md_content += "\n"
    
    # Find best models based on metrics
    best_correctness_model = ""
    best_correctness_score = 0
    fastest_model = ""
    best_speed = float('inf')
    best_overall_model = ""
    best_overall_score = 0
    
    for model in models:
        # Load test results
        basic_results = load_test_results(model)
        correctness_passed, correctness_total = load_correctness_results(model)
        performance_results = load_performance_results(model)
        
        # Calculate correctness percentage
        correctness_percent = (correctness_passed / correctness_total * 100) if correctness_total > 0 else 0
        if correctness_percent > best_correctness_score:
            best_correctness_score = correctness_percent
            best_correctness_model = model
        
        # Calculate speed
        avg_time = performance_results.get('avg_time', float('inf'))
        if avg_time < best_speed and avg_time > 0:
            best_speed = avg_time
            fastest_model = model
        
        # Calculate overall score
        basic_passed = basic_results['passed_tests']
        basic_total = basic_results['total_tests']
        perf_tests = performance_results.get("tests", 0)
        perf_passed = performance_results.get("passed_tests", 0)
        
        total_passed = basic_passed + correctness_passed + perf_passed
        total_possible = basic_total + correctness_total + perf_tests
        overall_percent = (total_passed / total_possible * 100) if total_possible > 0 else 0
        
        if overall_percent > best_overall_score:
            best_overall_score = overall_percent
            best_overall_model = model
    
    # Add conclusions section
    md_content += f"""
## Wnioski

Na podstawie przeprowadzonych testów można wyciągnąć następujące wnioski:

1. **Najlepszy model pod względem poprawności**: {best_correctness_model} ({best_correctness_score:.1f}%)
2. **Najszybszy model**: {fastest_model} (średni czas: {best_speed:.2f}s)
3. **Najlepszy model ogólnie**: {best_overall_model} (ogólny wynik: {best_overall_score:.1f}%)

## Metodologia testów

Testy zostały przeprowadzone w trzech kategoriach:

1. **Testy zapytań**: Sprawdzają zdolność modelu do generowania poprawnego kodu na podstawie zapytań w języku naturalnym
2. **Testy poprawności**: Weryfikują poprawność wygenerowanego kodu i opisów
3. **Testy wydajności**: Mierzą czas wykonania różnych operacji przez model

## Zalecenia

Na podstawie wyników testów zalecamy:

1. **Do zadań wymagających wysokiej dokładności**: {best_correctness_model}
2. **Do zadań wymagających szybkiego działania**: {fastest_model}
3. **Do ogólnego użytku**: {best_overall_model}
"""
    
    # Write to file
    with open(output_file, 'w') as f:
        f.write(md_content)
    
    logger.info(f"Markdown report generated: {output_file}")
    return md_content

def generate_html_report(markdown_content: str, output_file: str) -> None:
    """Convert markdown report to HTML."""
    try:
        # Add CSS styling for better HTML presentation
        html_header = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Evopy Model Comparison Report</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 30px;
        }
        h3 {
            color: #3498db;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f1f1f1;
        }
        .passed {
            color: #27ae60;
            font-weight: bold;
        }
        .failed {
            color: #e74c3c;
            font-weight: bold;
        }
        .unknown {
            color: #f39c12;
            font-weight: bold;
        }
        code {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 2px 5px;
            font-family: monospace;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 10px;
            overflow-x: auto;
        }
        .footer {
            margin-top: 50px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
            font-size: 0.9em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
"""
        
        # Add Mermaid support for diagrams and charts
        mermaid_script = """
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Mermaid diagrams
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: { useMaxWidth: false, htmlLabels: true },
            sequence: { useMaxWidth: false, showSequenceNumbers: true }
        });
        
        // Initialize Chart.js charts
        setTimeout(function() {
            const chartElements = document.querySelectorAll('.evopy-chart');
            chartElements.forEach(function(element) {
                const ctx = element.getContext('2d');
                const chartData = JSON.parse(element.getAttribute('data-chart'));
                new Chart(ctx, chartData);
            });
        }, 500);
    });
</script>
"""
        
        html_footer = """
<div class="footer">
    <p>Wygenerowano przez Evopy Report Generator</p>
    <p>© 2025 Evopy</p>
</div>
""" + mermaid_script + """
</body>
</html>
"""
        
        # Convert markdown to HTML using pandoc
        pandoc_cmd = [
            "pandoc", 
            "-f", "markdown", 
            "-t", "html", 
            "--standalone",
            "--metadata", "title=Evopy Model Comparison Report"
        ]
        
        process = subprocess.run(
            pandoc_cmd,
            input=markdown_content.encode(),
            capture_output=True,
            check=True
        )
        
        html_content = process.stdout.decode()
        
        # Extract the body content (between <body> and </body>)
        body_start = html_content.find("<body>") + len("<body>")
        body_end = html_content.find("</body>")
        body_content = html_content[body_start:body_end]
        
        # Replace emoji with styled text for better compatibility
        body_content = body_content.replace("✅", '<span class="passed">PASSED</span>')
        body_content = body_content.replace("❌", '<span class="failed">FAILED</span>')
        body_content = body_content.replace("❓", '<span class="unknown">UNKNOWN</span>')
        
        # Combine with our custom header and footer
        final_html = html_header + body_content + html_footer
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write(final_html)
        
        logger.info(f"HTML report generated: {output_file}")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating HTML report: {e}")
        logger.error(f"Pandoc stderr: {e.stderr.decode()}")
        raise

def generate_pdf_report(html_file: str, output_file: str) -> None:
    """Convert HTML report to PDF with landscape orientation."""
    try:
        # Use wkhtmltopdf to convert HTML to PDF
        wkhtmltopdf_cmd = [
            "wkhtmltopdf",
            "--orientation", "Landscape",  # Set landscape orientation
            "--page-size", "A4",
            "--margin-top", "15",
            "--margin-right", "15",
            "--margin-bottom", "15",
            "--margin-left", "15",
            "--header-right", "[page]/[topage]",
            "--header-font-size", "8",
            "--footer-center", "Evopy Model Comparison Report",
            "--footer-font-size", "8",
            html_file,
            output_file
        ]
        
        subprocess.run(wkhtmltopdf_cmd, check=True)
        logger.info(f"PDF report generated: {output_file}")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating PDF report: {e}")
        raise

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate comparison reports for Evopy models")
    parser.add_argument("--format", choices=["all", "md", "html", "pdf"], default="all",
                        help="Output format(s) to generate")
    parser.add_argument("--input", type=str, default=str(TEST_RESULTS_DIR),
                        help="Directory containing test results")
    parser.add_argument("--output", type=str, default=str(REPORTS_DIR),
                        help="Directory to save reports")
    
    args = parser.parse_args()
    
    # Check dependencies if generating HTML or PDF
    if args.format in ["all", "html", "pdf"]:
        if not check_dependencies():
            logger.error("Missing dependencies. Please install them and try again.")
            sys.exit(1)
    
    # Get available models
    models = get_available_models()
    if not models:
        logger.error("No test results found. Run tests first.")
        sys.exit(1)
    
    logger.info(f"Found results for {len(models)} models: {', '.join(models)}")
    
    # Generate timestamp for filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)
    
    # Generate reports in requested formats
    md_content = None
    html_file = None
    
    if args.format in ["all", "md"]:
        md_file = output_dir / f"comparison_report_{timestamp}.md"
        md_content = generate_markdown_report(models, str(md_file))
    
    if args.format in ["all", "html"]:
        html_file = output_dir / f"comparison_report_{timestamp}.html"
        if md_content is None:
            md_file = output_dir / f"comparison_report_{timestamp}.md"
            md_content = generate_markdown_report(models, str(md_file))
        generate_html_report(md_content, str(html_file))
    
    if args.format in ["all", "pdf"]:
        pdf_file = output_dir / f"comparison_report_{timestamp}.pdf"
        if html_file is None:
            html_file = output_dir / f"comparison_report_{timestamp}.html"
            if md_content is None:
                md_file = output_dir / f"comparison_report_{timestamp}.md"
                md_content = generate_markdown_report(models, str(md_file))
            generate_html_report(md_content, str(html_file))
        generate_pdf_report(str(html_file), str(pdf_file))
    
    logger.info(f"Report generation complete. Reports saved to: {output_dir}")
    logger.info("To view the reports, use:")
    if args.format in ["all", "md"]:
        logger.info(f"  Markdown: less {output_dir}/comparison_report_{timestamp}.md")
    if args.format in ["all", "html"]:
        logger.info(f"  HTML: xdg-open {output_dir}/comparison_report_{timestamp}.html")
    if args.format in ["all", "pdf"]:
        logger.info(f"  PDF: xdg-open {output_dir}/comparison_report_{timestamp}.pdf")

if __name__ == "__main__":
    main()
