# Raport porównawczy modeli LLM dla Evopy
Data wygenerowania: 2025-05-09 14:22:32

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
  "timestamp": "20250509_142038",
  "total_tests": 3,
  "passed_tests": 3,
  "failed_tests": 0,
  "tests": [
    {
      "name": "Proste zapytanie tekstowe",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 8.81s)",
      "execution_time": 8.807093143463135,
      "code": "from datetime import datetime\ndef execute():\n    now = datetime.now()\n    return f\"Actuel date and time is {now.strftime('%Y-%m-%d %H:%M:%S')}\"",
      "explanation": "I'd be happy to explain what this code does in simple terms.\n\nThis code is a function called `execute` that returns the current date and time in a specific format. Here's what it does:\n\n1. It imports the `datetime` module, which allows us to work with dates and times.\n2. The `execute` function creates a variable called `now` that stores the current date and time using the `datetime.now()` method.\n3. The code then uses the `strftime` method to format the date and time into a string in the format `YYYY-MM-DD HH:MM:SS`.\n4. Finally, the code returns this formatted string.\n\nIn other words, when you call the `execute` function, it will give you the current date and time in the specified format.\n\nThis code solves the problem of needing to get the current date and time in a specific format for use in your program or application. Its purpose is to provide a simple way to retrieve the current date and time in a human-readable format.\n\nSo, is this what you were expecting?"
    },
    {
      "name": "Zapytanie matematyczne",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 5.28s)",
      "execution_time": 5.279687881469727,
      "code": "def execute():\n    return sum(range(1, 101))",
      "explanation": "The code you provided is a function in Python called `execute`. This function calculates the sum of all integers from 1 to 100 (inclusive) and returns this sum.\n\nTo understand how it works, let's break it down:\n\n* The `range(1, 101)` part generates a sequence of numbers from 1 to 100. The `range` function takes two arguments: the starting number and the ending number.\n* The `sum` function then adds up all these numbers in the sequence.\n\nSo, when you call this `execute` function, it will calculate and return the sum of all integers from 1 to 100.\n\nFor example, if you run this code:\n```python\nprint(execute())\n```\nIt will output: `5050`, which is the sum of all numbers from 1 to 100.\n\nThis code solves no specific problem, but rather provides a simple way to calculate the sum of a range of numbers. The purpose of this code might be to demonstrate how to use Python's built-in functions like `range` and `sum`.\n\nIs this what you were expecting?"
    },
    {
      "name": "Zapytanie z przetwarzaniem tekstu",
      "status": "PASSED",
      "reason": "Test zakończony sukcesem (czas: 7.92s)",
      "execution_time": 7.916286945343018,
      "code": "def execute(text):\n    vowels = ['a', 'e', 'i', 'o', 'u']\n    result = [char for char in text.lower() if char in vowels]\n    return ''.join(result)",
      "explanation": "Let's break down this code together!\n\nThe code is a function called `execute` that takes one input parameter, `text`. This function does three main things:\n\n1. **Converts the text to lowercase**: The line `text.lower()` converts the entire text to all lowercase letters.\n2. **Finds and collects vowels**: The list comprehension `[char for char in text.lower() if char in vowels]` goes through each character in the modified text and checks if it's one of the five basic vowels (a, e, i, o, u). If it is, that vowel gets added to a new list called `result`.\n3. **Joins the vowels together**: The line `''.join(result)` takes all the vowels collected in step 2 and joins them together into a single string.\n\nSo, what does this code do? It takes some text as input, converts it to lowercase, extracts only the vowels from that text, and returns those vowels as a new string.\n\nFor example, if you call `execute(\"Hello World!\")`, the function would return the string `\"eo\"` because those are the vowels present in the original text.\n\nAs for problems solved or goals of this code, it seems to be designed to help with text processing tasks that require extracting specific characters (in this case, vowels) from a given input. Perhaps someone might use this code to analyze text data or clean up text strings by removing non-vowel characters.\n\nNow, let me ask you: is this what you were expecting?"
    }
  ]
}```

### Model: deepsek

Brak wyników testów zapytań dla modelu deepsek.

