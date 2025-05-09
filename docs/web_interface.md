# Interfejs Webowy Evopy

Evopy oferuje zaawansowany interfejs webowy do zarządzania zadaniami Docker, śledzenia konwersacji i korzystania z modułów konwersji. Interfejs ten jest dostępny pod adresem http://localhost:5000 po uruchomieniu serwera. Najnowsza wersja interfejsu zawiera rozszerzone funkcjonalności dla modułu text2python, umożliwiające generowanie zaawansowanego kodu dla różnych zastosowań.

## Uruchomienie interfejsu webowego

Aby uruchomić interfejs webowy, wykonaj następujące polecenie:

```bash
# Uruchomienie serwera webowego
bash modules/run_server.sh

# Dostęp do interfejsu przez przeglądarkę
# http://localhost:5000
```

## Główne funkcjonalności interfejsu

### 1. Strona główna

Strona główna zawiera listę dostępnych modułów i funkcji:

- **Moduły konwersji** - lista dostępnych modułów konwersji:
  - **text2python** - konwersja tekstu na kod Python z rozszerzonymi funkcjonalnościami:
    - Obsługa różnych typów danych (listy, słowniki, JSON, CSV, XML)
    - Algorytmy specjalistyczne (statystyka, sortowanie, uczenie maszynowe)
    - Przetwarzanie tekstu i NLP (analiza tekstu, tłumaczenia, analiza sentymentu)
    - Integracja z API i bazami danych
    - Generowanie klas i aplikacji webowych
    - Operacje asynchroniczne
  - **shell2text** - konwersja poleceń shell na opis w języku naturalnym
  - **text2sql** - konwersja opisu na zapytania SQL
  - **text2regex** - konwersja opisu na wyrażenia regularne
  - i inne
- **Zarządzanie zadaniami Docker** - link do panelu zarządzania kontenerami Docker
- **Historia konwersacji** - link do historii konwersacji z asystentem

### 2. Zarządzanie zadaniami Docker

Panel zarządzania zadaniami Docker (dostępny pod adresem `/docker`) oferuje następujące funkcjonalności:

#### 2.1. Widok zadań Docker

- **Lista zadań** - przejrzysty widok wszystkich zarejestrowanych zadań Docker
- **Szczegóły zadania** - dla każdego zadania wyświetlane są:
  - Identyfikator zadania
  - Data utworzenia
  - Status zadania
  - Zapytanie użytkownika (prompt)
  - Wyjaśnienie asystenta
  - Kod Python
  - Opcje wykonania

#### 2.2. Funkcje zarządzania zadaniami

- **Wykonywanie poleceń Docker** - możliwość uruchamiania poleceń Docker bezpośrednio z interfejsu
- **Zatrzymywanie kontenerów** - opcja zatrzymania działających kontenerów
- **Uruchamianie kodu** - możliwość uruchomienia kodu Python w kontenerze Docker
- **Podgląd logów** - dostęp do logów kontenerów Docker

#### 2.3. Interfejs użytkownika

- **Zapytania użytkownika** - wyświetlane w kompaktowej formie z możliwością rozwinięcia dłuższych zapytań
- **Kod Python** - wyświetlany z kolorowaniem składni i możliwością rozwinięcia do pełnej wysokości
- **Wyjaśnienia asystenta** - dostępne w sekcji szczegółów zadania
- **Responsywny design** - interfejs dostosowany do różnych urządzeń (desktop, tablet, mobile)

### 3. Historia konwersacji

Panel historii konwersacji (dostępny pod adresem `/conversations`) oferuje następujące funkcjonalności:

#### 3.1. Lista konwersacji

- **Przegląd konwersacji** - lista wszystkich zapisanych konwersacji z asystentem
- **Metadane konwersacji** - dla każdej konwersacji wyświetlane są:
  - Identyfikator konwersacji
  - Data utworzenia
  - Liczba wiadomości
  - Temat konwersacji

#### 3.2. Szczegóły konwersacji

Po kliknięciu na konwersację, użytkownik zostaje przekierowany do widoku szczegółów (dostępnego pod adresem `/conversation/<id>`), który zawiera:

- **Pełna treść konwersacji** - wszystkie wiadomości wymienione między użytkownikiem a asystentem
- **Kod Python** - wyodrębniony kod Python z odpowiedzi asystenta, wyświetlany z kolorowaniem składni
- **Powiązane zadania Docker** - linki do zadań Docker powiązanych z konwersacją
- **Polecenia curl** - przykłady poleceń curl do wykonania zadań Docker przez API

#### 3.3. Funkcje zarządzania konwersacjami

- **Filtrowanie konwersacji** - możliwość filtrowania konwersacji według daty, tematu, itp.
- **Eksport konwersacji** - opcja eksportu konwersacji do różnych formatów (JSON, Markdown, itp.)
- **Usuwanie konwersacji** - możliwość usunięcia wybranych konwersacji

## API REST

Interfejs webowy Evopy udostępnia również API REST do zarządzania zadaniami Docker i konwersacjami:

### Endpointy API

#### Zarządzanie zadaniami Docker

- `GET /docker/api/tasks` - pobieranie listy wszystkich zadań Docker
- `GET /docker/api/task/<id>` - pobieranie szczegółów konkretnego zadania Docker
- `POST /docker/api/run` - uruchamianie kodu w kontenerze Docker
- `POST /docker/api/stop/<id>` - zatrzymywanie kontenera Docker

#### Zarządzanie konwersacjami

