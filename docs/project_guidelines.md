---
layout: default
title: Wytyczne Projektu
---

# Wytyczne projektu evopy

## Główne założenia projektu

1. **Konwersja tekst-na-kod**: Każde zdanie/życzenie użytkownika jest konwertowane na funkcję w Pythonie
2. **Izolowane środowisko**: Kod jest uruchamiany w izolowanym środowisku Docker (sandbox)
3. **Informacja zwrotna**: Użytkownik jest informowany o statusie wykonania kodu (sukces/błąd)
4. **Wyjaśnienie kodu**: System generuje wyjaśnienie kodu w języku naturalnym (python2text)
5. **Weryfikacja oczekiwań**: System pyta użytkownika czy wynik spełnia jego oczekiwania
6. **Lokalne środowisko**: System działa lokalnie, bez zależności od zewnętrznych usług
7. **Ewolucyjny rozwój**: System rozwija się wraz z interakcjami z użytkownikiem
8. **Zarządzanie projektami**: Tworzenie i zarządzanie projektami w kontenerach Docker
9. **Automatyczna konfiguracja**: Sprawdzanie i instalacja wymaganych zależności
10. **Wykrywanie kodu**: Automatyczne wykrywanie i obsługa kodu generowanego przez model
11. **Bezpieczeństwo**: Wykonywanie kodu w izolowanym środowisku z ograniczeniami zasobów
12. **Przechowywanie historii**: Zapisywanie historii konwersacji i wykonanych kodów
13. **Modułowa architektura**: System zbudowany z niezależnych modułów, które można rozwijać
14. **Minimalistyczne podejście**: Startuje jako prosty skrypt, który ewoluuje w złożony system
15. **Samowystarczalność**: System sam instaluje potrzebne zależności
16. **Samodoskonalenie**: System identyfikuje obszary, w których ma trudności i aktywnie się w nich rozwija
17. **Zaawansowana analiza zapytań**: System analizuje zapytania użytkownika i dostosowuje odpowiedzi
18. **Wsparcie dla wielu platform**: System działa na różnych systemach operacyjnych (Linux, macOS, Windows)
19. **Programowanie deklaratywne**: System wspiera generowanie kodu deklaratywnego, który przekształca w imperatywny
20. **Adaptacja do ograniczonych zasobów**: System dostosowuje swoje działanie do dostępnych zasobów sprzętowych

## Specyfika projektu

1. **Architektura ewolucyjna**: System rozwija się od prostego skryptu do złożonego środowiska
2. **Podejście sandbox-first**: Każdy kod jest uruchamiany w izolowanym środowisku
3. **Konwersja język naturalny -> kod**: Automatyczna konwersja żądań użytkownika na kod Python
4. **Wyjaśnianie kodu**: Automatyczne generowanie wyjaśnień kodu w języku naturalnym
5. **Weryfikacja użytkownika**: System pyta użytkownika o potwierdzenie przed wykonaniem kodu
6. **Zarządzanie piaskownicami**: System tworzy i zarządza wieloma piaskownicami Docker
7. **Lokalny model językowy**: Wykorzystanie modelu DeepSeek poprzez Ollama lokalnie
8. **Przechowywanie kontekstu**: Zapamiętywanie kontekstu konwersacji i projektów
9. **Zarządzanie zależnościami**: Automatyczna instalacja i konfiguracja zależności
10. **Obsługa błędów**: Informowanie użytkownika o błędach w kodzie i propozycje naprawy
11. **Podejście konwersacyjne**: Interakcja z systemem w formie konwersacji
12. **Wielowątkowość**: Obsługa wielu wątków konwersacji i projektów jednocześnie
13. **Automatyzacja zadań**: Automatyczne wykonywanie powtarzalnych zadań
14. **Rozszerzalność**: Możliwość dodawania nowych funkcji i modułów
15. **Niezależność od chmury**: Działanie bez konieczności połączenia z usługami chmurowymi
16. **Inteligentna analiza zapytań**: Zaawansowana analiza zapytań użytkownika z identyfikacją intencji
17. **Mechanizm samodoskonalenia**: Śledzenie obszarów trudności i aktywne rozwijanie umiejętności
18. **Kompatybilność międzyplatformowa**: Działanie na różnych systemach operacyjnych
19. **Generowanie kodu deklaratywnego**: Tworzenie kodu w stylu deklaratywnym i przekształcanie go w imperatywny
20. **Adaptacja do zasobów**: Dostosowanie działania do dostępnych zasobów sprzętowych

