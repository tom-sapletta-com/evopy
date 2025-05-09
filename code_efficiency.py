#!/usr/bin/env python3
"""
Evopy Code Efficiency Analyzer
==============================
Ten moduł zawiera funkcje do analizy wydajności kodu generowanego przez modele LLM.
Funkcje te są wykorzystywane przez system raportowania Evopy do generowania
szczegółowych metryk wydajności kodu.

Główne funkcje:
- analyze_code_efficiency: Analiza ogólnej wydajności kodu
- estimate_time_complexity: Szacowanie złożoności czasowej
- estimate_space_complexity: Szacowanie złożoności pamięciowej
- analyze_resource_usage: Analiza wykorzystania zasobów
"""

import re
import ast
import time
import logging
import subprocess
from typing import Dict, Any, List, Tuple, Optional

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('evopy-code-efficiency')

def analyze_code_efficiency(code: str, execution_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analizuje wydajność wygenerowanego kodu.
    
    Args:
        code: Wygenerowany kod Python
        execution_result: Wynik wykonania kodu (opcjonalnie)
        
    Returns:
        Dict: Metryki wydajności kodu
    """
    metrics = {
        "time_complexity": "Unknown",
        "time_complexity_score": 0.0,
        "space_complexity": "Unknown",
        "space_complexity_score": 0.0,
        "code_size_efficiency": 0.0,
        "resource_usage_score": 0.0,
        "overall_efficiency_score": 0.0
    }
    
    # Sprawdź, czy kod nie jest pusty
    if not code or not code.strip():
        logger.warning("Otrzymano pusty kod do analizy")
        return metrics
    
    # Szacowanie złożoności czasowej i pamięciowej
    try:
        time_complexity, time_score = estimate_time_complexity(code)
        space_complexity, space_score = estimate_space_complexity(code)
        
        metrics["time_complexity"] = time_complexity
        metrics["time_complexity_score"] = time_score
        metrics["space_complexity"] = space_complexity
        metrics["space_complexity_score"] = space_score
    except Exception as e:
        logger.warning(f"Nie można oszacować złożoności: {e}")
    
    # Ocena efektywności rozmiaru kodu
    metrics["code_size_efficiency"] = analyze_code_size_efficiency(code)
    
    # Analiza wykorzystania zasobów
    if execution_result:
        metrics["resource_usage_score"] = analyze_resource_usage(execution_result)
    
    # Obliczenie ogólnej oceny wydajności
    available_metrics = []
    
    if metrics["time_complexity_score"] > 0:
        available_metrics.append(metrics["time_complexity_score"])
    
    if metrics["space_complexity_score"] > 0:
        available_metrics.append(metrics["space_complexity_score"])
    
    if metrics["code_size_efficiency"] > 0:
        available_metrics.append(metrics["code_size_efficiency"])
    
    if metrics["resource_usage_score"] > 0:
        available_metrics.append(metrics["resource_usage_score"])
    
    if available_metrics:
        metrics["overall_efficiency_score"] = sum(available_metrics) / len(available_metrics)
    
    return metrics

def estimate_time_complexity(code: str) -> Tuple[str, float]:
    """
    Szacuje złożoność czasową kodu.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        Tuple[str, float]: Złożoność czasowa (notacja O) i ocena (0-100)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Unknown", 50.0
    
    # Liczba zagnieżdżonych pętli
    max_loop_nesting = 0
    current_nesting = 0
    
    # Liczba operacji
    operations = 0
    
    # Przejdź przez drzewo AST
    for node in ast.walk(tree):
        # Sprawdź zagnieżdżone pętle
        if isinstance(node, (ast.For, ast.While)):
            current_nesting += 1
            max_loop_nesting = max(max_loop_nesting, current_nesting)
            
            # Po przetworzeniu pętli, zmniejsz poziom zagnieżdżenia
            current_nesting -= 1
        
        # Zlicz operacje
        if isinstance(node, (ast.BinOp, ast.UnaryOp, ast.Compare, ast.Call)):
            operations += 1
    
    # Określenie złożoności czasowej
    if max_loop_nesting == 0:
        complexity = "O(1)"  # Stała złożoność
        score = 100.0
    elif max_loop_nesting == 1:
        complexity = "O(n)"  # Liniowa złożoność
        score = 80.0
    elif max_loop_nesting == 2:
        complexity = "O(n²)"  # Kwadratowa złożoność
        score = 60.0
    elif max_loop_nesting == 3:
        complexity = "O(n³)"  # Sześcienna złożoność
        score = 40.0
    else:
        complexity = f"O(n^{max_loop_nesting})"  # Wielomianowa złożoność
        score = max(0, 100 - max_loop_nesting * 20)
    
    # Sprawdź specjalne przypadki
    if re.search(r'sort|sorted', code):
        # Jeśli kod używa sortowania, złożoność jest co najmniej O(n log n)
        if max_loop_nesting < 2:
            complexity = "O(n log n)"
            score = 70.0
    
    # Sprawdź rekurencję
    if has_recursion(tree):
        # Rekurencja może prowadzić do wykładniczej złożoności
        complexity = "O(2^n)"  # Zakładamy najgorszy przypadek
        score = 20.0
    
    return complexity, score

def estimate_space_complexity(code: str) -> Tuple[str, float]:
    """
    Szacuje złożoność pamięciową kodu.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        Tuple[str, float]: Złożoność pamięciowa (notacja O) i ocena (0-100)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "Unknown", 50.0
    
    # Liczba struktur danych
    data_structures = 0
    
    # Liczba zagnieżdżonych pętli z tworzeniem struktur danych
    max_data_nesting = 0
    current_nesting = 0
    
    # Przejdź przez drzewo AST
    for node in ast.walk(tree):
        # Sprawdź tworzenie struktur danych
        if isinstance(node, ast.List) or isinstance(node, ast.Dict) or isinstance(node, ast.Set):
            data_structures += 1
        
        # Sprawdź metody rozszerzające struktury danych
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in ['append', 'extend', 'insert', 'update']:
                data_structures += 1
        
        # Sprawdź zagnieżdżone pętle z tworzeniem struktur danych
        if isinstance(node, (ast.For, ast.While)):
            current_nesting += 1
            
            # Sprawdź, czy w pętli są tworzone struktury danych
            for child in ast.walk(node):
                if isinstance(child, (ast.List, ast.Dict, ast.Set)) or (
                    isinstance(child, ast.Call) and 
                    isinstance(child.func, ast.Attribute) and 
                    child.func.attr in ['append', 'extend', 'insert', 'update']
                ):
                    max_data_nesting = max(max_data_nesting, current_nesting)
                    break
            
            # Po przetworzeniu pętli, zmniejsz poziom zagnieżdżenia
            current_nesting -= 1
    
    # Określenie złożoności pamięciowej
    if data_structures == 0:
        complexity = "O(1)"  # Stała złożoność
        score = 100.0
    elif max_data_nesting == 0:
        complexity = "O(1)"  # Stała złożoność (brak tworzenia struktur w pętlach)
        score = 100.0
    elif max_data_nesting == 1:
        complexity = "O(n)"  # Liniowa złożoność
        score = 80.0
    elif max_data_nesting == 2:
        complexity = "O(n²)"  # Kwadratowa złożoność
        score = 60.0
    else:
        complexity = f"O(n^{max_data_nesting})"  # Wielomianowa złożoność
        score = max(0, 100 - max_data_nesting * 20)
    
    # Sprawdź rekurencję z tworzeniem struktur danych
    if has_recursion(tree) and data_structures > 0:
        complexity = "O(n)"  # Zakładamy liniową złożoność dla rekurencji
        score = 70.0
    
    return complexity, score

def has_recursion(tree: ast.AST) -> bool:
    """
    Sprawdza, czy kod zawiera rekurencję.
    
    Args:
        tree: Drzewo AST kodu
        
    Returns:
        bool: True, jeśli kod zawiera rekurencję, False w przeciwnym razie
    """
    # Znajdź wszystkie definicje funkcji
    function_defs = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            function_defs[node.name] = node
    
    # Sprawdź, czy funkcje wywołują same siebie
    for func_name, func_node in function_defs.items():
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == func_name:
                    return True
    
    return False

def analyze_code_size_efficiency(code: str) -> float:
    """
    Analizuje efektywność rozmiaru kodu.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Ocena efektywności rozmiaru kodu (0-100)
    """
    # Liczba linii kodu (bez pustych linii)
    lines = [line for line in code.split('\n') if line.strip()]
    line_count = len(lines)
    
    if line_count == 0:
        return 0.0
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 50.0  # Domyślna wartość w przypadku błędów składni
    
    # Liczba funkcjonalności (funkcje, klasy, importy, pętle, warunki)
    function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
    class_count = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
    import_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
    loop_count = len([node for node in ast.walk(tree) if isinstance(node, (ast.For, ast.While))])
    if_count = len([node for node in ast.walk(tree) if isinstance(node, ast.If)])
    
    # Większa waga dla funkcji i klas
    functionality_count = (function_count * 2) + (class_count * 3) + import_count + loop_count + if_count
    
    # Oblicz efektywność rozmiaru kodu (stosunek funkcjonalności do linii kodu)
    if functionality_count == 0:
        # Brak funkcjonalności, ale kod istnieje - niska efektywność
        return 30.0
    
    # Oblicz współczynnik efektywności
    efficiency_ratio = functionality_count / line_count
    
    # Konwersja współczynnika na ocenę (0-100)
    if efficiency_ratio < 0.1:
        # Bardzo niska efektywność (dużo kodu, mało funkcjonalności)
        score = efficiency_ratio * 300
    elif efficiency_ratio <= 0.5:
        # Normalna efektywność
        score = 30 + (efficiency_ratio - 0.1) * 100
    else:
        # Wysoka efektywność (dużo funkcjonalności w małej ilości kodu)
        score = 70 + (efficiency_ratio - 0.5) * 60
    
    # Ograniczenie wyniku do zakresu 0-100
    return min(100.0, max(0.0, score))

def analyze_resource_usage(execution_result: Dict[str, Any]) -> float:
    """
    Analizuje wykorzystanie zasobów na podstawie wyników wykonania kodu.
    
    Args:
        execution_result: Wynik wykonania kodu
        
    Returns:
        float: Ocena wykorzystania zasobów (0-100)
    """
    # Domyślna ocena
    score = 50.0
    
    # Sprawdź, czy mamy dane o czasie wykonania
    if "execution_time" in execution_result:
        execution_time = execution_result["execution_time"]
        
        # Ocena na podstawie czasu wykonania
        if execution_time < 0.1:
            time_score = 100.0  # Bardzo szybkie wykonanie
        elif execution_time < 1.0:
            time_score = 90.0 - (execution_time - 0.1) * 100  # 90-0 punktów
        else:
            time_score = max(0, 80 - (execution_time - 1.0) * 20)  # Nie mniej niż 0
        
        score = time_score
    
    # Sprawdź, czy mamy dane o wykorzystaniu pamięci
    if "memory_usage" in execution_result:
        memory_usage = execution_result["memory_usage"]
        
        # Konwersja na liczbę, jeśli to string
        if isinstance(memory_usage, str):
            try:
                # Usuń jednostki i konwertuj na liczbę
                memory_usage = float(re.search(r'[\d.]+', memory_usage).group())
            except (AttributeError, ValueError):
                memory_usage = 0
        
        # Ocena na podstawie wykorzystania pamięci (w MB)
        if memory_usage < 10:
            memory_score = 100.0  # Bardzo małe wykorzystanie pamięci
        elif memory_usage < 100:
            memory_score = 100.0 - (memory_usage - 10) * 0.5  # 100-55 punktów
        else:
            memory_score = max(0, 55 - (memory_usage - 100) * 0.1)  # Nie mniej niż 0
        
        # Średnia z ocen czasu i pamięci
        score = (score + memory_score) / 2
    
    # Sprawdź, czy mamy dane o wykorzystaniu CPU
    if "cpu_usage" in execution_result:
        cpu_usage = execution_result["cpu_usage"]
        
        # Konwersja na liczbę, jeśli to string
        if isinstance(cpu_usage, str):
            try:
                # Usuń procent i konwertuj na liczbę
                cpu_usage = float(re.search(r'[\d.]+', cpu_usage).group())
            except (AttributeError, ValueError):
                cpu_usage = 0
        
        # Ocena na podstawie wykorzystania CPU (w %)
        if cpu_usage < 10:
            cpu_score = 100.0  # Bardzo małe wykorzystanie CPU
        elif cpu_usage < 50:
            cpu_score = 100.0 - (cpu_usage - 10) * 1.25  # 100-50 punktów
        else:
            cpu_score = max(0, 50 - (cpu_usage - 50) * 1.0)  # Nie mniej niż 0
        
        # Średnia z poprzednich ocen i oceny CPU
        score = (score * 2 + cpu_score) / 3
    
    return score

def integrate_with_dependency_manager(code: str) -> Tuple[str, Dict[str, Any]]:
    """
    Integruje analizę wydajności z systemem autonaprawy zależności.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        Tuple[str, Dict[str, Any]]: Poprawiony kod i metryki wydajności
    """
    try:
        # Import modułu dependency_manager
        from dependency_manager import analyze_and_fix_imports
        
        # Analiza i naprawa importów
        fixed_code = analyze_and_fix_imports(code)
        
        # Analiza wydajności poprawionego kodu
        efficiency_metrics = analyze_code_efficiency(fixed_code)
        
        return fixed_code, efficiency_metrics
    except ImportError:
        logger.warning("Moduł dependency_manager nie jest dostępny. Używanie oryginalnego kodu.")
        efficiency_metrics = analyze_code_efficiency(code)
        return code, efficiency_metrics

if __name__ == "__main__":
    # Przykładowy kod do testowania
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
        
def calculate_fibonacci_sequence(length):
    result = []
    for i in range(length):
        result.append(fibonacci(i))
    return result
    
# Generuj sekwencję Fibonacciego o długości 10
sequence = calculate_fibonacci_sequence(10)
print(sequence)
"""
    
    # Testowanie funkcji
    efficiency_metrics = analyze_code_efficiency(sample_code)
    
    print("Metryki wydajności kodu:")
    for metric, value in efficiency_metrics.items():
        print(f"{metric}: {value}")
