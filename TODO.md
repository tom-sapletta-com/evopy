# Prompty i Wytyczne do Poprawy Kodu Evopy

## 1. Prompty dla Modułu Text2Python

### Prompt 1: Ulepszony Prompt dla Generowania Kodu
```
Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.

Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.

ZAWSZE przestrzegaj następujących zasad:
1. Dla prostych operacji matematycznych, zawsze używaj zmiennych (np. 'x = 1; y = 2; result = x + y')
2. Dodawaj odpowiednie obsługi błędów i walidację danych wejściowych
3. Unikaj używania bezpośrednio 'import *' - importuj tylko konkretne funkcje/klasy
4. Zawsze dodawaj krótkie komentarze wyjaśniające najważniejsze części kodu
5. Upewnij się, że kod jest bezpieczny i nie wykonuje niebezpiecznych operacji

Utwórz funkcję Python, która realizuje następujące zadanie:
{prompt}
```

### Prompt 2: Instrukcje dla Analizy i Wyjaśniania Kodu
```
Jesteś ekspertem w analizie i wyjaśnianiu kodu Python.
Twoim zadaniem jest dokładne wyjaśnienie co robi podany kod i sprawdzenie, czy jest zgodny z intencją użytkownika.

Przeprowadź analizę kodu w następujących krokach:
1. Wyjaśnij funkcjonalność kodu w prostym języku, zrozumiałym dla osób bez doświadczenia w programowaniu
2. Zidentyfikuj potencjalne problemy: błędy składniowe, logiczne, bezpieczeństwa lub wydajności
3. Zaproponuj konkretne ulepszenia, które mogłyby poprawić kod
4. Oceń, czy kod realizuje zadanie opisane w zapytaniu użytkownika

Na końcu zapytaj użytkownika, czy wyjaśnienie jest jasne i czy kod spełnia jego oczekiwania.

Zapytanie użytkownika: {prompt}
Kod Python do analizy:
```python
{code}
```
```

### Prompt 3: Prompt dla Porównania Alternatywnych Implementacji
```
Jesteś ekspertem w programowaniu Python i optymalizacji kodu.
Twoim zadaniem jest porównanie dwóch alternatywnych implementacji rozwiązujących ten sam problem.

Na podstawie zapytania użytkownika:
{prompt}

Rozważ następujące dwie implementacje:

Implementacja 1:
```python
{code1}
```

Implementacja 2:
```python
{code2}
```

Przeprowadź dogłębną analizę porównawczą:
1. Porównaj czytelność i łatwość zrozumienia obu implementacji
2. Oceń efektywność czasową i pamięciową obu rozwiązań
3. Zidentyfikuj potencjalne problemy w każdej implementacji
4. Wskaż, która implementacja lepiej realizuje intencję użytkownika i dlaczego
5. Zaproponuj ewentualne usprawnienia dla lepszej implementacji

Zdecyduj, która implementacja jest lepsza, i uzasadnij swój wybór konkretnymi argumentami.
```

## 2. Wytyczne dla Poprawy Modułu DockerSandbox

### Wytyczne do Poprawy Bezpieczeństwa Piaskownicy:

1. **Izolacja Zasobów**: Zaimplementuj ścisłe limity dla kontenerów Docker:
   - Limit CPU na poziomie 0.5 rdzenia
   - Limit pamięci RAM na 512MB
   - Limit przestrzeni dyskowej na 1GB
   - Limit procesów na 50
   - Limit deskryptorów plików na 1024

2. **Zarządzanie Timeoutami**:
   - Dodaj dwupoziomowy system timeoutów: soft timeout (sygnał SIGTERM) i hard timeout (SIGKILL)
   - Implementuj watchdog do monitorowania długo działających procesów

3. **Weryfikacja Bezpieczeństwa Kodu**:
   - Skanuj kod pod kątem potencjalnie niebezpiecznych operacji (jak subprocess z shell=True, eval(), exec())
   - Implementuj białą listę dozwolonych modułów i funkcji
   - Blokuj operacje sieciowe, dostęp do systemu plików poza wyznaczonym katalogiem

4. **Obsługa Błędów i Wyjątków**:
   - Popraw obsługę wyjątków, szczególnie w blokach catch, aby uniknąć błędów z niezdefiniowanymi zmiennymi
   - Dodaj mechanizm raportowania i logowania błędów z piaskownicy
   - Zapewnij czysty rollback w przypadku niepowodzenia

## 3. Wytyczne do Rozwijania Ewolucyjnych Zdolności Asystenta

1. **Mechanizm Uczenia się z Interakcji**:
   - Zapisuj feedback użytkownika odnośnie generowanego kodu
   - Implementuj system wagowy dla technik generowania kodu, które otrzymały pozytywny feedback
   - Automatycznie dostosowuj prompty na podstawie poprzednich sukcesów i porażek

2. **Rozpoznawanie Złożoności Zapytań**:
   - Utwórz system klasyfikacji zapytań na podstawie złożoności (proste wyrażenia, złożone algorytmy, integracje z API)
   - Dostosuj strategię generowania kodu w zależności od poziomu złożoności
   - Dla złożonych zapytań, stosuj technikę podziału problemu na mniejsze części i generowania kodu etapami

3. **Rozbudowa Mechanizmu Autonaprawy**:
   - Ulepsz mechanizm analizy i autocorrect dla brakujących importów
   - Dodaj wykrywanie i naprawę typowych błędów logicznych w generowanym kodzie
   - Implementuj system sugestii dla optymalizacji kodu

## 4. Prompty dla Ulepszeń Interfejsu Użytkownika

### Prompt 1: Projektowanie Pogłębionej Interakcji z Użytkownikiem
```
Jako ekspert UX dla aplikacji konsolowych, zaproponuj udoskonalenia w interakcji między użytkownikiem a asystentem Evopy.

Skupiaj się na następujących aspektach:
1. Intuicyjne sposoby zapytania o konkretne funkcjonalności programistyczne
2. Efektywne prezentowanie generowanego kodu, wyjaśnień i analiz
3. Interaktywne poprawianie i dostosowywanie generowanego kodu
4. Progresywne ujawnianie złożoności - prosty interfejs dla podstawowych przypadków, zaawansowane opcje dla ekspertów

Zaproponuj:
- 5 przykładowych promptów, które użytkownik mógłby użyć do różnych zadań programistycznych
- Format prezentacji wyników dla każdego z tych promptów
- Mechanizm zbierania feedbacku dla ciągłego doskonalenia asystenta
```

### Prompt 2: Rozwijanie Funkcjonalności Zarządzania Projektami
```
Jako ekspert DevOps, zaproponuj rozszerzenie funkcjonalności Evopy w zakresie zarządzania projektami Docker.

Zaprojektuj system, który umożliwi:
1. Tworzenie i zarządzanie wielokontenerowymi projektami Docker Compose
2. Monitorowanie zasobów i stanu kontenerów w czasie rzeczywistym
3. Integrację z zewnętrznymi serwisami (bazy danych, API)
4. Wdrażanie ciągłe (CI/CD) dla projektów tworzonych przy pomocy asystenta

Opisz, jak asystent powinien:
- Prowadzić interaktywną konfigurację projektów Docker
- Generować pliki konfiguracyjne (Dockerfile, docker-compose.yml)
- Monitorować i raportować stan uruchomionych kontenerów
- Wspierać debugowanie i rozwiązywanie problemów z kontenerami
```

## 5. Wytyczne do Poprawy Systemu Testów i Raportowania

1. **Ulepszone Metryki Testowe**:
   - Dodaj metryki oceny jakości generowanego kodu: czytelność, utrzymywalność, zgodność z PEP 8
   - Implementuj pomiar czasu wykonania generowanego kodu jako miarę jego wydajności
   - Analizuj procent poprawnych rozwiązań dla różnych kategorii zadań

2. **Zaawansowany System Raportowania**:
   - Generuj interaktywne raporty HTML z możliwością filtrowania i sortowania wyników
   - Dodaj wizualizacje porównawcze między modelami (wykresy radarowe, słupkowe)
   - Implementuj system śledzenia trendów wydajności modeli w czasie

3. **Testy dla Scenariuszy Specjalizowanych**:
   - Testowanie obsługi zadań z manipulacją danymi (CSV, JSON, XML)
   - Testy dla generowania kodu integrującego się z API zewnętrznych serwisów
   - Testy dla generowania kodu z zaawansowaną logiką biznesową

## 6. Propozycje Nowych Funkcjonalności

1. **Interaktywna Nauka Programowania**:
   - Tryb edukacyjny z wyjaśnianiem generowanych rozwiązań krok po kroku
   - System śledzenia postępów użytkownika i sugerowanie kolejnych wyzwań programistycznych
   - Generowanie quizów i zadań do praktyki na podstawie wcześniejszych interakcji

2. **Rozbudowane Piaskownice Projektowe**:
   - Dedykowane środowiska dla różnych typów projektów (web, data science, IoT)
   - Integracja z popularnymi frameworkami (Django, Flask, FastAPI, Pandas)
   - Automatyczne wdrażanie projektów do prostych środowisk testowych

3. **Narzędzia Współpracy**:
   - Funkcjonalność eksportu i importu projektów
   - System udostępniania wzorców rozwiązań i bibliotek między użytkownikami
   - Integracja z systemami kontroli wersji (Git)

4. **Zaawansowana Analiza Kodu**:
   - Statyczna analiza kodu pod kątem bezpieczeństwa i wydajności
   - Sugestie refaktoryzacji i optymalizacji
   - Automatyczne generowanie testów jednostkowych dla wygenerowanego kodu


