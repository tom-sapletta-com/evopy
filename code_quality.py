#!/usr/bin/env python3
"""
Evopy Code Quality Analyzer
===========================
Ten moduł zawiera funkcje do analizy i oceny jakości kodu generowanego przez modele LLM.
Funkcje te są wykorzystywane przez system raportowania Evopy do generowania
szczegółowych metryk jakości kodu.

Główne funkcje:
- evaluate_code_quality: Ocena ogólnej jakości kodu
- evaluate_documentation: Ocena jakości dokumentacji i komentarzy
- evaluate_code_readability: Ocena czytelności kodu
- evaluate_explanation_clarity: Ocena jakości wyjaśnień
- calculate_maintainability_index: Obliczanie indeksu utrzymywalności kodu
"""

import re
import ast
import math
import logging
from typing import Dict, Any, List, Tuple, Optional

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('evopy-code-quality')

def evaluate_code_quality(code: str, explanation: Optional[str] = None) -> Dict[str, float]:
    """
    Ocenia ogólną jakość kodu i wyjaśnień.
    
    Args:
        code: Kod Python do analizy
        explanation: Opcjonalne wyjaśnienie kodu
        
    Returns:
        Dict: Słownik z metrykami jakości kodu
    """
    metrics = {
        "documentation_quality": 0.0,
        "code_readability": 0.0,
        "explanation_clarity": 0.0,
        "maintainability_index": 0.0,
        "overall_quality_score": 0.0
    }
    
    # Sprawdź, czy kod nie jest pusty
    if not code or not code.strip():
        logger.warning("Otrzymano pusty kod do analizy")
        return metrics
    
    # Ocena jakości dokumentacji
    metrics["documentation_quality"] = evaluate_documentation(code)
    
    # Ocena czytelności kodu
    metrics["code_readability"] = evaluate_code_readability(code)
    
    # Ocena jakości wyjaśnień (jeśli dostępne)
    if explanation:
        metrics["explanation_clarity"] = evaluate_explanation_clarity(explanation)
    
    # Obliczenie indeksu utrzymywalności
    metrics["maintainability_index"] = calculate_maintainability_index(code)
    
    # Obliczenie ogólnej oceny jakości (średnia ważona)
    available_metrics = []
    weights = []
    
    if metrics["documentation_quality"] > 0:
        available_metrics.append(metrics["documentation_quality"])
        weights.append(0.25)  # 25% wagi
        
    if metrics["code_readability"] > 0:
        available_metrics.append(metrics["code_readability"])
        weights.append(0.35)  # 35% wagi
        
    if metrics["explanation_clarity"] > 0:
        available_metrics.append(metrics["explanation_clarity"])
        weights.append(0.20)  # 20% wagi
        
    if metrics["maintainability_index"] > 0:
        available_metrics.append(metrics["maintainability_index"])
        weights.append(0.20)  # 20% wagi
    
    if available_metrics:
        # Obliczenie średniej ważonej
        metrics["overall_quality_score"] = sum(m * w for m, w in zip(available_metrics, weights)) / sum(weights)
    
    return metrics

def evaluate_documentation(code: str) -> float:
    """
    Ocenia jakość dokumentacji i komentarzy w kodzie.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Ocena jakości dokumentacji (0-100)
    """
    try:
        # Liczba linii kodu
        code_lines = code.count('\n') + 1
        if code_lines <= 0:
            return 0.0
        
        # Liczba linii z komentarzami lub docstringami
        doc_lines = 0
        docstring_blocks = 0
        in_docstring = False
        
        for line in code.split('\n'):
            line = line.strip()
            
            # Sprawdź docstringi
            if '"""' in line or "'''" in line:
                if line.count('"""') % 2 == 1 or line.count("'''") % 2 == 1:
                    in_docstring = not in_docstring
                    if in_docstring:
                        docstring_blocks += 1
                doc_lines += 1
            # Linie w bloku docstring
            elif in_docstring:
                doc_lines += 1
            # Komentarze jednoliniowe
            elif line.startswith('#'):
                doc_lines += 1
            # Komentarze na końcu linii
            elif '#' in line and not line.startswith('print'):  # Ignoruj '#' w stringach print
                doc_lines += 1
        
        # Sprawdź jakość docstringów dla funkcji i klas
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.ClassDef))]
            functions_with_docstring = 0
            
            for func in functions:
                if ast.get_docstring(func):
                    functions_with_docstring += 1
            
            func_doc_ratio = functions_with_docstring / max(1, len(functions)) if functions else 0
        except SyntaxError:
            func_doc_ratio = 0
        
        # Oblicz wskaźnik dokumentacji
        # 1. Stosunek linii dokumentacji do linii kodu (optymalnie 15-30%)
        doc_ratio = doc_lines / code_lines
        if doc_ratio < 0.05:  # Zbyt mało dokumentacji
            doc_ratio_score = doc_ratio * 1000  # 0-50 punktów
        elif doc_ratio <= 0.3:  # Optymalna ilość dokumentacji
            doc_ratio_score = 50 + (doc_ratio - 0.05) * 200  # 50-100 punktów
        else:  # Zbyt dużo dokumentacji
            doc_ratio_score = 100 - (doc_ratio - 0.3) * 100  # 100-0 punktów
            doc_ratio_score = max(50, doc_ratio_score)  # Nie mniej niż 50
        
        # 2. Jakość dokumentacji funkcji
        func_doc_score = func_doc_ratio * 100
        
        # 3. Obecność bloków docstring
        docstring_score = min(100, docstring_blocks * 25)
        
        # Oblicz końcową ocenę (średnia ważona)
        final_score = (
            doc_ratio_score * 0.4 +
            func_doc_score * 0.4 +
            docstring_score * 0.2
        )
        
        return final_score
    
    except Exception as e:
        logger.error(f"Błąd podczas oceny dokumentacji: {e}")
        return 0.0

