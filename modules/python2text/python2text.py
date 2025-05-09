#!/usr/bin/env python3
"""
Python2Text - Moduł do konwersji kodu Python na opis w języku naturalnym

Ten moduł wykorzystuje modele językowe do konwersji kodu Python
na opis funkcjonalności w języku naturalnym.
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

logger = logging.getLogger("evo-assistant.python2text")

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

def get_model_config(model_id: str = None) -> Dict[str, Any]:
    """
    Zwraca konfigurację wybranego modelu lub aktywnego modelu
    
    Args:
        model_id: Identyfikator modelu (opcjonalnie)
        
    Returns:
        Dict: Konfiguracja modelu
    """
    if model_id is None:
        model_id = os.getenv("ACTIVE_MODEL", "deepsek")
    
    models = get_available_models()
    for model in models:
        if model["id"] == model_id:
            return model
    
    # Jeśli nie znaleziono modelu, zwróć domyślny
    logger.warning(f"Nie znaleziono modelu {model_id}, używam domyślnego (deepsek)")
    return next((m for m in models if m["id"] == "deepsek"), models[0])


class Python2Text:
    """Klasa do konwersji kodu Python na opis w języku naturalnym"""
    
    def __init__(self, model_id: str = None, output_dir: Path = None):
        """
        Inicjalizacja konwertera Python-na-tekst
        
        Args:
            model_id: Identyfikator modelu do użycia (deepsek, llama, bielik)
            output_dir: Katalog do zapisywania wygenerowanych opisów
        """
        self.model_config = get_model_config(model_id)
        self.model_id = self.model_config["id"]
        self.model_name = self.model_config["name"]
        self.output_dir = output_dir
        
        if self.output_dir:
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Inicjalizacja drzewa decyzyjnego
        self.decision_tree = create_decision_tree(name=f"Python2Text-{self.model_name}")
        
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
                
                # Próba pobrania modelu
                try:
                    pull_cmd = ["ollama", "pull", self.model_name]
                    pull_result = subprocess.run(pull_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
                    
                    if pull_result.returncode != 0:
                        raise Exception(f"Błąd podczas pobierania modelu: {pull_result.stderr}")
                    
                    logger.info(f"Model {self.model_name} został pomyślnie pobrany")
                except Exception as e:
                    logger.error(f"Nie można pobrać modelu {self.model_name}: {str(e)}")
                    
                    # Próba znalezienia alternatywnego modelu
                    available_models = result.stdout.strip().split('\n')[1:] if result.stdout.strip() else []
                    if available_models:
                        # Wybierz pierwszy dostępny model
                        alt_model = available_models[0].split()[0].split(':')[0]
                        logger.warning(f"Używanie alternatywnego modelu: {alt_model}")
                        self.model_name = alt_model
                        return True
                    else:
                        logger.error("Brak dostępnych modeli Ollama")
                        return False
            else:
                logger.info(f"Model {self.model_name} jest dostępny")
            
            return True
            
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas sprawdzania modelu: {str(e)}")
            return False
    
    def _calculate_complexity(self, code: str) -> float:
        """
        Oblicza złożoność kodu Python na podstawie różnych metryk
        
        Args:
            code: Kod Python
            
        Returns:
            float: Wartość złożoności od 0.0 do 1.0
        """
        # Prosta heurystyka złożoności oparta na długości, liczbie funkcji, klas i importów
        complexity = 0.0
        
        # Długość kodu (0.0-0.2)
        length_score = min(len(code) / 1000.0, 1.0) * 0.2
        complexity += length_score
        
        # Liczba funkcji i klas (0.0-0.3)
        function_count = len(re.findall(r'def\s+\w+\s*\(', code))
        class_count = len(re.findall(r'class\s+\w+\s*\(', code))
        structure_score = min((function_count + class_count) / 10.0, 1.0) * 0.3
        complexity += structure_score
        
        # Liczba importów (0.0-0.2)
        import_count = len(re.findall(r'import\s+\w+', code)) + len(re.findall(r'from\s+\w+\s+import', code))
        import_score = min(import_count / 10.0, 1.0) * 0.2
        complexity += import_score
        
        # Złożoność strukturalna (0.0-0.3) - liczba pętli, warunków, list comprehension
        loops = len(re.findall(r'for\s+\w+\s+in', code)) + len(re.findall(r'while\s+', code))
        conditions = len(re.findall(r'if\s+', code)) + len(re.findall(r'elif\s+', code)) + len(re.findall(r'else:', code))
        list_comp = len(re.findall(r'\[\s*\w+\s+for\s+', code))
        
        control_flow_score = min((loops + conditions + list_comp) / 15.0, 1.0) * 0.3
        complexity += control_flow_score
        
        return round(complexity, 2)
    
    def generate_description(self, code: str, detail_level: str = "medium") -> Dict[str, Any]:
        """
        Generuje opis kodu Python w języku naturalnym
        
        Args:
            code: Kod Python do opisania
            detail_level: Poziom szczegółowości opisu ("low", "medium", "high")
            
        Returns:
            Dict: Wygenerowany opis, metadane i dodatkowe informacje
        """
        logger.info(f"Analizowanie kodu Python o długości {len(code)} znaków...")
        
        # Oblicz złożoność kodu
        complexity = self._calculate_complexity(code)
        
        # Utwórz węzeł główny dla kodu w drzewie decyzyjnym
        root_node_id = self.decision_tree.add_node(
            query="Generowanie opisu kodu",
            decision_type="code_analysis",
            content=f"Analizowanie kodu Python o długości {len(code)} znaków"
        )
        
        # Dodaj metrykę złożoności do węzła
        self.decision_tree.add_node_metric(root_node_id, "complexity", complexity)
        self.decision_tree.add_node_metric(root_node_id, "code_length", len(code))
        self.decision_tree.add_node_metric(root_node_id, "model", self.model_id)
        self.decision_tree.add_node_metric(root_node_id, "detail_level", detail_level)
        
        # Sprawdź, czy model jest dostępny
        if not self.ensure_model_available():
            # Zapisz informację o błędzie w drzewie decyzyjnym
            self.decision_tree.set_node_result(root_node_id, False, f"Model {self.model_name} nie jest dostępny")
            self.decision_tree.save()
            
            return {
                "success": False,
                "description": "",
                "error": f"Model {self.model_name} nie jest dostępny"
            }
        
        # Sprawdź czy kod jest pusty
        if not code or code.strip() == "":
            logger.warning("Otrzymano pusty kod")
            return {
                "success": False,
                "description": "Nie można wygenerować opisu dla pustego kodu.",
                "error": "Kod jest pusty"
            }
        
        try:
            logger.info("Generowanie opisu kodu...")
            
            # Przygotuj zapytanie do modelu dla generowania opisu
            detail_instructions = {
                "low": "Wygeneruj krótki, ogólny opis kodu w 2-3 zdaniach.",
                "medium": "Wygeneruj szczegółowy opis kodu, wyjaśniając główne funkcje i ich działanie.",
                "high": "Wygeneruj bardzo szczegółowy opis kodu, wyjaśniając każdą funkcję, klasę i ich działanie krok po kroku."
            }
            
            detail_instruction = detail_instructions.get(detail_level, detail_instructions["medium"])
            
            system_prompt = f"""Jesteś ekspertem w analizie kodu Python i wyjaśnianiu go w języku naturalnym.
