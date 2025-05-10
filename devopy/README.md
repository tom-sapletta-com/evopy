# devopy

## Uniwersalna instrukcja uruchamiania

### 1. Szybki start jako standalone (rekomendowane dla rozwoju/prototypowania)

```bash
cd devopy
python3 cli.py "stwórz wykres z pliku excel"
python3 api.py
```
- Skrypt sam utworzy środowisko `.venv` i pobierze zależności, jeśli to konieczne.
- Nie musisz aktywować venv ani instalować nic ręcznie!

### 2. Jako paczka pip (instalacja globalna/użytkownika)

```bash
cd devopy
python3 -m venv .venv
source .venv/bin/activate
pip install .
cd ..
python3 -m devopy.cli "stwórz wykres z pliku excel"
python3 -m devopy.api
```

### 3. Automatyzacja środowiska i zależności
- devopy sam tworzy `.venv` jeśli nie istnieje
- Sam pobiera brakujące zależności (np. Flask, matplotlib, openpyxl)
- System automatycznie restartuje się w nowym środowisku

### 4. Przykłady użycia

#### CLI
Uruchom zadanie z poziomu terminala:
```bash
python3 cli.py "stwórz wykres z pliku excel"
python3 cli.py "pobierz dane z api i zapisz do excela"
```

#### API (REST)
Uruchom serwer API (domyślnie port 5000, jeśli zajęty: 5050):
```bash
python3 api.py
```
Lub na wybranym porcie:
```bash
DEVOPY_PORT=8080 python3 api.py
```

Wyślij żądanie HTTP do API:
```bash
curl -X POST http://localhost:5000/run -H 'Content-Type: application/json' -d '{"task": "stwórz wykres z pliku excel"}'
```
Jeśli uruchomiono na innym porcie (np. 8080):
```bash
curl -X POST http://localhost:8080/run -H 'Content-Type: application/json' -d '{"task": "pobierz dane z api i zapisz do excela"}'
```

#### Zmiana portu przez zmienną środowiskową
Możesz uruchomić API na dowolnym porcie przez zmienną środowiskową:
```bash
DEVOPY_PORT=5051 python3 api.py
```

---

### 5. Troubleshooting
#### Błąd: `externally-managed-environment` (PEP 668)
Jeśli zobaczysz komunikat:
```
This environment is externally managed
```
- Oznacza to, że próbujesz zainstalować paczki w systemowym Pythonie (np. na Ubuntu 22.04+).
- **Rozwiązanie:** zawsze korzystaj z lokalnego środowiska venv:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python3 cli.py "twoje zadanie"
  ```

### 6. Tryby uruchamiania
- **Standalone:** katalog `devopy` działa jako samodzielny projekt
- **Jako paczka:** po instalacji przez pip działa z dowolnego miejsca

---

## Test automatyczny (sprawdza oba tryby)

Uruchom:
```bash
bash test_readme.sh
```
Ten skrypt testuje czy polecenia z README działają zarówno w trybie standalone, jak i po instalacji pip.

---

## Kontakt
Autor: tom-sapletta-com
evopy – Dokumentacja modułu

Devopy to ewolucyjny system AI do automatyzacji zadań programistycznych, który samodzielnie instaluje wymagane paczki Python i uczy się na podstawie zadań użytkownika.

## Najważniejsze możliwości
- Interaktywny shell: wpisuj kod Python, polecenia lub importy – devopy sam zainstaluje zależności i wykona kod.
- Ewolucja: system zapamiętuje, jakie paczki były potrzebne do jakich zadań i sugeruje je przy podobnych poleceniach.
- Modularność: obsługa własnych i zewnętrznych paczek (np. text2python, text2shell, requests, matplotlib).
- Automatyczne środowisko: wszystkie paczki instalowane są w `.devopy_venv` i katalogu `.devopy/modules`.

## Szybki start

```bash
cd devopy
python -m devopy.main
```

## Przykłady użycia shellu devopy

```text
devopy> użyj text2python
[INFO] Moduł 'text2python' już dostępny.

devopy> import requests
[INFO] Instaluję paczkę: requests
[INFO] Paczka requests zainstalowana.

devopy> response = requests.get('https://api.github.com')
devopy> print(response.status_code)
200

devopy> zadanie pobierz dane z API
[INFO] Zadanie 'pobierz dane z API' zostało dodane.

devopy> sugeruj
[INFO] Sugerowane paczki: requests
```

## Kluczowe pliki
- `interactive.py` – główny shell, obsługa poleceń, ewolucja
- `dependency.py` – instalacja i wykrywanie paczek
- `evolution.py` – zapamiętywanie zadań i zależności
- `modules.py` – obsługa modularnych bibliotek
- `config.py`, `logger.py` – konfiguracja i logowanie

## Rozwój
- Dodawaj nowe polecenia i integracje w shellu (`interactive.py`)
- System można łatwo rozbudować o obsługę LLM, automatyczne naprawy kodu, analizę poleceń itp.

---

Więcej przykładów i zaawansowanych scenariuszy znajdziesz w głównym README projektu.