def evaluate_code_readability(code: str) -> float:
    """
    Ocenia czytelność kodu na podstawie różnych metryk.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Ocena czytelności kodu (0-100)
    """
    try:
        # Sprawdź, czy kod nie jest pusty
        if not code or not code.strip():
            return 0.0
        
        # 1. Średnia długość linii (optymalna to 40-60 znaków)
        lines = [line for line in code.split('\n') if line.strip()]
        if not lines:
            return 0.0
            
        avg_line_length = sum(len(line) for line in lines) / len(lines)
        
        if avg_line_length < 20:  # Zbyt krótkie linie
            line_length_score = avg_line_length * 2.5  # 0-50 punktów
        elif avg_line_length <= 60:  # Optymalna długość
            line_length_score = 50 + (1 - abs(avg_line_length - 40) / 20) * 50  # 50-100 punktów
        else:  # Zbyt długie linie
            line_length_score = max(0, 100 - (avg_line_length - 60) * 2)  # 100-0 punktów
        
        # 2. Spójność wcięć
        indent_consistency = analyze_indentation_consistency(lines)
        indent_score = indent_consistency * 100
        
        # 3. Jakość nazewnictwa zmiennych
        naming_score = analyze_variable_naming(code)
        
        # 4. Złożoność kodu
        try:
            complexity_score = analyze_code_complexity(code)
        except SyntaxError:
            complexity_score = 50  # Domyślna wartość w przypadku błędów składni
        
        # Oblicz końcową ocenę (średnia ważona)
        final_score = (
            line_length_score * 0.25 +
            indent_score * 0.25 +
            naming_score * 0.25 +
            complexity_score * 0.25
        )
        
        return final_score
    
    except Exception as e:
        logger.error(f"Błąd podczas oceny czytelności kodu: {e}")
        return 0.0

def analyze_indentation_consistency(lines: List[str]) -> float:
    """
    Analizuje spójność wcięć w kodzie.
    
    Args:
        lines: Lista linii kodu
        
    Returns:
        float: Współczynnik spójności wcięć (0-1)
    """
    if not lines:
        return 0.0
    
    indent_sizes = []
    prev_indent = 0
    inconsistencies = 0
    
    for line in lines:
        if not line.strip():
            continue
            
        # Oblicz rozmiar wcięcia
        indent = len(line) - len(line.lstrip())
        
        if indent > prev_indent:
            # Nowy poziom wcięcia
            indent_diff = indent - prev_indent
            if indent_diff not in indent_sizes:
                indent_sizes.append(indent_diff)
            
            # Sprawdź, czy wcięcie jest spójne z poprzednimi
            if len(indent_sizes) > 1 and indent_diff != indent_sizes[0]:
                inconsistencies += 1
        
        prev_indent = indent
    
    # Oblicz współczynnik spójności
    if not indent_sizes:
        return 1.0  # Brak wcięć, uznajemy za spójne
    
    consistency = 1.0 - (inconsistencies / len(lines))
    return max(0.0, consistency)

