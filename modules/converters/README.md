# Moduły Konwersji (Converters)

Ten katalog zawiera moduły do konwersji między różnymi formatami, takimi jak tekst naturalny, kod Python, polecenia shell, zapytania SQL i wyrażenia regularne.

## Dostępne Konwertery

- **Text2Python** - konwersja opisu w języku naturalnym na kod Python
  - Obsługa różnych typów danych (listy, słowniki, JSON, CSV, XML)
  - Algorytmy specjalistyczne (statystyka, sortowanie, uczenie maszynowe)
  - Przetwarzanie tekstu i NLP (analiza tekstu, tłumaczenia, analiza sentymentu)
  - Integracja z API i bazami danych
  - Generowanie klas i aplikacji webowych
  - Operacje asynchroniczne
- **Python2Text** - konwersja kodu Python na opis w języku naturalnym
- **Text2Shell** - konwersja opisu w języku naturalnym na polecenia shell
- **Shell2Text** - konwersja poleceń shell na opis w języku naturalnym
- **Text2SQL** - konwersja opisu w języku naturalnym na zapytania SQL
- **SQL2Text** - konwersja zapytań SQL na opis w języku naturalnym
- **Text2Regex** - konwersja opisu w języku naturalnym na wyrażenia regularne
- **Regex2Text** - konwersja wyrażeń regularnych na opis w języku naturalnym

## Wymagania

Wszystkie konwertery wymagają zainstalowanego narzędzia Ollama oraz modelu językowego. Domyślnie używany jest model `codellama:7b-code`.

## Przykłady Użycia

### Text2Python

```python
from modules.converters import Text2Python

# Inicjalizacja konwertera
converter = Text2Python()

# Konwersja opisu na kod Python
result = converter.text_to_python("Napisz funkcję, która oblicza silnię liczby")
if result["success"]:
    print(result["code"])
else:
    print(f"Błąd: {result['error']}")

# Wyjaśnienie kodu
code = """
def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)
"""
explanation = converter.explain_code(code)
print(explanation)
```

#### Przykłady zaawansowanych zastosowań Text2Python

```python
# Generowanie kodu do obsługi danych w różnych formatach
result = converter.text_to_python("konwertuj JSON {'name': 'Jan', 'age': 30} na XML")

# Operacje statystyczne
result = converter.text_to_python("oblicz średnią, medianę i odchylenie standardowe dla listy [1, 2, 3, 4, 5]")

# Generowanie kodu dla algorytmów uczenia maszynowego
result = converter.text_to_python("prosty klasyfikator kNN dla zbioru danych Iris")

# Przetwarzanie tekstu i NLP
result = converter.text_to_python("znajdź najczęściej występujące słowa w tekście")
result = converter.text_to_python("przetłumacz tekst z polskiego na angielski")

# Integracja z API
result = converter.text_to_python("pobierz dane pogodowe dla Warszawy z OpenWeatherMap API")

# Generowanie klas
result = converter.text_to_python("utwórz klasę Osoba z atrybutami imię, nazwisko i wiek")

# Generowanie aplikacji webowych
result = converter.text_to_python("stwórz prostą aplikację Flask z endpointem /hello")

# Funkcje asynchroniczne
result = converter.text_to_python("pobierz asynchronicznie dane z kilku URL-i")
```

### Text2Shell

```python
from modules.converters import Text2Shell

# Inicjalizacja konwertera
converter = Text2Shell()

# Konwersja opisu na polecenia shell
result = converter.text_to_shell("Znajdź wszystkie pliki .py w bieżącym katalogu i podkatalogach")
if result["success"]:
    print(result["code"])
else:
    print(f"Błąd: {result['error']}")

# Wyjaśnienie kodu shell
shell_code = "find . -name '*.py' -type f"
explanation = converter.explain_shell(shell_code)
print(explanation)
```

### Text2SQL

```python
from modules.converters import Text2SQL

# Inicjalizacja konwertera
converter = Text2SQL()

# Konwersja opisu na zapytanie SQL
schema = """
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP
);
"""
result = converter.text_to_sql("Znajdź wszystkich użytkowników, których email kończy się na gmail.com", schema)
if result["success"]:
    print(result["code"])
else:
    print(f"Błąd: {result['error']}")

# Wyjaśnienie zapytania SQL
sql_code = "SELECT * FROM users WHERE email LIKE '%gmail.com'"
explanation = converter.explain_sql(sql_code)
print(explanation)
```

### Text2Regex

```python
from modules.converters import Text2Regex

# Inicjalizacja konwertera
converter = Text2Regex()

# Konwersja opisu na wyrażenie regularne
result = converter.text_to_regex("Znajdź wszystkie adresy email w tekście")
if result["success"]:
    print(result["regex"])
else:
    print(f"Błąd: {result['error']}")

# Testowanie wyrażenia regularnego
regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
test_strings = ["user@example.com", "invalid-email", "another.user@gmail.com"]
test_results = converter.test_regex(regex, test_strings)
print(test_results["results"])
```

## Rozszerzone funkcjonalności Text2Python

Moduł Text2Python został rozszerzony o następujące funkcjonalności:

### 1. Obsługa różnych typów danych i struktur

- Generowanie kodu do obsługi list i kolekcji
- Operacje na słownikach i strukturach zagnieżdżonych
- Konwersja między formatami danych (JSON, CSV, XML)
- Przetwarzanie danych tabelarycznych z pandas

### 2. Funkcje i algorytmy specjalistyczne

- Operacje statystyczne (obliczanie średniej, mediany, odchylenia standardowego)
- Algorytmy sortowania z różnymi parametrami
- Generowanie kodu dla algorytmów uczenia maszynowego
- Wizualizacja danych z matplotlib i seaborn

### 3. Operacje na tekście i przetwarzanie języka naturalnego

- Zaawansowane przetwarzanie tekstu (tokenizacja, lematyzacja)
- Tłumaczenie tekstów między językami
- Analiza sentymentu i klasyfikacja tekstu
- Ekstrakcja informacji z tekstu

### 4. Obsługa API i integracje zewnętrzne

- Generowanie kodu do pobierania danych z API
- Integracja z bazami danych (SQLite, MySQL, PostgreSQL)
- Skrypty do automatyzacji zadań i monitorowania
- Obsługa protokołów sieciowych (HTTP, WebSocket)

### 5. Generowanie kodu dla zastosowań specjalistycznych

- Kod do analizy danych finansowych
- Kod do analizy danych biomedycznych
- Generowanie skryptów do automatyzacji pracy z multimediami
- Kod do obsługi danych geograficznych

### 6. Rozszerzenia strukturalne i architektoniczne

- Obsługa funkcji asynchronicznych (async/await)
- Generowanie klas zamiast prostych funkcji
- Kod generujący aplikacje webowe (Flask, FastAPI)
- Tworzenie mikroserwisów i API

### 7. Integracja z systemami zarządzania wersją i dokumentacją

- Generowanie testów jednostkowych
- Automatyczne dodawanie dokumentacji kodu
- Generowanie plików konfiguracyjnych (requirements.txt, setup.py)

## Uwagi

- Wszystkie konwertery używają modeli językowych, więc jakość wyników może się różnić w zależności od użytego modelu.
- Przed użyciem konwerterów upewnij się, że model jest dostępny za pomocą metody `ensure_model_available()`.
- W przypadku błędów sprawdź logi, które zawierają szczegółowe informacje o problemach.
- Dla zaawansowanych funkcjonalności mogą być wymagane dodatkowe biblioteki, które zostaną automatycznie zainstalowane przez system autonaprawy zależności.
