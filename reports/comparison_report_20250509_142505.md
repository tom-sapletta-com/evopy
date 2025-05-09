# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 14:25:05

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
  "timestamp": "20250509_142318",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 9.83s)",
      "execution_time": 9.8295738697052,
      "code": "import datetime\ndef execute():\n    now = datetime.datetime.now()\n    print(f'Acttual date and time: {now.strftime(\"%Y-%m-%d %H:%M:%S\")}')\n    return now.strftime(\"%Y-%m-%d %H:%M:%S\")",
      "explanation": "The code is written in Python, a popular programming language. Let's break it down and explain what each part does.\n\n**Importing a module**\nThe first line `import datetime` tells the program to use a built-in module called `datetime`. This module provides functions for working with dates and times.\n\n**Defining a function**\nThe next line `def execute():` defines a new function named `execute`. A function is like a recipe that takes some input (in this case, none), performs some calculations or operations, and returns an output.\n\n**Getting the current date and time**\nInside the `execute` function, we have two lines:\n\n1. `now = datetime.datetime.now()`: This line uses the `datetime` module to get the current date and time. The result is stored in a variable named `now`.\n2. `print(f'Acttual date and time: {now.strftime(\"%Y-%m-%d %H:%M:%S\")}')`: This line prints a message to the console, including the current date and time. The `{now.strftime(\"%Y-%m-%d %H:%M:%S\")}` part is using a format string to convert the `now` variable into a human-readable string.\n\n**Returning the formatted date and time**\nThe last line `return now.strftime(\"%Y-%m-%d %H:%M:%S\")` takes the formatted date and time from earlier and returns it as the output of the `execute` function. This means that if you call the `execute` function, it will return a string representing the current date and time in the format \"YYYY-MM-DD HH:MM:SS\".\n\nIn summary, this code provides a way to get the current date and time, print it to the console, and return it as a formatted string. This can be useful for logging or reporting purposes.\n\nSo, is this what you were expecting?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 7.06s)",
      "execution_time": 7.05618953704834,
      "code": "def execute():\n    return sum(range(1, 101))",
      "explanation": "Let's break down this code step by step!\n\nThe code defines a function called `execute` that returns the sum of numbers from 1 to 100.\n\nHere's what each part does:\n\n* `def execute():`: This line defines a new function named `execute`. The parentheses are empty, which means the function doesn't take any input arguments.\n* `return`: This keyword tells Python to return a value from the function. In this case, we're returning the result of the expression inside the parentheses.\n* `sum(range(1, 101))`: This is the expression that gets evaluated and returned by the function.\n\n`range(1, 101)` creates an iterator that generates numbers from 1 to 100 (inclusive). The `sum` function then adds up all these numbers and returns the total sum.\n\nIn simple terms, this code calculates the sum of all integers from 1 to 100. For example, if you run this code, it will return the value `5050`, which is the sum of all numbers from 1 to 100 (1 + 2 + ... + 100 = 5050).\n\nThis code doesn't solve any specific problems or address particular challenges. Its main purpose is to demonstrate a simple way to calculate the sum of consecutive integers using Python's built-in `range` and `sum` functions.\n\nSo, what do you think? Is this explanation helpful in understanding what this code does?"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 8.17s)",
      "execution_time": 8.165214776992798,
      "code": "```\ndef execute(text):\n    vowels = 'aeiouy'\n    result = [char for char in text.lower() if char in vowels]\n    return ''.join(result)",
      "explanation": "I'd be happy to help explain this code!\n\nThis is a Python function named `execute` that takes one input parameter, `text`. The function does the following:\n\n1. It defines a string called `vowels` that contains all the vowel characters (a, e, i, o, u, and y).\n2. It initializes an empty list called `result`.\n3. It iterates through each character in the input `text`, converts it to lowercase using the `.lower()` method, and checks if the character is present in the `vowels` string.\n4. If a vowel character is found, it adds that character to the `result` list.\n5. Finally, it returns a new string created by concatenating all the characters in the `result` list using the `.join()` method.\n\nIn simple terms, this code takes some text as input and returns a new string containing only the vowel characters from the original text. For example, if you call the function with the input `\"Hello World\"`, it would return the string `\"eoou\"` because those are the vowel characters present in the original text.\n\nThe problems this code solves include:\n\n* It helps extract specific characters (in this case, vowels) from a larger text.\n* It demonstrates basic string manipulation and iteration techniques using Python's list comprehensions.\n\nThe goal of this code is likely to be used as part of a more comprehensive program that processes text data in some way. For example, it could be used to filter out non-vowel characters before performing further text analysis or processing.\n\nNow, I'd like to ask: Is this what you were expecting?"
    }
  ]
}```

### Model: deepsek

Brak wyników testów zapytań dla modelu deepsek.