def analyze_variable_naming(code: str) -> float:
    """
    Analizuje jakość nazewnictwa zmiennych w kodzie.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Ocena jakości nazewnictwa (0-100)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 50.0  # Domyślna wartość w przypadku błędów składni
    
    # Zbierz wszystkie nazwy zmiennych, funkcji i klas
    variable_names = []
    function_names = []
    class_names = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            variable_names.append(node.id)
        elif isinstance(node, ast.FunctionDef):
            function_names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            class_names.append(node.name)
    
    # Sprawdź konwencje nazewnictwa
    snake_case_vars = sum(1 for name in variable_names if re.match(r'^[a-z][a-z0-9_]*$', name))
    camel_case_classes = sum(1 for name in class_names if re.match(r'^[A-Z][a-zA-Z0-9]*$', name))
    snake_case_funcs = sum(1 for name in function_names if re.match(r'^[a-z][a-z0-9_]*$', name))
    
    # Oblicz oceny dla każdej kategorii
    var_score = (snake_case_vars / max(1, len(variable_names))) * 100 if variable_names else 100
    class_score = (camel_case_classes / max(1, len(class_names))) * 100 if class_names else 100
    func_score = (snake_case_funcs / max(1, len(function_names))) * 100 if function_names else 100
    
    # Sprawdź długość nazw (zbyt krótkie lub zbyt długie są nieczytelne)
    all_names = variable_names + function_names + class_names
    if not all_names:
        return 80.0  # Domyślna wartość, jeśli nie ma nazw
    
    too_short = sum(1 for name in all_names if len(name) < 2)
    too_long = sum(1 for name in all_names if len(name) > 30)
    length_penalty = (too_short + too_long) / len(all_names)
    
    # Oblicz końcową ocenę (średnia ważona)
    final_score = (
        var_score * 0.4 +
        class_score * 0.3 +
        func_score * 0.3
    ) * (1 - length_penalty)
    
    return final_score

def analyze_code_complexity(code: str) -> float:
    """
    Analizuje złożoność kodu.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Ocena złożoności kodu (0-100, gdzie wyższa wartość oznacza mniejszą złożoność)
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 50.0  # Domyślna wartość w przypadku błędów składni
    
    # Liczba zagnieżdżonych bloków
    max_nesting = 0
    current_nesting = 0
    
    # Liczba warunków i pętli
    conditions = 0
    loops = 0
    
    # Przejdź przez drzewo AST
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
            current_nesting += 1
            max_nesting = max(max_nesting, current_nesting)
            
            if isinstance(node, (ast.If)):
                conditions += 1
            elif isinstance(node, (ast.For, ast.While)):
                loops += 1
                
            # Zmniejsz poziom zagnieżdżenia po wyjściu z bloku
            current_nesting -= 1
    
    # Oblicz złożoność cyklomatyczną (uproszczona)
    cyclomatic_complexity = 1 + conditions + loops
    
    # Oblicz ocenę złożoności
    # 1. Na podstawie maksymalnego zagnieżdżenia
    if max_nesting <= 2:
        nesting_score = 100  # Optymalne zagnieżdżenie
    elif max_nesting <= 4:
        nesting_score = 100 - (max_nesting - 2) * 20  # 100-60 punktów
    else:
        nesting_score = max(0, 60 - (max_nesting - 4) * 15)  # 60-0 punktów
    
    # 2. Na podstawie złożoności cyklomatycznej
    if cyclomatic_complexity <= 5:
        cc_score = 100  # Niska złożoność
    elif cyclomatic_complexity <= 10:
        cc_score = 100 - (cyclomatic_complexity - 5) * 10  # 100-50 punktów
    else:
        cc_score = max(0, 50 - (cyclomatic_complexity - 10) * 5)  # 50-0 punktów
    
    # Oblicz końcową ocenę
    final_score = (nesting_score * 0.5 + cc_score * 0.5)
    
    return final_score