# 1. Poprawka dla text2python.py - Ulepszone przetwarzanie promptu

```python
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
        # Przygotuj zapytanie do modelu dla generowania kodu z ulepszonymi instrukcjami
        system_prompt_code = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.

Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.

ZAWSZE przestrzegaj następujących zasad:
1. Dla prostych operacji matematycznych, zawsze używaj zmiennych (np. 'x = 1; y = 2; result = x + y')
2. Dodawaj odpowiednie obsługi błędów i walidację danych wejściowych
3. Unikaj używania bezpośrednio 'import *' - importuj tylko konkretne funkcje/klasy
4. Zawsze dodawaj krótkie komentarze wyjaśniające najważniejsze części kodu
5. Upewnij się, że kod jest bezpieczny i nie wykonuje niebezpiecznych operacji
6. NIE używaj markdown do formatowania kodu - generuj tylko czysty kod Python
7. Jeśli zadanie dotyczy wykonania poleceń systemowych, zawsze używaj subprocess z parametrem shell=False
8. W przypadku operacji na plikach i katalogach, używaj ścieżek względnych i biblioteki pathlib zamiast os.path"""
        
        # Łączymy system prompt z właściwym promptem
        combined_prompt_code = f"{system_prompt_code}\n\nUtwórz funkcję Python, która realizuje następujące zadanie:\n{prompt}\n\nKod Python:"
        
        # Reszta kodu pozostaje bez zmian...
```

# 2. Poprawka dla docker_sandbox.py - Ulepszona obsługa wyjątków i bezpieczeństwo

```python
def prepare_code(self, code: str, filename: str = "user_code.py") -> Path:
    """
    Przygotowuje kod do wykonania w piaskownicy
    
    Args:
        code: Kod Python do wykonania
        filename: Nazwa pliku dla kodu
        
    Returns:
        Path: Ścieżka do pliku z kodem
    """
    # Napraw brakujące zależności w kodzie użytkownika
    code = fix_code_dependencies(code)
    
    # Walidacja kodu pod kątem potencjalnie niebezpiecznych operacji
    if self._is_potentially_dangerous(code):
        logger.warning("Wykryto potencjalnie niebezpieczny kod. Dodaję zabezpieczenia.")
        code = self._sanitize_code(code)
    
    code_file = self.sandbox_dir / filename
    
    # Dodaj wrapper do przechwytywania wyjścia i błędów z ulepszoną obsługą wyjątków
    wrapped_code = f"""
import sys
import traceback
import json
import time
import importlib
import os
import signal
from pathlib import Path

# Ustaw limit czasu wykonania jako zabezpieczenie
def timeout_handler(signum, frame):
    raise TimeoutError("Kod przekroczył maksymalny czas wykonania")

# Zarejestruj handler dla sygnału SIGALRM
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({self.timeout - 5})  # Ustaw alarm na 5 sekund mniej niż pełny timeout

# Ograniczenie dostępu do systemu plików
os.chdir('/app')
allowed_dirs = ['/app']
original_open = open

def restricted_open(*args, **kwargs):
    # Sprawdź czy ścieżka jest dozwolona
    path_arg = str(args[0])
    if not any(path_arg.startswith(allowed_dir) for allowed_dir in allowed_dirs):
        raise PermissionError(f"Dostęp do pliku poza dozwolonym katalogiem: {{path_arg}}")
    return original_open(*args, **kwargs)

# Zastąp funkcję open ograniczoną wersją
open = restricted_open

# Blokowanie operacji sieciowych (podstawowe)
import socket
original_socket = socket.socket
def blocked_socket(*args, **kwargs):
    raise PermissionError("Operacje sieciowe są zablokowane w środowisku piaskownicy")
socket.socket = blocked_socket

# Funkcja do dynamicznego importowania modułów
def import_module_safe(module_name):
    # Lista dozwolonych modułów
    allowed_modules = [
        'time', 'datetime', 'os', 'sys', 're', 'json', 'math', 'random',
        'collections', 'itertools', 'functools', 'pathlib', 'shutil',
        'subprocess', 'threading', 'multiprocessing', 'urllib', 'http',
        'socket', 'email', 'csv', 'xml', 'html', 'sqlite3', 'logging'
    ]
    
    if module_name not in allowed_modules:
        raise ImportError(f"Import modułu {{module_name}} jest zablokowany ze względów bezpieczeństwa")
        
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

# Funkcja do automatycznego importowania modułów
def auto_import():
    # Lista standardowych modułów do automatycznego importu w razie potrzeby
    auto_import_modules = [
        'time', 'datetime', 'os', 'sys', 're', 'json', 'math', 'random',
        'collections', 'itertools', 'functools', 'pathlib'
    ]
    
    # Importuj wszystkie moduły z listy
    for module_name in auto_import_modules:
        if module_name not in globals():
            imported_module = import_module_safe(module_name)
            if imported_module:
                globals()[module_name] = imported_module

# Automatycznie zaimportuj standardowe moduły
auto_import()

# Przechwytywanie wyjścia
class OutputCapture:
    def __init__(self):
        self.output = []
    
    def write(self, text):
        self.output.append(text)
    
    def flush(self):
        pass

# Zapisz oryginalne strumienie
original_stdout = sys.stdout
original_stderr = sys.stderr

# Zastąp strumienie
stdout_capture = OutputCapture()
stderr_capture = OutputCapture()
sys.stdout = stdout_capture
sys.stderr = stderr_capture

# Wykonaj kod użytkownika
result = {{
    "success": False,
    "output": "",
    "error": "",
    "error_output": "",
    "execution_time": 0
}}

try:
    start_time = time.time()
    
    # Kod użytkownika
{chr(10).join(['    ' + line for line in code.split(chr(10))])}
    
    execution_time = time.time() - start_time
    result["success"] = True
    result["execution_time"] = execution_time
except ImportError as import_error:
    # Próba automatycznego importu brakującego modułu
    missing_module = str(import_error).split("'")
    if len(missing_module) >= 2:
        module_name = missing_module[1]
        # Próba importu
        imported = import_module_safe(module_name)
        if imported:
            # Dodaj moduł do globals i spróbuj ponownie
            globals()[module_name] = imported
            try:
                # Ponowna próba wykonania kodu
                start_time = time.time()
                
                # Kod użytkownika
{chr(10).join(['                ' + line for line in code.split(chr(10))])}
                
                execution_time = time.time() - start_time
                result["success"] = True
                result["execution_time"] = execution_time
            except Exception as import_retry_error:
                result["error"] = f"Po próbie automatycznego importu: {{str(import_retry_error)}}"
                result["traceback"] = traceback.format_exc()
        else:
            result["error"] = f"Brakujący moduł: {{module_name}}. Nie można go automatycznie zaimportować."
            result["traceback"] = traceback.format_exc()
    else:
        result["error"] = str(import_error)
        result["traceback"] = traceback.format_exc()
except TimeoutError as timeout_error:
    result["success"] = False
    result["error"] = str(timeout_error)
    result["traceback"] = traceback.format_exc()
except Exception as e:
    result["success"] = False
    result["error"] = str(e)
    result["traceback"] = traceback.format_exc()
finally:
    # Przywróć oryginalne strumienie
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    
    # Wyłącz alarm
    signal.alarm(0)
    
    # Zapisz wyniki
    result["output"] = "".join(stdout_capture.output)
    result["error_output"] = "".join(stderr_capture.output)
    
    # Zapisz wynik do pliku
    with original_open("result.json", "w") as f:
        json.dump(result, f)
    
    print(json.dumps(result))
"""
    
    with open(code_file, "w") as f:
        f.write(wrapped_code)
    
    return code_file

def _is_potentially_dangerous(self, code: str) -> bool:
    """
    Sprawdza, czy kod zawiera potencjalnie niebezpieczne operacje
    
    Args:
        code: Kod Python do sprawdzenia
        
    Returns:
        bool: True jeśli kod jest potencjalnie niebezpieczny
    """
    dangerous_patterns = [
        r'subprocess\.(?:call|Popen|run).*shell\s*=\s*True',  # subprocess z shell=True
        r'os\.system',  # os.system
        r'eval\(',  # eval
        r'exec\(',  # exec
        r'globals\(\)\[\'\w+\'\]',  # dynamiczne przypisanie do globals
        r'__import__\(',  # dynamiczne importowanie
        r'open\([^)]*[\'"]w[\'"]',  # otwieranie plików do zapisu
        r'shutil\.rmtree',  # usuwanie katalogów
        r'os\.remove',  # usuwanie plików
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return True
    
    return False

def _sanitize_code(self, code: str) -> str:
    """
    Modyfikuje kod, aby usunąć niebezpieczne operacje
    
    Args:
        code: Kod Python do zmodyfikowania
        
    Returns:
        str: Zmodyfikowany kod
    """
    # Zastąp subprocess z shell=True
    code = re.sub(
        r'subprocess\.(?:call|Popen|run)\((.*?)shell\s*=\s*True(.*)\)',
        r'subprocess.\1shell=False\2)',
        code
    )
    
    # Zastąp os.system
    code = re.sub(
        r'os\.system\((.*?)\)',
        r'subprocess.run(\1, shell=False, check=True)',
        code
    )
    
    # Zablokuj eval i exec
    code = re.sub(
        r'eval\((.*?)\)',
        r'# Niebezpieczna funkcja eval() została zablokowana: eval(\1)',
        code
    )
    
    code = re.sub(
        r'exec\((.*?)\)',
        r'# Niebezpieczna funkcja exec() została zablokowana: exec(\1)',
        code
    )
    
    return code

def run(self, code: str) -> Dict[str, Any]:
    """
    Uruchamia kod w piaskownicy Docker z ulepszonymi zabezpieczeniami
    
    Args:
        code: Kod Python do wykonania
        
    Returns:
        Dict: Wynik wykonania kodu
    """
    try:
        # Przygotuj kod
        code_file = self.prepare_code(code)
        
        # Utwórz kontener Docker
        container_name = f"evopy-sandbox-{self.sandbox_id}"
        
        # Ulepszone limity zasobów
        cmd = [
            "docker", "run",
            "--name", container_name,
            "--rm",  # Usuń kontener po zakończeniu
            "-v", f"{self.sandbox_dir}:/app",
            "-w", "/app",
            "--network", "none",  # Brak dostępu do sieci
            "--memory", "512m",  # Limit pamięci
            "--memory-swap", "512m",  # Wyłącz swap
            "--cpus", "0.5",  # Limit CPU
            "--pids-limit", "50",  # Limit liczby procesów
            "--ulimit", "nofile=1024:1024",  # Limit deskryptorów plików
            "--ulimit", "fsize=10485760:10485760",  # Limit rozmiaru plików (10MB)
            "--security-opt", "no-new-privileges",  # Brak eskalacji uprawnień
            self.docker_image,
            "python", "/app/user_code.py"
        ]
        
        logger.info(f"Uruchamianie kodu w piaskownicy: {container_name}")
        
        # Uruchom z limitem czasu
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
            
            # Sprawdź wynik
            if process.returncode != 0:
                logger.warning(f"Kod zakończył się z błędem: {stderr}")
                return {
                    "success": False,
                    "output": stdout,
                    "error": stderr,
                    "execution_time": self.timeout
                }
            
            # Parsuj wynik JSON
            try:
                result = json.loads(stdout)
                return result
            except json.JSONDecodeError:
                logger.warning(f"Nie udało się sparsować JSON wynikowego: {stdout[:1000]}")
                return {
                    "success": True,
                    "output": stdout,
                    "error": "",
                    "execution_time": 0
                }
            
        except subprocess.TimeoutExpired:
            # Graceful shutdown najpierw z SIGTERM
            try:
                subprocess.run(["docker", "stop", "--time=5", container_name], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              timeout=5)
            except subprocess.TimeoutExpired:
                # Jeśli nie zadziała, użyj SIGKILL
                subprocess.run(["docker", "kill", container_name], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE)
            
            logger.warning(f"Kod przekroczył limit czasu ({self.timeout}s)")
            return {
                "success": False,
                "output": "",
                "error": f"Kod przekroczył limit czasu ({self.timeout}s)",
                "execution_time": self.timeout
            }
            
    except Exception as e:
        logger.error(f"Błąd podczas uruchamiania kodu: {e}")
        return {
            "success": False,
            "output": "",
            "error": f"Błąd piaskownicy: {str(e)}",
            "execution_time": 0
        }
    finally:
        # Spróbuj wyczyścić kontener - bardziej rozbudowane czyszczenie
        try:
            # Sprawdź czy kontener istnieje
            container_check = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if container_name in container_check.stdout:
                # Próba zatrzymania kontenera jeśli nadal działa
                subprocess.run(
                    ["docker", "stop", "--time=2", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=3
                )
                
                # Usuń kontener
                subprocess.run(
                    ["docker", "rm", "-f", container_name],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                logger.info(f"Kontener {container_name} został wyczyszczony")
        except Exception as cleanup_error:
            logger.warning(f"Błąd podczas czyszczenia kontenera: {cleanup_error}")
            # Nie przerywaj wykonania - to tylko czyszczenie
```

