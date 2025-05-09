#!/usr/bin/env python3
"""
Architecture Analysis - Analiza architektury asystenta evopy

Ten moduł analizuje architekturę asystenta evopy i określa,
które podejście wykonuje złożone zadania najefektywniej.
"""

import os
import sys
import json
import time
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

# Dodaj katalog główny projektu do ścieżki importu
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modułów projektu
from modules.text2python.text2python import Text2Python
from docker_sandbox import DockerSandbox

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("architecture_analysis.log")
    ]
)
logger = logging.getLogger("evopy-architecture-analysis")

# Stałe
TEST_DIR = Path(__file__).parent
RESULTS_DIR = TEST_DIR / "results"
ANALYSIS_DIR = TEST_DIR / "analysis"

# Upewnij się, że katalogi istnieją
for directory in [RESULTS_DIR, ANALYSIS_DIR]:
    os.makedirs(directory, exist_ok=True)


class ArchitectureAnalyzer:
    """Klasa do analizy architektury asystenta evopy"""
    
    def __init__(self):
        """Inicjalizacja analizatora architektury"""
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "approaches": []
        }
    
    def analyze_approach(self, approach_name: str, test_cases: List[Dict[str, Any]], 
                         code_generator: Any, code_executor: Any):
        """
        Analizuje wydajność podejścia do wykonywania złożonych zadań
        
        Args:
            approach_name: Nazwa podejścia
            test_cases: Lista przypadków testowych
            code_generator: Funkcja generująca kod
            code_executor: Funkcja wykonująca kod
        """
        logger.info(f"Analizowanie podejścia: {approach_name}")
        
        approach_results = {
            "name": approach_name,
            "tests": []
        }
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"Test {i}/{len(test_cases)}: {test_case['name']}")
            
            test_result = self._run_test_case(test_case, code_generator, code_executor)
            approach_results["tests"].append(test_result)
            
            # Krótka przerwa między testami
            time.sleep(1)
        
        # Oblicz statystyki dla podejścia
        success_count = sum(1 for test in approach_results["tests"] if test["success"])
        total_count = len(approach_results["tests"])
        success_rate = success_count / total_count if total_count > 0 else 0
        
        approach_results["success_rate"] = success_rate
        approach_results["average_generation_time"] = sum(test["generation_time"] for test in approach_results["tests"]) / total_count if total_count > 0 else 0
        approach_results["average_execution_time"] = sum(test["execution_time"] for test in approach_results["tests"] if test["execution_success"]) / success_count if success_count > 0 else 0
        approach_results["average_total_time"] = sum(test["total_time"] for test in approach_results["tests"] if test["success"]) / success_count if success_count > 0 else 0
        
        self.results["approaches"].append(approach_results)
        
        logger.info(f"Podejście {approach_name} ukończone. Współczynnik sukcesu: {success_rate:.2%}")
    
    def _run_test_case(self, test_case: Dict[str, Any], code_generator: Any, 
                       code_executor: Any) -> Dict[str, Any]:
        """
        Uruchamia pojedynczy przypadek testowy dla danego podejścia
        
        Args:
            test_case: Przypadek testowy
            code_generator: Funkcja generująca kod
            code_executor: Funkcja wykonująca kod
            
        Returns:
            Dict: Wynik testu
        """
        prompt = test_case["prompt"]
        expected_output = test_case.get("expected_output", None)
        category = test_case.get("category", "Inne")
        
        # Inicjalizacja wyniku testu
        test_result = {
            "name": test_case["name"],
            "category": category,
            "success": False,
            "generation_success": False,
            "execution_success": False,
            "generation_time": 0,
            "execution_time": 0,
            "total_time": 0
        }
        
        try:
            # Pomiar czasu generowania kodu
            start_time = time.time()
            code_result = code_generator(prompt)
            generation_time = time.time() - start_time
            
            test_result["generation_time"] = generation_time
            test_result["generation_success"] = code_result.get("success", False)
            
            if test_result["generation_success"]:
                # Uruchomienie kodu
                start_time = time.time()
                execution_result = code_executor(code_result.get("code", ""))
                execution_time = time.time() - start_time
                
                test_result["execution_time"] = execution_time
                test_result["execution_success"] = execution_result.get("success", False)
                
                # Sprawdzenie oczekiwanego wyniku
                if expected_output is not None and test_result["execution_success"]:
                    output = execution_result.get("output", "")
                    test_result["success"] = self._check_output(output, expected_output)
                else:
                    test_result["success"] = test_result["execution_success"]
                
                test_result["total_time"] = generation_time + execution_time
            
        except Exception as e:
            logger.error(f"Błąd podczas testu {test_case['name']}: {e}")
            test_result["error"] = str(e)
        
        return test_result
    
    def _check_output(self, actual_output: str, expected_output: str) -> bool:
        """
        Sprawdza czy faktyczny wynik odpowiada oczekiwanemu
        
        Args:
            actual_output: Faktyczny wynik
            expected_output: Oczekiwany wynik
            
        Returns:
            bool: True jeśli wyniki są zgodne, False w przeciwnym razie
        """
        # Normalizacja wyników
        actual = actual_output.strip().lower()
        expected = expected_output.strip().lower()
        
        # Sprawdzenie dokładnej zgodności lub zawierania
        return actual == expected or expected in actual
    
    def save_results(self):
        """Zapisuje wyniki analizy do pliku JSON"""
        filename = ANALYSIS_DIR / f"architecture_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"Wyniki analizy zapisane do {filename}")
    
    def generate_report(self):
        """Generuje raport z analizy architektury"""
        if not self.results["approaches"]:
            logger.error("Brak wyników do wygenerowania raportu")
            return
        
        # Przygotuj dane do wykresów
        approach_names = [approach["name"] for approach in self.results["approaches"]]
        success_rates = [approach["success_rate"] * 100 for approach in self.results["approaches"]]
        generation_times = [approach["average_generation_time"] for approach in self.results["approaches"]]
        execution_times = [approach["average_execution_time"] for approach in self.results["approaches"]]
        total_times = [approach["average_total_time"] for approach in self.results["approaches"]]
        
        # Wykres współczynników sukcesu
        plt.figure(figsize=(10, 6))
        plt.bar(approach_names, success_rates, color='skyblue')
        plt.xlabel('Podejście')
        plt.ylabel('Współczynnik sukcesu (%)')
        plt.title('Porównanie współczynników sukcesu')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        chart_file = ANALYSIS_DIR / f"success_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file)
        
        # Wykres czasów
        plt.figure(figsize=(12, 6))
        
        x = range(len(approach_names))
        width = 0.25
        
        plt.bar([i - width for i in x], generation_times, width, label='Czas generowania', color='skyblue')
        plt.bar(x, execution_times, width, label='Czas wykonania', color='lightgreen')
        plt.bar([i + width for i in x], total_times, width, label='Całkowity czas', color='salmon')
        
        plt.xlabel('Podejście')
        plt.ylabel('Czas (s)')
        plt.title('Porównanie czasów')
        plt.xticks(x, approach_names, rotation=45, ha='right')
        plt.legend()
        plt.tight_layout()
        
        chart_file = ANALYSIS_DIR / f"times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file)
        
        # Generuj raport HTML
        self._generate_html_report(chart_file.parent)
    
    def _generate_html_report(self, charts_dir: Path):
        """
        Generuje raport HTML z analizy architektury
        
        Args:
            charts_dir: Katalog z wykresami
        """
        report_file = ANALYSIS_DIR / f"architecture_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Analiza architektury asystenta evopy</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2, h3 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .approach-summary {{ margin-bottom: 30px; }}
                img {{ max-width: 100%; height: auto; margin-bottom: 20px; }}
                .success {{ color: green; }}
                .failure {{ color: red; }}
            </style>
        </head>
        <body>
            <h1>Analiza architektury asystenta evopy</h1>
            <p>Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="summary">
                <h2>Podsumowanie</h2>
                <table>
                    <tr>
                        <th>Podejście</th>
                        <th>Współczynnik sukcesu</th>
                        <th>Czas generowania</th>
                        <th>Czas wykonania</th>
                        <th>Całkowity czas</th>
                    </tr>
        """
        
        for approach in self.results["approaches"]:
            html_content += f"""
                    <tr>
                        <td>{approach["name"]}</td>
                        <td>{approach["success_rate"]:.2%}</td>
                        <td>{approach["average_generation_time"]:.2f}s</td>
                        <td>{approach["average_execution_time"]:.2f}s</td>
                        <td>{approach["average_total_time"]:.2f}s</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <h2>Wykresy porównawcze</h2>
            <h3>Współczynnik sukcesu</h3>
            <img src="success_rates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" alt="Porównanie współczynników sukcesu">
            
            <h3>Czasy</h3>
            <img src="times_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png" alt="Porównanie czasów">
            
            <h2>Szczegółowe wyniki dla poszczególnych podejść</h2>
        """
        
        for approach in self.results["approaches"]:
            html_content += f"""
            <div class="approach-summary">
                <h3>{approach["name"]}</h3>
                <p>Współczynnik sukcesu: <strong>{approach["success_rate"]:.2%}</strong></p>
                <p>Średni czas generowania kodu: <strong>{approach["average_generation_time"]:.2f}s</strong></p>
                <p>Średni czas wykonania kodu: <strong>{approach["average_execution_time"]:.2f}s</strong></p>
                <p>Średni całkowity czas: <strong>{approach["average_total_time"]:.2f}s</strong></p>
                
                <h4>Wyniki testów</h4>
                <table>
                    <tr>
                        <th>Test</th>
                        <th>Kategoria</th>
                        <th>Status</th>
                        <th>Czas generowania</th>
                        <th>Czas wykonania</th>
                        <th>Całkowity czas</th>
                    </tr>
            """
            
            for test in approach["tests"]:
                status = "✅ Sukces" if test["success"] else "❌ Niepowodzenie"
                status_class = "success" if test["success"] else "failure"
                
                html_content += f"""
                    <tr>
                        <td>{test["name"]}</td>
                        <td>{test["category"]}</td>
                        <td class="{status_class}">{status}</td>
                        <td>{test["generation_time"]:.2f}s</td>
                        <td>{test["execution_time"]:.2f}s</td>
                        <td>{test["total_time"]:.2f}s</td>
                    </tr>
                """
            
            html_content += """
                </table>
            </div>
            """
        
        html_content += """
            <h2>Wnioski</h2>
            <p>Na podstawie przeprowadzonej analizy można wyciągnąć następujące wnioski:</p>
            <ul>
        """
        
        # Znajdź najlepsze podejście pod względem współczynnika sukcesu
        best_success_approach = max(self.results["approaches"], key=lambda x: x["success_rate"])
        
        # Znajdź najszybsze podejście pod względem całkowitego czasu
        best_time_approach = min(self.results["approaches"], key=lambda x: x["average_total_time"] if x["average_total_time"] > 0 else float('inf'))
        
        html_content += f"""
                <li>Najwyższy współczynnik sukcesu osiągnęło podejście <strong>{best_success_approach["name"]}</strong> z wynikiem {best_success_approach["success_rate"]:.2%}.</li>
                <li>Najkrótszy średni czas wykonania osiągnęło podejście <strong>{best_time_approach["name"]}</strong> z wynikiem {best_time_approach["average_total_time"]:.2f}s.</li>
        """
        
        # Dodaj dodatkowe wnioski
        if len(self.results["approaches"]) > 1:
            success_diff = best_success_approach["success_rate"] - min(approach["success_rate"] for approach in self.results["approaches"])
            time_diff = max(approach["average_total_time"] for approach in self.results["approaches"] if approach["average_total_time"] > 0) - best_time_approach["average_total_time"]
            
            html_content += f"""
                <li>Różnica między najlepszym a najgorszym podejściem pod względem współczynnika sukcesu wynosi {success_diff:.2%}.</li>
                <li>Różnica między najszybszym a najwolniejszym podejściem wynosi {time_diff:.2f}s.</li>
            """
        
        html_content += """
            </ul>
            
            <p>Rekomendowane podejście do implementacji asystenta evopy:</p>
        """
        
        # Rekomendacja
        if best_success_approach["name"] == best_time_approach["name"]:
            html_content += f"""
            <p>Podejście <strong>{best_success_approach["name"]}</strong> jest rekomendowane, ponieważ osiąga zarówno najwyższy współczynnik sukcesu, jak i najkrótszy czas wykonania.</p>
            """
        else:
            # Wybierz podejście z najlepszym kompromisem
            approaches = self.results["approaches"]
            best_compromise = max(approaches, key=lambda x: (x["success_rate"] / max(a["success_rate"] for a in approaches)) * 0.7 + 
                                                          (min(a["average_total_time"] for a in approaches if a["average_total_time"] > 0) / x["average_total_time"] if x["average_total_time"] > 0 else 0) * 0.3)
            
            html_content += f"""
            <p>Podejście <strong>{best_compromise["name"]}</strong> jest rekomendowane jako najlepszy kompromis między współczynnikiem sukcesu a czasem wykonania.</p>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Raport HTML zapisany do {report_file}")