def evaluate_explanation_clarity(explanation: str) -> float:
    """
    Ocenia jakość i klarowność wyjaśnienia kodu.
    
    Args:
        explanation: Tekstowe wyjaśnienie kodu
        
    Returns:
        float: Ocena jakości wyjaśnienia (0-100)
    """
    if not explanation or not explanation.strip():
        return 0.0
    
    # 1. Długość wyjaśnienia
    words = explanation.split()
    word_count = len(words)
    
    if word_count < 50:
        length_score = word_count / 50 * 100  # 0-100 punktów dla 0-50 słów
    elif word_count <= 300:
        length_score = 100  # Optymalna długość
    else:
        length_score = max(50, 100 - (word_count - 300) / 10)  # Nie mniej niż 50
    
    # 2. Struktura zdań
    sentences = re.split(r'[.!?]+', explanation)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return length_score * 0.5  # Jeśli brak zdań, oceniamy tylko długość
    
    # Średnia długość zdania (optymalna to 15-20 słów)
    avg_sentence_length = word_count / len(sentences)
    
    if avg_sentence_length < 5:
        sentence_score = avg_sentence_length / 5 * 50  # 0-50 punktów dla bardzo krótkich zdań
    elif avg_sentence_length <= 20:
        sentence_score = 50 + (1 - abs(avg_sentence_length - 15) / 10) * 50  # 50-100 punktów
    else:
        sentence_score = max(50, 100 - (avg_sentence_length - 20) * 2.5)  # Nie mniej niż 50
    
    # 3. Obecność kluczowych elementów wyjaśnienia
    key_elements = [
        r'\bfunkcj[aei]\b',          # Funkcja, funkcje
        r'\bparametr[y]?\b',         # Parametr, parametry
        r'\bzwrac[a]\b',             # Zwraca
        r'\bwynik\b',                # Wynik
        r'\bcel\b',                  # Cel
        r'\bprzyk[łl]ad\b',          # Przykład
        r'\bwyja[śs]ni[eę]\b',       # Wyjaśnienie
        r'\bkrok\b',                 # Krok (np. "krok po kroku")
        r'\bprzeprowadz[a]\b',       # Przeprowadza
        r'\bobliczy[ćc]?\b'          # Obliczyć, oblicza
    ]
    
    key_elements_count = sum(1 for pattern in key_elements if re.search(pattern, explanation.lower()))
    key_elements_score = min(100, key_elements_count * 10)
    
    # 4. Czytelność (na podstawie indeksu Flesch-Kincaid)
    # Uproszczona implementacja dla języka polskiego
    syllables = estimate_syllables(explanation)
    readability_score = 206.835 - 1.015 * (word_count / len(sentences)) - 84.6 * (syllables / word_count)
    readability_score = max(0, min(100, readability_score))
    
    # Oblicz końcową ocenę (średnia ważona)
    final_score = (
        length_score * 0.2 +
        sentence_score * 0.3 +
        key_elements_score * 0.3 +
        readability_score * 0.2
    )
    
    return final_score

def estimate_syllables(text: str) -> int:
    """
    Szacuje liczbę sylab w tekście (uproszczona implementacja dla języka polskiego).
    
    Args:
        text: Tekst do analizy
        
    Returns:
        int: Szacowana liczba sylab
    """
    # Usuwamy znaki interpunkcyjne i dzielimy na słowa
    words = re.sub(r'[^\w\s]', '', text.lower()).split()
    
    # Liczymy samogłoski jako przybliżenie liczby sylab
    vowels = 'aeiouyąęóąęćńóśźż'
    syllable_count = 0
    
    for word in words:
        # Liczymy samogłoski w słowie
        count = sum(1 for char in word if char in vowels)
        
        # Korekta dla dyftongu (np. "ia", "ie", "io", "iu")
        for pattern in ['ia', 'ie', 'io', 'iu', 'ią', 'ię', 'ió']:
            count -= word.count(pattern)
        
        # Każde słowo ma co najmniej jedną sylabę
        syllable_count += max(1, count)
    
    return syllable_count

def calculate_maintainability_index(code: str) -> float:
    """
    Oblicza indeks utrzymywalności kodu (Maintainability Index).
    
    Indeks utrzymywalności jest miarą łatwości utrzymania kodu.
    Wartość 100 oznacza doskonałą utrzymywalność, a 0 - bardzo trudną.
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        float: Indeks utrzymywalności (0-100)
    """
    try:
        # Sprawdź, czy kod nie jest pusty
        if not code or not code.strip():
            return 0.0
        
        # Liczba linii kodu (bez pustych linii)
        lines = [line for line in code.split('\n') if line.strip()]
        loc = len(lines)
        
        if loc == 0:
            return 0.0
        
        # Objętość Halsteada (uproszczona)
        operators, operands = count_operators_and_operands(code)
        n1 = len(operators)
        n2 = len(operands)
        N1 = sum(operators.values())
        N2 = sum(operands.values())
        
        # Zabezpieczenie przed zerowymi wartościami
        if n1 == 0 or n2 == 0 or N1 == 0 or N2 == 0:
            halstead_volume = 0
        else:
            vocabulary = n1 + n2
            length = N1 + N2
            halstead_volume = length * math.log2(vocabulary) if vocabulary > 0 else 0
        
        # Złożoność cyklomatyczna (uproszczona)
        try:
            tree = ast.parse(code)
            cyclomatic_complexity = 1  # Bazowa wartość
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                    cyclomatic_complexity += 1
        except SyntaxError:
            cyclomatic_complexity = 1
        
        # Obliczenie indeksu utrzymywalności
        if halstead_volume > 0:
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * cyclomatic_complexity - 16.2 * math.log(loc)
            # Normalizacja do zakresu 0-100
            mi = max(0, min(100, mi * 100 / 171))
        else:
            # Uproszczona formuła, gdy brak danych Halsteada
            mi = 100 - (cyclomatic_complexity * 10 / loc) * 20 - math.log(loc) * 15
            mi = max(0, min(100, mi))
        
        return mi
    
    except Exception as e:
        logger.error(f"Błąd podczas obliczania indeksu utrzymywalności: {e}")
        return 50.0  # Domyślna wartość w przypadku błędu

