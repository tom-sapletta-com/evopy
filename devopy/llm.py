"""
llm.py - interfejs do analizy polecenia użytkownika i wyboru paczek
Docelowo: podłączenie do prawdziwego LLM lub API (np. OpenAI, Ollama, DeepSeek)
Na razie: prosta heurystyka
"""

def analyze_task_llm(task):
    """
    Analizuje polecenie użytkownika i zwraca listę paczek Python.
    Wersja demo - heurystyka słów kluczowych. Możliwość podpięcia prawdziwego LLM/API.
    """
    pkgs = set()
    task_lower = task.lower()
    if "excel" in task_lower:
        pkgs.add("openpyxl")
    if "api" in task_lower:
        pkgs.add("requests")
    if "wykres" in task_lower or "chart" in task_lower:
        pkgs.add("matplotlib")
    if not pkgs:
        pkgs.add("requests")
    return list(pkgs)

# Przykład użycia:
if __name__ == "__main__":
    print(analyze_task_llm("pobierz dane z api i zapisz do excela"))
