# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 10:25:54

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| deepseek-coder | ✅ | ❓ | ❌ | 1/3 |
| deepsek | ✅ | ❓ | ❌ | 1/3 |
| llama | ✅ | ❌ | ❌ | 1/3 |

## Szczegółowe wyniki testów

### Model: deepseek-coder

#### Wyniki testów zapytań
- Zaliczone testy: 2/3
- Szczegóły testów:
  - ✅ Proste zapytanie tekstowe: Kod zawiera wszystkie oczekiwane elementy
  - ✅ Zapytanie matematyczne: Kod zawiera wszystkie oczekiwane elementy
  - ❌ Zapytanie z przetwarzaniem tekstu: Brakujące elementy w kodzie: re.findall

#### Wyniki testów poprawności
- Zaliczone testy: 0/0

#### Wyniki testów wydajności
- Brak wyników testów wydajności

### Model: deepsek

#### Wyniki testów zapytań
- Zaliczone testy: 3/3

#### Wyniki testów poprawności
- Zaliczone testy: 0/0

#### Wyniki testów wydajności
- Brak wyników testów wydajności

### Model: llama

#### Wyniki testów zapytań
- Zaliczone testy: 3/3

#### Wyniki testów poprawności
- Zaliczone testy: 0/6

#### Wyniki testów wydajności
- Brak wyników testów wydajności


## Wnioski

Na podstawie przeprowadzonych testów można wyciągnąć następujące wnioski:

1. **Najlepszy model pod względem poprawności**: Model z najwyższym wynikiem w testach poprawności
2. **Najszybszy model**: Model z najniższym średnim czasem wykonania
3. **Najlepszy model ogólnie**: Model z najwyższym całkowitym wynikiem

## Metodologia testów

Testy zostały przeprowadzone w trzech kategoriach:

1. **Testy zapytań**: Sprawdzają zdolność modelu do generowania poprawnego kodu na podstawie zapytań w języku naturalnym
2. **Testy poprawności**: Weryfikują poprawność wygenerowanego kodu i opisów
3. **Testy wydajności**: Mierzą czas wykonania różnych operacji przez model

## Zalecenia

Na podstawie wyników testów zaleca się:

1. Używanie modelu z najwyższym całkowitym wynikiem do większości zastosowań
2. W przypadku zadań wymagających wysokiej wydajności, rozważenie użycia najszybszego modelu
3. Dla zadań wymagających wysokiej dokładności, wybór modelu z najlepszymi wynikami w testach poprawności
