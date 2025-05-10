# Wykrywanie zmiennych w zapytaniach użytkownika

## Wprowadzenie

System Evopy posiada zaawansowany mechanizm wykrywania zmiennych w zapytaniach użytkownika, który umożliwia generowanie kodu Python z parametrami zamiast wartości hardcodowanych. Dzięki temu wygenerowany kod jest bardziej elastyczny, reuzywalny i zgodny z dobrymi praktykami programistycznymi.

## Mechanizm wykrywania zmiennych

### 1. QueryAnalyzer

Głównym komponentem odpowiedzialnym za wykrywanie zmiennych jest `QueryAnalyzer`, który analizuje zapytanie użytkownika i identyfikuje potencjalne zmienne oraz ich wartości. Proces ten obejmuje następujące kroki:

1. **Analiza zapytania** - zapytanie jest analizowane pod kątem występowania wyrażeń matematycznych, liczb i innych potencjalnych zmiennych.
2. **Identyfikacja zmiennych** - wykorzystywane są wyrażenia regularne i heurystyki do identyfikacji zmiennych w różnych kontekstach językowych.
3. **Ekstrakcja wartości** - dla każdej zidentyfikowanej zmiennej określana jest jej wartość początkowa.

### 2. Obsługa wyrażeń matematycznych

System szczególnie dobrze radzi sobie z wykrywaniem zmiennych w wyrażeniach matematycznych, takich jak:

- Proste operacje arytmetyczne (np. "2+2", "5*3")
- Złożone wyrażenia matematyczne (np. "sin(x) + cos(y)")
- Równania z wieloma zmiennymi (np. "ax² + bx + c = 0")

Przykład analizy zapytania "oblicz 2+2":

```python
query_analysis = {
    "variables": {
        "a": 2,
        "b": 2
    },
    "expression": "a+b",
    "query_type": "mathematical"
}
```

## Generowanie kodu z parametrami

### 1. CodeGenerator

Komponent `CodeGenerator` wykorzystuje wyniki analizy zapytania do generowania kodu Python z parametrami. Proces ten obejmuje:

1. **Generowanie funkcji execute** - tworzenie funkcji `execute` z parametrami odpowiadającymi wykrytym zmiennym.
2. **Inicjalizacja zmiennych** - dodawanie kodu inicjalizującego zmienne z wartościami domyślnymi.
3. **Implementacja logiki** - generowanie kodu realizującego żądaną funkcjonalność.

Przykład wygenerowanego kodu dla zapytania "oblicz 2+2":

```python
def execute(a=2, b=2):
    """Funkcja obliczająca sumę dwóch liczb.
    
    Args:
        a (int, optional): Pierwsza liczba. Domyślnie 2.
        b (int, optional): Druga liczba. Domyślnie 2.
        
    Returns:
        int: Suma liczb a i b.
    """
    return a + b
```

### 2. Metoda _wrap_in_execute_function

Metoda `_wrap_in_execute_function` w klasie `CodeGenerator` jest odpowiedzialna za opakowanie wygenerowanego kodu w funkcję `execute` z odpowiednimi parametrami. Metoda ta:

1. Analizuje kod pod kątem użytych zmiennych.
2. Tworzy listę parametrów funkcji z wartościami domyślnymi.
3. Dodaje dokumentację dla funkcji i parametrów.
4. Zapewnia, że funkcja zwraca odpowiedni wynik.

## Integracja z piaskownicą Docker

Wykryte zmienne są również wykorzystywane podczas wykonywania kodu w piaskownicy Docker:

1. Kod z parametrami jest przygotowywany do wykonania w kontenerze Docker.
2. Wartości zmiennych są przekazywane do kontenera.
3. Wynik wykonania kodu jest zwracany do użytkownika.

## Przykłady użycia

### Przykład 1: Proste wyrażenie matematyczne

**Zapytanie użytkownika:** "Oblicz 2+2"

**Wygenerowany kod:**
```python
def execute(a=2, b=2):
    """Funkcja obliczająca sumę dwóch liczb."""
    return a + b
```

### Przykład 2: Złożone wyrażenie matematyczne

**Zapytanie użytkownika:** "Oblicz pole koła o promieniu 5"

**Wygenerowany kod:**
```python
def execute(r=5, pi=3.14159):
    """Funkcja obliczająca pole koła.
    
    Args:
        r (float, optional): Promień koła. Domyślnie 5.
        pi (float, optional): Wartość liczby pi. Domyślnie 3.14159.
        
    Returns:
        float: Pole koła o podanym promieniu.
    """
    return pi * r**2
```

## Zalety parametryzacji kodu

1. **Elastyczność** - możliwość łatwej zmiany wartości zmiennych bez modyfikacji kodu.
2. **Reużywalność** - wygenerowany kod może być użyty wielokrotnie z różnymi parametrami.
3. **Czytelność** - kod z parametrami jest bardziej czytelny i zgodny z dobrymi praktykami programistycznymi.
4. **Testowalność** - łatwiejsze testowanie kodu z różnymi wartościami wejściowymi.

## Ograniczenia i przyszłe ulepszenia

1. **Obsługa bardziej złożonych kontekstów językowych** - poprawa wykrywania zmiennych w różnych językach i kontekstach.
2. **Inteligentne nazewnictwo zmiennych** - generowanie bardziej intuicyjnych nazw zmiennych na podstawie kontekstu.
3. **Obsługa typów danych** - automatyczne wykrywanie i obsługa różnych typów danych dla zmiennych.
4. **Integracja z systemem autonaprawy zależności** - automatyczne dodawanie brakujących importów dla zmiennych.