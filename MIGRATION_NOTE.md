# Migracja projektu Evopy do Devopy

Projekt Evopy został zmigrowany do nowego projektu Devopy, który jest dostępny pod adresem:
`/home/tom/github/tom-sapletta-com/devopy`

## Co zostało przeniesione?

- Wszystkie pliki z katalogu `devopy/`
- Dokumentacja związana z projektem devopy
- Skrypty pomocnicze do uruchamiania API i CLI

## Jak korzystać z nowego projektu?

```bash
# 1. Przejdź do katalogu projektu
cd /home/tom/github/tom-sapletta-com/devopy

# 2. Uruchom API
./scripts/run_api.sh

# 3. Uruchom CLI z wybranym zadaniem
./scripts/run_cli.sh "pobierz dane z api i zapisz do excela"
```

## Struktura nowego projektu

```
devopy/
├── devopy/           # Kod źródłowy pakietu
├── docs/             # Dokumentacja
├── examples/         # Przykłady użycia
├── scripts/          # Skrypty pomocnicze
├── tests/            # Testy
├── .venv/            # Środowisko wirtualne
├── pyproject.toml    # Konfiguracja budowania pakietu
├── README.md         # Główny plik README
├── requirements.txt  # Zależności projektu
└── setup.py          # Konfiguracja instalacji
```

Data migracji: Sat May 10 03:14:16 PM CEST 2025
