# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 10:41:18

## Podsumowanie wyników

| Model | Testy zapytań | Testy poprawności | Testy wydajności | Całkowity wynik |
|-------|--------------|-------------------|------------------|-----------------|
| llama | ✅ | ✅ | ✅ | 3/3 |
| phi | ✅ | ✅ | ✅ | 3/3 |
| bielik | ✅ | ✅ | ✅ | 3/3 |
| deepsek | ❌ | ✅ | ✅ | 2/3 |

## Szczegółowe wyniki testów

### Model: llama

#### Wyniki testów zapytań
```json
{
  "timestamp": "20250509_103501",
  "model_id": "llama",
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
      "code": "```\nfrom datetime import datetime\n\ndef execute():\n    now = datetime.now()\n    return f\"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}\"",
      "explanation": "The code!\n\nLet me break it down for you in simple terms:\n\n**What does the code do?**\n\nThis Python code defines a function called `execute()` that returns the current date and time.\n\n**How does it work?**\n\n1. The code imports the `datetime` module from the Python standard library, which provides functions for working with dates and times.\n2. The `execute()` function is defined, which has no input parameters (i.e., it's a \"black box\" that takes no arguments).\n3. Inside the `execute()` function:\n\t* The code uses the `datetime.now()` method to get the current date and time.\n\t* It assigns this value to a variable named `now`.\n4. The code then returns a string using the `f-string` formatting feature (introduced in Python 3.6). The string is formatted with the current date and time, using the `%Y-%m-%d %H:%M:%S` format specifier.\n\t* `%Y` represents the year (e.g., \"2022\")\n\t* `%m` represents the month (01-12)\n\t* `%d` represents the day of the month (01-31)\n\t* `%H` represents the hour (00-23)\n\t* `%M` represents the minute (00-59)\n\t* `%S` represents the second (00-59)\n\n**What's the purpose of this code?**\n\nThe main goal is to provide a simple way to get the current date and time, which can be useful in various applications, such as logging events, scheduling tasks, or displaying system information.\n\n**Problems solved:**\n\n* This code provides an easy-to-use interface for getting the current date and time.\n* It eliminates the need to manually create datetime objects using libraries like `datetime` or `dateutil`.\n\n**Your turn!**\n\nIs this what you expected?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Oblicz sumę liczb od 1 do 100",
      "code": "```\ndef execute():\n    return sum(range(1, 101))",
      "explanation": "A nice and simple piece of code!\n\nThis is a function called `execute` that calculates the sum of all numbers from 1 to 100 (inclusive). Let me break it down for you:\n\n* `def execute():`: This line defines a new function named `execute`. The `def` keyword is used to define a function, and the parentheses `()` are empty because this function doesn't take any arguments.\n* `return sum(range(1, 101))`: This is where the magic happens! Here's what's happening:\n\t+ `range(1, 101)`: This creates a special kind of object called a \"range\" that generates numbers from 1 to 100 (inclusive). Think of it like a counter that starts at 1 and ends at 100.\n\t+ `sum(...)`: This is a built-in Python function that adds up all the numbers in the range. In this case, we're passing the `range` object as an argument to `sum`.\n\t+ `return ...`: The `return` statement takes the result of the calculation (the sum of the numbers from 1 to 100) and returns it.\n\nSo, when you call the `execute()` function, it will calculate the sum of all numbers from 1 to 100 and return that value. For example, if you run this code, you'll get a result like 5050 (which is the correct sum!).\n\nAs for problems solved or goals achieved, this code helps with calculating sums quickly and efficiently. It's a simple but useful example of how Python can be used to automate calculations!\n\nNow, I'd love to hear from you: Is this what you were expecting?"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
      "code": "```\ndef execute(text):\n    vowels = 'aeiou'\n    result = [char for char in text if char.lower() in vowels]\n    return ''.join(result)",
      "explanation": "I'd be happy to explain what this code does!\n\nThis is a Python function called `execute` that takes one input parameter, `text`. The function's purpose is to extract all the vowel characters (A, E, I, O, U) from the input text and return them as a single string.\n\nHere's how it works:\n\n1. The function defines a variable `vowels` that contains the set of vowel characters.\n2. It then uses a list comprehension to iterate over each character in the input `text`.\n3. For each character, it checks if the lowercase version of the character (i.e., converting uppercase letters to lowercase) is present in the `vowels` string.\n4. If the character is a vowel, it adds it to a new list called `result`.\n5. Finally, the function uses the `join` method to concatenate all the vowel characters in the `result` list into a single string, which is then returned.\n\nIn simpler terms, this code takes some text as input and returns a new string that contains only the vowel characters from the original text.\n\nFor example, if you call the function with the input `\"Hello World!\"`, it would return the string `\"eo\"` because those are the vowel characters present in the original text.\n\nIs this what you were expecting?"
    }
  ]
}```

### Model: phi

Brak wyników testów zapytań dla modelu phi.

### Model: bielik

#### Wyniki testów zapytań
```json
{
  "timestamp": "20250509_103817",
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
      "code": "import datetime\ndef execute():\n    now = datetime.datetime.now()\n    return f\"Current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}\"",
      "explanation": "Let me explain what this code does in simple terms.\n\nThis code is a small Python program that prints the current date and time. Here's how it works:\n\n1. The first line, `import datetime`, tells Python to use a built-in module called \"datetime\". This module has tools for working with dates and times.\n2. The next line, `def execute():`, defines a function called `execute`. A function is like a recipe that takes some input, does some work, and returns an output.\n3. Inside the `execute` function, there are two lines:\n\t* `now = datetime.datetime.now()`: This line uses the \"datetime\" module to get the current date and time. It's like taking your pulse!\n\t* `return f\"Current date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}\"`: This line takes the current date and time, formats it into a nice string (e.g., \"2023-07-25 14:30:00\"), and returns that string as the output of the `execute` function.\n\nSo, when you run this code, it will print something like:\n\n\"Current date and time is 2023-07-25 14:30:00\"\n\nThis code solves a simple problem: how to get the current date and time in a nice format. Its main purpose is to provide a quick way to display the current date and time.\n\nNow, I'd love to ask you: Is this what you were expecting?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Oblicz sumę liczb od 1 do 100",
      "code": "def execute():\n    return sum(range(1, 101))",
      "explanation": "Let me explain what this code does in simple terms!\n\nThe code defines a function called `execute`. This function doesn't take any arguments (inputs). When you call the `execute` function, it will do something and return the result.\n\nWhat does it do? Well, inside the function, there are two main parts: `range(1, 101)` and `sum`.\n\nThe `range(1, 101)` part creates a sequence of numbers from 1 to 100 (inclusive). Think of it like a list of numbers: `[1, 2, 3, ..., 99, 100]`.\n\nThe `sum` function takes this sequence of numbers as input and returns the total sum of all those numbers. So, in this case, it would add up all the numbers from 1 to 100.\n\nWhen you call the `execute` function, it will execute this process: create a list of numbers from 1 to 100, then calculate the total sum of those numbers. The result is returned by the function.\n\nFor example, if you called `execute()`, the function would return the value `5050`, which is the sum of all numbers from 1 to 100 (1 + 2 + 3 + ... + 99 + 100).\n\nThe goal of this code is likely to calculate a total sum or aggregate value of some kind. In this case, it's calculating the sum of consecutive integers.\n\nSo, that's what this code does!"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
      "code": "```\ndef execute(text):\n    vowels = \"aeiouyAEIOUW\"\n    result = [char for char in text if char in vowels]\n    return \"\".join(result)",
      "explanation": "I'd be happy to explain what this code does!\n\nThis is a Python function named `execute` that takes one input parameter, `text`. The function's purpose is to extract all the vowel characters (A, E, I, O, U, and Y) from the given text and return them in a new string.\n\nHere's how it works:\n\n1. The code defines a string called `vowels` that contains all the vowel characters.\n2. It then uses a list comprehension to iterate through each character (`char`) in the input `text`.\n3. For each character, it checks if the character is present in the `vowels` string using an `if char in vowels` condition.\n4. If the character is a vowel (i.e., it's present in the `vowels` string), it adds that character to a new list called `result`.\n5. Finally, it uses the `join()` method to concatenate all the characters in the `result` list into a single string.\n\nThe purpose of this code is to isolate and collect only the vowel characters from a given text. This could be useful in various natural language processing tasks, such as text analysis or data preprocessing.\n\nSo, what do you think? Is this what you were expecting?"
    }
  ]
}```

### Model: deepsek

#### Wyniki testów zapytań
```json
{
  "timestamp": "20250509_104030",
  "model_id": "deepsek",
  "model_name": "deepseek-coder",
  "total_tests": 3,
  "passed_tests": 2,
  "failed_tests": 1,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "FAILED",
      "reason": "Brakujące elementy w kodzie: datetime",
      "query": "Wyświetl aktualną datę i godzinę",
      "code": "def execute():\n    # Kod wygenerowany na podstawie opisu użytkownika\n    Utwórz funkcję Pythona, która wypisze na ekran czyli \"Hello World\" lub inny tekst informujący o bieżącej datach i godzinie. Załóżmy zgodnie ze świadomo, by nazwa ta jest 'display_date'\n    \n    # Zwróć wynik jeśli funkcja nic nie zwraca\n    return \"Wykonano zadanie\"\n",
      "explanation": "Ten kod jest często stosowany w Python do inicjalizacji funkcji, takich jak `display_date`. Ten skrypt nazywa się \"Hello World\", a zamiast tego uruchamia puste polecenie o treści: 'Wykonano zadanie'. Zwyczajowej wersji programu powinna informować użytkownika datę i godzinę, którą uruchomiono ten skrypt."
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Oblicz sumę liczb od 1 do 100",
      "code": "def execute():\n    return sum(range(1, 101))\nprint('Suma liczb od 1 do 100 to',execute())",
      "explanation": "Ten prosty kod jest wykonywany za pomocą funkcji `sum()` i `range(start, stop)`. Wskazówki pochodzą z podstawowej cechi programu Python'a - oblicza sumę liczb od 1 do 99 (lub co najmniej to tyle). Tak jest na szyk, ale ten kod w pracy. Niestety po prostu powstały bardzo podobne rozwiązanie zamiast funkcji sum(), a dobrych miarowego potrzebujemy pokazywać także co robi i które problemy mooglibub wystarczyć, gdyby przerobili ten sam."
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Kod zawiera wszystkie oczekiwane elementy",
      "query": "Znajdź wszystkie samogłoski w tekście 'Python jest wspaniały'",
      "code": "def execute():\n    text = 'Python is very interesting'   # podana do opisu zadania, ale nie uzywam tutaj tekstowego argumentu. Zamiast to powinno być wywołanie funkcji za pomoca takiej jako ile chcesz\n    vowels = 'aeiouAEIOU'  # dopusobiam znany samoglosem do sprawdzania, np. Dodajem na koncu tych samych napisów wszytkiego tekstu - \"...is\"\n    result = [char for char in text if char in vowels]  # tworzymy listę znaków, dla których istnienia jest samoglosem (np. 'o' w tekście \"Python\")\n    return len(result)",
      "explanation": "Ten kod Python został utworzony do sprawdzenia ile samoglosek (typowych wyrazów dla języka polskiego, tj. pojedyncze słowa o podstawowej litery 'o') znajduje się we wpisanym tekscie i jeśli istnieje to wrzuć do listy (`result`), następnie zwróć liczebność takich samoglosek. \n\nRozsąd na temat danych wejściowych: Jednym argumentem jest podstawiony wzorczyst do sprawdzania czy istnieje tylu (typowe) samoglosek za pomoca listy `vowels`.\nRozsąd na potrzeby obliczeniowej: Wartościami, które szukamy wpisanych znakach (w tym przypadku pojedynczych liter samoglosek) i jeżeli to jest sprawdzone za pomocą listy `vowels`, następnie dodajemy do listy. W rezultacie zwróć będziemu liczebności takich samoglosek w tekscie wejściowym (np \"Python\" -> 'o' i nawias szeroko po lewej stronie)."
    }
  ]
}```