def get_test_cases() -> List[Dict[str, Any]]:
    """
    Zwraca listę przypadków testowych do analizy architektury
    
    Returns:
        List[Dict[str, Any]]: Lista przypadków testowych
    """
    # Importuj przypadki testowe z innych modułów
    from test_complex_tasks import get_complex_test_cases
    
    # Wybierz podzbiór testów do analizy
    complex_tests = get_complex_test_cases()
    selected_tests = complex_tests[:5]  # Wybierz pierwsze 5 testów dla szybszej analizy
    
    return selected_tests


def create_direct_approach() -> Tuple[Any, Any]:
    """
    Tworzy funkcje do bezpośredniego podejścia (generowanie i wykonanie kodu w jednym kroku)
    
    Returns:
        Tuple[function, function]: Funkcje do generowania i wykonywania kodu
    """
    text2python = Text2Python(model_name="deepseek-coder:instruct-6.7b", code_dir=Path.home() / ".evo-assistant" / "code")
    docker_sandbox = DockerSandbox(base_dir=Path.home() / ".evo-assistant" / "sandbox", timeout=30)
    
    def generate_code(prompt: str) -> Dict[str, Any]:
        return text2python.generate_code(prompt)
    
    def execute_code(code: str) -> Dict[str, Any]:
        return docker_sandbox.run(code)
    
    return generate_code, execute_code