- `GET /api/conversations` - pobieranie listy wszystkich konwersacji
- `GET /api/conversation/<id>` - pobieranie szczegółów konkretnej konwersacji
- `POST /api/conversation` - tworzenie nowej konwersacji
- `DELETE /api/conversation/<id>` - usuwanie konwersacji

### Przykłady użycia API

#### Pobieranie listy zadań Docker

```bash
curl -X GET http://localhost:5000/docker/api/tasks
```

#### Uruchamianie kodu w kontenerze Docker

```bash
curl -X POST http://localhost:5000/docker/api/run \
  -H "Content-Type: application/json" \
  -d '{"code": "print(1+1)", "task_id": "unique_task_id"}'
```

#### Pobieranie listy konwersacji

```bash
curl -X GET http://localhost:5000/api/conversations
```

## Integracja z innymi systemami

Interfejs webowy Evopy może być łatwo zintegrowany z innymi systemami poprzez API REST, co umożliwia:

- **Automatyzację zadań** - automatyczne uruchamianie zadań Docker z zewnętrznych systemów
- **Monitorowanie** - śledzenie statusu zadań i konwersacji
- **Raportowanie** - generowanie raportów na podstawie danych z API
- **Integrację z CI/CD** - włączenie Evopy do pipeline'ów CI/CD

## Bezpieczeństwo

Interfejs webowy Evopy zapewnia podstawowe mechanizmy bezpieczeństwa:

- **Izolacja kontenerów** - każde zadanie Docker jest uruchamiane w izolowanym kontenerze
- **Walidacja danych wejściowych** - wszystkie dane wejściowe są walidowane przed przetworzeniem
- **Ograniczenia zasobów** - kontenery Docker mają ograniczone zasoby (CPU, pamięć, itp.)
- **Logowanie zdarzeń** - wszystkie operacje są logowane dla celów audytowych

## Rozwiązywanie problemów

### Typowe problemy i ich rozwiązania

1. **Problem**: Serwer webowy nie uruchamia się
   **Rozwiązanie**: Sprawdź, czy port 5000 nie jest zajęty przez inną aplikację. Możesz zmienić port w pliku `modules/server.py`.

2. **Problem**: Zadania Docker nie są widoczne w interfejsie
   **Rozwiązanie**: Upewnij się, że Docker jest uruchomiony i dostępny dla użytkownika.

3. **Problem**: Konwersacje nie są zapisywane
   **Rozwiązanie**: Sprawdź, czy katalog `history` istnieje i ma odpowiednie uprawnienia.

4. **Problem**: Kod Python nie jest kolorowany
   **Rozwiązanie**: Upewnij się, że biblioteka Prism.js jest poprawnie załadowana.

## Rozszerzone funkcjonalności modułu text2python w interfejsie webowym

Interfejs webowy został rozszerzony o nowe funkcjonalności dla modułu text2python, dostępne pod adresem `/text2python`:

### 1. Kategorie zastosowań

Interfejs oferuje wybierane kategorie zastosowań dla modułu text2python:

- **Struktury danych** - generowanie kodu do pracy z listami, słownikami, JSON, CSV, XML
- **Algorytmy** - generowanie kodu dla różnych algorytmów i operacji matematycznych
- **Przetwarzanie tekstu** - generowanie kodu do analizy tekstu, tłumaczenia, analizy sentymentu
- **Integracje z API** - generowanie kodu do komunikacji z zewnętrznymi API
- **Aplikacje webowe** - generowanie kodu dla aplikacji Flask i FastAPI
- **Bazy danych** - generowanie kodu do pracy z różnymi bazami danych
- **Wizualizacja danych** - generowanie kodu do tworzenia wykresów i wizualizacji

### 2. Przykłady zapytań

Dla każdej kategorii interfejs oferuje przykłady zapytań, które można użyć jako punkt wyjścia:

- "Stwórz listę z liczbami od 1 do 10"
- "Oblicz średnią, medianę i odchylenie standardowe dla listy [1, 2, 3, 4, 5]"
- "Znajdź najczęściej występujące słowa w tekście"
- "Pobierz dane pogodowe dla Warszawy"
- "Stwórz prostą aplikację Flask z endpointem /hello"

### 3. Zaawansowane opcje

Interfejs oferuje zaawansowane opcje dla modułu text2python:

- **Wybór modelu** - możliwość wyboru różnych modeli językowych
- **Parametry generowania** - możliwość dostosowania parametrów generowania kodu (temperatura, max_tokens)
- **Automatyczna instalacja zależności** - opcja automatycznej instalacji brakujących bibliotek
- **Generowanie testów** - opcja automatycznego generowania testów jednostkowych dla wygenerowanego kodu
- **Generowanie dokumentacji** - opcja automatycznego generowania dokumentacji dla wygenerowanego kodu

## Rozwój interfejsu webowego

Interfejs webowy Evopy jest stale rozwijany. Planowane funkcjonalności:

- **Autentykacja użytkowników** - system logowania i zarządzania użytkownikami
- **Panel administracyjny** - zaawansowane opcje konfiguracji i zarządzania
- **Zaawansowana analityka** - statystyki i wykresy dotyczące użycia systemu
- **Integracja z zewnętrznymi repozytoriami** - możliwość importu kodu z GitHub, GitLab, itp.
- **Edytor kodu online** - możliwość edycji kodu bezpośrednio w interfejsie webowym
- **Interaktywne przykłady** - możliwość interaktywnego testowania wygenerowanego kodu
- **Współdzielenie kodu** - możliwość udostępniania wygenerowanego kodu innym użytkownikom
