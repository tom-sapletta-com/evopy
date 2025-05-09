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
    
    def generate_code(self, prompt: str, query_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generuje kod Python na podstawie opisu w języku naturalnym
        
        Args:
            prompt: Opis funkcjonalności w języku naturalnym
            query_analysis: Opcjonalny wynik analizy zapytania z QueryAnalyzer
            
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

            # Dodaj informacje o zmiennych, jeśli są dostępne
            variables_info = ""
            self.variable_initializations = ""
            
            # Automatyczne wykrywanie zmiennych dla zapytań o obliczenia geometryczne
            if "pole" in prompt.lower() and ("prostokąta" in prompt.lower() or "prostokat" in prompt.lower()):
                # Automatycznie dodaj zmienne a i b dla prostokąta
                if "długości" in prompt.lower() and "szerokości" in prompt.lower():
                    a_match = re.search(r'długości\s+([a-zA-Z])\s*=\s*(\d+)', prompt, re.IGNORECASE)
                    b_match = re.search(r'szerokości\s+([a-zA-Z])\s*=\s*(\d+)', prompt, re.IGNORECASE)
                    
                    if a_match and b_match:
                        a_name, a_value = a_match.groups()
                        b_name, b_value = b_match.groups()
                        
                        # Dodaj inicjalizacje zmiennych
                        self.variable_initializations += f"    {a_name} = {a_value}  # Długość prostokąta\n"
                        self.variable_initializations += f"    {b_name} = {b_value}  # Szerokość prostokąta\n"
                        
                        variables_info += f"\nW zapytaniu zidentyfikowano zmienne:\n"
                        variables_info += f"- {a_name}: typ=numeric, wartość={a_value}\n"
                        variables_info += f"- {b_name}: typ=numeric, wartość={b_value}\n"
                    else:
                        # Jeśli nie znaleziono konkretnych zmiennych, użyj domyślnych a=10, b=5
                        self.variable_initializations += f"    a = 10  # Domyślna długość prostokąta\n"
                        self.variable_initializations += f"    b = 5   # Domyślna szerokość prostokąta\n"
                        
                        variables_info += f"\nUżyto domyślnych wartości dla prostokąta:\n"
                        variables_info += f"- a: typ=numeric, wartość=10\n"
                        variables_info += f"- b: typ=numeric, wartość=5\n"
                else:
                    # Jeśli nie znaleziono słów kluczowych, użyj domyślnych a=10, b=5
                    self.variable_initializations += f"    a = 10  # Domyślna długość prostokąta\n"
                    self.variable_initializations += f"    b = 5   # Domyślna szerokość prostokąta\n"
                    
                    variables_info += f"\nUżyto domyślnych wartości dla prostokąta:\n"
                    variables_info += f"- a: typ=numeric, wartość=10\n"
                    variables_info += f"- b: typ=numeric, wartość=5\n"
            elif "pole" in prompt.lower() and ("koła" in prompt.lower() or "kola" in prompt.lower()):
                # Automatycznie dodaj zmienną r dla koła
                r_match = re.search(r'promieniu\s+([a-zA-Z])\s*=\s*(\d+)', prompt, re.IGNORECASE)
                
                if r_match:
                    r_name, r_value = r_match.groups()
                    self.variable_initializations += f"    {r_name} = {r_value}  # Promień koła\n"
                    self.variable_initializations += f"    pi = 3.14159265359  # Wartość liczby pi\n"
                    
                    variables_info += f"\nW zapytaniu zidentyfikowano zmienne:\n"
                    variables_info += f"- {r_name}: typ=numeric, wartość={r_value}\n"
                    variables_info += f"- pi: typ=numeric, wartość=3.14159265359\n"
                else:
                    # Jeśli nie znaleziono konkretnych zmiennych, użyj domyślnego r=5
                    self.variable_initializations += f"    r = 5  # Domyślny promień koła\n"
                    self.variable_initializations += f"    pi = 3.14159265359  # Wartość liczby pi\n"
                    
                    variables_info += f"\nUżyto domyślnych wartości dla koła:\n"
                    variables_info += f"- r: typ=numeric, wartość=5\n"
                    variables_info += f"- pi: typ=numeric, wartość=3.14159265359\n"
            
            # Standardowe przetwarzanie zmiennych z analizy zapytania
            if query_analysis and query_analysis.get("has_variables", False):
                variables = query_analysis.get("variables", {})
                if variables:
                    if not variables_info:  # Jeśli nie dodano jeszcze informacji o zmiennych
                        variables_info = "\nW zapytaniu zidentyfikowano następujące zmienne:\n"
                    
                    for var_name, var_info in variables.items():
                        var_type = var_info.get("type", "unknown")
                        var_value = var_info.get("value", "nieznana")
                        
                        # Dodaj tylko jeśli zmienna nie została już dodana
                        if var_name not in self.variable_initializations:
                            variables_info += f"- {var_name}: typ={var_type}, wartość={var_value}\n"
                            
                            # Przygotuj inicjalizacje zmiennych
                            if var_type == "numeric" and "value" in var_info:
                                self.variable_initializations += f"    {var_name} = {var_info['value']}  # Zmienna z zapytania użytkownika\n"
                            elif var_type == "string" and "value" in var_info:
                                self.variable_initializations += f"    {var_name} = \"{var_info['value']}\"  # Zmienna z zapytania użytkownika\n"
                            elif var_type == "boolean" and "value" in var_info:
                                bool_value = "True" if var_info['value'] else "False"
                                self.variable_initializations += f"    {var_name} = {bool_value}  # Zmienna z zapytania użytkownika\n"
                            elif var_type == "list" and "value" in var_info:
                                list_str = ", ".join([f'"{item}"' if isinstance(item, str) else str(item) for item in var_info['value']])
                                self.variable_initializations += f"    {var_name} = [{list_str}]  # Zmienna z zapytania użytkownika\n"
            
            if variables_info:
                variables_info += "Użyj tych zmiennych w kodzie, jeśli są istotne dla rozwiązania.\n"
                variables_info += "Zmienne zostaną automatycznie zainicjalizowane w funkcji.\n"
            
            # Łączymy system prompt z właściwym promptem i informacjami o zmiennych
            combined_prompt = f"{system_prompt}{variables_info}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"

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
                code = self._wrap_in_execute_function(code, query_analysis)

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
            # Zwracamy tylko zawartość bloku kodu, bez znaczników markdown
            return code_blocks[0].strip()
        
        # Usunięcie wszystkich znaczników markdown z tekstu
        # Usuwamy linie zawierające tylko ```
        text = re.sub(r'^```(?:python)?\s*$|^```\s*$', '', text, flags=re.MULTILINE)
        
        # Jeśli nie znaleziono bloków kodu, zwróć całą odpowiedź po oczyszczeniu
        return text.strip()
    
    def _wrap_in_execute_function(self, code: str, query_analysis: Optional[Dict[str, Any]] = None) -> str:
        """
        Owija kod w funkcję execute jeśli jej nie zawiera
        
        Args:
            code: Kod Python
            query_analysis: Opcjonalny wynik analizy zapytania z QueryAnalyzer
            
        Returns:
            str: Kod z funkcją execute
        """
        # Sprawdź czy kod już zawiera funkcję execute
        if "def execute" in code:
            # Jeśli kod już zawiera funkcję execute, ale nie ma inicjalizacji zmiennych,
            # dodaj inicjalizacje zmiennych na początku funkcji
            if hasattr(self, 'variable_initializations') and self.variable_initializations:
                # Znajdź pozycję po definicji funkcji execute
                execute_pos = code.find("def execute")
                body_start = code.find(":", execute_pos) + 1
                
                # Znajdź pierwszą linię kodu po definicji funkcji
                next_line_pos = code.find("\n", body_start) + 1
                
                # Wstaw inicjalizacje zmiennych po definicji funkcji
                if next_line_pos > 0:
                    # Jeśli funkcja zawiera docstring, znajdź koniec docstringa
                    if code[next_line_pos:].strip().startswith('"""'):
                        docstring_end = code.find('"""', next_line_pos + 3) + 3
                        next_line_pos = code.find("\n", docstring_end) + 1
                    
                    code = code[:next_line_pos] + self.variable_initializations + code[next_line_pos:]
            
            return code
        
        # Dodaj wcięcie do każdej linii kodu
        indented_code = "\n".join(["    " + line for line in code.split("\n")])
        
        # Przygotuj parametry funkcji execute na podstawie analizy zmiennych
        params = ""
        param_docs = ""
        
        if query_analysis and query_analysis.get("has_variables", False):
            variables = query_analysis.get("variables", {})
            param_list = []
            param_doc_list = []
            
            for var_name, var_info in variables.items():
                # Pomiń zmienne typu 'unknown' i zmienne bez wartości
                if var_info.get("type") != "unknown" and "value" in var_info:
                    param_list.append(var_name)
                    var_type = var_info.get("type")
                    var_type_str = "float/int" if var_type == "numeric" else var_type
                    param_doc_list.append(f"        {var_name} ({var_type_str}): Zmienna {var_name}")
            
            if param_list:
                params = ", ".join(param_list)
                param_docs = "\n" + "\n".join(param_doc_list)
        
        # Przygotuj inicjalizacje zmiennych, jeśli są dostępne
        variable_init_code = ""
        if hasattr(self, 'variable_initializations') and self.variable_initializations:
            variable_init_code = self.variable_initializations
        
        # Owij kod w funkcję execute z odpowiednimi parametrami
        if params:
            wrapped_code = f"def execute({params}):\n"
            wrapped_code += f"    \"\"\"\n"
            wrapped_code += f"    Funkcja wykonująca zadanie na podstawie opisu użytkownika\n\n"
            wrapped_code += f"    Args:{param_docs}\n\n"
            wrapped_code += f"    Returns:\n"
            wrapped_code += f"        Wynik działania funkcji\n"
            wrapped_code += f"    \"\"\"\n"
            # Dodaj inicjalizacje zmiennych przed kodem
            wrapped_code += variable_init_code
            wrapped_code += f"    # Kod wygenerowany na podstawie opisu użytkownika\n"
            wrapped_code += f"{indented_code}\n\n"
            wrapped_code += f"    # Zwróć wynik jeśli funkcja nic nie zwraca\n"
            wrapped_code += f"    return \"Wykonano zadanie\"\n"
        else:
            wrapped_code = f"def execute():\n"
            wrapped_code += f"    \"\"\"\n"
            wrapped_code += f"    Funkcja wykonująca zadanie na podstawie opisu użytkownika\n\n"
            wrapped_code += f"    Returns:\n"
            wrapped_code += f"        Wynik działania funkcji\n"
            wrapped_code += f"    \"\"\"\n"
            # Dodaj inicjalizacje zmiennych przed kodem
            wrapped_code += variable_init_code
            wrapped_code += f"    # Kod wygenerowany na podstawie opisu użytkownika\n"
            wrapped_code += f"{indented_code}\n\n"
            wrapped_code += f"    # Zwróć wynik jeśli funkcja nic nie zwraca\n"
            wrapped_code += f"    return \"Wykonano zadanie\"\n"
        
        return wrapped_code