def create_iterative_approach() -> Tuple[Any, Any]:
    """
    Tworzy funkcje do iteracyjnego podejścia (generowanie kodu z poprawkami)
    
    Returns:
        Tuple[function, function]: Funkcje do generowania i wykonywania kodu
    """
    text2python = Text2Python(model_name="deepseek-coder:instruct-6.7b", code_dir=Path.home() / ".evo-assistant" / "code")
    docker_sandbox = DockerSandbox(base_dir=Path.home() / ".evo-assistant" / "sandbox", timeout=30)
    
    def generate_code(prompt: str) -> Dict[str, Any]:
        # Pierwszy etap - generowanie kodu
        result = text2python.generate_code(prompt)
        
        if not result["success"]:
            return result
        
        # Drugi etap - testowanie kodu
        code = result["code"]
        execution_result = docker_sandbox.run(code)
        
        # Jeśli wykonanie się nie powiodło, spróbuj poprawić kod
        if not execution_result["success"] and execution_result.get("error"):
            error_message = execution_result["error"]
            
            # Dodaj informację o błędzie do promptu
            correction_prompt = f"""
            Poprzednio wygenerowany kod zawiera błąd:
            {error_message}
            
            Popraw kod, aby rozwiązać ten problem.
            
            Oryginalne zadanie:
            {prompt}
            """
            
            # Wygeneruj poprawiony kod
            corrected_result = text2python.generate_code(correction_prompt)
            
            if corrected_result["success"]:
                return corrected_result
        
        return result
    
    def execute_code(code: str) -> Dict[str, Any]:
        return docker_sandbox.run(code)
    
    return generate_code, execute_code


