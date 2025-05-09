# Uproszczony raport porównawczy modeli LLM

Data: 2025-05-09 14:53:48

## Podsumowanie wyników testów

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| llama3 | ❌ | ✅ | ✅ | 2/3 |
| gpt-4 | ✅ | ✅ | ✅ | 3/3 |
| claude | ❌ | ✅ | ✅ | 2/3 |
| gemini | ❌ | ✅ | ✅ | 2/3 |
| deepsek | ❌ | ✅ | ✅ | 2/3 |

## Szczegółowe wyniki testów

### Model: llama3

Brak wyników testów zapytań dla modelu llama3.

### Model: gpt-4

#### Wyniki testów zapytań
```json
{
  "model_name": "gpt-4",
  "timestamp": "20250509_145317",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 2.38s)",
      "execution_time": 2.3793511390686035,
      "code": "import datetime  # Do obsługi daty i godziny.\ndef execute():    # Rozpoczynamym definicję funkcji.\n   now = datetime.datetime.now()     # Pobieramy aktualną datę i czas. \n   print('Aktualna data i godzina:', now)    # Wyświetlam dane na ekranie.\nexecute()      # uruchamiamy naszą funkcję zdefiniowaną powyżej",
      "explanation": "Oto wprowadzenie do odpowiedzi. Obejrzeć daleko, jakim kod python nazywa się? Czego potrafi on zrobić i na co podał/aby byś gorąco pragnęto rozwiązywanie ten problem. Pamiętaj o obsahu, dlatego najpierw jakim kodem potrzebuje wyjaśnienia i oceny celów oraz możliwech błędach?",
      "code_lines": 5,
      "quality_metrics": {
        "documentation_quality": 20.0,
        "code_readability": 99.5,
        "explanation_clarity": 38.5,
        "maintainability_index": 35.858431313488495,
        "overall_quality_score": 54.696686262697696
      },
      "efficiency_metrics": {
        "time_complexity": "O(1)",
        "time_complexity_score": 100.0,
        "space_complexity": "O(1)",
        "space_complexity_score": 100.0,
        "code_size_efficiency": 76.0,
        "overall_efficiency_score": 92.0
      }
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 4.49s)",
      "execution_time": 4.48622727394104,
      "code": "def execute():\n    return sum(range(1, 101))\nprint('Suma liczb od 1 do 100 wynosi',execute())",
      "explanation": "Ten kod Python oblicza sumę liczb od `1` do `100 (range(1, 101))`. Zwraca ona taktywno wynik pochodzenia z metody nazwanej 'sum' i przesyłaniu obliczonego sumarycznego liczby do ekranu (print).\n  \nWprowadza czerwony, mniejszy komunikat: `Suma liczb od 1 do 100 wynosi`. Zamiast używać rozszerzonego przedstawiania sumarycznego (np., \"sum of numbers from 1 to N is\") czyli tylko umieszcza liczebno na ekranie wynik pochodzenia z metody nazwanej 'execute'.\n  \nWyjaśnieniem dobrego kodu jest fakt, że ona to czyta się od tył i szczególnie przechowujemi. W ten sposob nazywamy \"DRY - Don't Repeat Yourself\". Powtarzać kod wielokrotnie pojedynczo zamiast rozwiń problem jest cenny dobrym podejściem, dlatego musimy uważnić swój temat.\n  \nW ten sposób nie wydarzeła się kolejna pyta: \"Czy to jest mniejsz problem? Czy moja metoda sumujących liczby od 1 do N zwraca tylko ostatni rezultat, czy powinien dalej obliczać i zwrócić wyniki poszczególnych cyfr?\", ale kod podany jest głęboko uważniony na problemach poprawy.\n  \nJeśli to nie zaobserwowano, co chcesz zrobić oraz odpowiadajemu opcji (wyjawnieniu lub eksperymencie), moglibec wskazywać? Zamiast tych jednoinformacyjnyczrych komunikatów na stronach internetowych, przykazaliśmy kilka rzeczy.\n  \nCelem tego zadania było upewnienie Cię, że wszystko działało dobrze i moją metoda rozwiązać problemy jest bardzo uporządkowana.",
      "code_lines": 3,
      "quality_metrics": {
        "documentation_quality": 0.0,
        "code_readability": 93.95833333333333,
        "explanation_clarity": 54.17857142857143,
        "maintainability_index": 16.854149003311683,
        "overall_quality_score": 62.78928100405772
      },
      "efficiency_metrics": {
        "time_complexity": "O(1)",
        "time_complexity_score": 100.0,
        "space_complexity": "O(1)",
        "space_complexity_score": 100.0,
        "code_size_efficiency": 80.0,
        "overall_efficiency_score": 93.33333333333333
      }
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 25.20s)",
      "execution_time": 25.20356321334839,
      "code": "def execute():\n    text = 'Python is fun!' # podstawne dane wejsciowe, mozna by zmienic na inne teksty lub pozytywnie jesli potrzebny. \n    \n    vowels_in_text = 0   # licznik samoglosek w pliku wejsciowym (np 'Python is fun') to zera, najpierw musimy dodac logike do tego\n                         \n      for i in text: \t\t\t# iterujemy po kazdym znaku na teksie\n          if(i =='a' or i== 'e'or i== 'i' or i ==  'o'   or i == 'u') :    # jesli obecny znak to samogloska, \n                                                         \t\t\t\t\t\t# to_string++ na tyle. (zmienna ++ w Python nie istnieje)               \t              \t\t       \t \t     \t   \t       \t\t\t\t     \t\t\t          .compareAndSwap(...)  |  for-each it : i in objects | lambda.. |  ...      \n                                                         \t\t\t\t\t\t# to_string++ na tyle.  (zmienna ++ w Python nie istnieje)               \t              \t\t       \t \t   \t       \t\t\t\t     \t\t\t          .compareAndSwap(...)  |  for-each it : i in objects | lambda.. |  ...      \n                  vowels_in_text += 1     # jeśli obecny znak to samogloska,  tj ++ liczniku. (+= w Python nie istnieje)  \t              \t\t       \t \t   \t       \t\t\t\t     \t\t\t          .compareAndSwap(...)  | for-each it : i in objects | lambda.. |  ...      \n              if vowels_in_text == 0:    # jeśli licznik jest równy 0, to wypisze \"Brak samoglosek\" (można zmienić na inną wiadomość lub dodatki)\n                  print(\"Nie ma żadnych samoglosek\")    # najpierw musimy uruchomic logike do tego. (print w Python nie istnieje, mozna zamiast ją użyc 'return')\n          return vowels_in_text \t\t\t# przyjrzyjemu podstawne dane wejsciowe to zero samoglosek. Moze być równa liczba sylwetki w teksie lub po prostu użyc zmienna 'vowels_in_text'\n                  \t\t\t\t\t# do przyrótnej funkcji tak jako to, co chcesz odebrać.  Najpierw musimy uruchomic logike i dodac wynik konwersji na zmienna 'vowels_in_text'\n                  \t\t\t\t\t# lub sprawdzic czy takie polecenie jest obecne, a następnie odpalić go.  (np: return vowels)  \t              \t\t       \t \t   \t       \t\t\t\t     \t\t\t          .compareAndSwap(...)  | for-each it : i in objects | lambda.. |  ...",
      "explanation": "Nie udało się wygenerować wyjaśnienia kodu.",
      "code_lines": 15,
      "quality_metrics": {
        "documentation_quality": 22.66666666666667,
        "code_readability": 44.230769230769226,
        "explanation_clarity": 18.9,
        "maintainability_index": 52.308079625679405,
        "overall_quality_score": 35.38905182257178
      },
      "efficiency_metrics": {
        "time_complexity": "Unknown",
        "time_complexity_score": 50.0,
        "space_complexity": "Unknown",
        "space_complexity_score": 50.0,
        "code_size_efficiency": 50.0,
        "overall_efficiency_score": 50.0
      }
    }
  ]
}```

### Model: claude

Brak wyników testów zapytań dla modelu claude.

### Model: gemini

Brak wyników testów zapytań dla modelu gemini.

### Model: deepsek

Brak wyników testów zapytań dla modelu deepsek.

