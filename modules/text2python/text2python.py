#!/usr/bin/env python3
"""
Text2Python - Moduł do konwersji tekstu na kod Python

Ten moduł wykorzystuje modele językowe do konwersji żądań użytkownika
wyrażonych w języku naturalnym na funkcje Python.
"""

import os
import re
import ast
import json
import uuid
import logging
import subprocess
import importlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Import modułu drzewa decyzyjnego
import sys
from pathlib import Path

# Dodaj katalog główny do ścieżki, aby zaimportować moduły Evopy
sys.path.append(str(Path(__file__).parents[2]))
from decision_tree import create_decision_tree, DecisionTree

logger = logging.getLogger("evo-assistant.text2python")

# Załaduj zmienne środowiskowe z pliku .env
ENV_PATH = Path(__file__).parents[2] / "config" / ".env"
load_dotenv(ENV_PATH)

def get_available_models() -> List[Dict[str, Any]]:
    """
    Zwraca listę dostępnych modeli LLM
    
    Returns:
        List[Dict]: Lista modeli z ich konfiguracją
    """
    models = [
        {
            "id": "deepsek",
            "name": os.getenv("DEEPSEK_MODEL", "deepseek-coder-33b-instruct"),
            "version": os.getenv("DEEPSEK_VERSION", "1.5"),
            "repo": os.getenv("DEEPSEK_REPO", "deepseek-ai/deepseek-coder-33b-instruct"),
            "url": os.getenv("DEEPSEK_URL", "https://huggingface.co/deepseek-ai/deepseek-coder-33b-instruct")
        },
        {
            "id": "llama",
            "name": os.getenv("LLAMA_MODEL", "llama3"),
            "version": os.getenv("LLAMA_VERSION", "70b"),
            "repo": os.getenv("LLAMA_REPO", "meta-llama/llama-3-70b-instruct"),
            "url": os.getenv("LLAMA_URL", "https://huggingface.co/meta-llama/llama-3-70b-instruct")
        },
        {
            "id": "bielik",
            "name": os.getenv("BIELIK_MODEL", "bielik"),
            "version": os.getenv("BIELIK_VERSION", "7b"),
            "repo": os.getenv("BIELIK_REPO", "allegro/bielik-7b"),
            "url": os.getenv("BIELIK_URL", "https://huggingface.co/allegro/bielik-7b")
        }
    ]
    return models

def get_model_config(model_name: str = None) -> Dict[str, Any]:
    """
    Pobiera konfigurację modelu
    
    Args:
        model_name: Nazwa modelu (opcjonalnie)
        
    Returns:
        Dict[str, Any]: Konfiguracja modelu
    """
    if model_name is None:
        model_name = os.getenv("ACTIVE_MODEL", "deepsek")
    
    models = get_available_models()
    for model in models:
        if model["id"] == model_name:
            return model
    
    # Jeśli nie znaleziono modelu, zwróć domyślny
    logger.warning(f"Nie znaleziono modelu {model_name}, używam domyślnego (deepsek)")
    return next((m for m in models if m["id"] == "deepsek"), models[0])


