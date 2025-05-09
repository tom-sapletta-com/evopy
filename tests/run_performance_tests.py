#!/usr/bin/env python3
"""
Run Performance Tests - Uruchamianie testów wydajności

Ten skrypt uruchamia testy wydajności asystenta evopy i generuje szczegółowe raporty.
"""

import os
import sys
import json
import time
import argparse
import logging
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Dodaj katalog główny projektu do ścieżki importu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modułu testowego
from test_assistant_performance import AssistantTester, get_test_cases

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_runner.log")
    ]
)
logger = logging.getLogger("evopy-test-runner")

# Stałe
TEST_DIR = Path(__file__).parent
RESULTS_DIR = TEST_DIR / "results"
REPORTS_DIR = TEST_DIR / "reports"

# Upewnij się, że katalogi istnieją
for directory in [RESULTS_DIR, REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)


def parse_arguments():
    """Parsuje argumenty wiersza poleceń"""
    parser = argparse.ArgumentParser(description="Uruchamianie testów wydajności asystenta evopy")
    parser.add_argument(
        "--model", 
        default="deepseek-coder:instruct-6.7b",
        help="Nazwa modelu Ollama do użycia (domyślnie: deepseek-coder:instruct-6.7b)"
    )
    parser.add_argument(
        "--categories", 
        nargs="+", 
        help="Kategorie testów do uruchomienia (domyślnie: wszystkie)"
    )
    parser.add_argument(
        "--generate-report", 
        action="store_true",
        help="Generuj szczegółowy raport po zakończeniu testów"
    )
    parser.add_argument(
        "--compare-models", 
        nargs="+",
        help="Porównaj wyniki z innymi modelami (podaj nazwy modeli)"
    )
    
    return parser.parse_args()


