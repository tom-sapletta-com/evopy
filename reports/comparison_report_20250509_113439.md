# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 11:34:39

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| llama | ✅ | ✅ | ✅ | 3/3 |
| phi | ❌ | ✅ | ✅ | 2/3 |
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
  "timestamp": "20250509_113126",
  "model_id": "bielik",
  "model_name": "llama3",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Wyświetl aktualną datę i godzinę",
      "code": "def execute():\n    # Kod wygenerowany na podstawie opisu użytkownika\n    execute = lambda: print(datetime.now())\n    \n    # Zwróć wynik jeśli funkcja nic nie zwraca\n    return \"Wykonano zadanie\"\n",
      "explanation": "I'd be happy to explain what this code does.\n\nThis code defines a function called `execute`. When you call the `execute` function, it executes another piece of code that prints the current date and time using the `datetime.now()` function. This is because the `lambda` expression inside the `execute` function creates an anonymous function (or a \"function within a function\") that takes no arguments and simply prints the current date and time.\n\nIn other words, when you run the `execute` function, it will print something like this: `2023-02-20 14:30:00.123456` (depending on the actual time).\n\nThe code also includes a return statement, which returns the string `\"Wykonano zadanie\"` if no value is returned by the `execute` function.\n\nSo, what problem does this code solve? It seems to be a simple example of how to create and use an anonymous function in Python. The code doesn't really \"solve\" any specific problem, but it demonstrates how to define and execute a small piece of code that performs a specific task.\n\nWhat's the purpose of this code? Well, it could be used as a basic building block for more complex programs or scripts. For example, you might use this code in a larger program to print the current date and time at certain intervals or to record when specific events occur.\n\nSo, did I help you understand what this code does?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Oblicz sumę liczb od 1 do 100",
      "code": "def execute():\n    return sum(range(1, 101))",
      "explanation": "Let's break down what this code does in simple terms!\n\nThe code defines a function called `execute`. A function is like a recipe that takes some inputs and produces an output. In this case, the `execute` function returns a value.\n\nHere's what happens when you call the `execute` function:\n\n1. The `range(1, 101)` part creates a sequence of numbers from 1 to 100 (inclusive). Think of it like a list with numbers from 1 to 100.\n2. The `sum` function takes this sequence of numbers and adds them all together. This is like calculating the total sum of all those numbers.\n3. The `return` statement says that the value calculated in step 2 should be returned as the output of the `execute` function.\n\nSo, when you call the `execute` function, it will calculate the sum of all numbers from 1 to 100 and return that value. For example, if you run this code, the output would be 5050 (which is the sum of all numbers from 1 to 100).\n\nIn simple terms, this code calculates the total sum of numbers from 1 to 100 and returns it as the result.\n\nNow, are you satisfied with this explanation?"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
      "code": "```\ndef execute(text):\n    vowels = ['a', 'e', 'i', 'o', 'u']\n    result = [char for char in text.lower() if char in vowels]\n    return ''.join(result)",
      "explanation": "I'd be happy to help!\n\nThe code you provided is a Python function called `execute` that takes a string (`text`) as an input. Its purpose is to extract all the vowels (A, E, I, O, U) from the given text and return them in lowercase.\n\nHere's what the code does step by step:\n\n1. It defines a list of vowels (`vowels = ['a', 'e', 'i', 'o', 'u']`).\n2. It converts the input `text` to lowercase using the `lower()` method.\n3. It uses a list comprehension (`[char for char in text.lower() if char in vowels]`) to iterate through each character of the modified text.\n4. For each character, it checks if the character is present in the `vowels` list using the `in` operator.\n5. If the character is a vowel, it adds it to a new list (`result`) containing only the vowels.\n6. Finally, it uses the `join()` method to concatenate all the vowels in the `result` list into a single string.\n\nThe purpose of this code is to extract and return the vowels from an input text. This could be useful in various applications, such as:\n\n* Text processing: For example, you might want to count the frequency of vowels in a text or create a vowel-consonant balanced text.\n* Natural Language Processing (NLP): You can use this code as a building block for more complex NLP tasks, like text classification or sentiment analysis.\n\nNow, I'd love to ask: Is this what you were expecting?"
    }
  ]
}```

### Model: deepsek

#### Wyniki testów zapytań
```json
{
  "timestamp": "20250509_113331",
  "model_id": "deepsek",
  "model_name": "deepseek-coder",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Wyświetl aktualną datę i godzinę",
      "code": "import datetime  # import the required module\n  \ndef execute():    \n    now = datetime.datetime.now()       # get current date and time from python's in-build library to display it on console using print function, use 'date', '\\n'' if you want a new line after displaying  for next operation or as required by the problem statement itself we are not doing any operations here\n    return now  \n    \nprint(execute()) # calling execute() method and printing result to see it on console. If no exception occurs, then this will print current date & time in a readable format else error message along with traceback info is printed out by python's runtime environment which usually indicates where the bug happened/how your code was supposed be executed etc...",
      "explanation": "Kod Python, właściwy podczas nazywania się \"w języku naturalnym\", używa modułów do obliczania dat i godzin. Zamiast pisac konkretne instrukcje, pojawiło się sześć czerwonych napisów z eksperta pracy w programowaniu oraz dodatkiem ostrzeganszych informacji na temat rzeczywiści.\n \nNasza grana polega na zaimportujeniu modułu `datetime`, który po prostu wybiera aktualną datę i czas oraz jednego z najczęstszych sposobów przedstawia go na ekranie za pomocą funkcji `print`.\n \nTen moduł po prostu wybiera bieżący czas, który jest uważany za moment uruchomić teraz (np., \"now\") i zwraca go do ekranu lub potwierdzenia dodatku.\n \nFunkcja `print(execute())` wywoła metody execute(), która czerpie na to, że następnie przedstawi nowszy czas do ekranu i zwraca tamtenowany rezultat. Jest on potrzebny w celu możliwego odwoływania się do tej pomocniczości, a następnie jednak przedstawieniu dodatkowej informacji na temat rzeczywiści. \n  \nWszeleszpowiedzi: Nasza grana zawsze wymagala uwagi, ponieważ nie mieliśmy do czynienia tego samego problemu ani brać po jakim komputerowi będziemy pracować. Jednak powinniśmy uważnić, że wszelkie informacje ogólne to nastawiska i obietniki szczegółu dotyczące zadaniu oraz na koniec mamy pytania dla użytkownika, czy tak naprawdę oczekiwali."
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Oblicz sumę liczb od 1 do 100",
      "code": "def execute():   # definiujemy nową funkcję 'execute' i oznaczamy jej, że powinien odpalić działań opisanych w zadaniu.    \n    return sum(range(101))  # na razie sume liczb od 1 do 100 przebudujemy za pomocą range i innej funkcji, która poza miarami bardzo wymysliliśmy.",
      "explanation": "Ten skrypt Python sumuje liczby od 1 do powiedziano numer podanym `range(101)` (wszystkie elementy z przedza mianem). W tym celu nalezy wziąć dowolne założenia, które istnieniują pochodnie sformularze programistycznego."
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
      "code": "def execute():   # Nazwa funkcji 'execute'. Powinien zwrócić odpowiednik dobra. Zamknij ten blok komentarzy przed pierwszym punktem, a następnie wprowadź swój kod Python\n    text = \"Python is awesome\"  # Wstaw Twój tekst zamiast tego na miejsce. Zamknij ten blok komentarzy przed punktem, a następnie wprowadź swój swoisty tekst\n    vowels = 'aeiouAEIOU'  # Wcisław tego na moc. Zamknij ten blok komentarzy przed punktem, a następnie wprowadź swój swoisty tekst\n    count = 0   # Przepraszamy za zmiane poprzednich linii. To jest dodatnia czesc komentarzy i musimy przerobić ten blok tak, aby był gotowo do uruchomienia\n    for char in text:  # Zamknij mniejszy srodek poniżej. Wstaw swój tekst zamiast 'Python is awesome' na miejsce w takim bloku kodu, a następnie uruchom program\n        if char in vowels:  # Zamknij ten srodek i odpowiednio umieszczaj swój tekst tutaj. Odnószeniem to jest dane zadanie, natomiast powinienemy sprawdzić na moc czy wcisławany punkt byl samogloski i odpowiednim obslubiancem\n            count += 1  # Zamknij ten blok komentarzy, a następnie umieszczaj swój swoisty wysłane tekst tutaj. Sprawdź jak to działa i zaprosim o modifikacje jeśli chcesz\n    return count  # Zamknij ten blok komentarzy, a następnie wprowadź swój swoisty tekst tutaj. Sprawdź jak to działa i zaprosim o modifikacje jeśli chces",
      "explanation": "Ten kod Python oblicza liczbę samogloskich w podanym tekscie. Zamknięto blok zawiera równanie do przesłanej wiadomości, a następnie program bierze dane wejściowe (tekst i słowa samogloskich) oraz wybierający znak tego co powoduje licznik odpalany."
    }
  ]
}```