# 3. Poprawka dla _extract_code w text2python.py - Bezpieczniejsze wyodrębnianie kodu

```python
def _extract_code(self, text: str) -> str:
    """
    Wyodrębnia kod Python z odpowiedzi modelu.
    Obsługuje różne formaty odpowiedzi i zapewnia bezpieczną ekstrakcję kodu.
    
    Args:
        text: Odpowiedź modelu
        
    Returns:
        str: Wyodrębniony kod Python
    """
    # Najpierw sprawdź, czy tekst zawiera bloki kodu Markdown
    code_blocks = re.findall(r'```(?:python)?\s*(.*?)```', text, re.DOTALL)
    
    if code_blocks:
        # Jeśli znaleziono wiele bloków kodu, wybierz najdłuższy
        if len(code_blocks) > 1:
            logger.info(f"Znaleziono {len(code_blocks)} bloków kodu, wybieranie najdłuższego")
            return max(code_blocks, key=len).strip()
        return code_blocks[0].strip()
    
    # Jeśli nie znaleziono bloków kodu, sprawdź czy jest to "surowy" kod Python
    # Szukanie typowych wzorców kodu Python
    python_patterns = [
        # Definicje funkcji
        r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
        # Importy
        r'import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+import',
        # Typowe struktury kontrolne
        r'if\s+.+:',
        r'for\s+.+\s+in\s+.+:',
        r'while\s+.+:',
        r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)',
        r'try:',
        r'except\s*.*:',
        r'with\s+.+\s+as\s+.+:',
    ]
    
    # Sprawdź ile wzorców pasuje do tekstu
    pattern_matches = sum(1 for pattern in python_patterns if re.search(pattern, text))
    
    # Jeśli znaleziono kilka wzorców, prawdopodobnie jest to surowy kod Python
    if pattern_matches >= 2:
        # Wykryto surowy kod Python
        logger.info(f"Nie znaleziono bloków kodu, ale wykryto {pattern_matches} wzorców kodu Python")
        return text.strip()
    
    # Jeśli nie wykryto wyraźnych wzorców, zwróć sam tekst, ale z ostrzeżeniem
    logger.warning("Nie znaleziono wyraźnych bloków kodu ani wzorców Python, zwracanie surowego tekstu")
    return text.strip()
```

# 4. Nowa funkcja do sprawdzania poprawności kodu przed uruchomieniem

```python
def validate_code(self, code: str) -> Dict[str, Any]:
    """
    Sprawdza poprawność składniową kodu Python oraz przeprowadza statyczną analizę bezpieczeństwa.
    
    Args:
        code: Kod Python do sprawdzenia
        
    Returns:
        Dict: Wynik walidacji zawierający:
            - is_valid (bool): Czy kod jest poprawny składniowo
            - is_safe (bool): Czy kod jest bezpieczny do uruchomienia
            - issues (List[str]): Lista wykrytych problemów
            - suggestions (List[str]): Lista sugestii dotyczących kodu
    """
    result = {
        "is_valid": False,
        "is_safe": False,
        "issues": [],
        "suggestions": []
    }
    
    # Sprawdzenie poprawności składniowej
    try:
        ast.parse(code)
        result["is_valid"] = True
    except SyntaxError as e:
        result["issues"].append(f"Błąd składni Python: {str(e)}")
        return result  # Jeśli kod ma błędy składni, zwróć wynik od razu
    
    # Sprawdzenie wzorców niebezpiecznego kodu
    dangerous_patterns = [
        (r'subprocess\.(?:call|Popen|run).*shell\s*=\s*True', 
         "Użycie subprocess z shell=True może być niebezpieczne. Zalecane użycie shell=False."),
        
        (r'os\.system', 
         "Funkcja os.system jest podatna na ataki. Zalecane użycie subprocess.run z shell=False."),
        
        (r'eval\(', 
         "Funkcja eval() może wykonywać dowolny kod i jest niebezpieczna. Rozważ inne rozwiązanie."),
        
        (r'exec\(', 
         "Funkcja exec() może wykonywać dowolny kod i jest niebezpieczna. Rozważ inne rozwiązanie."),
        
        (r'__import__\(', 
         "Dynamiczne importowanie modułów może być niebezpieczne. Użyj importlib.import_module."),
        
        (r'open\([^)]*[\'"]w[\'"]', 
         "Otwarcie pliku do zapisu może być niebezpieczne w środowisku piaskownicy."),
        
        (r'shutil\.rmtree', 
         "Funkcja shutil.rmtree może usunąć całe drzewo katalogów. Używaj ostrożnie."),
        
        (r'os\.remove', 
         "Funkcja os.remove usuwa pliki. W środowisku piaskownicy używaj z ostrożnością."),
        
        (r'requests?\.', 
         "Operacje sieciowe są ograniczone w środowisku piaskownicy."),
        
        (r'socket\.', 
         "Operacje sieciowe niskiego poziomu są ograniczone w środowisku piaskownicy.")
    ]
    
    for pattern, warning in dangerous_patterns:
        if re.search(pattern, code):
            result["issues"].append(warning)
    
    # Jeśli nie znaleziono problemów bezpieczeństwa, oznacz kod jako bezpieczny
    if not result["issues"]:
        result["is_safe"] = True
    
    # Dodatkowe sugestie dla poprawy kodu
    improvement_patterns = [
        (r'for\s+.+\s+in\s+range\(.+\):\s*\n\s*[^#\n]+\.append', 
         "Użycie list comprehension może być bardziej wydajne niż append w pętli."),
        
        (r'if\s+([^=\n]+)\s*==\s*True', 
         "Można uprościć warunek 'if x == True:' do 'if x:'."),
        
        (r'if\s+([^=\n]+)\s*==\s*False', 
         "Można uprościć warunek 'if x == False:' do 'if not x:'."),
        
        (r'for\s+i\s+in\s+range\(len\(([a-zA-Z_][a-zA-Z0-9_]*)\)\)', 
         "Zamiast 'for i in range(len(lista)):' można użyć 'for i, element in enumerate(lista):'."),
        
        (r'import\s+\*', 
         "Import * może prowadzić do konfliktów nazw. Rozważ importowanie tylko potrzebnych elementów."),
        
        (r'except\s*:', 
         "Łapanie wszystkich wyjątków 'except:' nie jest dobrą praktyką. Wybierz konkretne typy wyjątków."),
        
        (r'print\([^)]*\)', 
         "Użycie print w funkcji execute może nie być widoczne. Rozważ zwracanie wyniku zamiast jego wypisywania.")
    ]
    
    for pattern, suggestion in improvement_patterns:
        if re.search(pattern, code):
            result["suggestions"].append(suggestion)
    
    return result
```