def filter_test_cases(test_cases: List[Dict[str, Any]], categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Filtruje przypadki testowe według kategorii
    
    Args:
        test_cases: Lista przypadków testowych
        categories: Lista kategorii do uwzględnienia
        
    Returns:
        List[Dict[str, Any]]: Przefiltrowana lista przypadków testowych
    """
    if not categories:
        return test_cases
    
    return [test for test in test_cases if test.get("category", "Inne") in categories]


def generate_detailed_report(results_file: Path):
    """
    Generuje szczegółowy raport na podstawie wyników testów
    
    Args:
        results_file: Ścieżka do pliku z wynikami testów
    """
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    model_name = results["model"]
    timestamp = datetime.fromisoformat(results["timestamp"])
    tests = results["tests"]
    
    # Przygotuj dane do analizy
    df = pd.DataFrame(tests)
    
    # Dodaj kolumny z czasami
    df["generation_time"] = df.apply(lambda x: x["code_generation"]["time_taken"], axis=1)
    df["execution_time"] = df.apply(lambda x: x["code_execution"]["time_taken"] if x["code_execution"]["success"] else 0, axis=1)
    df["total_time"] = df["generation_time"] + df["execution_time"]
    
    # Generuj raport HTML
    report_file = REPORTS_DIR / f"report_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Raport testów wydajności - {model_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .success {{ color: green; }}
            .failure {{ color: red; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .category-summary {{ margin-bottom: 30px; }}
            pre {{ background-color: #f8f8f8; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <h1>Raport testów wydajności asystenta evopy</h1>
        <p>Model: <strong>{model_name}</strong></p>
        <p>Data: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Podsumowanie</h2>
            <p>Liczba testów: <strong>{len(tests)}</strong></p>
            <p>Udane testy: <strong class="success">{sum(1 for test in tests if test["success"])}</strong></p>
            <p>Nieudane testy: <strong class="failure">{sum(1 for test in tests if not test["success"])}</strong></p>
            <p>Współczynnik sukcesu: <strong>{sum(1 for test in tests if test["success"]) / len(tests) * 100:.2f}%</strong></p>
            <p>Średni czas generowania kodu: <strong>{df["generation_time"].mean():.2f}s</strong></p>
            <p>Średni czas wykonania kodu: <strong>{df["execution_time"].mean():.2f}s</strong></p>
            <p>Średni całkowity czas: <strong>{df["total_time"].mean():.2f}s</strong></p>
        </div>
    """
    
    # Podsumowanie według kategorii
    categories = df["category"].unique()
    
    html_content += """
        <h2>Wyniki według kategorii</h2>
    """
    
    for category in categories:
        category_df = df[df["category"] == category]
        success_count = sum(1 for _, row in category_df.iterrows() if row["success"])
        total_count = len(category_df)
        success_rate = success_count / total_count * 100 if total_count > 0 else 0
        
        html_content += f"""
        <div class="category-summary">
            <h3>{category}</h3>
            <p>Liczba testów: <strong>{total_count}</strong></p>
            <p>Udane testy: <strong class="success">{success_count}</strong></p>
            <p>Współczynnik sukcesu: <strong>{success_rate:.2f}%</strong></p>
            <p>Średni czas generowania kodu: <strong>{category_df["generation_time"].mean():.2f}s</strong></p>
            <p>Średni czas wykonania kodu: <strong>{category_df["execution_time"].mean():.2f}s</strong></p>
            
            <table>
                <tr>
                    <th>Test</th>
                    <th>Status</th>
                    <th>Czas generowania</th>
                    <th>Czas wykonania</th>
                </tr>
        """
        
        for _, test in category_df.iterrows():
            status = "✅ Sukces" if test["success"] else "❌ Niepowodzenie"
            status_class = "success" if test["success"] else "failure"
            
            html_content += f"""
                <tr>
                    <td>{test["name"]}</td>
                    <td class="{status_class}">{status}</td>
                    <td>{test["generation_time"]:.2f}s</td>
                    <td>{test["execution_time"]:.2f}s</td>
                </tr>
            """
        
        html_content += """
            </table>
        </div>
        """
    
    # Szczegółowe wyniki testów
    html_content += """
        <h2>Szczegółowe wyniki testów</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Kategoria</th>
                <th>Status</th>
                <th>Czas generowania</th>
                <th>Czas wykonania</th>
            </tr>
    """
    
    for test in tests:
        status = "✅ Sukces" if test["success"] else "❌ Niepowodzenie"
        status_class = "success" if test["success"] else "failure"
        
        html_content += f"""
            <tr>
                <td><a href="#test-{tests.index(test)}">{test["name"]}</a></td>
                <td>{test["category"]}</td>
                <td class="{status_class}">{status}</td>
                <td>{test["code_generation"]["time_taken"]:.2f}s</td>
                <td>{test["code_execution"]["time_taken"]:.2f}s</td>
            </tr>
        """
    
    html_content += """
        </table>
    """
    
    # Szczegóły każdego testu
    for test in tests:
        test_id = tests.index(test)
        status = "✅ Sukces" if test["success"] else "❌ Niepowodzenie"
        status_class = "success" if test["success"] else "failure"
        
        html_content += f"""
        <div id="test-{test_id}" style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px;">
            <h3>{test["name"]}</h3>
            <p>Kategoria: <strong>{test["category"]}</strong></p>
            <p>Status: <strong class="{status_class}">{status}</strong></p>
            
            <h4>Prompt</h4>
            <pre>{test["prompt"]}</pre>
            
            <h4>Wygenerowany kod</h4>
            <pre>{test["code_generation"]["code"]}</pre>
            
            <h4>Wynik wykonania</h4>
            <pre>{test["code_execution"]["output"]}</pre>
            
            {f'<h4>Oczekiwany wynik</h4><pre>{test["expected_output"]}</pre>' if test.get("expected_output") else ''}
            
            {f'<h4>Błąd</h4><pre>{test["code_execution"]["error"]}</pre>' if test["code_execution"]["error"] else ''}
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Szczegółowy raport zapisany do {report_file}")
    
    # Generuj wykresy
    generate_charts(df, model_name, timestamp)


def generate_charts(df: pd.DataFrame, model_name: str, timestamp: datetime):
    """
    Generuje wykresy na podstawie wyników testów
    
    Args:
        df: DataFrame z wynikami testów
        model_name: Nazwa modelu
        timestamp: Znacznik czasu
    """
    # Wykres współczynnika sukcesu według kategorii
    plt.figure(figsize=(12, 6))
    
    categories = df["category"].unique()
    success_rates = []
    
    for category in categories:
        category_df = df[df["category"] == category]
        success_count = sum(1 for _, row in category_df.iterrows() if row["success"])
        total_count = len(category_df)
        success_rate = success_count / total_count * 100 if total_count > 0 else 0
        success_rates.append(success_rate)
    
    plt.bar(categories, success_rates, color='skyblue')
    plt.axhline(y=sum(success_rates) / len(success_rates), color='r', linestyle='-', label='Średnia')
    plt.xlabel('Kategoria')
    plt.ylabel('Współczynnik sukcesu (%)')
    plt.title(f'Współczynnik sukcesu według kategorii - {model_name}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.legend()
    
    chart_file = REPORTS_DIR / f"success_rate_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_file)
    
    # Wykres czasów według kategorii
    plt.figure(figsize=(12, 6))
    
    generation_times = []
    execution_times = []
    
    for category in categories:
        category_df = df[df["category"] == category]
        generation_times.append(category_df["generation_time"].mean())
        execution_times.append(category_df["execution_time"].mean())
    
    width = 0.35
    x = range(len(categories))
    
    plt.bar([i - width/2 for i in x], generation_times, width, label='Czas generowania', color='skyblue')
    plt.bar([i + width/2 for i in x], execution_times, width, label='Czas wykonania', color='lightgreen')
    
    plt.xlabel('Kategoria')
    plt.ylabel('Czas (s)')
    plt.title(f'Średnie czasy według kategorii - {model_name}')
    plt.xticks(x, categories, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    chart_file = REPORTS_DIR / f"times_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_file)


def compare_models(model_results: List[Dict[str, Any]]):
    """
    Porównuje wyniki testów dla różnych modeli
    
    Args:
        model_results: Lista wyników dla różnych modeli
    """
    if len(model_results) < 2:
        logger.warning("Potrzebne są wyniki co najmniej dwóch modeli do porównania")
        return
    
    # Przygotuj dane do porównania
    model_names = [result["model"] for result in model_results]
    success_rates = []
    generation_times = []
    execution_times = []
    
    for result in model_results:
        tests = result["tests"]
        success_rate = sum(1 for test in tests if test["success"]) / len(tests) * 100
        success_rates.append(success_rate)
        
        gen_time = sum(test["code_generation"]["time_taken"] for test in tests) / len(tests)
        generation_times.append(gen_time)
        
        exec_time = sum(test["code_execution"]["time_taken"] for test in tests if test["code_execution"]["success"]) / sum(1 for test in tests if test["code_execution"]["success"])
        execution_times.append(exec_time)
    
    # Generuj wykresy porównawcze
    plt.figure(figsize=(10, 6))
    
    plt.bar(model_names, success_rates, color='skyblue')
    plt.xlabel('Model')
    plt.ylabel('Współczynnik sukcesu (%)')
    plt.title('Porównanie współczynników sukcesu')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    chart_file = REPORTS_DIR / f"model_comparison_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_file)
    
    # Wykres czasów
    plt.figure(figsize=(10, 6))
    
    width = 0.35
    x = range(len(model_names))
    
    plt.bar([i - width/2 for i in x], generation_times, width, label='Czas generowania', color='skyblue')
    plt.bar([i + width/2 for i in x], execution_times, width, label='Czas wykonania', color='lightgreen')
    
    plt.xlabel('Model')
    plt.ylabel('Czas (s)')
    plt.title('Porównanie czasów')
    plt.xticks(x, model_names, rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    
    chart_file = REPORTS_DIR / f"model_comparison_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(chart_file)
    
    # Generuj raport HTML
    report_file = REPORTS_DIR / f"model_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Porównanie modeli</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            img {{ max-width: 100%; height: auto; margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <h1>Porównanie modeli</h1>
        <p>Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>Podsumowanie</h2>
            <table>
                <tr>
                    <th>Model</th>
                    <th>Współczynnik sukcesu</th>
                    <th>Średni czas generowania</th>
                    <th>Średni czas wykonania</th>
                </tr>
    """
    
    for i, model in enumerate(model_names):
        html_content += f"""
                <tr>
                    <td>{model}</td>
                    <td>{success_rates[i]:.2f}%</td>
                    <td>{generation_times[i]:.2f}s</td>
                    <td>{execution_times[i]:.2f}s</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <h2>Wykresy porównawcze</h2>
        <h3>Współczynnik sukcesu</h3>
        <img src="model_comparison_success_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" alt="Porównanie współczynników sukcesu">
        
        <h3>Czasy</h3>
        <img src="model_comparison_times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" alt="Porównanie czasów">
    </body>
    </html>
    """
    
    with open(report_file, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Raport porównawczy zapisany do {report_file}")


def main():
    """Funkcja główna"""
    args = parse_arguments()
    
    # Sprawdź czy Ollama jest uruchomiona
    try:
        subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Ollama nie jest uruchomiona. Uruchom Ollama przed rozpoczęciem testów.")
        sys.exit(1)
    
    # Sprawdź czy matplotlib i pandas są zainstalowane
    try:
        import matplotlib
        import pandas
    except ImportError:
        logger.error("Brakujące zależności. Zainstaluj matplotlib i pandas:")
        logger.error("pip install matplotlib pandas")
        sys.exit(1)
    
    # Pobierz przypadki testowe
    test_cases = get_test_cases()
    
    # Filtruj przypadki testowe według kategorii
    if args.categories:
        logger.info(f"Filtrowanie testów do kategorii: {args.categories}")
        test_cases = filter_test_cases(test_cases, args.categories)
        if not test_cases:
            logger.error(f"Nie znaleziono testów dla podanych kategorii: {args.categories}")
            sys.exit(1)
    
    # Uruchom testy
    logger.info(f"Uruchamianie testów dla modelu {args.model}")
    tester = AssistantTester(model_name=args.model)
    tester.run_tests(test_cases)
    
    # Znajdź najnowszy plik wyników
    results_files = list(RESULTS_DIR.glob("results_*.json"))
    if not results_files:
        logger.error("Nie znaleziono plików z wynikami testów")
        sys.exit(1)
    
    latest_results_file = max(results_files, key=os.path.getctime)
    
    # Generuj szczegółowy raport
    if args.generate_report:
        logger.info("Generowanie szczegółowego raportu")
        generate_detailed_report(latest_results_file)
    
    # Porównaj z innymi modelami
    if args.compare_models:
        logger.info(f"Porównywanie z modelami: {args.compare_models}")
        
        model_results = []
        
        # Dodaj wyniki bieżącego modelu
        with open(latest_results_file, 'r') as f:
            model_results.append(json.load(f))
        
        # Znajdź wyniki dla innych modeli
        for model_name in args.compare_models:
            model_files = list(RESULTS_DIR.glob(f"results_*_{model_name.replace(':', '_')}.json"))
            if model_files:
                latest_model_file = max(model_files, key=os.path.getctime)
                with open(latest_model_file, 'r') as f:
                    model_results.append(json.load(f))
            else:
                logger.warning(f"Nie znaleziono wyników dla modelu {model_name}")
        
        if len(model_results) > 1:
            compare_models(model_results)
        else:
            logger.warning("Niewystarczająca liczba modeli do porównania")


if __name__ == "__main__":
    main()