def create_modular_approach() -> Tuple[Any, Any]:
    """
    Tworzy funkcje do modularnego podejścia (rozbicie zadania na mniejsze części)
    
    Returns:
        Tuple[function, function]: Funkcje do generowania i wykonywania kodu
    """
    text2python = Text2Python(model_name="deepseek-coder:instruct-6.7b", code_dir=Path.home() / ".evo-assistant" / "code")
    docker_sandbox = DockerSandbox(base_dir=Path.home() / ".evo-assistant" / "sandbox", timeout=30)
    
    def generate_code(prompt: str) -> Dict[str, Any]:
        # Etap 1: Analiza zadania i podział na moduły
        analysis_prompt = f"""
        Przeanalizuj następujące zadanie i podziel je na mniejsze, niezależne moduły:
        
        {prompt}
        
        Zwróć listę modułów w formacie:
        1. [nazwa_modułu]: [krótki opis]
        2. [nazwa_modułu]: [krótki opis]
        ...
        """
        
        analysis_result = text2python.generate_code(analysis_prompt)
        
        if not analysis_result["success"]:
            # Jeśli analiza się nie powiodła, wróć do standardowego podejścia
            return text2python.generate_code(prompt)
        
        # Etap 2: Generowanie kodu dla każdego modułu
        modules_code = []
        
        # Parsuj wynik analizy, aby wyodrębnić moduły
        # Uproszczona wersja - zakładamy, że wynik zawiera listę modułów
        analysis_lines = analysis_result["code"].strip().split("\n")
        modules = []
        
        for line in analysis_lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("- ")):
                modules.append(line)
        
        if not modules:
            # Jeśli nie udało się wyodrębnić modułów, wróć do standardowego podejścia
            return text2python.generate_code(prompt)
        
        # Generuj kod dla każdego modułu
        for i, module in enumerate(modules[:3]):  # Ogranicz do 3 modułów dla uproszczenia
            module_prompt = f"""
            Wygeneruj kod dla następującego modułu, który jest częścią większego zadania:
            
            {module}
            
            Kontekst zadania:
            {prompt}
            
            Zwróć tylko kod dla tego modułu, bez dodatkowych wyjaśnień.
            """
            
            module_result = text2python.generate_code(module_prompt)
            
            if module_result["success"]:
                modules_code.append(module_result["code"])
        
        if not modules_code:
            # Jeśli nie udało się wygenerować kodu dla żadnego modułu, wróć do standardowego podejścia
            return text2python.generate_code(prompt)
        
        # Etap 3: Integracja modułów
        integration_prompt = f"""
        Zintegruj następujące moduły w jeden spójny program:
        
        {chr(10).join([f"--- Moduł {i+1} ---{chr(10)}{code}" for i, code in enumerate(modules_code)])}
        
        Oryginalne zadanie:
        {prompt}
        
        Zwróć kompletny, zintegrowany kod.
        """
        
        return text2python.generate_code(integration_prompt)
    
    def execute_code(code: str) -> Dict[str, Any]:
        return docker_sandbox.run(code)
    
    return generate_code, execute_code


def main():
    """Funkcja główna"""
    # Sprawdź czy Ollama jest uruchomiona
    try:
        subprocess.run(["curl", "-s", "http://localhost:11434/api/tags"], 
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        logger.error("Ollama nie jest uruchomiona. Uruchom Ollama przed rozpoczęciem analizy.")
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
    
    # Utwórz analizator architektury
    analyzer = ArchitectureAnalyzer()
    
    # Analizuj różne podejścia
    # 1. Podejście bezpośrednie
    direct_generator, direct_executor = create_direct_approach()
    analyzer.analyze_approach("Podejście bezpośrednie", test_cases, direct_generator, direct_executor)
    
    # 2. Podejście iteracyjne
    iterative_generator, iterative_executor = create_iterative_approach()
    analyzer.analyze_approach("Podejście iteracyjne", test_cases, iterative_generator, iterative_executor)
    
    # 3. Podejście modularne
    modular_generator, modular_executor = create_modular_approach()
    analyzer.analyze_approach("Podejście modularne", test_cases, modular_generator, modular_executor)
    
    # Zapisz wyniki i wygeneruj raport
    analyzer.save_results()
    analyzer.generate_report()
    
    logger.info("Analiza architektury zakończona")


if __name__ == "__main__":
    main()
