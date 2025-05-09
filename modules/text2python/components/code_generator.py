#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CodeGenerator - Komponent odpowiedzialny za generowanie kodu Python
na podstawie opisu w języku naturalnym.
"""

import re
import logging
import subprocess
from typing import Dict, Any, List, Optional

class CodeGenerator:
    """
    Klasa odpowiedzialna za generowanie kodu Python na podstawie
    opisu w języku naturalnym.
    """
    
    def __init__(self, model_name: str = "llama3", config: Optional[Dict[str, Any]] = None):
        """
        Inicjalizacja generatora kodu
        
        Args:
            model_name: Nazwa modelu językowego do użycia
            config: Dodatkowa konfiguracja
        """
        self.model_name = model_name
        self.config = config or {}
        self.logger = logging.getLogger('CodeGenerator')
    
    def generate_code(self, prompt: str) -> Dict[str, Any]:
        """
        Generuje kod Python na podstawie opisu w języku naturalnym
        
        Args:
            prompt: Opis funkcjonalności w języku naturalnym
            
        Returns:
            Dict[str, Any]: Wygenerowany kod i metadane
        """
        try:
            self.logger.info(f"Generowanie kodu dla zapytania: {prompt[:50]}...")
            
            # Przygotuj zapytanie do modelu dla generowania kodu
            system_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""

            # Łączymy system prompt z właściwym promptem, ponieważ Ollama nie obsługuje flagi --system
            combined_prompt = f"{system_prompt}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"

            # Wywołaj model Ollama dla generowania kodu
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

            return {
                "success": True,
                "code": code,
                "raw_response": stdout
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
