#!/usr/bin/env python3
"""
Narzędzia do ulepszenia interfejsu konsolowego Evopy

Ten moduł zawiera funkcje i klasy do poprawy doświadczenia użytkownika
w interfejsie konsolowym, w tym kolorowanie składni, autouzupełnianie
i formatowanie wyników.
"""

import os
import re
import sys
import json
import shutil
from typing import List, Dict, Any, Optional, Tuple

# Spróbuj zaimportować opcjonalne moduły
try:
    import pygments
    from pygments import highlight
    from pygments.lexers import PythonLexer, get_lexer_by_name
    from pygments.formatters import TerminalFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    READLINE_AVAILABLE = False

# Klasa kolorów (skopiowana z evo.py dla spójności)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class CodeHighlighter:
    """Klasa do kolorowania składni kodu"""
    
    def __init__(self):
        """Inicjalizacja kolorowacza kodu"""
        self.pygments_available = PYGMENTS_AVAILABLE
        
        # Sprawdź, czy terminal obsługuje kolory
        self.color_supported = sys.stdout.isatty() and os.name != 'nt'
    
    def highlight_python(self, code: str) -> str:
        """
        Koloruje składnię kodu Python
        
        Args:
            code: Kod Python do kolorowania
            
        Returns:
            str: Kolorowy kod lub oryginalny kod, jeśli kolorowanie nie jest dostępne
        """
        if not self.pygments_available or not self.color_supported:
            return code
        
        try:
            return highlight(code, PythonLexer(), TerminalFormatter())
        except Exception:
            return code
    
    def highlight_code(self, code: str, language: str = 'python') -> str:
        """
        Koloruje składnię kodu w podanym języku
        
        Args:
            code: Kod do kolorowania
            language: Język programowania (domyślnie python)
            
        Returns:
            str: Kolorowy kod lub oryginalny kod, jeśli kolorowanie nie jest dostępne
        """
        if not self.pygments_available or not self.color_supported:
            return code
        
        try:
            lexer = get_lexer_by_name(language)
            return highlight(code, lexer, TerminalFormatter())
        except Exception:
            return code
    
    def format_output(self, output: str) -> str:
        """
        Formatuje wyjście z wykonania kodu
        
        Args:
            output: Wyjście z wykonania kodu
            
        Returns:
            str: Sformatowane wyjście
        """
        # Próba wykrycia kodu w wyjściu
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', output, re.DOTALL)
        
        if not code_blocks:
            return output
        
        # Zamień bloki kodu na kolorowe
        formatted_output = output
        for lang, code in code_blocks:
            language = lang.strip() if lang.strip() else 'python'
            highlighted_code = self.highlight_code(code, language)
            formatted_output = formatted_output.replace(
                f'```{lang}\n{code}```',
                highlighted_code
            )
        
        return formatted_output

class CommandCompleter:
    """Klasa do autouzupełniania komend"""
    
    def __init__(self, commands: List[str]):
        """
        Inicjalizacja uzupełniacza komend
        
        Args:
            commands: Lista dostępnych komend
        """
        self.commands = commands
        
        # Inicjalizacja readline, jeśli dostępne
        if READLINE_AVAILABLE:
            readline.set_completer(self.complete)
            readline.parse_and_bind("tab: complete")
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """
        Funkcja uzupełniania dla readline
        
        Args:
            text: Tekst do uzupełnienia
            state: Indeks dopasowania
            
        Returns:
            Optional[str]: Uzupełniona komenda lub None
        """
        if not READLINE_AVAILABLE:
            return None
        
        # Uzupełnianie komend zaczynających się od /
        if text.startswith('/'):
            matches = [cmd for cmd in self.commands if cmd.startswith(text)]
            if state < len(matches):
                return matches[state]
        
        return None

