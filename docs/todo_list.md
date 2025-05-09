# Lista zadań do wykonania w celu poprawy struktury projektu Evopy

## Priorytety zadań

Poniższe zadania zostały podzielone na kategorie według priorytetu i obszaru działania. Zadania o wysokim priorytecie powinny zostać wykonane w pierwszej kolejności, ponieważ mają największy wpływ na funkcjonalność i stabilność systemu.

## 1. Wysoki priorytet

### 1.1. Migracja do nowej architektury

- [ ] **Dokończyć migrację modułu text2python do nowej architektury**
  - Dostosować klasę Text2Python do dziedziczenia po BaseText2XModule
  - Zaimplementować wszystkie wymagane metody abstrakcyjne
  - Zachować kompatybilność wsteczną z istniejącym kodem

- [ ] **Ujednolicić interfejs dla wszystkich modułów konwersji**
  - Zapewnić spójny interfejs dla wszystkich modułów (text2python, text2sql, shell2text, itp.)
  - Zdefiniować wspólne metody i struktury danych dla wszystkich modułów

- [ ] **Zintegrować ConfigManager z wszystkimi modułami**
  - Przenieść konfigurację z poszczególnych modułów do centralnego ConfigManager
  - Zapewnić mechanizm ładowania konfiguracji specyficznych dla modułów

### 1.2. Ulepszenie wykrywania i obsługi zmiennych

- [ ] **Rozszerzyć mechanizm wykrywania zmiennych w QueryAnalyzer**
  - Dodać obsługę bardziej złożonych wyrażeń matematycznych
  - Poprawić wykrywanie zmiennych w różnych kontekstach językowych (nie tylko polski)
  - Dodać obsługę zmiennych dla innych typów zapytań (nie tylko geometrycznych)

- [ ] **Usprawnić generowanie kodu z parametrami wejściowymi**
  - Zapewnić, że wszystkie wykryte zmienne są przekazywane jako parametry funkcji execute
  - Dodać odpowiednią dokumentację dla parametrów funkcji
  - Zapewnić obsługę wartości domyślnych dla parametrów

### 1.3. Poprawa bezpieczeństwa i stabilności

- [ ] **Wzmocnić system piaskownicy Docker**
  - Dodać limity zasobów dla kontenerów Docker
  - Zapewnić izolację kontenerów od systemu hosta
  - Dodać mechanizm czyszczenia nieużywanych kontenerów

- [ ] **Rozszerzyć system autonaprawy zależności**
  - Dodać obsługę bardziej złożonych zależności
  - Zaimplementować mechanizm wykrywania cyklicznych zależności
  - Dodać obsługę zależności dla bibliotek zewnętrznych

## 2. Średni priorytet

### 2.1. Rozszerzenie funkcjonalności

- [ ] **Rozbudować system rozszerzeń**
  - Dodać więcej rozszerzeń dla różnych dziedzin (statystyka, analiza danych, itp.)
  - Usprawnić mechanizm ładowania i identyfikacji rozszerzeń
  - Dodać dokumentację dla tworzenia nowych rozszerzeń

- [ ] **Zaimplementować ErrorCorrector**
  - Stworzyć system automatycznego korygowania błędów w wygenerowanym kodzie
  - Zintegrować ErrorCorrector z modułem text2python
  - Dodać mechanizm uczenia się na podstawie popełnionych błędów

- [ ] **Rozszerzyć interfejs webowy**
  - Dodać bardziej zaawansowane funkcje zarządzania kontenerami Docker
  - Poprawić interfejs użytkownika
  - Dodać możliwość zapisywania i ładowania historii zapytań

### 2.2. Poprawa jakości kodu

- [ ] **Refaktoryzacja istniejącego kodu**
  - Poprawić strukturę kodu zgodnie z zasadami SOLID
  - Usunąć zduplikowany kod
  - Poprawić nazewnictwo zmiennych i funkcji

- [ ] **Dodać testy jednostkowe i integracyjne**
  - Zwiększyć pokrycie kodu testami
  - Dodać testy dla kluczowych komponentów
  - Zaimplementować ciągłą integrację (CI)

## 3. Niski priorytet

### 3.1. Dokumentacja i wsparcie

- [ ] **Rozszerzyć dokumentację**
  - Dodać dokumentację API dla wszystkich modułów
  - Stworzyć przewodnik dla użytkowników
  - Dodać przykłady użycia dla różnych scenariuszy

- [ ] **Poprawić wsparcie cross-platform**
  - Przetestować i poprawić działanie na różnych systemach operacyjnych
  - Dodać szczegółowe instrukcje instalacji dla różnych platform
  - Zaimplementować automatyczną detekcję i konfigurację dla różnych środowisk

### 3.2. Optymalizacja i wydajność

- [ ] **Zoptymalizować wydajność generowania kodu**
  - Poprawić czas odpowiedzi modelu językowego
  - Zaimplementować mechanizm buforowania dla często używanych zapytań
  - Zoptymalizować wykorzystanie zasobów

- [ ] **Poprawić zarządzanie pamięcią**
  - Zoptymalizować wykorzystanie pamięci w kontenerach Docker
  - Poprawić zarządzanie zasobami dla długotrwałych operacji
  - Zaimplementować mechanizm ograniczania zużycia zasobów

## 4. Zadania długoterminowe

### 4.1. Rozwój i skalowalność

- [ ] **Przygotować system do obsługi większej liczby użytkowników**
  - Zaimplementować mechanizm kolejkowania zapytań
  - Dodać obsługę równoległego przetwarzania
  - Przygotować architekturę do skalowania poziomego

- [ ] **Rozszerzyć wsparcie dla innych języków programowania**
  - Dodać moduły dla innych języków (JavaScript, Java, C++, itp.)
  - Zapewnić spójny interfejs dla wszystkich języków
  - Zaimplementować mechanizm wykrywania najlepszego języka dla danego zapytania

### 4.2. Integracja z innymi systemami

- [ ] **Dodać integrację z popularnymi IDE**
  - Stworzyć wtyczki dla VSCode, PyCharm, itp.
  - Zapewnić płynną integrację z istniejącymi narzędziami deweloperskimi
  - Dodać funkcje podpowiedzi i uzupełniania kodu

- [ ] **Zaimplementować API dla integracji z zewnętrznymi systemami**
  - Stworzyć RESTful API dla wszystkich funkcji systemu
  - Dodać dokumentację API
  - Zapewnić mechanizmy autoryzacji i uwierzytelniania

## Uwagi końcowe

Powyższa lista zadań stanowi kompleksowy plan rozwoju projektu Evopy. Realizacja tych zadań powinna być przeprowadzana iteracyjnie, z regularnym testowaniem i weryfikacją wyników. Priorytetyzacja może ulec zmianie w zależności od bieżących potrzeb i odkrytych problemów.

Zalecane jest również regularne przeglądanie i aktualizowanie tej listy, aby odzwierciedlała aktualny stan projektu i nowe wymagania.
