# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 14:39:00

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| llama | ❓ | ❓ | ❓ | 0/3 |
| phi | ❓ | ❓ | ❓ | 0/3 |
| bielik | ✅ | ✅ | ✅ | 3/3 |
| deepsek | ✅ | ✅ | ✅ | 3/3 |

## Szczegółowe wyniki testów

### Model: llama

Brak wyników testów zapytań dla modelu llama.

### Model: phi

Brak wyników testów zapytań dla modelu phi.

### Model: bielik

#### Wyniki testów zapytań
```json
{
  "model_name": "bielik",
  "timestamp": "20250509_143623",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 15.82s)",
      "execution_time": 15.824142694473267,
      "code": "from datetime import datetime\n\ndef execute():\n    now = datetime.now()\n    print(f\"Current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}\")\n    return now.strftime('%Y-%m-%d %H:%M:%S')",
      "explanation": "So, let's break down this code step by step.\n\nThis code is written in Python, and it does a simple task: it prints the current date and time to the console. Here's what each part of the code does:\n\n1. `from datetime import datetime`: This line imports a module called `datetime` from a library called `datetime`. Think of modules like libraries or folders that contain useful functions and classes. In this case, we're importing just one specific class from the `datetime` module: `datetime`.\n2. `def execute():`: This defines a function called `execute()`. Functions are like reusable blocks of code that can be run multiple times with different inputs. When you call the `execute()` function, it will do what's inside this block.\n3. `now = datetime.now()`: Inside the `execute()` function, we create a variable called `now` and assign it the current date and time using the `datetime.now()` method. This gives us the current moment in time!\n4. `print(f\"Current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}\")`: We use an f-string (a new way of formatting strings in Python) to print a message that includes the current date and time. The `{now.strftime('%Y-%m-%d %H:%M:%S')}` part is where we insert the actual value of `now`. We format it as a string using the `%Y-%m-%d %H:%M:%S` format code, which gives us the year, month, day, hour, minute, and second.\n5. `return now.strftime('%Y-%m-%d %H:%M:%S')`: Finally, we return the formatted current date and time as a string. This means that if someone called this function from another part of their code, they would get the same output: the current date and time!\n\nSo, what problems does this code solve? Well, it's quite simple actually – it just prints the current date and time to the console. But think about it: how many times have you wanted to know what time it is or when a task needs to be done? This code makes it easy to get that information!\n\nAnd what's the purpose of this code? Well, it's mainly for demonstration purposes – to show off some basic Python concepts and how to work with dates and times. It could also be used in a real-world scenario where you need to display the current date and time, like in a system or application.\n\nNow, is this what you were expecting?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 5.53s)",
      "execution_time": 5.529914617538452,
      "code": "def execute():\n    return sum(range(1, 101))",
      "explanation": "I'd be happy to explain what this code does in simple terms!\n\nThis code is a function named `execute` that calculates the sum of all numbers from 1 to 100. That's right, it's a simple math problem!\n\nHere's how it works:\n\n1. The function uses the built-in `range` function to create a sequence of numbers from 1 to 100 (inclusive). This is like creating a list with the numbers 1, 2, 3, ..., 99, 100.\n2. The `sum` function takes this sequence of numbers and adds them all up to get a total sum.\n\nSo, when you run this code, it will return the value of the sum, which is... (drumroll please)... 5050!\n\nThe purpose of this code is likely to demonstrate how to use the `range` and `sum` functions in Python. It's not a particularly useful or complex calculation, but it shows how to create a simple function that does something.\n\nNow, I'd like to ask you: Is this what you were expecting?"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 8.18s)",
      "execution_time": 8.182230472564697,
      "code": "def execute(text):\n    vowels = ['a', 'e', 'i', 'o', 'u']\n    result = [char for char in text.lower() if char in vowels]\n    return result",
      "explanation": "A nice and simple code to explain!\n\nThis Python code defines a function called `execute` that takes one input, which is a string of text. The function's purpose is to find all the vowels (the letters \"a\", \"e\", \"i\", \"o\", and \"u\") in the given text and return them as a list.\n\nHere's what the code does step by step:\n\n1. It defines an empty list called `result`.\n2. It creates a list of vowel characters (`vowels`) containing the letters \"a\", \"e\", \"i\", \"o\", and \"u\".\n3. The function then iterates through each character in the input text, converts it to lowercase using the `lower()` method, and checks if that character is present in the `vowels` list.\n4. If a vowel is found, it's added to the `result` list.\n5. Finally, the function returns the `result` list, which now contains all the vowels from the original text.\n\nIn simple terms, this code helps you find and extract all the vowels (the letters \"a\", \"e\", \"i\", \"o\", and \"u\") from a given piece of text.\n\nWhat problems does it solve? It solves the problem of extracting specific characters (in this case, vowels) from a larger text. This can be useful in various applications, such as data processing, natural language processing, or even just for fun!\n\nSo, what do you think? Is this explanation helpful and clear?"
    }
  ]
}```

### Model: deepsek

#### Wyniki testów zapytań
```json
{
  "model_name": "deepsek",
  "timestamp": "20250509_143818",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 4.61s)",
      "execution_time": 4.614249229431152,
      "code": "import datetime  # importowanie biblioteki do obsługi dat ygora.\ndef execute():    # definicja funkcji zwracajacej aktualna data i godzinę.\n   now = datetime.datetime.now()     # obecna data, czas oraz wypelnienie ewentualnych danymi np: miesiąca lub roku rano/poza nocą. \n    print(\"Aktualna daty i godzin jest to\", now)   # Wyswietlenie aktualnej date, czasu oraz wypelnieniem ewentualnych danymi np: miesiaca lub roku rano/poza nocą. \nexecute()     # Wywołanie funkcji execute",
      "explanation": "Ten kod Python importuje moduł datetime, co można pisać `import datetime` i zaczyna się wydrukować aktualnych daty oraz czasów. Następnie deklarujemy funkcję 'execute' do wypisywania danych na ekranie i zwraca też obecną date, godzinę lub datę tygodnia najbardziej potrzebnym. \nNa koniec uruchamiamy funkcję 'execute', co pozwala wydrukować aktualną date, godzinę oraz datę tygodnia najbardziej potrzebnym do użytkownika."
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 3.82s)",
      "execution_time": 3.8178553581237793,
      "code": "def execute():   # Nazwa funkcji 'execute' i powinna być taka sama jak nazewnictwo modułu w którym znajduje się nasza funkcja.  (Przypomnienie: def execute(): in module_name)\n    return sum(range(1, 101))   # Zwraca środki cumulative od n to m przy podejsciu 'sum' jest bezużytkowany i tak dlugo służy do zliczenia liczb.",
      "explanation": "Dokładnie, co robi ten kod Python w języku naturalnym? \nTen plik definiowany ma nazwę 'execute' i powinien być taka sama jak nazewnictwo modułu do którego został on zaimportowany. Oznacza to, że ta funkcja można wywołać poprzez importując ten plik wewnętrznie i nazwijem 'execute' do odpowiednich zmiennych lub obiektów.\n  \nTen kod pokazuje, jak działają liczby od 1 do 100 (wszytkie numery w tym przedziale są inicjalizowane). Jednym z głównych użytkowników, którym ten program jest potrzebny, będzie mianopatykcyja na dodawaniu liczby całkiem naturalnej od 1 do n. W takim wypadku zwraca sumaryczną tej liczbie (czyli łacznych, czasu obliczeniowego i dlatego jest bezużytkowany).\n  \nJeden problem to właściwy cel ten program. Jak znajduje się on wewnętrznie? Dla osób nie dokonywanej obliczeń, które mogą być potrzebnymi w dowolnej aplikacji i bardzo częste są problemy związane z bezużytkowaniem liczb (czas obliczeniowych), co jest mianopatykcyja do rozwiązywania ten problę."
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 5.32s)",
      "execution_time": 5.319284200668335,
      "code": "def execute():\n    # Kod wygenerowany na podstawie opisu użytkownika\n    def find_consonants(text):\n        vowels = 'aeiouAEIOU'\n        \n        consonantList=[]   #tworzymy pustą listę do będą ściśle zapamiętanej samogłosek \n          \n        for char in text:         #wczytywanie każdego znaku w tekscie  \n            if(char.isalpha()):    \n                ch = char             #zamieniamy na małe litery aby sprawdzić czy jest on samoglosskiem lub nie \n                                         #jesli znak to duża literka a w kodzie Python string są interpretowane tylko raz, więc używamy .lower()  \n                if ch not in vowels:     consonantList.append(ch)    #dopisujemy do listy samogłosek  gdy jest to duża litera i nie jest to słowo przeciwne (tj w tym miejscu musimy się usunąć)\n        return consonantList   # zwracamy listę samoglosek \n        \n    print(find_consonants('Python is a wonderful language'))\n    \n    # Zwróć wynik jeśli funkcja nic nie zwraca\n    return \"Wykonano zadanie\"\n",
      "explanation": "Ten kod Python przechowuje tekst na jednej stronie i generuje listę samogłosek (wypełniać słów, w tym miejscu nigdy się nie powtarza). Następnie przechodzi do druga części zadania:\n- Wczytuje tekst (na stronie) –'Python is a wonderful language'. Dla każdego słowa w tym ciężko Ci to się dzieje, co jest równoległe do licencyjnego pisania i rozwiązywania zadnych problemów.\n- Generuje listę samoglosek: Tworzone są pustej tablicy (`consonantList = []`) dla każdego wystąpienia literki, aby przejrzysto zapamiętać te same.\n- Dopasowuje samoglosek: Sprawdza czy jest on duża litera (nigdy nie się powtarza), a także sprawda, czy słowo to wyraz przeciwne lub po prostu miałoby innego sensu.\n- Zwraca listę samoglosek: Po zakończeniu pętli nastawionym na tekst sprawdzane słowo jest dodany do `consonantList` i ten stan powinien być wylistowany.\n- Zwraca wiadomość: W takim razie zamknięto nasze polecenie, gdy funkcja nigdy nie uruchomiła dodatkowego rzutu obliczeniowego."
    }
  ]
}```