Twoim zadaniem jest wygenerowanie opisu podanego kodu Python.
{detail_instruction}
Wyjaśnij, co kod robi, jakie problemy rozwiązuje i jak działa.
Używaj prostego języka, zrozumiałego dla osób bez doświadczenia w programowaniu."""
            
            # Łączymy system prompt z kodem
            combined_prompt = f"{system_prompt}\n\nKod Python do opisania:\n```python\n{code}\n```\n\nOpis kodu:"
            
            # Utwórz węzeł dla generowania opisu w drzewie decyzyjnym
            description_node_id = self.decision_tree.add_node(
                query="Generowanie opisu",
                decision_type="description_generation",
                content=combined_prompt,
                parent_id=root_node_id
            )
            
            # Wywołaj model Ollama dla generowania opisu
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania opisu: {stderr}")
                self.decision_tree.set_node_result(description_node_id, False, f"Błąd: {stderr}")
                return {
                    "success": False,
                    "description": "",
                    "error": stderr
                }
            
            # Wyodrębnij opis z odpowiedzi
            description = stdout.strip()
            
            # Dodaj wynik generowania opisu do węzła
            self.decision_tree.set_node_result(description_node_id, True, "Wygenerowano opis")
            self.decision_tree.add_node_metric(description_node_id, "description_length", len(description))
            
            # Zapisz opis do pliku jeśli podano katalog
            description_id = str(uuid.uuid4())
            description_file = None
            if self.output_dir:
                description_file = self.output_dir / f"{description_id}.txt"
                with open(description_file, "w", encoding="utf-8") as f:
                    f.write(description)
            
            # Zapisz drzewo decyzyjne
            self.decision_tree.save()
            
            # Zwróć wyniki
            return {
                "success": True,
                "description": description,
                "description_id": description_id,
                "description_file": str(description_file) if description_file else None,
                "model": self.model_id,
                "model_name": self.model_name,
                "complexity": complexity,
                "detail_level": detail_level,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania opisu: {e}")
            self.decision_tree.set_node_result(root_node_id, False, f"Błąd: {str(e)}")
            self.decision_tree.save()
            return {
                "success": False,
                "description": "",
                "error": str(e)
            }
    
    def generate_documentation(self, code: str) -> Dict[str, Any]:
        """
        Generuje dokumentację dla kodu Python (docstringi, komentarze)
        
        Args:
            code: Kod Python do udokumentowania
            
        Returns:
            Dict: Wygenerowana dokumentacja, metadane i dodatkowe informacje
        """
        logger.info(f"Generowanie dokumentacji dla kodu Python o długości {len(code)} znaków...")
        
        # Oblicz złożoność kodu
        complexity = self._calculate_complexity(code)
        
        # Utwórz węzeł główny dla kodu w drzewie decyzyjnym
        root_node_id = self.decision_tree.add_node(
            query="Generowanie dokumentacji kodu",
            decision_type="documentation_generation",
            content=f"Generowanie dokumentacji dla kodu Python o długości {len(code)} znaków"
        )
        
        # Dodaj metrykę złożoności do węzła
        self.decision_tree.add_node_metric(root_node_id, "complexity", complexity)
        self.decision_tree.add_node_metric(root_node_id, "code_length", len(code))
        self.decision_tree.add_node_metric(root_node_id, "model", self.model_id)
        
        # Sprawdź, czy model jest dostępny
        if not self.ensure_model_available():
            # Zapisz informację o błędzie w drzewie decyzyjnym
            self.decision_tree.set_node_result(root_node_id, False, f"Model {self.model_name} nie jest dostępny")
            self.decision_tree.save()
            
            return {
                "success": False,
                "documented_code": "",
                "error": f"Model {self.model_name} nie jest dostępny"
            }
        
        # Sprawdź czy kod jest pusty
        if not code or code.strip() == "":
            logger.warning("Otrzymano pusty kod")
            return {
                "success": False,
                "documented_code": "",
                "error": "Kod jest pusty"
            }
        
        try:
            logger.info("Generowanie dokumentacji kodu...")
            
            # Przygotuj zapytanie do modelu dla generowania dokumentacji
            system_prompt = """Jesteś ekspertem w dokumentowaniu kodu Python.
