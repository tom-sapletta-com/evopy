# Text2Python - Rozszerzenia i Zaawansowane Funkcjonalności

Ten dokument opisuje rozszerzone funkcjonalności modułu Text2Python, które znacząco zwiększają jego możliwości w zakresie generowania kodu Python na podstawie opisów w języku naturalnym.

## Spis treści

1. [Obsługa różnych typów danych i struktur](#1-obsługa-różnych-typów-danych-i-struktur)
2. [Funkcje i algorytmy specjalistyczne](#2-funkcje-i-algorytmy-specjalistyczne)
3. [Operacje na tekście i przetwarzanie języka naturalnego](#3-operacje-na-tekście-i-przetwarzanie-języka-naturalnego)
4. [Obsługa API i integracje zewnętrzne](#4-obsługa-api-i-integracje-zewnętrzne)
5. [Generowanie kodu dla zastosowań specjalistycznych](#5-generowanie-kodu-dla-zastosowań-specjalistycznych)
6. [Rozszerzenia strukturalne i architektoniczne](#6-rozszerzenia-strukturalne-i-architektoniczne)
7. [Integracja z systemami zarządzania wersją i dokumentacją](#7-integracja-z-systemami-zarządzania-wersją-i-dokumentacją)
8. [Przykłady zastosowań](#8-przykłady-zastosowań)
9. [Integracja z systemem autonaprawy zależności](#9-integracja-z-systemem-autonaprawy-zależności)

## 1. Obsługa różnych typów danych i struktur

Moduł Text2Python został rozszerzony o zaawansowane możliwości pracy z różnymi typami danych i strukturami.

### 1.1. Generowanie kodu do obsługi list i kolekcji

```python
# Zapytanie: "stwórz listę z liczbami od 1 do 10"
def execute():
    return list(range(1, 11))
```

### 1.2. Obsługa operacji na słownikach

```python
# Zapytanie: "słownik z krajami i ich stolicami: Polska -> Warszawa, Niemcy -> Berlin"
def execute():
    return {"Polska": "Warszawa", "Niemcy": "Berlin"}
```

### 1.3. Konwersja między formatami danych

```python
# Zapytanie: "konwertuj JSON {'name': 'Jan', 'age': 30} na XML"
def execute(data={"name": "Jan", "age": 30}):
    import xml.etree.ElementTree as ET
    root = ET.Element("person")
    for key, value in data.items():
        ET.SubElement(root, key).text = str(value)
    return ET.tostring(root, encoding="unicode")
```

### 1.4. Przetwarzanie danych tabelarycznych

```python
# Zapytanie: "wczytaj dane z CSV i oblicz statystyki dla kolumny 'Wartość'"
def execute(csv_file="dane.csv"):
    import pandas as pd
    
    # Wczytaj dane z pliku CSV
    df = pd.read_csv(csv_file)
    
    # Oblicz statystyki dla kolumny 'Wartość'
    if 'Wartość' in df.columns:
        return {
            "średnia": df['Wartość'].mean(),
            "mediana": df['Wartość'].median(),
            "min": df['Wartość'].min(),
            "max": df['Wartość'].max(),
            "odchylenie_std": df['Wartość'].std()
        }
    else:
        return {"error": "Kolumna 'Wartość' nie istnieje w pliku CSV"}
```

## 2. Funkcje i algorytmy specjalistyczne

Moduł oferuje generowanie kodu dla różnych algorytmów i operacji specjalistycznych.

### 2.1. Obsługa operacji statystycznych

```python
# Zapytanie: "oblicz średnią, medianę i odchylenie standardowe dla listy [1, 2, 3, 4, 5]"
def execute(data=[1, 2, 3, 4, 5]):
    import statistics
    return {
        "średnia": statistics.mean(data),
        "mediana": statistics.median(data),
        "odchylenie_std": statistics.stdev(data)
    }
```

### 2.2. Algorytmy sortowania z różnymi parametrami

```python
# Zapytanie: "posortuj listę słowników po polu 'wiek'"
def execute(data=[{"imię": "Anna", "wiek": 30}, {"imię": "Jan", "wiek": 25}]):
    return sorted(data, key=lambda x: x["wiek"])
```

### 2.3. Generowanie kodu dla algorytmów uczenia maszynowego

```python
# Zapytanie: "prosty klasyfikator kNN"
def execute(X_train=None, y_train=None, X_test=None, n_neighbors=3):
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.datasets import load_iris
    
    # Jeśli dane nie zostały dostarczone, użyj zbioru Iris
    if X_train is None or y_train is None:
        iris = load_iris()
        X_train, y_train = iris.data, iris.target
    
    if X_test is None:
        # Użyj części danych treningowych jako testowych
        X_test = X_train[:10]
    
    # Utwórz i wytrenuj model
    model = KNeighborsClassifier(n_neighbors=n_neighbors)
    model.fit(X_train, y_train)
    
    # Wykonaj predykcję
    predictions = model.predict(X_test)
    
    return {
        "predictions": predictions.tolist(),
        "model": model
    }
```

### 2.4. Wizualizacja danych

```python
# Zapytanie: "wykres liniowy dla danych [1, 4, 9, 16, 25]"
def execute(data=[1, 4, 9, 16, 25], save_path="wykres.png"):
    import matplotlib.pyplot as plt
    
    plt.figure(figsize=(10, 6))
    plt.plot(data, marker='o', linestyle='-', color='blue')
    plt.title('Wykres liniowy')
    plt.xlabel('Indeks')
    plt.ylabel('Wartość')
    plt.grid(True)
    
    # Zapisz wykres do pliku
    plt.savefig(save_path)
    
    return f"Wykres został zapisany do pliku {save_path}"
```

## 3. Operacje na tekście i przetwarzanie języka naturalnego

Moduł umożliwia generowanie kodu do zaawansowanego przetwarzania tekstu i NLP.

### 3.1. Zaawansowane przetwarzanie tekstu

```python
# Zapytanie: "znajdź najczęściej występujące słowa w tekście"
def execute(text, n=5):
    import re
    from collections import Counter
    words = re.findall(r'\w+', text.lower())
    return Counter(words).most_common(n)
```

### 3.2. Tłumaczenie tekstów

```python
# Zapytanie: "przetłumacz tekst z polskiego na angielski"
def execute(text, source_lang="pl", target_lang="en"):
    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(text)
    except ImportError:
        return "Zainstaluj moduł deep_translator: pip install deep_translator"
```

### 3.3. Analiza sentymentu

```python
# Zapytanie: "oceń sentyment tekstu"
def execute(text):
    try:
        from textblob import TextBlob
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return "Pozytywny"
        elif analysis.sentiment.polarity < 0:
            return "Negatywny"
        else:
            return "Neutralny"
    except ImportError:
        return "Zainstaluj moduł textblob: pip install textblob"
```

### 3.4. Ekstrakcja informacji z tekstu

```python
# Zapytanie: "wyodrębnij adresy email z tekstu"
def execute(text):
    import re
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails
```

## 4. Obsługa API i integracje zewnętrzne

Moduł umożliwia generowanie kodu do integracji z zewnętrznymi API i usługami.

### 4.1. Generowanie kodu do pobierania danych z API

```python
# Zapytanie: "pobierz dane pogodowe dla Warszawy"
def execute(city="Warszawa", api_key=None):
    import requests
    if not api_key:
        return "Potrzebny jest klucz API. Zarejestruj się na OpenWeatherMap."
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    return response.json()
```

### 4.2. Integracja z bazami danych

```python
# Zapytanie: "pobierz dane z bazy SQLite"
def execute(db_path, query="SELECT * FROM users"):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    conn.close()
    return result
```

### 4.3. Skrypty do automatyzacji zadań

```python
# Zapytanie: "monitoruj stronę internetową co godzinę"
def execute(url, interval=3600):
    import requests
    import time
    import hashlib
    
    def monitor():
        last_hash = None
        while True:
            response = requests.get(url)
            content_hash = hashlib.md5(response.content).hexdigest()
            if last_hash and last_hash != content_hash:
                print(f"Strona {url} została zmieniona!")
            last_hash = content_hash
            time.sleep(interval)
    
    # W rzeczywistym kodzie należałoby użyć wątku lub procesu
    return "Uruchomiono monitoring strony " + url
```

### 4.4. Obsługa protokołów sieciowych

```python
# Zapytanie: "stwórz prosty serwer HTTP"
def execute(port=8000):
    import http.server
    import socketserver
    
    handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serwer uruchomiony na porcie {port}")
        httpd.serve_forever()
```

## 5. Generowanie kodu dla zastosowań specjalistycznych

Moduł umożliwia generowanie kodu dla różnych zastosowań specjalistycznych.

### 5.1. Kod do analizy danych finansowych

```python
# Zapytanie: "oblicz zwrot z inwestycji"
def execute(początkowa_inwestycja, końcowa_wartość, lata):
    # Wzór na roczną stopę zwrotu (CAGR)
    cagr = (końcowa_wartość / początkowa_inwestycja) ** (1 / lata) - 1
    return {
        "CAGR": cagr,
        "zwrot_procentowy": cagr * 100,
        "całkowity_zwrot": końcowa_wartość - początkowa_inwestycja
    }
```

### 5.2. Kod do analizy danych biomedycznych

```python
# Zapytanie: "oblicz wskaźnik BMI"
def execute(waga_kg, wzrost_m):
    bmi = waga_kg / (wzrost_m ** 2)
    kategoria = None
    if bmi < 18.5:
        kategoria = "niedowaga"
    elif bmi < 25:
        kategoria = "waga prawidłowa"
    elif bmi < 30:
        kategoria = "nadwaga"
    else:
        kategoria = "otyłość"
    return {"bmi": bmi, "kategoria": kategoria}
```

### 5.3. Generowanie skryptów do automatyzacji pracy z multimediami

```python
# Zapytanie: "zmień rozmiar wszystkich obrazów w katalogu"
def execute(directory, width=800, height=600):
    try:
        from PIL import Image
        import os
        
        resized_files = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(directory, filename)
                with Image.open(filepath) as img:
                    img_resized = img.resize((width, height))
                    output_path = os.path.join(directory, f"resized_{filename}")
                    img_resized.save(output_path)
                    resized_files.append(output_path)
        return resized_files
    except ImportError:
        return "Zainstaluj moduł Pillow: pip install Pillow"
```

### 5.4. Kod do obsługi danych geograficznych

```python
# Zapytanie: "oblicz odległość między współrzędnymi geograficznymi"
def execute(lat1, lon1, lat2, lon2):
    from math import radians, cos, sin, asin, sqrt
    
    # Konwersja stopni na radiany
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Wzór haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Promień Ziemi w kilometrach
    
    return c * r
```

## 6. Rozszerzenia strukturalne i architektoniczne

Moduł umożliwia generowanie bardziej złożonych struktur kodu.

### 6.1. Obsługa funkcji asynchronicznych

```python
# Zapytanie: "pobierz asynchronicznie dane z kilku URL-i"
async def execute(urls):
    import aiohttp
    import asyncio
    
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()
    
    async def fetch_all(urls):
        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, url) for url in urls]
            return await asyncio.gather(*tasks)
    
    if asyncio.get_event_loop().is_running():
        return "Funkcja wymaga uruchomienia w pętli zdarzeń asyncio"
    else:
        return asyncio.run(fetch_all(urls))
```

### 6.2. Generowanie klas zamiast prostych funkcji

```python
# Zapytanie: "utwórz klasę Osoba z atrybutami imię, nazwisko i wiek"
def execute():
    class Osoba:
        def __init__(self, imię, nazwisko, wiek):
            self.imię = imię
            self.nazwisko = nazwisko
            self.wiek = wiek
        
        def pełne_imię(self):
            return f"{self.imię} {self.nazwisko}"
        
        def jest_pełnoletni(self):
            return self.wiek >= 18
    
    # Przykład użycia
    return Osoba("Jan", "Kowalski", 30)
```

### 6.3. Kod generujący aplikacje webowe

```python
# Zapytanie: "stwórz prostą aplikację Flask z endpointem /hello"
def execute():
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/hello')
    def hello():
        return {'message': 'Hello, World!'}
    
    # Instrukcja uruchomienia
    return "Aplikacja została utworzona. Uruchom ją za pomocą: app.run()"
```

### 6.4. Tworzenie mikroserwisów i API

```python
# Zapytanie: "stwórz API REST z FastAPI do zarządzania zadaniami"
def execute():
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    from typing import List, Optional
    import uvicorn
    
    app = FastAPI(title="API Zadań", description="API do zarządzania zadaniami")
    
    class Task(BaseModel):
        id: Optional[int] = None
        title: str
        description: Optional[str] = None
        completed: bool = False
    
    # Symulacja bazy danych
    db = []
    
    @app.post("/tasks/", response_model=Task)
    def create_task(task: Task):
        task_dict = task.dict()
        task_dict["id"] = len(db) + 1
        db.append(task_dict)
        return task_dict
    
    @app.get("/tasks/", response_model=List[Task])
    def read_tasks():
        return db
    
    @app.get("/tasks/{task_id}", response_model=Task)
    def read_task(task_id: int):
        for task in db:
            if task["id"] == task_id:
                return task
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Instrukcja uruchomienia
    return "API zostało utworzone. Uruchom je za pomocą: uvicorn main:app --reload"
```

## 7. Integracja z systemami zarządzania wersją i dokumentacją

Moduł umożliwia generowanie kodu związanego z zarządzaniem wersją i dokumentacją.

### 7.1. Generowanie testów jednostkowych

```python
# Zapytanie: "stwórz testy jednostkowe dla funkcji kalkulator"
def execute():
    import unittest
    
    def add(a, b):
        return a + b
    
    def subtract(a, b):
        return a - b
    
    class TestCalculator(unittest.TestCase):
        def test_add(self):
            self.assertEqual(add(1, 2), 3)
            self.assertEqual(add(-1, 1), 0)
            
        def test_subtract(self):
            self.assertEqual(subtract(5, 2), 3)
            self.assertEqual(subtract(1, 1), 0)
    
    # Przykład użycia
    return "Uruchom testy za pomocą: unittest.main()"
```

### 7.2. Automatyczne dodawanie dokumentacji kodu

```python
# Zapytanie: "dokumentacja dla funkcji obliczającej silnię"
def execute(n):
    """
    Oblicza silnię liczby n.
    
    Parametry:
    n (int): Nieujemna liczba całkowita
    
    Zwraca:
    int: n!, czyli iloczyn liczb od 1 do n
    
    Wyjątki:
    ValueError: Jeśli n jest ujemne
    
    Przykłady:
    >>> execute(5)
    120
    >>> execute(0)
    1
    """
    if n < 0:
        raise ValueError("Silnia jest zdefiniowana tylko dla nieujemnych liczb całkowitych")
    if n == 0:
        return 1
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```

### 7.3. Generowanie plików konfiguracyjnych

```python
# Zapytanie: "stwórz plik requirements.txt dla projektu Flask z obsługą bazy danych"
def execute():
    requirements = """
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
SQLAlchemy==1.4.23
pytest==6.2.5
python-dotenv==0.19.0
gunicorn==20.1.0
"""
    with open("requirements.txt", "w") as f:
        f.write(requirements.strip())
    
    return "Plik requirements.txt został utworzony"
```

## 8. Przykłady zastosowań

Poniżej przedstawiono przykłady zastosowań modułu Text2Python w różnych scenariuszach.

### 8.1. Analiza danych

```python
from modules.text2python import Text2Python

# Inicjalizacja konwertera
converter = Text2Python()

# Generowanie kodu do analizy danych
query = "wczytaj dane z pliku CSV 'dane.csv', oblicz średnią dla kolumny 'Wartość' i narysuj histogram"
result = converter.generate_code(query)

if result["success"]:
    print(result["code"])
    
    # Wykonanie kodu w piaskownicy Docker
    execution_result = converter.execute_in_sandbox(result["code"])
    print(execution_result["output"])
```

### 8.2. Tworzenie aplikacji webowej

```python
from modules.text2python import Text2Python

# Inicjalizacja konwertera
converter = Text2Python()

# Generowanie kodu aplikacji Flask
query = "stwórz aplikację Flask z formularzem logowania i bazą danych SQLite"
result = converter.generate_code(query)

if result["success"]:
    print(result["code"])
    
    # Zapisanie kodu do pliku
    with open("app.py", "w") as f:
        f.write(result["code"])
    
    print("Aplikacja została zapisana do pliku app.py")
```

### 8.3. Automatyzacja zadań

```python
from modules.text2python import Text2Python

# Inicjalizacja konwertera
converter = Text2Python()

# Generowanie skryptu automatyzacji
query = "stwórz skrypt, który co godzinę sprawdza dostępność strony internetowej i wysyła powiadomienie email w przypadku awarii"
result = converter.generate_code(query)

if result["success"]:
    print(result["code"])
    
    # Zapisanie kodu do pliku
    with open("monitor.py", "w") as f:
        f.write(result["code"])
    
    print("Skrypt monitorujący został zapisany do pliku monitor.py")
```

## 9. Integracja z systemem autonaprawy zależności

Moduł Text2Python jest zintegrowany z systemem autonaprawy zależności, który automatycznie wykrywa i naprawia brakujące importy w kodzie.

### 9.1. Automatyczne wykrywanie brakujących importów

System analizuje kod przed wykonaniem i dodaje brakujące importy, co rozwiązuje problemy takie jak "name 'time' is not defined".

### 9.2. Dynamiczne importy podczas wykonania

System obsługuje dynamiczne importy podczas wykonania kodu, co umożliwia korzystanie z bibliotek, które nie były jawnie zaimportowane.

### 9.3. Automatyczna instalacja brakujących bibliotek

System może automatycznie instalować brakujące biblioteki, jeśli są one wymagane przez wygenerowany kod.

```python
# Przykład działania systemu autonaprawy zależności
kod_z_brakującym_importem = """
def execute():
    # Brakuje importu modułu time
    time.sleep(1)
    return "Wykonano"
"""

# Kod po naprawie
kod_naprawiony = """
import time

def execute():
    time.sleep(1)
    return "Wykonano"
"""
```

---

## Powiązane pliki i dokumentacja

### Dokumentacja
- [Struktura projektu](project_structure.md)
- [Architektura piaskownicy](sandbox_architecture.md)
- [Lista TODO](todo_list.md)
- [Interfejs webowy](web_interface.md)

### Moduły i komponenty Python
- [geometry.py](../modules/text2python/extensions/math/geometry.py) — Rozszerzenia geometryczne
- [code_generator.py](../modules/text2python/components/code_generator.py) — Generator kodu
- [extension_manager.py](../modules/text2python/components/extension_manager.py) — Menedżer rozszerzeń
- [code_analyzer.py](../modules/text2python/components/code_analyzer.py) — Analizator kodu
- [text2python.py](../modules/text2python/text2python.py) — Główny moduł konwersji
- [text2python_new.py](../modules/text2python/text2python_new.py) — Nowa architektura

---

Dokumentacja została zaktualizowana: 2025-05-09