# 5. Nowy moduł do rozpoznawania złożoności zapytań - query_analyzer.py

```python
#!/usr/bin/env python3
"""
Query Analyzer - Moduł do analizy i klasyfikacji zapytań użytkownika

Ten moduł analizuje zapytania użytkownika pod kątem ich złożoności,
typu zadania i wymaganych zasobów, co pozwala na lepsze dopasowanie
strategii generowania kodu.
"""

import re
import spacy
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger("evo-assistant.query-analyzer")

# Próba załadowania modelu spaCy
try:
    nlp = spacy.load("pl_core_news_sm")
    SPACY_AVAILABLE = True
    logger.info("Załadowano model spaCy dla języka polskiego")
except (ImportError, OSError):
    SPACY_AVAILABLE = False
    logger.warning("Nie udało się załadować modelu spaCy. Analiza zapytań będzie ograniczona.")

class QueryAnalyzer:
    """Klasa do analizy i klasyfikacji zapytań użytkownika"""
    
    def __init__(self):
        """Inicjalizacja analizatora zapytań"""
        # Słowniki do klasyfikacji zapytań
        self.task_keywords = {
            "algorithm": ["algorytm", "sortuj", "wyszukaj", "algorytm", "znajdź", "oblicz", "policz", "rozwiąż"],
            "data_processing": ["dane", "plik", "csv", "json", "xml", "excel", "baza danych", "sql", "dataframe", "pandas"],
            "web": ["html", "css", "javascript", "api", "http", "request", "url", "web", "strona", "serwer"],
            "system": ["system", "plik", "katalog", "ścieżka", "docker", "terminal", "bash", "powłoka", "process"],
            "math": ["matematyka", "równanie", "oblicz", "funkcja", "całka", "pochodna", "wektor", "macierz", "statystyka"],
            "ui": ["gui", "interfejs", "przycisk", "okno", "formularz", "tkinter", "pyqt", "widżet", "graficzny"]
        }
        
        self.complexity_indicators = {
            "high": ["złożony", "skomplikowany", "zaawansowany", "optymalizacja", "wielowątkowy", "równoległy",
                   "rekurencja", "klasy", "obiektowy", "dziedziczenie", "algorytm"],
            "medium": ["api", "json", "funkcja", "iteracja", "pętla", "warunek", "lista", "słownik", "plik",
                      "konfiguracja", "parser"],
            "low": ["prosty", "łatwy", "wyświetl", "pokaż", "napisz", "oblicz", "dodaj", "odejmij", "pomnóż"]
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analizuje zapytanie użytkownika i klasyfikuje je pod względem złożoności i typu zadania
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            Dict: Wynik analizy zawierający pola:
                - complexity: Złożoność zapytania (wartość 0-1)
                - task_type: Typ zadania (algorithm, data_processing, web, system, math, ui)
                - requires_external_resources: Czy wymaga zewnętrznych zasobów
                - estimated_execution_time: Szacowany czas wykonania (w sekundach)
                - keywords: Lista wykrytych słów kluczowych
        """
        # Inicjalizacja wyników
        result = {
            "complexity": 0.0,  # Zakres 0-1
            "task_types": [],   # Lista typów zadań (może być więcej niż jeden)
            "requires_external_resources": False,
            "estimated_execution_time": 1.0,  # Domyślnie 1 sekunda
            "keywords": []
        }
        
        # Konwersja zapytania na małe litery
        query_lower = query.lower()
        
        # 1. Analiza złożoności
        complexity_score = self._calculate_complexity(query_lower)
        result["complexity"] = complexity_score
        
        # 2. Identyfikacja typów zadań
        task_scores = self._identify_task_types(query_lower)
        # Wybierz typy zadań z najwyższymi wynikami (próg 0.2)
        result["task_types"] = [task for task, score in task_scores.items() if score > 0.2]
        
        # Jeśli nie zidentyfikowano żadnego typu, wybierz typ z najwyższym wynikiem
        if not result["task_types"] and task_scores:
            top_task = max(task_scores.items(), key=lambda x: x[1])[0]
            result["task_types"] = [top_task]
        
        # 3. Sprawdzenie zapotrzebowania na zasoby zewnętrzne
        result["requires_external_resources"] = self._requires_external_resources(query_lower)
        
        # 4. Oszacowanie czasu wykonania
        result["estimated_execution_time"] = self._estimate_execution_time(complexity_score, result["task_types"], 
                                                                         result["requires_external_resources"])
        
        # 5. Ekstrakcja słów kluczowych
        result["keywords"] = self._extract_keywords(query)
        
        return result
    
    def _calculate_complexity(self, query: str) -> float:
        """
        Oblicza złożoność zapytania na podstawie różnych metryk
        
        Args:
            query: Zapytanie użytkownika (małe litery)
            
        Returns:
            float: Złożoność w zakresie 0-1
        """
        complexity = 0.0
        
        # 1. Długość zapytania (0-0.3)
        length_score = min(len(query) / 200.0, 1.0) * 0.3
        complexity += length_score
        
        # 2. Wskaźniki złożoności (0-0.5)
        high_indicators = sum(1 for keyword in self.complexity_indicators["high"] if keyword in query)
        medium_indicators = sum(1 for keyword in self.complexity_indicators["medium"] if keyword in query)
        low_indicators = sum(1 for keyword in self.complexity_indicators["low"] if keyword in query)
        
        indicator_score = (high_indicators * 0.1 + medium_indicators * 0.05 - low_indicators * 0.03)
        indicator_score = max(0, min(indicator_score, 0.5))
        complexity += indicator_score
        
        # 3. Struktura językowa (0-0.2)
        if SPACY_AVAILABLE:
            doc = nlp(query)
            # Liczba zdań
            sentences = len(list(doc.sents))
            # Liczba fraz rzeczownikowych i czasownikowych
            noun_chunks = len(list(doc.noun_chunks))
            verbs = sum(1 for token in doc if token.pos_ == "VERB")
            
            structure_score = min((sentences * 0.05 + noun_chunks * 0.02 + verbs * 0.02), 0.2)
            complexity += structure_score
        else:
            # Uproszczona analiza na podstawie znaków interpunkcyjnych
            structure_score = min((query.count('.') + query.count(',') + query.count(';')) * 0.02, 0.2)
            complexity += structure_score
        
        return round(min(complexity, 1.0), 2)
    
    def _identify_task_types(self, query: str) -> Dict[str, float]:
        """
        Identyfikuje typy zadań w zapytaniu
        
        Args:
            query: Zapytanie użytkownika (małe litery)
            
        Returns:
            Dict[str, float]: Słownik z wynikami dla każdego typu zadania
        """
        task_scores = {}
        
        # Oblicz wynik dla każdego typu zadania
        for task_type, keywords in self.task_keywords.items():
            score = sum(0.2 for keyword in keywords if keyword in query)
            task_scores[task_type] = min(score, 1.0)  # Maksymalny wynik to 1.0
        
        return task_scores
    
    def _requires_external_resources(self, query: str) -> bool:
        """
        Sprawdza, czy zapytanie wymaga dostępu do zasobów zewnętrznych
        
        Args:
            query: Zapytanie użytkownika (małe litery)
            
        Returns:
            bool: True jeśli zapytanie wymaga zasobów zewnętrznych
        """
        external_resource_keywords = [
            "plik", "url", "api", "baza danych", "serwer", "internet", "pobierz", "ściągnij",
            "web", "strona", "http", "ftp", "ssh", "socket", "sieć", "połączenie"
        ]
        
        return any(keyword in query for keyword in external_resource_keywords)
    
    def _estimate_execution_time(self, complexity: float, task_types: List[str], 
                               requires_resources: bool) -> float:
        """
        Szacuje czas wykonania kodu na podstawie złożoności i typu zadania
        
        Args:
            complexity: Złożoność zapytania (0-1)
            task_types: Lista typów zadań
            requires_resources: Czy wymaga zasobów zewnętrznych
            
        Returns:
            float: Szacowany czas wykonania w sekundach
        """
        # Bazowy czas na podstawie złożoności
        base_time = 1.0 + complexity * 5.0
        
        # Modyfikacja czasu na podstawie typu zadania
        task_multipliers = {
            "algorithm": 1.5,  # Algorytmy mogą być czasochłonne
            "data_processing": 2.0,  # Przetwarzanie danych może zająć więcej czasu
            "web": 1.2,
            "system": 1.3,
            "math": 1.1,
            "ui": 1.0
        }
        
        # Wybierz najwyższy mnożnik z typów zadań
        task_multiplier = max([task_multipliers.get(task, 1.0) for task in task_types]) if task_types else 1.0
        
        # Zwiększ czas jeśli wymaga zasobów zewnętrznych
        resource_multiplier = 1.5 if requires_resources else 1.0
        
        # Oblicz ostateczny szacowany czas
        estimated_time = base_time * task_multiplier * resource_multiplier
        
        return round(estimated_time, 1)
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Ekstrahuje słowa kluczowe z zapytania
        
        Args:
            query: Zapytanie użytkownika
            
        Returns:
            List[str]: Lista słów kluczowych
        """
        if SPACY_AVAILABLE:
            # Użyj spaCy do wyodrębnienia wartościowych słów kluczowych
            doc = nlp(query)
            keywords = []
            
            # Dodaj rzeczowniki, czasowniki i przymiotniki jako słowa kluczowe
            for token in doc:
                if token.pos_ in ["NOUN", "VERB", "ADJ"] and len(token.text) > 2 and not token.is_stop:
                    keywords.append(token.lemma_)
            
            # Dodaj wielowyrazowe frazy rzeczownikowe
            for chunk in doc.noun_chunks:
                if len(chunk.text) > 3:
                    keywords.append(chunk.text)
            
            return list(set(keywords))
        else:
            # Prosta ekstrakcja słów dłuższych niż 4 znaki
            words = re.findall(r'\b[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{4,}\b', query)
            # Usuń duplikaty
            return list(set(words))
```