class ResultFormatter:
    """Klasa do formatowania wyników wykonania kodu"""
    
    def __init__(self):
        """Inicjalizacja formatera wyników"""
        self.highlighter = CodeHighlighter()
        
        # Określ szerokość terminala
        self.terminal_width = shutil.get_terminal_size().columns
    
    def format_execution_result(self, result: Dict[str, Any]) -> str:
        """
        Formatuje wynik wykonania kodu
        
        Args:
            result: Wynik wykonania kodu
            
        Returns:
            str: Sformatowany wynik
        """
        if not result:
            return f"{Colors.RED}Brak wyników wykonania.{Colors.END}"
        
        success = result.get("success", False)
        output = result.get("output", "")
        error = result.get("error", "")
        execution_time = result.get("execution_time", 0)
        
        # Formatowanie nagłówka
        header = f"{Colors.GREEN}✓ Kod wykonany pomyślnie{Colors.END}" if success else f"{Colors.RED}✗ Błąd wykonania kodu{Colors.END}"
        
        # Formatowanie czasu wykonania
        time_str = f"{Colors.BLUE}Czas wykonania: {execution_time:.2f}s{Colors.END}"
        
        # Formatowanie wyjścia
        formatted_output = ""
        if output:
            # Ogranicz długość wyjścia, jeśli jest bardzo długie
            if len(output) > 1000:
                output_preview = output[:1000] + "...\n[Wyjście zostało skrócone. Pełne wyjście zapisano w pliku output.txt]"
                # Zapisz pełne wyjście do pliku
                with open("output.txt", "w") as f:
                    f.write(output)
                output = output_preview
            
            formatted_output = f"\n{Colors.CYAN}Wyjście:{Colors.END}\n{output}"
        
        # Formatowanie błędu
        formatted_error = ""
        if error and not success:
            formatted_error = f"\n{Colors.RED}Błąd:{Colors.END}\n{error}"
        
        # Połącz wszystkie elementy
        separator = "-" * min(80, self.terminal_width)
        result_str = f"{header}\n{time_str}\n{separator}{formatted_output}{formatted_error}"
        
        return result_str
    
    def format_code(self, code: str) -> str:
        """
        Formatuje kod Python
        
        Args:
            code: Kod Python
            
        Returns:
            str: Sformatowany kod
        """
        return self.highlighter.highlight_python(code)
    
    def format_json(self, json_data: Dict[str, Any]) -> str:
        """
        Formatuje dane JSON
        
        Args:
            json_data: Dane JSON
            
        Returns:
            str: Sformatowany JSON
        """
        try:
            json_str = json.dumps(json_data, indent=2)
            return self.highlighter.highlight_code(json_str, 'json')
        except Exception:
            return str(json_data)

# Lista dostępnych komend dla autouzupełniania
DEFAULT_COMMANDS = [
    "/help", "/exit", "/quit", "/new", "/list", "/load", "/title", 
    "/clear", "/model", "/skills", "/projects", "/docker", "/save",
    "/status", "/history", "/export", "/import", "/monitor", "/config"
]

# Funkcje pomocnicze

def print_header(title: str):
    """
    Wyświetla nagłówek z tytułem
    
    Args:
        title: Tytuł nagłówka
    """
    terminal_width = shutil.get_terminal_size().columns
    padding = max(0, terminal_width - len(title) - 4)
    left_padding = padding // 2
    right_padding = padding - left_padding
    
    print(f"{Colors.HEADER}{'=' * left_padding} {title} {'=' * right_padding}{Colors.END}")

def print_table(headers: List[str], rows: List[List[str]]):
    """
    Wyświetla dane w formie tabeli
    
    Args:
        headers: Nagłówki kolumn
        rows: Wiersze danych
    """
    if not headers or not rows:
        return
    
    # Oblicz szerokość każdej kolumny
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Wyświetl nagłówki
    header_row = " | ".join(f"{h:{w}s}" for h, w in zip(headers, col_widths))
    print(f"{Colors.BOLD}{header_row}{Colors.END}")
    
    # Wyświetl separator
    separator = "-+-".join("-" * w for w in col_widths)
    print(separator)
    
    # Wyświetl wiersze
    for row in rows:
        row_str = " | ".join(f"{str(c):{w}s}" for c, w in zip(row, col_widths))
        print(row_str)

def create_progress_bar(progress: float, width: int = 40) -> str:
    """
    Tworzy pasek postępu
    
    Args:
        progress: Postęp (0.0 - 1.0)
        width: Szerokość paska
        
    Returns:
        str: Pasek postępu
    """
    filled_width = int(width * progress)
    bar = '█' * filled_width + '░' * (width - filled_width)
    return f"[{bar}] {progress*100:.1f}%"

# Inicjalizacja globalnych obiektów
highlighter = CodeHighlighter()
completer = CommandCompleter(DEFAULT_COMMANDS)
formatter = ResultFormatter()
