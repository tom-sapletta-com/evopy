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

def load_test_results(model_id: str) -> Dict[str, Any]:
    """Load the most recent test results for a specific model."""
    # Find the most recent results file for this model
    pattern = f"{TEST_RESULTS_DIR}/test_results_{model_id}_*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    
    default_results = {
        "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
        "model_id": model_id,
        "passed_tests": 0,
        "failed_tests": 0,
        "total_tests": 0,
        "test_results": []
    }
    
    if not files:
        logger.warning(f"No test results found for model: {model_id}")
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
        logger.error(f"Error loading test results for {model_id}: {e}")
        return default_results

def load_correctness_results(model_id: str) -> Tuple[int, int]:
    """Load correctness test results for a specific model."""
    # Look for text2python and python2text results
    t2p_pattern = f"{CORRECTNESS_RESULTS_DIR}/text2python_correctness_{model_id}_*.json"
    p2t_pattern = f"{CORRECTNESS_RESULTS_DIR}/python2text_correctness_{model_id}_*.json"
    
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
            logger.error(f"Error loading text2python correctness results for {model_id}: {e}")
    
    # Process python2text results
    if p2t_files:
        try:
            with open(p2t_files[0], 'r') as f:
                data = json.load(f)
                passed += data.get("passed_tests", 0)
                total += data.get("total_tests", 0)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading python2text correctness results for {model_id}: {e}")
    
    return passed, total

def load_performance_results(model_id: str) -> Dict[str, Any]:
    """Load performance test results for a specific model."""
    pattern = f"{PERFORMANCE_RESULTS_DIR}/performance_{model_id}_*.json"
    files = sorted(glob.glob(pattern), reverse=True)
    
    default_results = {"avg_time": 0, "tests": 0}
    
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
        logger.error(f"Error loading performance results for {model_id}: {e}")
        return default_results

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
            model_id = parts[2]  # Assuming format: test_results_MODEL_TIMESTAMP.json
            models.add(model_id)
    
    return sorted(list(models))

def generate_markdown_report(models: List[str], output_file: str) -> str:
    """Generate a markdown report comparing all models."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Start building the markdown content
    md_content = f"""# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: {timestamp}

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
"""
    
    # Add a row for each model
    for model in models:
        # Load test results
        basic_results = load_test_results(model)
        correctness_passed, correctness_total = load_correctness_results(model)
        performance_results = load_performance_results(model)
        
        # Calculate basic test status
        basic_status = "✅" if basic_results["passed_tests"] > 0 else "❌"
        if basic_results["total_tests"] == 0:
            basic_status = "❓"
        
        # Calculate correctness test status
        correctness_status = "✅" if correctness_passed > 0 else "❌"
        if correctness_total == 0:
            correctness_status = "❓"
        
        # Calculate performance test status
        performance_status = "✅" if performance_results.get("tests", 0) > 0 else "❌"
        
        # Calculate total score
        total_passed = (basic_results["passed_tests"] > 0) + (correctness_passed > 0) + (performance_results.get("tests", 0) > 0)
        total_possible = 3  # Three categories of tests
        
        # Add row to table
        md_content += f"| {model} | {basic_status} | {correctness_status} | {performance_status} | {total_passed}/{total_possible} |\n"
    
    # Add detailed results section
    md_content += "\n## Szczegółowe wyniki testów\n\n"
    
    for model in models:
        md_content += f"### Model: {model}\n\n"
        
        # Basic test results
        basic_results = load_test_results(model)
        md_content += f"#### Wyniki testów zapytań\n"
        md_content += f"- Zaliczone testy: {basic_results['passed_tests']}/{basic_results['total_tests']}\n"
        
        if basic_results["test_results"]:
            md_content += "- Szczegóły testów:\n"
            for test in basic_results["test_results"]:
                status = "✅" if test["status"] == "PASSED" else "❌"
                md_content += f"  - {status} {test['name']}: {test['reason']}\n"
        
        # Correctness test results
        correctness_passed, correctness_total = load_correctness_results(model)
        md_content += f"\n#### Wyniki testów poprawności\n"
        md_content += f"- Zaliczone testy: {correctness_passed}/{correctness_total}\n"
        
        # Performance test results
        performance_results = load_performance_results(model)
        md_content += f"\n#### Wyniki testów wydajności\n"
        if performance_results.get("tests", 0) > 0:
            md_content += f"- Średni czas wykonania: {performance_results.get('avg_time', 0):.2f} s\n"
            md_content += f"- Liczba testów: {performance_results.get('tests', 0)}\n"
        else:
            md_content += "- Brak wyników testów wydajności\n"
        
        md_content += "\n"
    
    # Add conclusions section
    md_content += """
## Wnioski

Na podstawie przeprowadzonych testów można wyciągnąć następujące wnioski:

1. **Najlepszy model pod względem poprawności**: Model z najwyższym wynikiem w testach poprawności
2. **Najszybszy model**: Model z najniższym średnim czasem wykonania
3. **Najlepszy model ogólnie**: Model z najwyższym całkowitym wynikiem

## Metodologia testów

Testy zostały przeprowadzone w trzech kategoriach:

1. **Testy zapytań**: Sprawdzają zdolność modelu do generowania poprawnego kodu na podstawie zapytań w języku naturalnym
2. **Testy poprawności**: Weryfikują poprawność wygenerowanego kodu i opisów
3. **Testy wydajności**: Mierzą czas wykonania różnych operacji przez model

## Zalecenia

Na podstawie wyników testów zaleca się:

1. Używanie modelu z najwyższym całkowitym wynikiem do większości zastosowań
2. W przypadku zadań wymagających wysokiej wydajności, rozważenie użycia najszybszego modelu
3. Dla zadań wymagających wysokiej dokładności, wybór modelu z najlepszymi wynikami w testach poprawności
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
        
        html_footer = """
<div class="footer">
    <p>Wygenerowano przez Evopy Report Generator</p>
    <p>© 2025 Evopy</p>
</div>
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