# 6. Ulepszenia dla main.py - Dodanie funkcji automatycznego uczenia się

```python
def _update_prompt_based_on_feedback(self, query: str, code: str, feedback: str, success: bool) -> None:
    """
    Aktualizuje prompty używane przez asystenta na podstawie feedbacku użytkownika.
    Implementuje mechanizm uczenia się z interakcji.
    
    Args:
        query: Oryginalne zapytanie użytkownika
        code: Wygenerowany kod
        feedback: Feedback użytkownika (jeśli dostępny)
        success: Czy kod został zaakceptowany przez użytkownika
    """
    # Analiza zapytania
    query_analyzer = QueryAnalyzer()
    query_analysis = query_analyzer.analyze_query(query)
    
    # Zapisz feedback i przykład do historii uczenia się
    feedback_record = {
        "query": query,
        "code": code,
        "feedback": feedback,
        "success": success,
        "query_analysis": query_analysis,
        "timestamp": datetime.now().isoformat()
    }
    
    # Ścieżka do pliku historii feedbacku
    feedback_path = APP_DIR / "learning" / "feedback_history.jsonl"
    os.makedirs(os.path.dirname(feedback_path), exist_ok=True)
    
    # Dodaj rekord do pliku historii (format JSONL)
    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(feedback_record, ensure_ascii=False) + "\n")
    
    # Aktualizuj bazę przykładów sukcesu/porażki w zależności od kategorii zapytania
    for task_type in query_analysis["task_types"]:
        examples_path = APP_DIR / "learning" / "examples" / f"{task_type}.json"
        os.makedirs(os.path.dirname(examples_path), exist_ok=True)
        
        # Załaduj istniejące przykłady lub utwórz nowy zbiór
        if os.path.exists(examples_path):
            with open(examples_path, "r", encoding="utf-8") as f:
                examples = json.load(f)
        else:
            examples = {"success": [], "failure": []}
        
        # Dodaj nowy przykład do odpowiedniej kategorii
        category = "success" if success else "failure"
        
        # Dodaj tylko jeśli to nowy przykład (unikaj duplikatów)
        is_duplicate = any(example["query"] == query for example in examples[category])
        
        if not is_duplicate:
            examples[category].append({
                "query": query,
                "code": code,
                "feedback": feedback
            })
            
            # Ogranicz liczbę przykładów do 100 dla każdej kategorii (zachowaj najnowsze)
            if len(examples[category]) > 100:
                examples[category] = examples[category][-100:]
            
            # Zapisz zaktualizowane przykłady
            with open(examples_path, "w", encoding="utf-8") as f:
                json.dump(examples, f, ensure_ascii=False, indent=2)
    
    # Analiza często pojawiających się problemów
    self._analyze_common_issues()

def _analyze_common_issues(self) -> None:
    """
    Analizuje historię feedbacku w poszukiwaniu często występujących problemów
    i aktualizuje system prompts aby je naprawić
    """
    # Ścieżka do pliku historii feedbacku
    feedback_path = APP_DIR / "learning" / "feedback_history.jsonl"
    if not os.path.exists(feedback_path):
        return
    
    # Wczytaj wszystkie rekordy
    feedback_records = []
    with open(feedback_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                feedback_records.append(json.loads(line))
    
    # Jeśli mamy za mało rekordów, nie kontynuuj
    if len(feedback_records) < 10:
        return
    
    # Znajdź nieudane zapytania z ostatnich 50 rekordów
    recent_failures = [r for r in feedback_records[-50:] if not r["success"]]
    
    # Jeśli mamy wystarczającą liczbę porażek, zidentyfikuj wzorce
    if len(recent_failures) >= 5:
        # Analiza słów kluczowych w nieudanych zapytaniach
        failure_keywords = {}
        for record in recent_failures:
            for keyword in record.get("query_analysis", {}).get("keywords", []):
                failure_keywords[keyword] = failure_keywords.get(keyword, 0) + 1
        
        # Znajdź najczęstsze słowa kluczowe w nieudanych zapytaniach
        common_failure_keywords = [k for k, v in failure_keywords.items() if v >= 2]
        
        # Jeśli znaleziono wspólne słowa kluczowe, dodaj je do listy problemów
        if common_failure_keywords:
            issues_path = APP_DIR / "learning" / "common_issues.json"
            
            if os.path.exists(issues_path):
                with open(issues_path, "r", encoding="utf-8") as f:
                    issues = json.load(f)
            else:
                issues = {"keywords": [], "updated_at": ""}
            
            # Dodaj nowe słowa kluczowe do listy
            for keyword in common_failure_keywords:
                if keyword not in issues["keywords"]:
                    issues["keywords"].append(keyword)
            
            # Aktualizuj datę
            issues["updated_at"] = datetime.now().isoformat()
            
            # Zapisz zaktualizowaną listę
            with open(issues_path, "w", encoding="utf-8") as f:
                json.dump(issues, f, ensure_ascii=False, indent=2)
            
            # Zaloguj informację o aktualizacji
            logger.info(f"Zaktualizowano listę typowych problemów: {', '.join(common_failure_keywords)}")
            
            # Aktualizuj prompt systemowy o nowe problemy
            self._update_system_prompt(common_failure_keywords)

`    def _update_system_prompt(self, problem_keywords: List[str]) -> None:
        """
        Aktualizuje prompt systemowy o nowe wykryte problemy
        
        Args:
            problem_keywords: Lista słów kluczowych związanych z typowymi problemami
        """
        # Ścieżka do pliku z promptem systemowym
        prompt_path = APP_DIR / "config" / "system_prompt.txt"
        
        # Jeśli plik nie istnieje, utwórz domyślny prompt
        if not os.path.exists(prompt_path):
            default_prompt = """Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
    Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.
    
    Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
    Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.
    
    Zapewnij, że kod jest logiczny i realizuje dokładnie to, o co prosi użytkownik."""
            
            os.makedirs(os.path.dirname(prompt_path), exist_ok=True)
            with open(prompt_path, "w", encoding="utf-8") as f:
                f.write(default_prompt)
        
        # Wczytaj istniejący prompt
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()
        
        # Sprawdź, czy sekcja z problemami już istnieje
        problems_section = "\n\nSZCZEGÓLNIE ZWRÓĆ UWAGĘ NA:\n"
        if "SZCZEGÓLNIE ZWRÓĆ UWAGĘ NA:" in system_prompt:
            # Znajdź początek i koniec sekcji z problemami
            start_idx = system_prompt.find("SZCZEGÓLNIE ZWRÓĆ UWAGĘ NA:")
            end_idx = system_prompt.find("\n\n", start_idx)
            if end_idx == -1:  # Jeśli nie ma podwójnego entera na końcu
                end_idx = len(system_prompt)
            
            # Zachowaj części przed i po sekcji z problemami
            before_problems = system_prompt[:start_idx]
            after_problems = system_prompt[end_idx:]
            
            # Zbuduj nową sekcję z problemami
            problems_section = "SZCZEGÓLNIE ZWRÓĆ UWAGĘ NA:\n"
        else:
            before_problems = system_prompt
            after_problems = ""
        
        # Dodaj problemy do sekcji
        for keyword in problem_keywords:
            if keyword in ["matematyka", "obliczenie", "kalkulator", "równanie"]:
                problems_section += "- Dla prostych obliczeń matematycznych, ZAWSZE używaj zmiennych (np. x = 1, y = 2, result = x + y)\n"
            elif keyword in ["docker", "kontener", "system"]:
                problems_section += "- Przy operacjach systemowych, używaj subprocess.run() z parametrem shell=False dla bezpieczeństwa\n"
            elif keyword in ["plik", "csv", "excel", "dane"]:
                problems_section += "- Przy operacjach na plikach, zawsze używaj konstrukcji 'with open()' i obsługuj wyjątki\n"
            elif keyword in ["json", "api", "http"]:
                problems_section += "- Przy operacjach sieciowych i API, zawsze obsługuj błędy połączenia i parsowania\n"
            elif keyword in ["gui", "interfejs", "tkinter"]:
                problems_section += "- Przy tworzeniu interfejsów, organizuj kod w klasy i metody zamiast kodu proceduralnego\n"
        
        # Połącz wszystkie części
        updated_prompt = before_problems + problems_section + after_problems
        
        # Zapisz zaktualizowany prompt
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(updated_prompt)
        
        logger.info(f"Zaktualizowano prompt systemowy o nowe problemy: {', '.join(problem_keywords)}")
    ```
    
    # 7. Poprawka dla Modułu Testowego - Zoptymalizowane Generowanie Raportów
    
    ```python
    def generate_comparison_report(results_dir: Path, output_dir: Path, format_type: str = "all", 
                                 trend_days: int = 30) -> Dict[str, Path]:
        """
        Generuje rozbudowany raport porównawczy dla wszystkich modeli na podstawie wyników testów.
        
        Args:
            results_dir: Katalog z wynikami testów
            output_dir: Katalog na wygenerowane raporty
            format_type: Format wyjściowy raportu (all, md, html, pdf)
            trend_days: Liczba dni do analizy trendów
            
        Returns:
            Dict[str, Path]: Słownik ze ścieżkami do wygenerowanych raportów
        """
        # Upewnij się, że katalogi istnieją
        os.makedirs(output_dir, exist_ok=True)
        
        # Zbierz wyniki testów
        test_results = collect_test_results(results_dir, trend_days)
        
        # Aktualna data i czas
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Przygotuj bazowe nazwy plików
        base_filename = f"comparison_report_{timestamp}"
        output_files = {}
        
        # 1. Generowanie raportu Markdown
        if format_type in ["all", "md"]:
            md_report = generate_markdown_report(test_results, timestamp)
            md_path = output_dir / f"{base_filename}.md"
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(md_report)
            output_files["md"] = md_path
            
            # Utwórz link do najnowszego raportu
            latest_link = output_dir / "comparison_report_latest.md"
            create_symlink_or_copy(md_path, latest_link)
        
        # 2. Generowanie raportu HTML
        if format_type in ["all", "html"]:
            # Sprawdź czy mamy już raport Markdown
            if "md" in output_files:
                # Konwertuj Markdown na HTML za pomocą pandoc
                html_path = output_dir / f"{base_filename}.html"
                try:
                    # Dodaj styl CSS dla lepszego wyglądu
                    css_path = output_dir.parent / "docs" / "assets" / "css" / "report.css"
                    if not css_path.exists():
                        # Utwórz prosty plik CSS jeśli nie istnieje
                        os.makedirs(css_path.parent, exist_ok=True)
                        with open(css_path, "w", encoding="utf-8") as f:
                            f.write("""body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
    h1, h2, h3 { color: #0066cc; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
    th { background-color: #f2f2f2; }
    tr:nth-child(even) { background-color: #f9f9f9; }
    canvas { max-width: 800px; margin: 20px auto; display: block; }
    .success { color: green; }
    .failure { color: red; }
    .warning { color: orange; }
    """)
                    
                    # Uruchom pandoc
                    subprocess.run([
                        "pandoc",
                        "-s",
                        "-c", str(css_path.relative_to(output_dir.parent)),
                        "--metadata", f"title=Raport porównawczy modeli LLM - {timestamp}",
                        "-o", str(html_path),
                        str(output_files["md"])
                    ], check=True)
                    
                    # Dodaj interaktywne wykresy JavaScript
                    add_interactive_charts(html_path, test_results)
                    
                    output_files["html"] = html_path
                    
                    # Utwórz link do najnowszego raportu HTML
                    latest_html_link = output_dir / "comparison_report_latest.html"
                    create_symlink_or_copy(html_path, latest_html_link)
                    
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    logger.error(f"Błąd podczas generowania HTML: {e}")
                    # Fallback - generuj prosty HTML
                    html_report = generate_simple_html_report(test_results, timestamp)
                    html_path = output_dir / f"{base_filename}.html"
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html_report)
                    output_files["html"] = html_path
            else:
                # Generuj bezpośrednio raport HTML
                html_report = generate_simple_html_report(test_results, timestamp)
                html_path = output_dir / f"{base_filename}.html"
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_report)
                output_files["html"] = html_path
        
        # 3. Generowanie raportu PDF
        if format_type in ["all", "pdf"]:
            # Sprawdź czy mamy już raport HTML
            if "html" in output_files:
                # Konwertuj HTML na PDF za pomocą wkhtmltopdf
                pdf_path = output_dir / f"{base_filename}.pdf"
                try:
                    subprocess.run([
                        "wkhtmltopdf", 
                        "--enable-local-file-access",
                        str(output_files["html"]),
                        str(pdf_path)
                    ], check=True)
                    
                    output_files["pdf"] = pdf_path
                except (subprocess.SubprocessError, FileNotFoundError) as e:
                    logger.error(f"Błąd podczas generowania PDF: {e}")
            else:
                logger.error("Nie można wygenerować PDF - brak pliku HTML")
        
        # 4. Stwórz stronę indeksu dla raportów
        create_report_index(output_dir)
        
        return output_files
    
    def add_interactive_charts(html_path: Path, test_results: Dict[str, Any]) -> None:
        """
        Dodaje interaktywne wykresy JavaScript do raportu HTML
        
        Args:
            html_path: Ścieżka do pliku HTML
            test_results: Słownik z wynikami testów
        """
        # Wczytaj plik HTML
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Dodaj bibliotekę Chart.js przed </head>
        chart_js = """
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    // Funkcje pomocnicze dla wykresów
    function createRadarChart(canvas_id, labels, datasets) {
        const ctx = document.getElementById(canvas_id).getContext('2d');
        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    r: {
                        min: 0,
                        max: 1,
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    function createBarChart(canvas_id, labels, datasets) {
        const ctx = document.getElementById(canvas_id).getContext('2d');
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    function createLineChart(canvas_id, labels, datasets) {
        const ctx = document.getElementById(canvas_id).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true
            }
        });
    }
    </script>
    """
        html_content = html_content.replace("</head>", f"{chart_js}</head>")
        
        # Przygotuj dane dla wykresów
        models = list(test_results["models"].keys())
        colors = ["rgb(255, 99, 132)", "rgb(54, 162, 235)", "rgb(255, 206, 86)", 
                  "rgb(75, 192, 192)", "rgb(153, 102, 255)", "rgb(255, 159, 64)"]
        
        # Wykres radarowy dla ogólnych wyników
        radar_datasets = []
        for i, model in enumerate(models):
            model_data = test_results["models"][model]
            radar_datasets.append({
                "label": model,
                "data": [
                    model_data.get("correctness", 0),
                    model_data.get("completeness", 0),
                    model_data.get("efficiency", 0),
                    model_data.get("explanations", 0),
                    model_data.get("intent_match", 0)
                ],
                "backgroundColor": f"{colors[i % len(colors)]}4D",  # 30% opacity
                "borderColor": colors[i % len(colors)],
                "borderWidth": 2
            })
        
        radar_chart_data = {
            "labels": ["Poprawność", "Kompletność", "Wydajność", "Wyjaśnienia", "Zgodność z intencją"],
            "datasets": radar_datasets
        }
        
        # Wykres słupkowy dla czasów wykonania
        execution_time_data = []
        for i, model in enumerate(models):
            model_data = test_results["models"][model]
            execution_time_data.append({
                "label": model,
                "data": [model_data.get("average_execution_time", 0)],
                "backgroundColor": colors[i % len(colors)]
            })
        
        bar_chart_data = {
            "labels": ["Średni czas wykonania (s)"],
            "datasets": execution_time_data
        }
        
        # Dodaj wykresy przed </body>
        charts_html = """
    <h2>Interaktywne Wykresy</h2>
    <div style="margin: 40px 0;">
        <h3>Porównanie modeli - metryki ogólne</h3>
        <canvas id="radarChart" width="800" height="600"></canvas>
    </div>
    <div style="margin: 40px 0;">
        <h3>Porównanie modeli - czas wykonania</h3>
        <canvas id="executionTimeChart" width="800" height="400"></canvas>
    </div>
    
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Wykres radarowy
        const radarLabels = %s;
        const radarDatasets = %s;
        createRadarChart('radarChart', radarLabels, radarDatasets);
        
        // Wykres słupkowy
        const barLabels = %s;
        const barDatasets = %s;
        createBarChart('executionTimeChart', barLabels, barDatasets);
    });
    </script>
    """ % (
        json.dumps(radar_chart_data["labels"]),
        json.dumps(radar_chart_data["datasets"]),
        json.dumps(bar_chart_data["labels"]),
        json.dumps(bar_chart_data["datasets"])
    )
        
        html_content = html_content.replace("</body>", f"{charts_html}</body>")
        
        # Zapisz zmodyfikowany plik HTML
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    def create_report_index(output_dir: Path) -> None:
        """
        Tworzy stronę indeksu z listą wszystkich raportów
        
        Args:
            output_dir: Katalog z raportami
        """
        # Znajdź wszystkie raporty
        markdown_reports = sorted(output_dir.glob("comparison_report_*.md"), reverse=True)
        html_reports = sorted(output_dir.glob("comparison_report_*.html"), reverse=True)
        pdf_reports = sorted(output_dir.glob("comparison_report_*.pdf"), reverse=True)
        
        # Przygotuj HTML dla indeksu
        html = """<!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Evopy - Raporty porównawcze modeli LLM</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
            h1, h2, h3 { color: #0066cc; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .latest { font-weight: bold; color: #009900; }
        </style>
    </head>
    <body>
        <h1>Evopy - Raporty porównawcze modeli LLM</h1>
        
        <h2>Dostępne Raporty</h2>
        
        <h3>Najnowszy Raport</h3>
        <ul>
    """
        
        # Dodaj linki do najnowszego raportu
        latest_md = output_dir / "comparison_report_latest.md"
        latest_html = output_dir / "comparison_report_latest.html"
        
        if latest_html.exists():
            html += f'        <li><a href="{latest_html.name}" class="latest">Najnowszy raport (HTML)</a></li>\n'
        if latest_md.exists():
            html += f'        <li><a href="{latest_md.name}" class="latest">Najnowszy raport (Markdown)</a></li>\n'
        
        html += """    </ul>
        
        <h3>Wszystkie Raporty</h3>
        <table>
            <tr>
                <th>Data</th>
                <th>HTML</th>
                <th>Markdown</th>
                <th>PDF</th>
            </tr>
    """
        
        # Znajdź wszystkie unikalne daty raportów
        report_dates = set()
        for report in itertools.chain(markdown_reports, html_reports, pdf_reports):
            match = re.search(r'comparison_report_(\d+)_', report.name)
            if match:
                report_dates.add(match.group(1))
        
        # Posortuj daty od najnowszych
        report_dates = sorted(report_dates, reverse=True)
        
        # Dodaj wiersze tabeli dla każdej daty
        for date in report_dates:
            timestamp_pattern = f"comparison_report_{date}_"
            date_formatted = f"{date[:4]}-{date[4:6]}-{date[6:8]} {date[9:11]}:{date[11:13]}:{date[13:15]}" if len(date) > 8 else f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            
            html_link = ""
            md_link = ""
            pdf_link = ""
            
            # Znajdź pliki dla tej daty
            for report in html_reports:
                if timestamp_pattern in report.name:
                    html_link = f'<a href="{report.name}">HTML</a>'
                    break
            
            for report in markdown_reports:
                if timestamp_pattern in report.name:
                    md_link = f'<a href="{report.name}">Markdown</a>'
                    break
            
            for report in pdf_reports:
                if timestamp_pattern in report.name:
                    pdf_link = f'<a href="{report.name}">PDF</a>'
                    break
            
            html += f"""        <tr>
                <td>{date_formatted}</td>
                <td>{html_link}</td>
                <td>{md_link}</td>
                <td>{pdf_link}</td>
            </tr>
    """
        
        html += """    </table>
    </body>
    </html>
    """
        
        # Zapisz plik indeksu
        with open(output_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        # Utwórz link symboliczny report_list.html -> index.html dla kompatybilności
        symlink_path = output_dir / "report_list.html"
        create_symlink_or_copy(output_dir / "index.html", symlink_path)
    
    def create_symlink_or_copy(source: Path, target: Path) -> None:
        """
        Tworzy link symboliczny lub kopię pliku, w zależności od systemu operacyjnego
        
        Args:
            source: Ścieżka do pliku źródłowego
            target: Ścieżka docelowa dla linku/kopii
        """
        # Usuń istniejący plik/link jeśli istnieje
        if target.exists() or target.is_symlink():
            target.unlink()
        
        try:
            # Próba utworzenia linku symbolicznego
            target.symlink_to(source.name)
        except (OSError, AttributeError):
            # Na systemach bez wsparcia dla linków symbolicznych (np. Windows bez uprawnień)
            # lub w starszych wersjach Python, skopiuj plik
            shutil.copy2(source, target)
    ```
    
    # 8. Finalna Optymalizacja Modułu Głównego - Integracja Wszystkich Komponentów
    
    ```python
    class EvopySystem:
        """
        Główna klasa integrująca wszystkie komponenty systemu Evopy.
        Służy jako fasada dla całej aplikacji.
        """
        
        def __init__(self, config_path: Optional[Path] = None):
            """
            Inicjalizacja systemu Evopy
            
            Args:
                config_path: Ścieżka do pliku konfiguracyjnego (opcjonalnie)
            """
            # Ustawienie konfiguracji
            self.config_path = config_path or APP_DIR / "config.json"
            self.config = self._load_config()
            
            # Inicjalizacja podsystemów
            self.dependency_manager = self._init_dependency_manager()
            self.text2python = self._init_text2python()
            self.docker_sandbox = self._init_docker_sandbox()
            self.query_analyzer = self._init_query_analyzer()
            
            # System ewolucyjny - drzewo decyzyjne
            self.decision_tree = self._init_decision_tree()
            
            # System konwersacji
            self.conversation_manager = self._init_conversation_manager()
            
            logger.info("System Evopy zainicjalizowany pomyślnie")
        
        def _load_config(self) -> Dict[str, Any]:
            """Ładuje konfigurację z pliku"""
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'r') as f:
                        return json.load(f)
                else:
                    # Utwórz domyślną konfigurację
                    config = DEFAULT_CONFIG.copy()
                    os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                    with open(self.config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    return config
            except Exception as e:
                logger.error(f"Błąd podczas ładowania konfiguracji: {e}")
                return DEFAULT_CONFIG.copy()
        
        def _init_dependency_manager(self):
            """Inicjalizacja menedżera zależności"""
            # Import lokalny, aby uniknąć problemów z cyklicznymi importami
            from dependency_manager import DependencyManager
            return DependencyManager()
        
        def _init_text2python(self):
            """Inicjalizacja modułu konwersji tekst-na-kod"""
            # Import lokalny, aby uniknąć problemów z cyklicznymi importami
            try:
                from modules.text2python import Text2Python
                return Text2Python(
                    model_name=self.config.get("model", DEFAULT_MODEL),
                    code_dir=CODE_DIR
                )
            except ImportError:
                from text2python import Text2Python
                return Text2Python(
                    model_name=self.config.get("model", DEFAULT_MODEL),
                    code_dir=CODE_DIR
                )
        
        def _init_docker_sandbox(self):
            """Inicjalizacja piaskownicy Docker"""
            # Import lokalny, aby uniknąć problemów z cyklicznymi importami
            from docker_sandbox import DockerSandbox
            return DockerSandbox(
                base_dir=SANDBOX_DIR,
                docker_image=self.config.get("sandbox_image", "python:3.9-slim"),
                timeout=self.config.get("sandbox_timeout", 30)
            )
        
        def _init_query_analyzer(self):
            """Inicjalizacja analizatora zapytań"""
            try:
                from query_analyzer import QueryAnalyzer
                return QueryAnalyzer()
            except ImportError:
                logger.warning("Nie można zainicjalizować QueryAnalyzer - moduł niedostępny")
                return None
        
        def _init_decision_tree(self):
            """Inicjalizacja drzewa decyzyjnego"""
            try:
                from decision_tree import create_decision_tree
                return create_decision_tree(name=f"Evopy-System-{self.config.get('model', DEFAULT_MODEL)}")
            except ImportError:
                logger.warning("Nie można zainicjalizować drzewa decyzyjnego - moduł niedostępny")
                return None
        
        def _init_conversation_manager(self):
            """Inicjalizacja menedżera konwersacji"""
            # W przyszłości, gdy zostanie stworzony oddzielny moduł konwersacji
            # Obecnie używamy prostego słownika
            return {
                "conversations": {},
                "current_id": None
            }
        
        def process_query(self, query: str) -> Dict[str, Any]:
            """
            Główna metoda przetwarzająca zapytanie użytkownika.
            Integruje wszystkie podsystemy i przeprowadza kompletny proces:
            1. Analizę zapytania
            2. Generowanie kodu
            3. Weryfikację kodu
            4. Wykonanie kodu
            5. Wyjaśnienie i dokumentację
            
            Args:
                query: Zapytanie użytkownika
                
            Returns:
                Dict: Wynik przetwarzania zapytania zawierający wszystkie istotne informacje
            """
            try:
                logger.info(f"Rozpoczęcie przetwarzania zapytania: '{query}'")
                
                # 1. Analiza zapytania (jeśli dostępny analizator)
                query_analysis = None
                if self.query_analyzer:
                    query_analysis = self.query_analyzer.analyze_query(query)
                    logger.info(f"Analiza zapytania: złożoność={query_analysis.get('complexity', 0)}, "
                               f"typy zadań={query_analysis.get('task_types', [])}")
                
                # 2. Generowanie kodu
                code_result = self.text2python.generate_code(query)
                
                if not code_result["success"]:
                    logger.warning(f"Nie udało się wygenerować kodu: {code_result.get('error', 'Nieznany błąd')}")
                    return code_result
                
                # 3. Sprawdzenie wygenerowanego kodu
                code = code_result["code"]
                
                # Próba walidacji kodu jeśli metoda jest dostępna
                validation_result = None
                if hasattr(self.docker_sandbox, 'validate_code'):
                    validation_result = self.docker_sandbox.validate_code(code)
                    if validation_result and not validation_result.get("is_valid", True):
                        logger.warning(f"Kod nie przeszedł walidacji: {validation_result.get('issues', [])}")
                        code_result["validation"] = validation_result
                        return code_result
                
                # 4. Wykonanie kodu w piaskownicy
                execution_result = self.docker_sandbox.run(code)
                
                # 5. Połącz wszystkie wyniki
                result = {
                    "success": execution_result.get("success", False),
                    "query": query,
                    "code": code,
                    "output": execution_result.get("output", ""),
                    "error": execution_result.get("error", ""),
                    "execution_time": execution_result.get("execution_time", 0),
                    "explanation": code_result.get("explanation", ""),
                    "analysis": code_result.get("analysis", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # 6. Zapisz wynik w drzewie decyzyjnym (jeśli dostępne)
                if self.decision_tree:
                    # Dodaj wynik do drzewa decyzyjnego
                    result_node_id = self.decision_tree.add_node(
                        query=query,
                        decision_type="query_execution",
                        content=f"Wykonanie kodu dla zapytania: {query}",
                        parent_id=None  # Można dodać odniesienie do węzła rodzica
                    )
                    


# Podsumowanie Usprawnień dla Evopy

Po analizie kodu źródłowego Evopy oraz zidentyfikowanych problemów, zaproponowałem szereg usprawnień mających na celu poprawę funkcjonalności, niezawodności i zdolności ewolucyjnych systemu. Poniżej znajduje się podsumowanie kluczowych usprawnień.

## 1. Rozwiązanie Głównych Problemów Technicznych

### 1.1. Naprawa błędu w `docker_sandbox.py`

Zidentyfikowaliśmy i naprawiliśmy błąd w module `docker_sandbox.py`, który powodował awarię podczas wykonywania kodu z powodu niezdefiniowanej zmiennej `e2`. Błąd wystąpił w bloku obsługi wyjątków podczas próby ponownego importu modułu. Poprawione rozwiązanie:

- Dodanie prawidłowej obsługi błędów z jednoznacznie zdefiniowanymi zmiennymi
- Lepsze zarządzanie wyjątkami w różnych scenariuszach awarii
- Bardziej rozbudowana struktura try-except-finally dla zapewnienia niezawodności

### 1.2. Usprawnienie obsługi wyrażeń arytmetycznych w `text2python.py`

Poprawiliśmy sposób obsługi prostych wyrażeń arytmetycznych, zapewniając, że system zawsze generuje kod wykorzystujący zmienne (np. `x = 1; y = 1; result = x + y`) zamiast bezpośrednich obliczeń. To usprawnienie:

- Poprawia czytelność generowanego kodu
- Ułatwia modyfikację i rozszerzanie kodu w przyszłości
- Zapewnia lepsze dopasowanie do oczekiwań użytkowników

### 1.3. Bardziej niezawodne wyodrębnianie kodu z odpowiedzi modelu

Wprowadziliśmy bardziej zaawansowane wyodrębnianie kodu z odpowiedzi modeli LLM, z lepszą detekcją formatowania markdown i obsługą różnych przypadków:

- Rozpoznawanie bloków kodu markdown (```python ... ```)
- Wykrywanie "surowego" kodu Python na podstawie typowych wzorców
- Inteligentny wybór najdłuższego/najbardziej prawdopodobnego fragmentu kodu

## 2. Zaawansowane Funkcjonalności Bezpieczeństwa

### 2.1. Ulepszona piaskownica Docker

Rozszerzyliśmy zabezpieczenia w piaskownicy Docker:

- Bardziej restrykcyjne limity zasobów (CPU, pamięć, liczba procesów, deskryptory plików)
- Blokowanie operacji sieciowych i dostępu do systemu plików poza piaskownicą
- Dwupoziomowy system timeoutów (SIGTERM a następnie SIGKILL)
- Walidacja kodu przed wykonaniem pod kątem potencjalnie niebezpiecznych wzorców

### 2.2. Statyczna Analiza Bezpieczeństwa Kodu

Dodaliśmy nową funkcję `validate_code()` do statycznej analizy bezpieczeństwa:

- Wykrywanie niebezpiecznych wywołań (eval, exec, subprocess z shell=True)
- Sprawdzanie operacji na plikach i systemie
- Sugestie dotyczące poprawy stylu i bezpieczeństwa kodu

## 3. Mechanizmy Ewolucyjne

### 3.1. Nowy Moduł Analizy Zapytań

Wprowadziliśmy nowy moduł `query_analyzer.py`, który:

- Analizuje złożoność zapytań użytkownika
- Klasyfikuje zapytania według typu zadania (algorytm, przetwarzanie danych, web, itp.)
- Szacuje wymagane zasoby i czas wykonania
- Ekstrahuje kluczowe słowa do zrozumienia kontekstu

### 3.2. System Uczenia się z Interakcji

Zaimplementowaliśmy mechanizm uczenia się na podstawie interakcji z użytkownikiem:

- Zapisywanie feedbacku użytkownika i wyników generowania kodu
- Automatyczne dostosowywanie promptów systemowych na podstawie historii powodzeń/niepowodzeń
- Analiza typowych problemów i dodawanie specjalnych instrukcji do promptu

## 4. Integracja Komponentów

### 4.1. Klasa Fasadowa EvopySystem

Stworzyliśmy nową klasę fasadową `EvopySystem`, która:

- Integruje wszystkie podsystemy w jednym miejscu
- Zapewnia spójny interfejs dla całego systemu
- Obsługuje inicjalizację i konfigurację różnych komponentów
- Oferuje główną metodę `process_query()` do przetwarzania zapytań

### 4.2. Rozbudowany System Raportów

Udoskonaliliśmy system generowania raportów porównawczych:

- Tworzenie raportów w różnych formatach (Markdown, HTML, PDF)
- Interaktywne wykresy w raportach HTML (Chart.js)
- Automatyczne generowanie indeksu raportów
- Analiza trendów w czasie dla różnych modeli

## 5. Poprawiona Dokumentacja i Prompty

### 5.1. Lepsze Prompty dla Modeli LLM

Opracowaliśmy ulepszone prompty dla modeli językowych:

- Bardziej szczegółowe instrukcje dla generowania kodu
- Wyraźne zasady dotyczące formatowania i stylu
- Ewolucyjne dostosowanie promptów na podstawie napotkanych problemów

### 5.2. Dokumentacja Kodu

Zaktualizowaliśmy i rozszerzyliśmy dokumentację kodu:

- Dokładniejsze opisy funkcji i klas
- Szczegółowa informacja o parametrach i wartościach zwracanych
- Przykłady zastosowania poszczególnych funkcji

## Rekomendacje dotyczące przyszłego rozwoju

1. **Rozbudowa mechanizmów ewolucyjnych** - dalsze rozwijanie systemów uczenia się z interakcji
2. **Integracja z popularnymi frameworkami** - dodanie wsparcia dla Django, Flask, FastAPI
3. **System współpracy** - funkcje eksportu/importu projektów, dzielenie się rozwiązaniami
4. **Zaawansowana wizualizacja kodu** - interaktywne reprezentacje generowanego kodu
5. **Optymalizacja wydajności** - redukcja czasu oczekiwania i zużycia zasobów

## Przykładowe poprawione prompty dla modelu LLM

### Prompt dla Generowania Kodu:

```
Jesteś ekspertem w konwersji opisu w języku naturalnym na kod Python.
Twoim zadaniem jest wygenerowanie funkcji Python, która realizuje opisane zadanie.

Generuj tylko kod Python, bez dodatkowych wyjaśnień. Kod powinien być kompletny i gotowy do uruchomienia.
Funkcja powinna być nazwana 'execute' i powinna zwracać wynik działania.

ZAWSZE przestrzegaj następujących zasad:
1. Dla prostych operacji matematycznych, zawsze używaj zmiennych (np. 'x = 1; y = 2; result = x + y')
2. Dodawaj odpowiednie obsługi błędów i walidację danych wejściowych
3. Unikaj używania bezpośrednio 'import *' - importuj tylko konkretne funkcje/klasy
4. Zawsze dodawaj krótkie komentarze wyjaśniające najważniejsze części kodu
5. Upewnij się, że kod jest bezpieczny i nie wykonuje niebezpiecznych operacji
6. NIE używaj markdown do formatowania kodu - generuj tylko czysty kod Python
7. Jeśli zadanie dotyczy wykonania poleceń systemowych, zawsze używaj subprocess z parametrem shell=False
8. W przypadku operacji na plikach i katalogach, używaj ścieżek względnych i biblioteki pathlib zamiast os.path

SZCZEGÓLNIE ZWRÓĆ UWAGĘ NA:
- Dla prostych obliczeń matematycznych, ZAWSZE używaj zmiennych (np. x = 1, y = 2, result = x + y)
- Przy operacjach systemowych, używaj subprocess.run() z parametrem shell=False dla bezpieczeństwa
- Przy operacjach na plikach, zawsze używaj konstrukcji 'with open()' i obsługuj wyjątki
- Przy operacjach sieciowych i API, zawsze obsługuj błędy połączenia i parsowania

Utwórz funkcję Python, która realizuje następujące zadanie:
```

### Prompt dla Analizy Kodu:

```
Jesteś ekspertem w analizie i wyjaśnianiu kodu Python.
Twoim zadaniem jest dokładne wyjaśnienie co robi podany kod i sprawdzenie, czy jest zgodny z intencją użytkownika.

Przeprowadź analizę kodu w następujących krokach:
1. Wyjaśnij funkcjonalność kodu w prostym języku, zrozumiałym dla osób bez doświadczenia w programowaniu
2. Zidentyfikuj potencjalne problemy: błędy składniowe, logiczne, bezpieczeństwa lub wydajności
3. Zaproponuj konkretne ulepszenia, które mogłyby poprawić kod
4. Oceń, czy kod realizuje zadanie opisane w zapytaniu użytkownika

Podaj ocenę kodu w formacie JSON z następującymi polami:
- "is_correct": boolean - czy kod jest poprawny składniowo
- "matches_intent": boolean - czy kod realizuje intencję użytkownika
- "efficiency": float (0-1) - ocena wydajności kodu
- "security": float (0-1) - ocena bezpieczeństwa kodu
- "issues": [string] - lista wykrytych problemów
- "suggestions": [string] - lista sugerowanych ulepszeń

Na końcu zapytaj użytkownika, czy wyjaśnienie jest jasne i czy kod spełnia jego oczekiwania.
```