#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CodeAnalyzer - Komponent odpowiedzialny za analizę i wyjaśnianie
wygenerowanego kodu Python.
"""

import re
import ast
import logging
import subprocess
from typing import Dict, Any, List, Optional, Tuple

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
        
        # Typowe wzorce niebezpiecznego kodu
        self.dangerous_patterns = [
            (r'os\\.system', "Bezpośrednie wywołanie poleceń systemowych"),
            (r'subprocess\\.', "Wywołanie procesów zewnętrznych"),
            (r'eval\\(', "Użycie funkcji eval"),
            (r'exec\\(', "Użycie funkcji exec"),
            (r'__import__\\(', "Dynamiczny import modułów"),
            (r'open\\(.+?\\,\\s*[\'\\"]w[\'\\"]', "Zapisywanie do plików")
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
        # Inicjalizacja wyniku analizy
        analysis = {
            "is_logical": True,
            "matches_intent": True,
            "issues": [],
            "suggestions": []
        }
        
        # Sprawdź podstawowe problemy składniowe
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError as e:
            analysis["is_logical"] = False
            analysis["issues"].append(f"Błąd składni: {str(e)}")
            analysis["error_message"] = f"SyntaxError: {str(e)}"
        
        # Sprawdź czy kod zawiera funkcję execute
        if "def execute" not in code:
            analysis["issues"].append("Brak funkcji execute")
            analysis["suggestions"].append("Dodaj funkcję execute")
        
        # Sprawdź czy kod zawiera return
        if "return" not in code:
            analysis["issues"].append("Brak instrukcji return")
            analysis["suggestions"].append("Dodaj instrukcję return w funkcji execute")
        
        # Sprawdź czy kod zawiera podstawowe elementy związane z zapytaniem
        keywords = self._extract_keywords(prompt)
        code_lower = code.lower()
        missing_keywords = []
        
        for keyword in keywords:
            if keyword.lower() not in code_lower:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            analysis["matches_intent"] = False
            analysis["issues"].append(f"Brak kluczowych elementów: {', '.join(missing_keywords)}")
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
        try:
            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu kodu Python. Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób. Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku.'

            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"

            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"

            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]

            self.logger.info("Generowanie wyjaśnienia kodu...")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"

            return stdout.strip()

        except Exception as e:
            self.logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Wyodrębnia słowa kluczowe z tekstu
        
        Args:
            text: Tekst do analizy
            
        Returns:
            List[str]: Lista słów kluczowych
        """
        # Usuń znaki interpunkcyjne i zamień na małe litery
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        
        # Podziel na słowa
        words = text.split()
        
        # Usuń słowa stop (krótkie, powszechne słowa)
        stop_words = ['i', 'w', 'na', 'z', 'do', 'dla', 'jest', 'są', 'to', 'a', 'o', 'że', 'by']
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Zwróć unikalne słowa kluczowe
        return list(set(keywords))
    
    def _analyze_ast(self, code: str) -> Dict[str, Any]:
        """
        Analizuje kod przy użyciu Abstract Syntax Tree
        
        Args:
            code: Kod do analizy
            
        Returns:
            Dict[str, Any]: Wynik analizy AST
        """
        result = {
            "complexity": 0,
            "used_modules": [],
            "function_count": 0,
            "class_count": 0,
            "variable_count": 0
        }
        
        try:
            tree = ast.parse(code)
            
            # Analiza importów
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        result["used_modules"].append(name.name)
                elif isinstance(node, ast.ImportFrom):
                    result["used_modules"].append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    result["function_count"] += 1
                elif isinstance(node, ast.ClassDef):
                    result["class_count"] += 1
                elif isinstance(node, ast.Assign):
                    result["variable_count"] += len(node.targets)
            
            # Obliczenie złożoności (prosta metryka)
            result["complexity"] = result["function_count"] + result["class_count"] * 2 + len(result["used_modules"])
            
        except SyntaxError:
            # Jeśli kod ma błędy składniowe, nie możemy go przeanalizować
            pass
        
        return result
