#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CodeAnalyzer - Komponent odpowiedzialny za analizę i wyjaśnianie
wygenerowanego kodu Python.

Ten moduł zawiera klasę CodeAnalyzer, która analizuje wygenerowany kod Python
pod kątem logiczności, bezpieczeństwa i zgodności z intencją użytkownika.
Dodatkowo generuje wyjaśnienia kodu w języku naturalnym.
"""

import re
import ast
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

class CodeAnalyzer:
    """
    Klasa odpowiedzialna za analizę i wyjaśnianie wygenerowanego kodu Python.
    """
    
    def __init__(self, model_name: str = "llama3", config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja analizatora kodu
        
        Args:
            model_name: Nazwa modelu językowego do użycia
            config: Dodatkowa konfiguracja
        """
        self.model_name = model_name
        self.config = config or {}
        self.logger = logging.getLogger('CodeAnalyzer')
        
        # Typowe wzorce niebezpiecznego kodu - poprawione wyrażenia regularne
        self.dangerous_patterns = [
            (r'os\.system', "Bezpośrednie wywołanie poleceń systemowych"),
            (r'subprocess\.', "Wywołanie procesów zewnętrznych"),
            (r'eval\(', "Użycie funkcji eval"),
            (r'exec\(', "Użycie funkcji exec"),
            (r'__import__\(', "Dynamiczny import modułów"),
            (r'open\(.+?\,\s*[\'"]w[\'"]', "Zapisywanie do plików")
        ]
    
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        """
        Analizuje kod pod kątem logiczności i zgodności z intencją użytkownika
        
        Args:
            code: Kod do analizy
            prompt: Oryginalne zapytanie użytkownika
            
        Returns:
            Dict[str, Any]: Wynik analizy
        """
        if not code or code.strip() == "":
            return {
                "is_logical": False,
                "matches_intent": False,
                "issues": ["Kod jest pusty"],
                "suggestions": ["Podaj bardziej szczegółowe zapytanie"]
            }
        
        # Inicjalizacja wyniku analizy
        analysis = {
            "is_logical": True,
            "matches_intent": True,
            "issues": [],
            "suggestions": []
        }
        
        # Wyodrębnij słowa kluczowe z zapytania
        prompt_keywords = self._extract_keywords(prompt)
        
        # Sprawdź czy kod zawiera słowa kluczowe z zapytania
        code_keywords = self._extract_keywords(code)
        
        # Sprawdź czy kod zawiera wszystkie słowa kluczowe z zapytania
        missing_keywords = [kw for kw in prompt_keywords if kw not in code_keywords]
        if missing_keywords:
            analysis["matches_intent"] = False
            analysis["issues"].append(f"Kod może nie realizować wszystkich aspektów zapytania")
            analysis["suggestions"].append(f"Dodaj obsługę dla: {', '.join(missing_keywords)}")
        
        # Sprawdź czy kod zawiera potencjalnie niebezpieczne operacje
        for pattern, description in self.dangerous_patterns:
            if re.search(pattern, code):
                analysis["issues"].append(f"Potencjalnie niebezpieczna operacja: {description}")
                analysis["suggestions"].append(f"Rozważ alternatywne podejście zamiast: {description}")
        
        # Analiza AST (Abstract Syntax Tree)
        ast_analysis = self._analyze_ast(code)
        analysis.update(ast_analysis)
        
        return analysis
    
    def explain_code(self, code: str) -> str:
        """
        Generuje wyjaśnienie kodu w języku naturalnym
        
        Args:
            code: Kod Python do wyjaśnienia
            
        Returns:
            str: Wyjaśnienie kodu w języku naturalnym
        """
        if not code or code.strip() == "":
            return "Brak kodu do wyjaśnienia."
        
        # W rzeczywistej implementacji, tutaj byłoby wywołanie modelu językowego
        # W tej wersji demonstracyjnej, generujemy proste wyjaśnienie na podstawie analizy AST
        
        try:
            tree = ast.parse(code)
            
            # Analizuj funkcje i klasy
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            
            explanation_parts = ["Ten kod:"]
            
            # Opisz importy
            if imports:
                import_names = []
                for imp in imports:
                    if isinstance(imp, ast.Import):
                        import_names.extend([name.name for name in imp.names])
                    else:  # ImportFrom
                        module = imp.module or ""
                        import_names.extend([f"{module}.{name.name}" for name in imp.names])
                
                explanation_parts.append(f"- Importuje moduły: {', '.join(import_names)}")
            
            # Opisz funkcje
            if functions:
                for func in functions:
                    args = [arg.arg for arg in func.args.args]
                    explanation_parts.append(f"- Definiuje funkcję '{func.name}' przyjmującą argumenty: {', '.join(args) if args else 'brak argumentów'}")
            
            # Opisz klasy
            if classes:
                for cls in classes:
                    explanation_parts.append(f"- Definiuje klasę '{cls.name}'")
                    methods = [node for node in ast.walk(cls) if isinstance(node, ast.FunctionDef)]
                    if methods:
                        method_names = [method.name for method in methods]
                        explanation_parts.append(f"  z metodami: {', '.join(method_names)}")
            
            # Dodaj ogólne podsumowanie
            explanation_parts.append("\nPodsumowanie: Ten kod implementuje rozwiązanie zgodnie z zapytaniem użytkownika.")
            
            return "\n".join(explanation_parts)
            
        except SyntaxError:
            return "Kod zawiera błędy składniowe, które uniemożliwiają jego analizę."
        except Exception as e:
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Wyodrębnia słowa kluczowe z tekstu
        
        Args:
            text: Tekst do analizy
            
        Returns:
            List[str]: Lista słów kluczowych
        """
        if not text:
            return []
        
        # Usuwamy znaki specjalne i dzielimy na słowa
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Usuwamy słowa stop (krótkie, nieistotne słowa)
        stop_words = {'i', 'w', 'na', 'z', 'do', 'dla', 'jest', 'są', 'to', 'a', 'o', 'że', 'by', 'jak', 'co'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _analyze_ast(self, code: str) -> Dict[str, Any]:
        """
        Analizuje kod przy użyciu Abstract Syntax Tree
        
        Args:
            code: Kod do analizy
            
        Returns:
            Dict[str, Any]: Wynik analizy AST
        """
        result = {
            "has_syntax_errors": False,
            "complexity": 0,
            "function_count": 0,
            "class_count": 0,
            "import_count": 0
        }
        
        try:
            tree = ast.parse(code)
            
            # Liczenie funkcji, klas i importów
            result["function_count"] = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
            result["class_count"] = len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)])
            result["import_count"] = len([node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))])
            
            # Prosta metryka złożoności: liczba węzłów AST
            result["complexity"] = sum(1 for _ in ast.walk(tree))
            
        except SyntaxError:
            result["has_syntax_errors"] = True
            result["issues"] = ["Kod zawiera błędy składniowe"]
            result["is_logical"] = False
        except Exception as e:
            result["issues"] = [f"Błąd podczas analizy AST: {str(e)}"]
        
        return result
