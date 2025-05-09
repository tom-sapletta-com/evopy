# Moduły Konwersji (Converters)

Ten katalog zawiera moduły do konwersji między różnymi formatami, takimi jak tekst naturalny, kod Python, polecenia shell, zapytania SQL i wyrażenia regularne.

## Dostępne Konwertery

- **Text2Python** - konwersja opisu w języku naturalnym na kod Python
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

## Uwagi

- Wszystkie konwertery używają modeli językowych, więc jakość wyników może się różnić w zależności od użytego modelu.
- Przed użyciem konwerterów upewnij się, że model jest dostępny za pomocą metody `ensure_model_available()`.
- W przypadku błędów sprawdź logi, które zawierają szczegółowe informacje o problemach.
