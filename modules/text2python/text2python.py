#!/usr/bin/env python3
"""
Text2Python - Moduł do konwersji tekstu na kod Python

Ten moduł wykorzystuje model językowy do konwersji żądań użytkownika
wyrażonych w języku naturalnym na funkcje Python.
"""

import os
import re
import sys
import json
import time
import uuid
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# Próba importu modułu decision_tree
try:
    from decision_tree import create_decision_tree
except ImportError:
    # Jeśli nie udało się zaimportować, dostarczamy zaślepkę
    def create_decision_tree(name=None):
        """Zaślepka dla create_decision_tree w przypadku braku modułu"""
        return None

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('text2python')


class Text2Python:
    """Klasa do konwersji tekstu na kod Python"""

    def __init__(self, model_name: str = "llama3", code_dir: Optional[Path] = None):
        """
        Inicjalizacja konwertera tekst-na-Python

        Args:
            model_name: Nazwa modelu Ollama do użycia
            code_dir: Katalog do zapisywania wygenerowanego kodu
        """
        self.model_name = model_name
        self.code_dir = code_dir

        if self.code_dir:
            os.makedirs(self.code_dir, exist_ok=True)

        # Inicjalizacja drzewa decyzyjnego
        self.decision_tree = create_decision_tree(name=f"Text2Python-{model_name}")

        # Upewnij się, że model jest dostępny
        self.ensure_model_available()

    def ensure_model_available(self) -> bool:
        """
        Sprawdza czy model jest dostępny w Ollama i pobiera go jeśli nie jest

        Returns:
            bool: True jeśli model jest dostępny, False w przeciwnym przypadku
        """
        try:
            # Sprawdź czy model jest dostępny
            logger.info(f"Sprawdzanie dostępności modelu {self.model_name}...")
            check_cmd = ["ollama", "list"]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                logger.error(f"Błąd podczas sprawdzania modeli Ollama: {result.stderr}")
                return False

            # Sprawdź czy model jest na liście
            if self.model_name not in result.stdout:
                logger.warning(f"Model {self.model_name} nie jest dostępny. Próba pobrania...")

                # Pobierz model
                pull_cmd = ["ollama", "pull", self.model_name]
                pull_result = subprocess.run(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if pull_result.returncode != 0:
                    logger.error(f"Błąd podczas pobierania modelu {self.model_name}: {pull_result.stderr}")
                    return False

                logger.info(f"Model {self.model_name} został pomyślnie pobrany")
            else:
                logger.info(f"Model {self.model_name} jest dostępny")

            return True

        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas sprawdzania modelu: {str(e)}")
            return False

    def generate_code(self, prompt: str) -> Dict[str, Any]:
        """
        Generuje kod Python na podstawie opisu w języku naturalnym, a następnie weryfikuje go
        poprzez ponowną konwersję na tekst w celu potwierdzenia intencji użytkownika.

        Args:
            prompt: Opis funkcjonalności w języku naturalnym

        Returns:
            Dict: Wygenerowany kod, metadane i wyjaśnienie kodu
        """
        try:
            logger.info(f"Analizowanie zapytania: '{prompt}'")

            # Oblicz złożoność zapytania
            complexity = self._calculate_complexity(prompt)

            # Utwórz węzeł główny dla zapytania w drzewie decyzyjnym
            if self.decision_tree:
                root_node_id = self.decision_tree.add_node(
                    query=prompt,
                    decision_type="query_analysis",
                    content=f"Analizowanie zapytania: {prompt}"
                )

                # Dodaj metrykę złożoności do węzła
                self.decision_tree.add_node_metric(root_node_id, "complexity", complexity)
                self.decision_tree.add_node_metric(root_node_id, "query_length", len(prompt))

            # Sprawdź czy zapytanie jest puste lub zawiera tylko znaki specjalne
            if not prompt or prompt.strip() == "" or all(not c.isalnum() for c in prompt):
                logger.warning(f"Otrzymano nieprawidłowe zapytanie: '{prompt}'")
                return {
                    "success": False,
                    "code": "def execute():\n    return 'Proszę podać prawidłowe zapytanie'",
                    "error": "Zapytanie jest puste lub zawiera tylko znaki specjalne",
                    "analysis": "Nieprawidłowe zapytanie",
                    "explanation": "Twoje zapytanie nie zawierało wystarczających informacji do wygenerowania kodu."
                }

            # Sprawdź czy zapytanie jest prostym wyrażeniem arytmetycznym
            import re
            arithmetic_pattern = re.compile(r'^\s*(\d+\s*[+\-*/]\s*\d+)\s*$')
            match = arithmetic_pattern.match(prompt)

            if match:
                # Wyodrębnij wyrażenie arytmetyczne
                expression = match.group(1).strip()
                logger.info(f"Wykryto proste wyrażenie arytmetyczne: {expression}")

                # Generuj kod, który faktycznie wykonuje obliczenie
                code = f"def execute():\n    # Obliczenie wyrażenia {expression}\n    result = {expression}\n    return result"

                # Generuj wyjaśnienie
                explanation = f"Ten kod wykonuje proste obliczenie matematyczne: {expression}.\n\nFunkcja 'execute' oblicza wartość wyrażenia {expression} i zwraca wynik.\n\nCzy to jest to, czego oczekiwałeś?"

                # Utwórz analizę
                analysis = {
                    "is_logical": True,
                    "matches_intent": True,
                    "issues": [],
                    "suggestions": []
                }

                # Zapisz kod do pliku jeśli podano katalog
                code_id = str(uuid.uuid4())
                code_file = None
                if self.code_dir:
                    code_file = self.code_dir / f"{code_id}.py"
                    with open(code_file, "w", encoding="utf-8") as f:
                        f.write(code)

                return {
                    "success": True,
                    "code": code,
                    "code_id": code_id,
                    "code_file": str(code_file) if code_file else None,
                    "explanation": explanation,
                    "analysis": "Kod wydaje się poprawny i zgodny z intencją.",
                    "analysis_details": analysis,
                    "matches_intent": True,
                    "is_logical": True,
                    "suggestions": [],
                    "timestamp": datetime.now().isoformat()
                }

            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                logger.error(f"Model {self.model_name} nie jest dostępny")
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {self.model_name} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }

            logger.info(f"Generowanie kodu dla zapytania: {prompt}...")

            # KROK 1: Konwersja tekstu na kod Python
            # Przygotuj zapytanie do modelu dla generowania kodu
            system_prompt_code = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""

            # Łączymy system prompt z właściwym promptem, ponieważ Ollama nie obsługuje flagi --system
            combined_prompt_code = f"{system_prompt_code}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"

            # Wywołaj model Ollama dla generowania kodu
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt_code
            ]

            logger.info(f"Generowanie kodu dla zapytania: {prompt[:50]}...")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania kodu: {stderr}")
                return {
                    "success": False,
                    "code": "",
                    "error": stderr
                }

            # Wyodrębnij kod Python z odpowiedzi
            code = self._extract_code(stdout)

            # Upewnij się, że kod zawiera funkcję execute
            if "def execute" not in code:
                code = self._wrap_in_execute_function(code)

            # KROK 2: Konwersja kodu z powrotem na tekst w celu weryfikacji intencji
            logger.info("Generowanie wyjaśnienia kodu w celu weryfikacji intencji użytkownika...")

            # Przygotuj zapytanie do modelu dla wyjaśnienia kodu
            system_prompt_explain = """Jesteś ekspertem w wyjaśnianiu kodu Python.
Twoim zadaniem jest wyjaśnienie co robi podany kod Python w języku naturalnym.
Wyjaśnij dokładnie, co kod robi, jakie problemy rozwiązuje i jaki jest jego cel.
Wyjaśnij to prostym językiem, zrozumiałym dla osób bez doświadczenia w programowaniu.
Na końcu zapytaj użytkownika, czy to jest to, czego oczekiwał."""

            combined_prompt_explain = f"{system_prompt_explain}\n\nWyjaśnij co robi następujący kod Python:\n```python\n{code}\n```\n\nWyjaśnienie:"

            # Wywołaj model Ollama dla wyjaśnienia kodu
            cmd_explain = [
                "ollama", "run", self.model_name,
                combined_prompt_explain
            ]

            process_explain = subprocess.Popen(
                cmd_explain,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout_explain, stderr_explain = process_explain.communicate()

            explanation = ""
            if process_explain.returncode == 0:
                explanation = stdout_explain.strip()
            else:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr_explain}")
                explanation = "Nie udało się wygenerować wyjaśnienia kodu."

            # KROK 3: Analiza logiczna kodu
            logger.info("Analizowanie logiki kodu...")

            # Przygotuj zapytanie do modelu dla analizy logicznej kodu
            system_prompt_analyze = """Jesteś ekspertem w analizie kodu Python.
Twoim zadaniem jest sprawdzenie, czy podany kod Python jest logiczny i realizuje dokładnie to, o co prosił użytkownik.
Zwróć uwagę na potencjalne błędy logiczne, nieefektywne rozwiązania lub niezgodności z intencją użytkownika.
Podaj krótką analizę w formacie JSON z polami: 'is_logical' (true/false), 'matches_intent' (true/false), 'issues' (lista problemów) i 'suggestions' (lista sugestii)."""

            combined_prompt_analyze = f"{system_prompt_analyze}\n\nZapytanie użytkownika: {prompt}\n\nWygenerowany kod Python:\n```python\n{code}\n```\n\nAnaliza JSON:"

            # Wywołaj model Ollama dla analizy logicznej kodu
            cmd_analyze = [
                "ollama", "run", self.model_name,
                combined_prompt_analyze
            ]

            process_analyze = subprocess.Popen(
                cmd_analyze,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout_analyze, stderr_analyze = process_analyze.communicate()

            analysis = {}
            if process_analyze.returncode == 0:
                try:
                    # Próba wyodrębnienia JSON z odpowiedzi
                    import re
                    import json

                    # Bardziej zaawansowany sposób wyodrębniania JSON
                    # Szukamy tekstu pomiędzy nawiasami klamrowymi, ale upewniamy się, że są one zbalansowane
                    text = stdout_analyze.strip()

                    # Najpierw spróbujmy znaleźć pełny JSON
                    json_match = re.search(r'\{[^{}]*((\{[^{}]*\})[^{}]*)*\}', text)

                    if json_match:
                        json_str = json_match.group(0)
                        # Spróbujmy naprawić typowe problemy z JSON
                        json_str = json_str.replace("'", '"')  # Zamień pojedyncze cudzysłowy na podwójne
                        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":',
                                          json_str)  # Dodaj cudzysłowy do kluczy

                        try:
                            analysis = json.loads(json_str)
                        except json.JSONDecodeError:
                            # Jeśli nadal nie możemy sparsować, utwórzmy prosty JSON
                            logger.warning(f"Nie można sparsować JSON po naprawie: {json_str}")
                            analysis = self._create_default_analysis(text)
                    else:
                        # Jeśli nie znaleziono JSON, utwórzmy go na podstawie tekstu
                        logger.warning(f"Nie znaleziono JSON w odpowiedzi: {text[:100]}...")
                        analysis = self._create_default_analysis(text)
                except Exception as e:
                    logger.error(f"Błąd podczas parsowania analizy JSON: {str(e)}")
                    analysis = {
                        "is_logical": True,
                        "matches_intent": True,
                        "issues": [],
                        "suggestions": []
                    }
            else:
                logger.error(f"Błąd podczas generowania analizy: {stderr_analyze}")
                analysis = {
                    "is_logical": True,
                    "matches_intent": True,
                    "issues": [],
                    "suggestions": []
                }

            # Zapisz kod do pliku jeśli podano katalog
            code_id = str(uuid.uuid4())
            code_file = None
            if self.code_dir:
                code_file = self.code_dir / f"{code_id}.py"
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code)

            # Utwórz podsumowanie analizy
            analysis_summary = ""
            if analysis.get("issues") and len(analysis["issues"]) > 0:
                analysis_summary = "Potencjalne problemy: " + ", ".join(analysis["issues"])
            elif not analysis.get("is_logical", True):
                analysis_summary = "Kod może zawierać błędy logiczne."
            elif not analysis.get("matches_intent", True):
                analysis_summary = "Kod może nie realizować dokładnie tego, o co prosiłeś."
            else:
                analysis_summary = "Kod wydaje się poprawny i zgodny z intencją."

            # Zwróć wyniki
            return {
                "success": True,
                "code": code,
                "code_id": code_id,
                "code_file": str(code_file) if code_file else None,
                "explanation": explanation,
                "analysis": analysis_summary,
                "analysis_details": analysis,
                "matches_intent": analysis.get("matches_intent", True),
                "is_logical": analysis.get("is_logical", True),
                "suggestions": analysis.get("suggestions", []),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Błąd podczas generowania kodu: {e}")
            return {
                "success": False,
                "code": "",
                "error": str(e)
            }

    def _extract_code(self, text: str) -> str:
        """
        Wyodrębnia kod Python z odpowiedzi modelu

        Args:
            text: Odpowiedź modelu

        Returns:
            str: Wyodrębniony kod Python
        """
        # Próba wyodrębnienia kodu z bloków kodu markdown
        code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)

        if code_blocks:
            return code_blocks[0].strip()

        # Jeśli nie znaleziono bloków kodu, zwróć całą odpowiedź
        return text.strip()

    def _wrap_in_execute_function(self, code: str) -> str:
        """
        Owija kod w funkcję execute jeśli jej nie zawiera

        Args:
            code: Kod Python

        Returns:
            str: Kod z funkcją execute
        """
        # Sprawdź czy kod już zawiera funkcję execute
        if "def execute" in code:
            return code

        # Dodaj wcięcie do każdej linii kodu
        indented_code = "\n".join(["    " + line for line in code.split("\n")])

        # Owij kod w funkcję execute
        wrapped_code = f"""def execute():
    # Kod wygenerowany na podstawie opisu użytkownika
{indented_code}

    # Zwróć wynik jeśli funkcja nic nie zwraca
    return "Wykonano zadanie"
"""

        return wrapped_code

    def _calculate_complexity(self, text: str) -> float:
        """
        Oblicza złożoność zapytania na podstawie różnych metryk

        Args:
            text: Tekst zapytania

        Returns:
            float: Wartość złożoności od 0.0 do 1.0
        """
        # Prosta heurystyka złożoności oparta na długości, liczbie słów kluczowych i strukturze
        complexity = 0.0

        # Długość tekstu (0.0-0.3)
        length_score = min(len(text) / 500.0, 1.0) * 0.3
        complexity += length_score

        # Liczba słów kluczowych technicznych (0.0-0.4)
        tech_keywords = ['plik', 'dane', 'oblicz', 'algorytm', 'funkcja', 'klasa', 'obiekt',
                         'lista', 'słownik', 'iteracja', 'rekurencja', 'sortowanie', 'filtrowanie',
                         'API', 'baza danych', 'HTTP', 'JSON', 'XML', 'CSV', 'SQL', 'wykres',
                         'analiza', 'statystyka', 'uczenie maszynowe', 'AI', 'sieć neuronowa']

        keyword_count = sum(1 for keyword in tech_keywords if keyword.lower() in text.lower())
        keyword_score = min(keyword_count / 10.0, 1.0) * 0.4
        complexity += keyword_score

        # Złożoność strukturalna (0.0-0.3) - liczba zdań, przecinków, nawiasów
        structure_indicators = len(re.findall(r'[.!?]', text)) + len(re.findall(r',', text)) + len(
            re.findall(r'[()]', text))
        structure_score = min(structure_indicators / 20.0, 1.0) * 0.3
        complexity += structure_score

        return round(complexity, 2)

    def _create_default_analysis(self, text: str) -> dict:
        """
        Tworzy domyślną analizę na podstawie tekstu odpowiedzi

        Args:
            text: Tekst odpowiedzi modelu

        Returns:
            dict: Domyślna analiza w formacie słownika
        """
        # Spróbujmy wyciągnąć informacje z tekstu
        is_logical = True
        matches_intent = True
        issues = []
        suggestions = []

        # Szukamy typowych słów kluczowych wskazujących na problemy
        if re.search(r'nie\s+jest\s+logiczn', text, re.IGNORECASE) or \
                re.search(r'bł[aę]d\s+logiczn', text, re.IGNORECASE) or \
                re.search(r'nielogiczn', text, re.IGNORECASE):
            is_logical = False

        if re.search(r'nie\s+realizuje', text, re.IGNORECASE) or \
                re.search(r'nie\s+spełnia', text, re.IGNORECASE) or \
                re.search(r'nie\s+odpowiada', text, re.IGNORECASE) or \
                re.search(r'nie\s+zgodn', text, re.IGNORECASE):
            matches_intent = False

        # Szukamy problemów i sugestii
        problem_lines = re.findall(r'(?:problem|błąd|issue|error)[^.]*\.', text, re.IGNORECASE)
        for line in problem_lines:
            issues.append(line.strip())

        suggestion_lines = re.findall(r'(?:sugestia|propozycja|suggestion|recommend)[^.]*\.', text, re.IGNORECASE)
        for line in suggestion_lines:
            suggestions.append(line.strip())

        # Jeśli nie znaleziono problemów ani sugestii, ale tekst wskazuje na problemy
        if not issues and (not is_logical or not matches_intent):
            issues.append("Wykryto potencjalne problemy z kodem, ale nie można ich dokładnie określić.")

        return {
            "is_logical": is_logical,
            "matches_intent": matches_intent,
            "issues": issues[:3],  # Ograniczamy liczbę problemów do 3
            "suggestions": suggestions[:3]  # Ograniczamy liczbę sugestii do 3
        }

    def explain_code(self, code: str) -> str:
        """
        Generuje wyjaśnienie kodu w języku naturalnym

        Args:
            code: Kod Python do wyjaśnienia

        Returns:
            str: Wyjaśnienie kodu w języku naturalnym
        """
        try:
            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.model_name} nie jest dostępny."

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

            logger.info("Generowanie wyjaśnienia kodu...")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"

            return stdout.strip()

        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Python(model={self.model_name})"