Twoim zadaniem jest dodanie docstringów i komentarzy do podanego kodu Python.
Dodaj docstringi w formacie Google dla wszystkich funkcji, klas i metod.
Dodaj krótkie komentarze wyjaśniające skomplikowane fragmenty kodu.
Nie zmieniaj logiki kodu, tylko dodaj dokumentację."""
            
            # Łączymy system prompt z kodem
            combined_prompt = f"{system_prompt}\n\nKod Python do udokumentowania:\n```python\n{code}\n```\n\nUdokumentowany kod Python:"
            
            # Utwórz węzeł dla generowania dokumentacji w drzewie decyzyjnym
            doc_node_id = self.decision_tree.add_node(
                query="Generowanie dokumentacji",
                decision_type="documentation_generation",
                content=combined_prompt,
                parent_id=root_node_id
            )
            
            # Wywołaj model Ollama dla generowania dokumentacji
            cmd = [
                "ollama", "run", self.model_name,
                combined_prompt
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Błąd podczas generowania dokumentacji: {stderr}")
                self.decision_tree.set_node_result(doc_node_id, False, f"Błąd: {stderr}")
                return {
                    "success": False,
                    "documented_code": "",
                    "error": stderr
                }
            
            # Wyodrębnij udokumentowany kod z odpowiedzi
            documented_code = self._extract_code(stdout)
            
            # Dodaj wynik generowania dokumentacji do węzła
            self.decision_tree.set_node_result(doc_node_id, True, "Wygenerowano dokumentację")
            
            # Zapisz udokumentowany kod do pliku jeśli podano katalog
            doc_id = str(uuid.uuid4())
            doc_file = None
            if self.output_dir:
                doc_file = self.output_dir / f"{doc_id}_documented.py"
                with open(doc_file, "w", encoding="utf-8") as f:
                    f.write(documented_code)
            
            # Zapisz drzewo decyzyjne
            self.decision_tree.save()
            
            # Zwróć wyniki
            return {
                "success": True,
                "documented_code": documented_code,
                "doc_id": doc_id,
                "doc_file": str(doc_file) if doc_file else None,
                "model": self.model_id,
                "model_name": self.model_name,
                "complexity": complexity,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania dokumentacji: {e}")
            self.decision_tree.set_node_result(root_node_id, False, f"Błąd: {str(e)}")
            self.decision_tree.save()
            return {
                "success": False,
                "documented_code": "",
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
