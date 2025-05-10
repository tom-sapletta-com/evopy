import pytest
from devopy.llm import analyze_task

def test_analyze_task_wykres():
    assert "matplotlib" in analyze_task("narysuj wykres")

def test_analyze_task_api():
    assert "requests" in analyze_task("pobierz dane z api")

def test_analyze_task_excel():
    assert "openpyxl" in analyze_task("zapisz do pliku excel")

def test_analyze_task_json():
    assert "json" in analyze_task("przetwórz dane json")
