# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 10:21:39

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| deepseek-coder | ✅ | ❓ | ❓ | 1/3 |

## Szczegółowe wyniki testów

### Model: deepseek-coder

#### Wyniki testów zapytań
```json
{
        "timestamp": "20250509_102139",
        "model_id": "deepseek-coder",
        "passed_tests": 2,
        "failed_tests": 1,
        "total_tests": 3,
        "test_results": [
            {
                "name": "Proste zapytanie tekstowe",
                "status": "PASSED",
                "reason": "Kod zawiera wszystkie oczekiwane elementy"
            },
            {
                "name": "Zapytanie matematyczne",
                "status": "PASSED",
                "reason": "Kod zawiera wszystkie oczekiwane elementy"
            },
            {
                "name": "Zapytanie z przetwarzaniem tekstu",
                "status": "FAILED",
                "reason": "Brakujące elementy w kodzie: re.findall"
            }
        ]
    }
```

## Wnioski

Ten raport zawiera przykładowe wyniki dla modelu deepseek-coder. Aby wygenerować pełny raport porównawczy, uruchom skrypt `report.sh` i wybierz modele do przetestowania.

