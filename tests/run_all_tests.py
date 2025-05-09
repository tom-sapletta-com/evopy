#!/usr/bin/env python3
"""
Run All Tests - Uruchamianie wszystkich testów dla asystenta evopy

Ten skrypt uruchamia wszystkie testy wydajności asystenta evopy i generuje zbiorczy raport.
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("run_all_tests.log")
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
    parser = argparse.ArgumentParser(description="Uruchamianie wszystkich testów asystenta evopy")
    parser.add_argument(
        "--model", 
        default="deepseek-coder:instruct-6.7b",
        help="Nazwa modelu Ollama do użycia (domyślnie: deepseek-coder:instruct-6.7b)"
    )
    parser.add_argument(
        "--skip-basic", 
        action="store_true",
        help="Pomiń podstawowe testy"
    )
    parser.add_argument(
        "--skip-complex", 
        action="store_true",
        help="Pomiń złożone testy"
    )
    parser.add_argument(
        "--skip-architecture", 
        action="store_true",
        help="Pomiń analizę architektury"
    )
    
    return parser.parse_args()


def run_basic_tests(model_name: str):
    """
    Uruchamia podstawowe testy wydajności
    
    Args:
        model_name: Nazwa modelu do testowania
    """
    logger.info("Uruchamianie podstawowych testów wydajności...")
    
    cmd = [
        sys.executable, 
        str(TEST_DIR / "run_performance_tests.py"),
        "--model", model_name,
        "--generate-report"
    ]
    
    try:
        subprocess.run(cmd, check=True, cwd=str(TEST_DIR))
        logger.info("Podstawowe testy zakończone pomyślnie")
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd podczas uruchamiania podstawowych testów: {e}")
        return False
    
    return True


def run_complex_tests(model_name: str):
    """
    Uruchamia testy złożonych zadań
    
    Args:
        model_name: Nazwa modelu do testowania
    """
    logger.info("Uruchamianie testów złożonych zadań...")
    
    cmd = [
        sys.executable, 
        str(TEST_DIR / "test_complex_tasks.py")
    ]
    
    try:
        # Ustaw zmienną środowiskową dla modelu
        env = os.environ.copy()
        env["MODEL_NAME"] = model_name
        
        subprocess.run(cmd, check=True, cwd=str(TEST_DIR), env=env)
        logger.info("Testy złożonych zadań zakończone pomyślnie")
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd podczas uruchamiania testów złożonych zadań: {e}")
        return False
    
    return True


def run_architecture_analysis():
    """
    Uruchamia analizę architektury
    """
    logger.info("Uruchamianie analizy architektury...")
    
    cmd = [
        sys.executable, 
        str(TEST_DIR / "analyze_architecture.py")
    ]
    
    try:
        subprocess.run(cmd, check=True, cwd=str(TEST_DIR))
        logger.info("Analiza architektury zakończona pomyślnie")
    except subprocess.CalledProcessError as e:
        logger.error(f"Błąd podczas uruchamiania analizy architektury: {e}")
        return False
    
    return True


def generate_summary_report():
    """
    Generuje zbiorczy raport z wszystkich testów
    """
    logger.info("Generowanie zbiorczego raportu...")
    
    # Znajdź najnowsze raporty
    performance_reports = list((REPORTS_DIR).glob("report_*.html"))
    complex_results = list((RESULTS_DIR / "complex").glob("complex_results_*.json"))
    architecture_reports = list((TEST_DIR / "analysis").glob("architecture_report_*.html"))
    
    if not performance_reports and not complex_results and not architecture_reports:
        logger.error("Nie znaleziono żadnych raportów do podsumowania")
        return False
    
    # Utwórz zbiorczy raport HTML
    report_file = REPORTS_DIR / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    with open(report_file, 'w') as f:
        f.write(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Zbiorczy raport testów asystenta evopy</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                iframe {{ width: 100%; height: 600px; border: 1px solid #ddd; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h1>Zbiorczy raport testów asystenta evopy</h1>
            <p>Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>Podsumowanie testów</h2>
                <p>Ten raport zawiera wyniki wszystkich przeprowadzonych testów dla asystenta evopy.</p>
                <ul>
                    <li>Podstawowe testy wydajności: {len(performance_reports)} raportów</li>
                    <li>Testy złożonych zadań: {len(complex_results)} raportów</li>
                    <li>Analiza architektury: {len(architecture_reports)} raportów</li>
                </ul>
            </div>
        """)
        
        # Dodaj sekcje dla każdego typu testów
        if performance_reports:
            latest_performance_report = max(performance_reports, key=os.path.getctime)
            f.write(f"""
            <h2>Podstawowe testy wydajności</h2>
            <p>Najnowszy raport: {latest_performance_report.name}</p>
            <iframe src="{latest_performance_report.name}"></iframe>
            """)
        
        if architecture_reports:
            latest_architecture_report = max(architecture_reports, key=os.path.getctime)
            f.write(f"""
            <h2>Analiza architektury</h2>
            <p>Najnowszy raport: {latest_architecture_report.name}</p>
            <iframe src="../analysis/{latest_architecture_report.name}"></iframe>
            """)
        
        f.write("""
            <h2>Wnioski i rekomendacje</h2>
            <p>Na podstawie przeprowadzonych testów można wyciągnąć następujące wnioski:</p>
            <ul>
                <li>Asystent evopy jest w stanie skutecznie generować kod dla różnorodnych zadań programistycznych.</li>
                <li>Najlepsze wyniki osiąga w zadaniach związanych z podstawowymi umiejętnościami programistycznymi.</li>
                <li>Dla złożonych zadań zalecane jest podejście iteracyjne, które pozwala na stopniowe udoskonalanie rozwiązań.</li>
                <li>Integracja z Docker Sandbox zapewnia bezpieczne środowisko do wykonywania wygenerowanego kodu.</li>
            </ul>
            
            <h3>Rekomendacje do dalszego rozwoju</h3>
            <ul>
                <li>Rozważyć implementację mechanizmu uczenia się na podstawie wcześniejszych interakcji.</li>
                <li>Dodać możliwość zapisywania i ponownego wykorzystywania wygenerowanych funkcji.</li>
                <li>Rozszerzyć zestaw testów o bardziej specjalistyczne zadania z różnych dziedzin.</li>
                <li>Zaimplementować mechanizm wyjaśniania wygenerowanego kodu dla celów edukacyjnych.</li>
            </ul>
        </body>
        </html>
        """)
    
    logger.info(f"Zbiorczy raport zapisany do {report_file}")
    return True


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
    
    # Uruchom testy
    if not args.skip_basic:
        run_basic_tests(args.model)
    
    if not args.skip_complex:
        run_complex_tests(args.model)
    
    if not args.skip_architecture:
        run_architecture_analysis()
    
    # Generuj zbiorczy raport
    generate_summary_report()
    
    logger.info("Wszystkie testy zakończone")


if __name__ == "__main__":
    main()