def count_operators_and_operands(code: str) -> Tuple[Dict[str, int], Dict[str, int]]:
    """
    Liczy operatory i operandy w kodzie (uproszczona implementacja).
    
    Args:
        code: Kod Python do analizy
        
    Returns:
        Tuple[Dict[str, int], Dict[str, int]]: Słowniki z liczbą wystąpień operatorów i operandów
    """
    # Uproszczona lista operatorów w Pythonie
    python_operators = [
        '+', '-', '*', '/', '//', '%', '**',
        '==', '!=', '>', '<', '>=', '<=',
        'and', 'or', 'not', 'is', 'in',
        '=', '+=', '-=', '*=', '/=', '//=', '%=', '**=',
        '&', '|', '^', '~', '<<', '>>'
    ]
    
    # Inicjalizacja słowników
    operators = {op: 0 for op in python_operators}
    operands = {}
    
    try:
        # Parsowanie kodu
        tree = ast.parse(code)
        
        # Przejście przez drzewo AST
        for node in ast.walk(tree):
            # Operatory
            if isinstance(node, ast.BinOp):
                op_type = type(node.op).__name__
                if op_type in operators:
                    operators[op_type] += 1
            elif isinstance(node, ast.UnaryOp):
                op_type = type(node.op).__name__
                if op_type in operators:
                    operators[op_type] += 1
            elif isinstance(node, ast.Compare):
                for op in node.ops:
                    op_type = type(op).__name__
                    if op_type in operators:
                        operators[op_type] += 1
            
            # Operandy (zmienne, literały)
            if isinstance(node, ast.Name):
                name = node.id
                operands[name] = operands.get(name, 0) + 1
            elif isinstance(node, ast.Num):
                num = str(node.n)
                operands[num] = operands.get(num, 0) + 1
            elif isinstance(node, ast.Str):
                # Używamy skróconej reprezentacji dla długich stringów
                str_repr = f"str_{len(node.s)}"
                operands[str_repr] = operands.get(str_repr, 0) + 1
    
    except SyntaxError:
        # W przypadku błędów składni, używamy prostszej metody
        for op in python_operators:
            operators[op] = code.count(op)
        
        # Przybliżone liczenie operandów (słowa, które nie są operatorami)
        words = re.findall(r'\b\w+\b', code)
        for word in words:
            if word not in python_operators and not word.isdigit():
                operands[word] = operands.get(word, 0) + 1
    
    return operators, operands

if __name__ == "__main__":
    # Przykładowy kod do testowania
    sample_code = """
def calculate_average(numbers):
    \"\"\"
    Oblicza średnią arytmetyczną listy liczb.
    
    Args:
        numbers: Lista liczb
        
    Returns:
        float: Średnia arytmetyczna
    \"\"\"
    if not numbers:
        return 0
    
    total = sum(numbers)
    count = len(numbers)
    
    # Oblicz średnią
    average = total / count
    
    return average
"""
    
    # Przykładowe wyjaśnienie
    sample_explanation = """
Ta funkcja oblicza średnią arytmetyczną listy liczb. Przyjmuje jeden parametr 'numbers', który powinien być listą liczb.
Najpierw sprawdza, czy lista nie jest pusta - jeśli jest, zwraca 0.
Następnie oblicza sumę wszystkich liczb w liście za pomocą funkcji sum() i liczbę elementów za pomocą len().
Na końcu dzieli sumę przez liczbę elementów, aby uzyskać średnią, i zwraca wynik.
"""
    
    # Testowanie funkcji
    quality_metrics = evaluate_code_quality(sample_code, sample_explanation)
    
    print("Metryki jakości kodu:")
    for metric, value in quality_metrics.items():
        print(f"{metric}: {value:.2f}")
