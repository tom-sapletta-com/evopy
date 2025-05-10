# Devopy – Dokumentacja modułu

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