## Struktura systemu

1. **Moduł text2python**: Konwersja tekstu na kod Python
2. **Moduł docker_sandbox**: Bezpieczne uruchamianie kodu w kontenerach Docker
3. **Moduł zarządzania konwersacjami**: Przechowywanie i zarządzanie historią konwersacji
4. **Moduł zarządzania projektami**: Tworzenie i zarządzanie projektami Docker
5. **Moduł integracji z modelem językowym**: Komunikacja z modelem DeepSeek przez Ollama
6. **Moduł konfiguracji**: Zarządzanie konfiguracją systemu
7. **Moduł instalacji**: Instalacja i konfiguracja zależności
8. **Moduł diagnostyczny**: Monitorowanie i debugowanie systemu
9. **Moduł interfejsu użytkownika**: Interakcja z użytkownikiem przez konsolę
10. **Moduł zarządzania piaskownicami**: Tworzenie i zarządzanie piaskownicami Docker
11. **Moduł samodoskonalenia**: Śledzenie obszarów trudności i rozwijanie umiejętności
12. **Moduł analizy zapytań**: Zaawansowana analiza i interpretacja zapytań użytkownika
13. **Moduł międzyplatformowy**: Zapewnienie kompatybilności z różnymi systemami operacyjnymi
14. **Moduł generowania kodu deklaratywnego**: Tworzenie kodu deklaratywnego i przekształcanie go w imperatywny
15. **Moduł adaptacji zasobów**: Dostosowanie działania do dostępnych zasobów sprzętowych

## Planowane rozszerzenia

1. **Private Sandbox**: Izolowane środowisko dla wewnętrznych usług systemu
2. **Public Sandbox**: Środowisko dla projektów zleconych przez użytkownika
3. **Biblioteka gotowych usług**: Zbiór gotowych usług do wykorzystania przez system
4. **API dla usług**: Interfejs do komunikacji z usługami w piaskownicach
5. **System zarządzania zasobami**: Kontrola zasobów przydzielanych piaskownicom
6. **System monitorowania**: Monitorowanie stanu piaskownic i usług
7. **System logowania**: Rejestrowanie działań systemu i piaskownic
8. **System zarządzania wersjami**: Kontrola wersji kodu i usług
9. **System zarządzania zależnościami**: Zarządzanie zależnościami dla usług
10. **System zarządzania dostępem**: Kontrola dostępu do usług i piaskownic
11. **Mechanizm aktywnego uczenia**: System aktywnie poszukuje zasobów edukacyjnych w obszarach, w których ma trudności
12. **Raportowanie postępów samodoskonalenia**: Generowanie raportów pokazujących postępy w rozwijaniu umiejętności
13. **Integracja z zewnętrznymi źródłami wiedzy**: Połączenie z repozytoriami kodu, dokumentacją i forami
14. **Generowanie kodu w wielu językach**: Rozszerzenie konwersji tekst-na-kod na inne języki programowania
15. **Interfejs webowy**: Graficzny interfejs użytkownika dostępny przez przeglądarkę
16. **Adaptacyjne generowanie kodu**: Dostosowanie generowanego kodu do preferencji użytkownika
17. **Automatyczna optymalizacja kodu**: Wykrywanie i optymalizacja wąskich gardeł w generowanym kodzie
18. **Mechanizm wyjaśniania decyzji**: Wyjaśnianie dlaczego system wygenerował dany kod w określony sposób
19. **System rekomendacji zasobów**: Sugerowanie zasobów edukacyjnych dla użytkownika
20. **Integracja z IDE**: Wtyczki do popularnych środowisk programistycznych
