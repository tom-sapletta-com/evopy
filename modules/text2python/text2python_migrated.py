#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Text2Python - Moduł do konwersji tekstu na kod Python

Ten moduł wykorzystuje model językowy do konwersji żądań użytkownika
wyrażonych w języku naturalnym na funkcje Python.
Zaimplementowany zgodnie z nową architekturą bazową Evopy.
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

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj klasy bazowe
from modules.base import BaseText2XModule, ConfigManager, ErrorCorrector

# Import math_expressions module
try:
    from modules.utils.math_expressions import is_math_expression, handle_math_expression
except ImportError:
    # Jeśli ścieżka jest inna, dostosuj import
    try:
        from math_expressions import is_math_expression, handle_math_expression
    except ImportError:
        # Jeśli nie udało się zaimportować, dostarczamy zaślepki
        def is_math_expression(text):
            return False
            
        def handle_math_expression(text):
            return {"success": False, "error": "Moduł math_expressions nie jest dostępny"}

# Próba importu modułu decision_tree
try:
    from decision_tree import create_decision_tree
except ImportError:
    # Jeśli nie udało się zaimportować, dostarczamy zaślepkę
    def create_decision_tree(name=None):
        """Zaślepka dla create_decision_tree w przypadku braku modułu"""
        return None

# Konfiguracja logowania
logger = logging.getLogger('text2python')


