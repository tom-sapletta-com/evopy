# devopy/llm.py

def analyze_task(task_text):
    """
    Prosty heurystyczny analizator polecenia.
    Docelowo tu integracja z LLM (np. DeepSeek, OpenAI, Ollama).
    """
    task_text = task_text.lower()
    suggestions = []
    if "wykres" in task_text or "plot" in task_text:
        suggestions.append("matplotlib")
    if "api" in task_text or "requests" in task_text or "http" in task_text:
        suggestions.append("requests")
    if "excel" in task_text or "xlsx" in task_text:
        suggestions.append("openpyxl")
    if "json" in task_text:
        suggestions.append("json")
    # Możesz dodać więcej reguł lub zintegrować z prawdziwym LLM
    return suggestions
