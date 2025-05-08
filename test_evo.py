#!/usr/bin/env python3
"""
test_evo.py - Skrypt testujący Ewolucyjny Asystent

Ten skrypt testuje różne scenariusze użycia Ewolucyjnego Asystenta,
symulując interakcję użytkownika i monitorując zachowanie systemu.
"""

import os
import sys
import time
import json
import signal
import subprocess
import threading
import pexpect
from datetime import datetime
from pathlib import Path

# Konfiguracja
HOME_DIR = Path.home()
ASSISTANT_DIR = HOME_DIR / ". evopy"
LOG_DIR = Path("./logs")
RESULTS_DIR = Path("./test_results")
TIMEOUT = 300  # 5 minut na każdy test
MAX_RESPONSE_TIME = 60  # Maksymalny czas oczekiwania na odpowiedź (w sekundach)
SCRIPT_PATH = "./evo.py"

# Kolory dla terminala
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# Utwórz katalogi na logi i wyniki, jeśli nie istnieją
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Funkcje pomocnicze
def log_message(message, level="INFO"):
    """Zapisuje wiadomość do pliku logów z odpowiednim poziomem"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOG_DIR / f"test_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, "a") as f:
        f.write(f"[{timestamp}] [{level}] {message}\n")
    
    # Wyświetlenie na konsoli
    color_map = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED,
        "DEBUG": Colors.HEADER
    }
    
    color = color_map.get(level, Colors.END)
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.END}")

def save_test_result(test_name, status, details=None):
    """Zapisuje wynik testu do pliku JSON"""
    result_file = RESULTS_DIR / f"{test_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    result = {
        "test_name": test_name,
        "status": status,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    
    with open(result_file, "w") as f:
        json.dump(result, f, indent=2)
    
    log_message(f"Zapisano wynik testu '{test_name}': {status}", level="INFO")

def run_command(command, timeout=60):
    """Uruchamia komendę i zwraca jej wynik"""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=True
        )
        return result.stdout, result.stderr, 0
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode
    except subprocess.TimeoutExpired as e:
        return "", f"Timeout po {timeout} sekundach", -1

def wait_for_prompt(child, timeout=5):
    """Czeka na pojawienie się promptu asystenta"""
    try:
        child.expect([r"> ", pexpect.EOF, pexpect.TIMEOUT], timeout=timeout)
        return True
    except pexpect.exceptions.TIMEOUT:
        log_message("Timeout podczas oczekiwania na prompt asystenta", level="WARNING")
        return False
    except pexpect.exceptions.EOF:
        log_message("Asystent zakończył działanie nieoczekiwanie", level="ERROR")
        return False

def send_message_and_wait(child, message, expect_patterns=None, timeout=MAX_RESPONSE_TIME):
    """Wysyła wiadomość do asystenta i czeka na odpowiedź"""
    log_message(f"Wysyłanie: '{message}'", level="DEBUG")
    
    # Wyślij wiadomość
    child.sendline(message)
    
    # Jeśli wzorce odpowiedzi nie zostały określone, czekaj na prompt
    if not expect_patterns:
        return wait_for_prompt(child, timeout)
    
    # W przeciwnym razie czekaj na określone wzorce
    try:
        index = child.expect(expect_patterns, timeout=timeout)
        log_message(f"Otrzymano odpowiedź pasującą do wzorca {index}", level="DEBUG")
        return index
    except pexpect.exceptions.TIMEOUT:
        log_message("Timeout podczas oczekiwania na odpowiedź", level="WARNING")
        return -1
    except pexpect.exceptions.EOF:
        log_message("Asystent zakończył działanie nieoczekiwanie", level="ERROR")
        return -2

# Klasy testów
class AssistantTest:
    """Klasa bazowa dla testów asystenta"""
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.child = None
        self.result = {
            "status": "NOT_RUN",
            "steps": [],
            "error": None,
            "start_time": None,
            "end_time": None,
            "duration": None
        }
    
    def setup(self):
        """Przygotowanie do testu"""
        log_message(f"Rozpoczynam test: {self.name}", level="INFO")
        log_message(f"Opis: {self.description}", level="INFO")
        
        self.result["start_time"] = datetime.now().isoformat()
        
        # Uruchom asystenta z pexpect
        try:
            self.child = pexpect.spawn(f"python {SCRIPT_PATH}", encoding="utf-8")
            self.child.logfile = open(LOG_DIR / f"{self.name}_{datetime.now().strftime('%Y%m%d%H%M%S')}_interaction.log", "w")
            
            # Poczekaj na inicjalizację asystenta (maksymalnie 30 sekund)
            self.child.expect(["Asystent gotowy do pracy!", pexpect.EOF, pexpect.TIMEOUT], timeout=30)
            
            # Poczekaj na pojawienie się promptu
            if not wait_for_prompt(self.child):
                self.result["status"] = "FAILED"
                self.result["error"] = "Timeout podczas inicjalizacji asystenta"
                return False
            
            return True
        
        except Exception as e:
            self.result["status"] = "FAILED"
            self.result["error"] = f"Błąd podczas uruchamiania asystenta: {str(e)}"
            log_message(f"Błąd podczas uruchamiania asystenta: {str(e)}", level="ERROR")
            return False
    
    def run(self):
        """Wykonaj test - do nadpisania w klasach pochodnych"""
        pass
    
    def teardown(self):
        """Sprzątanie po teście"""
        if self.child:
            # Zakończ asystenta
            try:
                self.child.sendline("/exit")
                self.child.expect([pexpect.EOF, pexpect.TIMEOUT], timeout=5)
            except:
                pass
            
            # Zamknij plik logów
            if self.child.logfile:
                self.child.logfile.close()
            
            # Zabij proces, jeśli nadal działa
            try:
                self.child.kill(signal.SIGTERM)
            except:
                pass
        
        self.result["end_time"] = datetime.now().isoformat()
        
        # Oblicz czas trwania testu
        if self.result["start_time"]:
            start = datetime.fromisoformat(self.result["start_time"])
            end = datetime.fromisoformat(self.result["end_time"])
            self.result["duration"] = (end - start).total_seconds()
        
        # Zapisz wynik testu
        save_test_result(self.name, self.result["status"], self.result)
        
        log_message(f"Zakończono test: {self.name} - {self.result['status']}", 
                   level="SUCCESS" if self.result["status"] == "PASSED" else "ERROR")
    
    def execute(self):
        """Wykonaj pełny test: setup, run, teardown"""
        if not self.setup():
            self.teardown()
            return False
        
        try:
            result = self.run()
            self.result["status"] = "PASSED" if result else "FAILED"
        except Exception as e:
            self.result["status"] = "FAILED"
            self.result["error"] = f"Wyjątek podczas testu: {str(e)}"
            log_message(f"Wyjątek podczas testu {self.name}: {str(e)}", level="ERROR")
        
        self.teardown()
        return self.result["status"] == "PASSED"
    
    def add_step(self, name, status, details=None):
        """Dodaje krok do wyniku testu"""
        step = {
            "name": name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        
        self.result["steps"].append(step)
        
        log_level = "SUCCESS" if status == "PASSED" else "ERROR"
        log_message(f"Krok '{name}': {status}", level=log_level)

class BasicFunctionalityTest(AssistantTest):
    """Test podstawowej funkcjonalności asystenta"""
    
    def __init__(self):
        super().__init__(
            "basic_functionality",
            "Test podstawowej funkcjonalności asystenta: inicjalizacja, odpowiedzi na proste pytania"
        )
    
    def run(self):
        # Test prostego zapytania
        self.add_step("init", "RUNNING", {"message": "Sprawdzanie inicjalizacji asystenta"})
        
        # Wyślij proste zapytanie
        simple_query = "Powiedz cześć"
        success = send_message_and_wait(self.child, simple_query)
        
        if not success:
            self.add_step("simple_query", "FAILED", {"message": "Nie otrzymano odpowiedzi na proste zapytanie"})
            return False
        
        self.add_step("simple_query", "PASSED", {"message": "Otrzymano odpowiedź na proste zapytanie"})
        
        # Test komendy pomocy
        help_command = "/help"
        success = send_message_and_wait(self.child, help_command)
        
        if not success:
            self.add_step("help_command", "FAILED", {"message": "Nie otrzymano odpowiedzi na komendę pomocy"})
            return False
        
        self.add_step("help_command", "PASSED", {"message": "Otrzymano odpowiedź na komendę pomocy"})
        
        # Test tworzenia nowej konwersacji
        new_command = "/new"
        success = send_message_and_wait(self.child, new_command)
        
        if not success:
            self.add_step("new_conversation", "FAILED", {"message": "Nie udało się utworzyć nowej konwersacji"})
            return False
        
        self.add_step("new_conversation", "PASSED", {"message": "Utworzono nową konwersację"})
        
        return True

class CodeGenerationTest(AssistantTest):
    """Test generowania kodu Python"""
    
    def __init__(self):
        super().__init__(
            "code_generation",
            "Test generowania kodu Python i wykrywania go przez asystenta"
        )
    
    def run(self):
        # Wygeneruj prosty kod Python
        python_query = "Napisz prosty skrypt w Pythonie, który wyświetla liczby od 1 do 10"
        
        self.add_step("python_request", "RUNNING", {"message": "Wysyłanie zapytania o kod Python"})
        
        success = send_message_and_wait(
            self.child, 
            python_query, 
            expect_patterns=["```python", "AI:", pexpect.TIMEOUT],
            timeout=60
        )
        
        if success != 0 and success != 1:
            self.add_step("python_response", "FAILED", {"message": "Nie otrzymano kodu Python"})
            return False
        
        self.add_step("python_response", "PASSED", {"message": "Otrzymano kod Python"})
        
        # Wygeneruj prosty plik Docker Compose
        docker_query = "Stwórz prosty plik Docker Compose z usługą Nginx"
        
        self.add_step("docker_request", "RUNNING", {"message": "Wysyłanie zapytania o Docker Compose"})
        
        success = send_message_and_wait(
            self.child, 
            docker_query, 
            expect_patterns=["```yaml", "```docker-compose", "AI:", pexpect.TIMEOUT],
            timeout=60
        )
        
        if success != 0 and success != 1 and success != 2:
            self.add_step("docker_response", "FAILED", {"message": "Nie otrzymano kodu Docker Compose"})
            return False
        
        self.add_step("docker_response", "PASSED", {"message": "Otrzymano kod Docker Compose"})
        
        # Odrzuć zapisanie projektu (to przetestujemy w innym teście)
        self.child.expect(["Czy chcesz zapisać ten kod", pexpect.TIMEOUT], timeout=10)
        self.child.sendline("n")
        
        # Poczekaj na prompt
        wait_for_prompt(self.child)
        
        return True

class ProjectCreationTest(AssistantTest):
    """Test tworzenia projektu Docker Compose"""
    
    def __init__(self):
        super().__init__(
            "project_creation",
            "Test tworzenia projektu Docker Compose i zarządzania nim"
        )
    
    def run(self):
        # Wygeneruj plik Docker Compose
        docker_query = "Stwórz prosty projekt Docker Compose z bazą danych PostgreSQL i aplikacją Python Flask"
        
        self.add_step("docker_request", "RUNNING", {"message": "Wysyłanie zapytania o projekt Docker Compose"})
        
        success = send_message_and_wait(
            self.child, 
            docker_query, 
            expect_patterns=["```yaml", "```docker-compose", "AI:", pexpect.TIMEOUT],
            timeout=60
        )
        
        if success != 0 and success != 1 and success != 2:
            self.add_step("docker_response", "FAILED", {"message": "Nie otrzymano kodu Docker Compose"})
            return False
        
        self.add_step("docker_response", "PASSED", {"message": "Otrzymano kod Docker Compose"})
        
        # Akceptuj zapisanie projektu
        self.child.expect(["Czy chcesz zapisać ten kod", pexpect.TIMEOUT], timeout=10)
        self.child.sendline("t")
        
        # Podaj nazwę projektu
        self.child.expect(["Podaj nazwę projektu", pexpect.TIMEOUT], timeout=10)
        project_name = f"test-project-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.child.sendline(project_name)
        
        # Sprawdź czy projekt został utworzony
        self.child.expect(["Utworzono projekt", pexpect.TIMEOUT], timeout=10)
        
        # Odrzuć uruchomienie projektu
        self.child.expect(["Czy chcesz uruchomić ten projekt", pexpect.TIMEOUT], timeout=10)
        self.child.sendline("n")
        
        # Poczekaj na prompt
        wait_for_prompt(self.child)
        
        # Sprawdź listę projektów
        self.add_step("list_projects", "RUNNING", {"message": "Sprawdzanie listy projektów"})
        
        success = send_message_and_wait(self.child, "/projects")
        
        if not success:
            self.add_step("list_projects", "FAILED", {"message": "Nie otrzymano listy projektów"})
            return False
        
        # Sprawdź czy nasz projekt jest widoczny
        if project_name not in self.child.before:
            self.add_step("project_visibility", "FAILED", {"message": "Utworzony projekt nie jest widoczny na liście"})
            return False
        
        self.add_step("project_visibility", "PASSED", {"message": "Utworzony projekt jest widoczny na liście"})
        
        return True

def run_all_tests():
    """Uruchamia wszystkie testy"""
    log_message("Rozpoczynam uruchamianie wszystkich testów", level="INFO")
    
    tests = [
        BasicFunctionalityTest(),
        CodeGenerationTest(),
        ProjectCreationTest()
    ]
    
    results = {
        "total": len(tests),
        "passed": 0,
        "failed": 0,
        "tests": []
    }
    
    for test in tests:
        success = test.execute()
        
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        results["tests"].append({
            "name": test.name,
            "status": test.result["status"],
            "error": test.result["error"]
        })
    
    # Zapisz podsumowanie
    summary_file = RESULTS_DIR / f"summary_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
    
    with open(summary_file, "w") as f:
        json.dump(results, f, indent=2)
    
    log_message(f"Zakończono uruchamianie wszystkich testów. Wyniki: {results['passed']} przeszło, {results['failed']} nie przeszło", 
               level="INFO")
    
    return results

if __name__ == "__main__":
    log_message("Uruchamianie skryptu testującego Ewolucyjny Asystent", level="INFO")
    
    # Sprawdź czy skrypt asystenta istnieje
    if not os.path.exists(SCRIPT_PATH):
        log_message(f"Nie znaleziono skryptu asystenta pod ścieżką: {SCRIPT_PATH}", level="ERROR")
        sys.exit(1)
    
    # Uruchom wszystkie testy
    results = run_all_tests()
    
    # Wyświetl podsumowanie
    print("\n" + "="*80)
    print(f"{Colors.BOLD}PODSUMOWANIE TESTÓW{Colors.END}")
    print("="*80)
    print(f"Łącznie testów: {results['total']}")
    print(f"{Colors.GREEN}Przeszło: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Nie przeszło: {results['failed']}{Colors.END}")
    print("="*80)
    
    # Wyświetl szczegóły testów, które nie przeszły
    if results["failed"] > 0:
        print(f"\n{Colors.BOLD}Testy, które nie przeszły:{Colors.END}")
        for test in results["tests"]:
            if test["status"] != "PASSED":
                print(f"{Colors.RED}- {test['name']}: {test['error']}{Colors.END}")
    
    # Zakończ z odpowiednim kodem
    sys.exit(0 if results["failed"] == 0 else 1)