class Text2Python(BaseText2XModule):
    """Klasa do konwersji tekstu na kod Python"""

    def initialize(self) -> None:
        """
        Inicjalizacja specyficzna dla modułu TEXT2PYTHON
        """
        super().initialize()
        
        # Domyślna konfiguracja
        default_config = {
            "model": "llama3",
            "dependencies": ["numpy", "pandas", "matplotlib"],
            "max_tokens": 1000,
            "temperature": 0.7,
            "use_sandbox": True,
            "sandbox_type": "docker",
            "code_dir": None
        }
        
        # Aktualizacja konfiguracji
        for key, value in default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Ładowanie konfiguracji z pliku
        self.load_config()
        
        # Inicjalizacja menedżera konfiguracji
        self.config_manager = ConfigManager()
        
        # Załaduj konfigurację modułu z centralnego menedżera
        module_config = self.config_manager.get_module_config("text2python")
        self.config.update(module_config)
        
        # Ustawienie katalogu dla wygenerowanego kodu
        self.code_dir = self.config.get("code_dir")
        if self.code_dir:
            self.code_dir = Path(self.code_dir)
            os.makedirs(self.code_dir, exist_ok=True)
        
        # Inicjalizacja drzewa decyzyjnego
        self.decision_tree = create_decision_tree(name=f"Text2Python-{self.config['model']}")
        
        # Upewnij się, że model jest dostępny
        self.ensure_model_available()
        
        self.logger.info(f"Moduł TEXT2PYTHON zainicjalizowany z modelem: {self.config['model']}")

    def ensure_model_available(self) -> bool:
        """
        Sprawdza czy model jest dostępny w Ollama i pobiera go jeśli nie jest

        Returns:
            bool: True jeśli model jest dostępny, False w przeciwnym przypadku
        """
        try:
            # Sprawdź czy model jest dostępny
            self.logger.info(f"Sprawdzanie dostępności modelu {self.config['model']}...")
            check_cmd = ["ollama", "list"]
            result = subprocess.run(check_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            if result.returncode != 0:
                self.logger.error(f"Błąd podczas sprawdzania modeli Ollama: {result.stderr}")
                return False

            # Sprawdź czy model jest na liście
            if self.config['model'] not in result.stdout:
                self.logger.warning(f"Model {self.config['model']} nie jest dostępny. Próba pobrania...")

                # Pobierz model
                pull_cmd = ["ollama", "pull", self.config['model']]
                pull_result = subprocess.run(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

                if pull_result.returncode != 0:
                    self.logger.error(f"Błąd podczas pobierania modelu {self.config['model']}: {pull_result.stderr}")
                    return False

                self.logger.info(f"Model {self.config['model']} został pomyślnie pobrany")
            else:
                self.logger.info(f"Model {self.config['model']} jest dostępny")

            return True

        except Exception as e:
            self.logger.error(f"Nieoczekiwany błąd podczas sprawdzania modelu: {str(e)}")
            return False

    def process(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Przetwarza tekst na kod Python
        
        Args:
            text: Tekst wejściowy do przetworzenia
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict[str, Any]: Wygenerowany kod Python
        """
        return self.generate_code(text)

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
            self.logger.info(f"Analizowanie zapytania: '{prompt}'")

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
                self.logger.warning(f"Otrzymano nieprawidłowe zapytanie: '{prompt}'")
                return {
                    "success": False,
                    "code": "def execute():\n    return 'Proszę podać prawidłowe zapytanie'",
                    "error": "Zapytanie jest puste lub zawiera tylko znaki specjalne",
                    "analysis": "Nieprawidłowe zapytanie",
                    "explanation": "Twoje zapytanie nie zawierało wystarczających informacji do wygenerowania kodu."
                }

            # Sprawdź czy zapytanie jest wyrażeniem matematycznym
            if is_math_expression(prompt):
                self.logger.info(f"Wykryto wyrażenie matematyczne: '{prompt}'")
                math_result = handle_math_expression(prompt)
                
                # Jeśli potrzebne, dostosuj ścieżkę do pliku kodu
                if self.code_dir and math_result.get("code_file"):
                    math_result["code_file"] = str(self.code_dir / f"{math_result['code_id']}.py")
                
                return math_result

            # Oryginalny kod dla prostych wyrażeń arytmetycznych (pozostawiony jako fallback)
            import re
            arithmetic_pattern = re.compile(r'^\s*(\d+\s*[+\-*/]\s*\d+)\s*$')
            match = arithmetic_pattern.match(prompt)

            if match:
                # Wyodrębnij wyrażenie arytmetyczne
                expression = match.group(1).strip()
                self.logger.info(f"Wykryto proste wyrażenie arytmetyczne: {expression}")

                # Użyj funkcji handle_math_expression zamiast oryginalnego kodu
                return handle_math_expression(expression)

            # Upewnij się, że model jest dostępny
            if not self.ensure_model_available():
                self.logger.error(f"Model {self.config['model']} nie jest dostępny")
                return {
                    "success": False,
                    "code": "",
                    "error": f"Model {self.config['model']} nie jest dostępny",
                    "analysis": "Problem z modelem"
                }

            self.logger.info(f"Generowanie kodu dla zapytania: {prompt}...")

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
                "ollama", "run", self.config['model'],
                combined_prompt_code
            ]

            self.logger.info(f"Generowanie kodu dla zapytania: {prompt[:50]}...")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                self.logger.error(f"Błąd podczas generowania kodu: {stderr}")
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
            self.logger.info("Generowanie wyjaśnienia kodu w celu weryfikacji intencji użytkownika...")

            # Przygotuj zapytanie do modelu dla wyjaśnienia kodu
            system_prompt_explain = """Jesteś ekspertem w wyjaśnianiu kodu Python.
Twoim zadaniem jest wyjaśnienie co robi podany kod Python w języku naturalnym.
Wyjaśnij dokładnie, co kod robi, jakie problemy rozwiązuje i jaki jest jego cel.
Wyjaśnij to prostym językiem, zrozumiałym dla osób bez doświadczenia w programowaniu.
Na końcu zapytaj użytkownika, czy to jest to, czego oczekiwał."""

            combined_prompt_explain = f"{system_prompt_explain}\n\nWyjaśnij co robi następujący kod Python:\n```python\n{code}\n```\n\nWyjaśnienie:"

            # Wywołaj model Ollama dla wyjaśnienia kodu
            cmd_explain = [
                "ollama", "run", self.config['model'],
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
                self.logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr_explain}")
                explanation = "Nie udało się wygenerować wyjaśnienia kodu."

            # KROK 3: Analiza logiczna kodu
            self.logger.info("Analizowanie logiki kodu...")

            # Implementacja analizy kodu lokalnie, ponieważ ErrorCorrector nie ma metody analyze_code
            analysis = self._analyze_code(code, prompt)
            
            # Sprawdź czy kod wymaga korekcji
            if not analysis.get("is_logical", True) or not analysis.get("matches_intent", True) or analysis.get("issues"):
                # Popraw kod używając ErrorCorrector jeśli mamy konkretny błąd
                if analysis.get("error_message"):
                    corrected_code, corrections = ErrorCorrector.correct_code(code, analysis.get("error_message"))
                else:
                    corrections = []
                    corrected_code = code
                if corrections:
                    self.logger.info(f"Zastosowano {len(corrections)} korekcji kodu")
                    code = corrected_code

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
            self.logger.error(f"Błąd podczas generowania kodu: {e}")
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

    def _analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
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
        dangerous_patterns = [
            (r'os\.system', "Bezpośrednie wywołanie poleceń systemowych"),
            (r'subprocess\.', "Wywołanie procesów zewnętrznych"),
            (r'eval\(', "Użycie funkcji eval"),
            (r'exec\(', "Użycie funkcji exec"),
            (r'__import__\(', "Dynamiczny import modułów"),
            (r'open\(.+?\,\s*[\'\"]w[\'\"]', "Zapisywanie do plików")
        ]
        
        for pattern, description in dangerous_patterns:
            if re.search(pattern, code):
                analysis["issues"].append(f"Potencjalnie niebezpieczna operacja: {description}")
                analysis["suggestions"].append(f"Rozważ alternatywne podejście zamiast: {description}")
        
        return analysis
    
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
                return f"Nie można wygenerować wyjaśnienia, ponieważ model {self.config['model']} nie jest dostępny."

            # Przygotuj zapytanie do modelu
            system_prompt = 'Jesteś ekspertem w wyjaśnianiu kodu Python. Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób. Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku.'

            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"

            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"

            # Wywołaj model Ollama
            cmd = [
                "ollama", "run", self.config['model'],
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

    def validate_input(self, text: str, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Walidacja danych wejściowych
        
        Args:
            text: Tekst wejściowy do walidacji
            **kwargs: Dodatkowe parametry do walidacji
            
        Returns:
            Tuple[bool, Optional[str]]: (czy_poprawne, komunikat_błędu)
        """
        if not text or not isinstance(text, str):
            return False, "Tekst wejściowy musi być niepustym ciągiem znaków"
            
        if len(text) < 3:
            return False, "Tekst jest zbyt krótki (minimum 3 znaki)"
            
        return True, None

    def execute_code(self, code: str, use_sandbox: bool = None) -> Dict[str, Any]:
        """
        Wykonuje wygenerowany kod Python
        
        Args:
            code: Kod do wykonania
            use_sandbox: Czy użyć piaskownicy (opcjonalne)
            
        Returns:
            Dict[str, Any]: Wynik wykonania kodu
        """
        if use_sandbox is None:
            use_sandbox = self.config.get('use_sandbox', True)
        
        self.logger.info(f"Wykonywanie kodu (use_sandbox={use_sandbox})...")
        
        if use_sandbox:
            # W rzeczywistej implementacji tutaj byłoby wywołanie piaskownicy Docker
            try:
                from modules.docker_sandbox import DockerSandbox
                sandbox = DockerSandbox()
                return sandbox.run_code(code)
            except ImportError:
                self.logger.error("Nie można zaimportować modułu DockerSandbox")
                return {
                    "success": False,
                    "error": "Moduł DockerSandbox nie jest dostępny"
                }
        else:
            # Wykonanie kodu bezpośrednio (niebezpieczne!)
            try:
                import tempfile
                import subprocess
                
                # Zapisz kod do tymczasowego pliku
                with tempfile.NamedTemporaryFile(suffix='.py', mode='w', delete=False) as f:
                    f.write(code)
                    temp_file = f.name
                
                # Wykonaj kod
                result = subprocess.run(
                    [sys.executable, temp_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Usuń tymczasowy plik
                os.unlink(temp_file)
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr if result.returncode != 0 else None,
                    "execution_time": 0.5  # Symulowany czas wykonania
                }
            except Exception as e:
                self.logger.error(f"Błąd podczas wykonywania kodu: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }

    def correct_code(self, code: str, error_message: str) -> Dict[str, Any]:
        """
        Koryguje kod na podstawie komunikatu o błędzie
        
        Args:
            code: Kod do skorygowania
            error_message: Komunikat o błędzie
            
        Returns:
            Dict[str, Any]: Skorygowany kod i zastosowane korekcje
        """
        self.logger.info(f"Korygowanie kodu na podstawie błędu: {error_message[:50]}...")
        
        # Użyj systemu korekcji błędów
        corrected_code, corrections = ErrorCorrector.correct_code(code, error_message)
        
        # Analiza błędu
        error_analysis = ErrorCorrector.analyze_error(error_message)
        
        return {
            "success": True,
            "original_code": code,
            "corrected_code": corrected_code,
            "corrections": corrections,
            "error_analysis": error_analysis
        }

    def __str__(self):
        """Reprezentacja tekstowa obiektu"""
        return f"Text2Python(model={self.config['model']})"


# Przykład użycia
if __name__ == "__main__":
    # Konfiguracja logowania
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    
    # Tworzenie instancji modułu
    text2python = Text2Python()
    
    # Przetwarzanie tekstu
    query = "Napisz funkcję, która sumuje dwie liczby"
    result = text2python.execute(query)
    
    # Wyświetlenie wyniku
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Wykonanie wygenerowanego kodu
    if result["success"]:
        code = result["result"]["code"]
        execution_result = text2python.execute_code(code, use_sandbox=True)
        print("\nWynik wykonania kodu:")
        print(json.dumps(execution_result, indent=2, ensure_ascii=False))