class Text2Python:
    """Klasa do konwersji tekstu na kod Python"""
    
    def __init__(self, model_name: str = None, code_dir: Path = None):
        """
        Inicjalizacja konwertera tekst-na-Python
        
        Args:
            model_name: Nazwa modelu do użycia (deepsek, llama, bielik)
            code_dir: Katalog do zapisywania wygenerowanego kodu
        """
        self.model_config = get_model_config(model_name)
        self.model_id = self.model_config["id"]
        self.model_name = self.model_config["name"]
        self.code_dir = code_dir
        
        if self.code_dir:
            os.makedirs(self.code_dir, exist_ok=True)
        
        # Inicjalizacja drzewa decyzyjnego
        self.decision_tree = create_decision_tree(name=f"Text2Python-{self.model_name}")
        
        # Upewnij się, że model jest dostępny
        self.ensure_model_available()
    
    def ensure_model_available(self) -> bool:
        """
        Sprawdza czy model jest dostępny w Ollama i pobiera go jeśli nie jest
        Jeśli model nie jest dostępny, próbuje użyć alternatywnego modelu
        
        Returns:
            bool: True jeśli model jest dostępny, False w przeciwnym przypadku
        """
        try:
            # Użyj nowego model_manager do sprawdzenia dostępności modelu
            from .model_manager import check_ollama_models, pull_model, find_best_available_model
            
            # Sprawdź czy model jest dostępny (z timeoutem 5 sekund)
            logger.info(f"Sprawdzanie dostępności modelu {self.model_name}...")
            available_models = check_ollama_models(timeout=5)
            
            # Sprawdź czy model jest na liście
            if self.model_name not in available_models:
                logger.warning(f"Model {self.model_name} nie jest dostępny. Próba pobrania...")
                
                # Próba pobrania modelu (z timeoutem 60 sekund)
                if pull_model(self.model_name, timeout=60):
                    logger.info(f"Model {self.model_name} został pomyślnie pobrany")
                    return True
                else:
                    error_msg = f"Nie można pobrać modelu {self.model_name}"
                    logger.error(error_msg)
                    return self._fallback_to_default_model(error_msg, available_models)
            else:
                logger.info(f"Model {self.model_name} jest dostępny")
                return True
            
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas sprawdzania modelu: {str(e)}")
            return self._fallback_to_default_model(f"Nieoczekiwany błąd: {str(e)}")
    
    def _fallback_to_default_model(self, error_reason: str, available_models: list = None) -> bool:
        """
        Próbuje użyć alternatywnego modelu w przypadku problemów z wybranym modelem
        
        Args:
            error_reason: Powód, dla którego potrzebny jest model zastępczy
            available_models: Lista dostępnych modeli (opcjonalnie)
            
        Returns:
            bool: True jeśli udało się znaleźć model zastępczy, False w przeciwnym przypadku
        """
        # Użyj nowego model_manager do znalezienia najlepszego dostępnego modelu
        from .model_manager import find_best_available_model, check_ollama_models
        
        # Specjalna obsługa dla modelu Bielik
        if self.model_name.lower() == "bielik":
            logger.warning(f"Model {self.model_name} nie jest dostępny w publicznym repozytorium Ollama.")
            logger.info("Bielik to polski model językowy, który wymaga ręcznej instalacji.")
            logger.info("Instrukcje instalacji: https://github.com/bielik-project/bielik")
            # Kontynuuj z fallbackiem do innego modelu
        
        # Preferowana kolejność modeli zastępczych (bez Bielika, który nie jest dostępny w publicznym repozytorium)
        preferred_models = ["llama3", "deepseek-coder", "phi3", "mistral"]
        
        if available_models is None:
            # Pobierz listę dostępnych modeli z timeoutem
            available_models = check_ollama_models(timeout=5)
        
        # Znajdź najlepszy dostępny model
        fallback_model = find_best_available_model(preferred_models)
        
        if fallback_model:
            logger.warning(f"Nie znaleziono modelu {self.model_name}, używam domyślnego ({fallback_model})")
            self.model_name = fallback_model
            return True
        else:
            logger.error(f"Nie znaleziono żadnego dostępnego modelu zastępczego")
            logger.error("Upewnij się, że Ollama jest uruchomiona i ma zainstalowane modele.")
            logger.info("Możesz zainstalować modele ręcznie poleceniem: ollama pull llama3")
            return False
    
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
        structure_indicators = len(re.findall(r'[.!?]', text)) + len(re.findall(r',', text)) + len(re.findall(r'[()]', text))
        structure_score = min(structure_indicators / 20.0, 1.0) * 0.3
        complexity += structure_score
        
        return round(complexity, 2)
    
    def generate_code(self, prompt: str) -> Dict[str, Any]:
        """
        Generuje kod Python na podstawie opisu w języku naturalnym, a następnie weryfikuje go
        poprzez ponowną konwersję na tekst w celu potwierdzenia intencji użytkownika.
        
        Args:
            prompt: Opis funkcjonalności w języku naturalnym
            
        Returns:
            Dict: Wygenerowany kod, metadane i wyjaśnienie kodu
        """
        logger.info(f"Analizowanie zapytania: '{prompt}'")
        
        # Oblicz złożoność zapytania
        complexity = self._calculate_complexity(prompt)
        
        # Utwórz węzeł główny dla zapytania w drzewie decyzyjnym
        root_node_id = self.decision_tree.add_node(
            query=prompt,
            decision_type="query_analysis",
            content=f"Analizowanie zapytania: {prompt}"
        )
        
        # Dodaj metrykę złożoności do węzła
        self.decision_tree.add_node_metric(root_node_id, "complexity", complexity)
        self.decision_tree.add_node_metric(root_node_id, "query_length", len(prompt))
        self.decision_tree.add_node_metric(root_node_id, "model", self.model_id)
        
        # Sprawdź, czy model jest dostępny
        if not self.ensure_model_available():
            # Zapisz informację o błędzie w drzewie decyzyjnym
            self.decision_tree.set_node_result(root_node_id, False, f"Model {self.model_name} nie jest dostępny")
            self.decision_tree.save()
            
            return {
                "success": False,
                "code": "",
                "error": f"Model {self.model_name} nie jest dostępny"
            }
        
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
        
        try:
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
            
            # Utwórz węzeł dla generowania kodu w drzewie decyzyjnym
            code_node_id = self.decision_tree.add_node(
                query=prompt,
                decision_type="code_generation",
                content=combined_prompt_code,
                parent_id=root_node_id
            )
            
            # Użyj nowego model_manager do uruchomienia modelu z timeoutem
            from .model_manager import run_model_with_timeout
            
            logger.info(f"Generowanie kodu dla zapytania: {prompt[:50]}...")
            
            # Uruchom model z timeoutem 30 sekund
            returncode, stdout, stderr = run_model_with_timeout(
                model_name=self.model_name,
                prompt=combined_prompt_code,
                timeout=30
            )
            
            if returncode != 0:
                logger.error(f"Błąd podczas generowania kodu: {stderr}")
                self.decision_tree.set_node_result(code_node_id, False, f"Błąd: {stderr}")
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
            
            # Dodaj wynik generowania kodu do węzła
            self.decision_tree.set_node_result(code_node_id, True, "Wygenerowano kod")
            self.decision_tree.add_node_metric(code_node_id, "code_length", len(code))
            
            # KROK 2: Konwersja kodu z powrotem na tekst w celu weryfikacji intencji
            logger.info("Generowanie wyjaśnienia kodu w celu weryfikacji intencji użytkownika...")
            
            # Przygotuj zapytanie do modelu dla wyjaśnienia kodu
            system_prompt_explain = """Jesteś ekspertem w wyjaśnianiu kodu Python.
    Twoim zadaniem jest wyjaśnienie co robi podany kod Python w języku naturalnym.
    Wyjaśnij dokładnie, co kod robi, jakie problemy rozwiązuje i jaki jest jego cel.
    Wyjaśnij to prostym językiem, zrozumiałym dla osób bez doświadczenia w programowaniu.
    Na końcu zapytaj użytkownika, czy to jest to, czego oczekiwał."""
            
            combined_prompt_explain = f"{system_prompt_explain}\n\nWyjaśnij co robi następujący kod Python:\n```python\n{code}\n```\n\nWyjaśnienie:"
            
            # Utwórz węzeł dla wyjaśnienia kodu w drzewie decyzyjnym
            explain_node_id = self.decision_tree.add_node(
                query=prompt,
                decision_type="code_explanation",
                content=combined_prompt_explain,
                parent_id=code_node_id
            )
            
            # Użyj nowego model_manager do uruchomienia modelu z timeoutem
            from .model_manager import run_model_with_timeout
            
            logger.info("Generowanie wyjaśnienia kodu...")
            
            # Uruchom model z timeoutem 20 sekund (wyjaśnienie powinno być szybsze niż generowanie kodu)
            returncode, stdout, stderr = run_model_with_timeout(
                model_name=self.model_name,
                prompt=combined_prompt_explain,
                timeout=20
            )
            
            if returncode != 0:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                self.decision_tree.set_node_result(explain_node_id, False, f"Błąd: {stderr}")
                explanation = "Nie udało się wygenerować wyjaśnienia kodu."
            else:
                explanation = stdout.strip()
                self.decision_tree.set_node_result(explain_node_id, True, "Wygenerowano wyjaśnienie")
                self.decision_tree.add_node_metric(explain_node_id, "explanation_length", len(explanation))
            
            # Zapisz kod do pliku jeśli podano katalog
            code_id = str(uuid.uuid4())
            code_file = None
            if self.code_dir:
                code_file = self.code_dir / f"{code_id}.py"
                with open(code_file, "w", encoding="utf-8") as f:
                    f.write(code)
            
            # Zapisz drzewo decyzyjne
            self.decision_tree.save()
            
            # Zwróć wyniki
            return {
                "success": True,
                "code": code,
                "code_id": code_id,
                "code_file": str(code_file) if code_file else None,
                "explanation": explanation,
                "model": self.model_id,
                "model_name": self.model_name,
                "complexity": complexity,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania kodu: {e}")
            self.decision_tree.set_node_result(root_node_id, False, f"Błąd: {str(e)}")
            self.decision_tree.save()
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
            system_prompt = """Jesteś ekspertem w wyjaśnianiu kodu Python.
Twoim zadaniem jest wyjaśnienie działania podanego kodu w prosty i zrozumiały sposób.
Wyjaśnienie powinno być krótkie, ale kompletne, opisujące co kod robi krok po kroku."""
            
            prompt = f"Wyjaśnij działanie następującego kodu Python:\n\n```python\n{code}\n```"
            
            # Łączymy system prompt z właściwym promptem
            combined_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Użyj nowego model_manager do uruchomienia modelu z timeoutem
            from .model_manager import run_model_with_timeout
            
            logger.info("Generowanie wyjaśnienia kodu...")
            
            # Uruchom model z timeoutem 20 sekund (wyjaśnienie powinno być szybsze niż generowanie kodu)
            returncode, stdout, stderr = run_model_with_timeout(
                model_name=self.model_name,
                prompt=combined_prompt,
                timeout=20
            )
            
            if returncode != 0:
                logger.error(f"Błąd podczas generowania wyjaśnienia: {stderr}")
                return f"Nie udało się wygenerować wyjaśnienia: {stderr}"
            
            return stdout.strip()
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania wyjaśnienia: {e}")
            return f"Nie udało się wygenerować wyjaśnienia: {str(e)}"
