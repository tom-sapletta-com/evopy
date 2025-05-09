# Dokumentacja struktury projektu Evopy

## Wprowadzenie

Evopy to system konwersji języka naturalnego na kod Python, który umożliwia użytkownikom generowanie kodu na podstawie opisów w języku naturalnym. Projekt składa się z kilku modułów, które współpracują ze sobą, aby zapewnić płynne i dokładne tłumaczenie zapytań użytkownika na wykonywalne skrypty Python.

## Aktualna struktura projektu

```
evopy/
├── cross_platform.md            # Dokumentacja wsparcia cross-platform
├── evo.py                       # Główny punkt wejścia aplikacji
├── modules/                     # Katalog zawierający wszystkie moduły
│   ├── text2python/             # Moduł konwersji tekstu na Python
│   │   ├── components/          # Komponenty modułu text2python
│   │   │   ├── code_analyzer.py # Analizator kodu
│   │   │   ├── code_generator.py# Generator kodu Python
│   │   │   ├── docker_sandbox.py# Piaskownica Docker do bezpiecznego wykonania kodu
│   │   │   ├── extension_manager.py # Menedżer rozszerzeń
│   │   │   └── query_analyzer.py# Analizator zapytań użytkownika
│   │   ├── extensions/          # Rozszerzenia dla modułu text2python
│   │   │   └── math/            # Rozszerzenie matematyczne
│   │   │       └── geometry.py  # Funkcje geometryczne
│   │   ├── text2python.py       # Główna klasa modułu text2python
│   │   └── text2python_new.py   # Nowa implementacja modułu text2python
│   └── [inne moduły]            # Inne moduły (text2sql, shell2text, itp.)
├── reports/                     # Raporty i analizy
├── run.sh                       # Skrypt uruchamiający aplikację
└── [inne pliki]                 # Inne pliki konfiguracyjne i pomocnicze
```

## Kluczowe komponenty

### 1. Moduł Text2Python

Główny moduł odpowiedzialny za konwersję tekstu na kod Python. Składa się z następujących komponentów:

#### 1.1. QueryAnalyzer

Analizuje zapytanie użytkownika, aby określić jego typ, złożoność i wykryć zmienne. Wykorzystuje wyrażenia regularne i heurystyki do identyfikacji zmiennych i ich wartości w tekście zapytania.

**Kluczowe funkcje:**
- `analyze_query(query: str) -> Dict[str, Any]`: Analizuje zapytanie i zwraca słownik z informacjami o typie zapytania, wykrytych zmiennych i ich wartościach.

#### 1.2. CodeGenerator

Generuje kod Python na podstawie opisu w języku naturalnym. Wykorzystuje model językowy do wygenerowania kodu, a następnie przetwarza go, aby zapewnić, że jest poprawny i gotowy do wykonania.

**Kluczowe funkcje:**
- `generate_code(prompt: str, query_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`: Generuje kod Python na podstawie opisu i analizy zapytania.
- `_extract_code(text: str) -> str`: Wyodrębnia kod Python z odpowiedzi modelu.
- `_wrap_in_execute_function(code: str, query_analysis: Optional[Dict[str, Any]] = None) -> str`: Owija kod w funkcję execute, jeśli jej nie zawiera.

#### 1.3. ExtensionManager

Zarządza rozszerzeniami modułu text2python, które mogą dostarczać specjalistyczne funkcje dla określonych typów zapytań.

**Kluczowe funkcje:**
- `load_extensions() -> None`: Ładuje wszystkie dostępne rozszerzenia.
- `get_extension_for_query(query: str) -> Optional[Dict[str, Any]]`: Zwraca odpowiednie rozszerzenie dla danego zapytania.

#### 1.4. DockerSandbox

Zapewnia bezpieczne środowisko do wykonania wygenerowanego kodu Python w kontenerze Docker.

**Kluczowe funkcje:**
- `run_code(code: str) -> Dict[str, Any]`: Uruchamia kod w piaskownicy Docker i zwraca wynik.

### 2. Główna klasa Text2Python

Integruje wszystkie komponenty i zapewnia jednolity interfejs dla konwersji tekstu na kod Python.

**Kluczowe funkcje:**
- `process(text: str, **kwargs) -> Dict[str, Any]`: Przetwarza tekst, analizuje zapytanie, generuje kod i zwraca wynik.

## Nowa architektura (w trakcie migracji)

Projekt jest w trakcie migracji do nowej architektury opartej na:

### 1. BaseText2XModule

Abstrakcyjna klasa bazowa dla wszystkich modułów TEXT2X, definiująca wspólny interfejs i funkcjonalności.

**Kluczowe metody:**
- `process(text: str, **kwargs) -> Dict[str, Any]`: Przetwarza tekst i zwraca wynik.
- `validate_input(text: str) -> bool`: Waliduje dane wejściowe.
- `handle_error(error: Exception) -> Dict[str, Any]`: Obsługuje błędy.
- `manage_dependencies() -> None`: Zarządza zależnościami.

### 2. ConfigManager

Centralny menedżer konfiguracji dla wszystkich modułów.

**Kluczowe funkcje:**
- `load_config(module_name: str) -> Dict[str, Any]`: Ładuje konfigurację dla określonego modułu.
- `save_config(module_name: str, config: Dict[str, Any]) -> None`: Zapisuje konfigurację dla określonego modułu.

### 3. ErrorCorrector

System automatycznego korygowania błędów w wygenerowanym kodzie.

**Kluczowe funkcje:**
- `correct_code(code: str, error: str) -> str`: Koryguje kod na podstawie błędu.

## Interfejs webowy

Projekt zawiera również interfejs webowy oparty na Flask, który umożliwia interakcję z modułami konwersji poprzez przeglądarkę.

**Kluczowe funkcje:**
- Wyświetlanie wszystkich dostępnych modułów konwersji.
- Zarządzanie kontenerami Docker.
- Logowanie działań serwera.

## System autonaprawy zależności

Projekt zawiera system autonaprawy zależności, który automatycznie wykrywa i naprawia brakujące importy w kodzie uruchamianym w kontenerze Docker.

**Kluczowe komponenty:**
- `dependency_manager.py`: Analizuje kod i dodaje brakujące importy.
- Integracja z `docker_sandbox.py`: Naprawia kod przed wykonaniem i obsługuje dynamiczne importy.
- Mechanizm `auto_import`: Automatycznie importuje standardowe moduły w środowisku wykonawczym.
