import builtins
import pytest
from devopy.shell import interactive

def test_shell_exit(monkeypatch):
    # Testuje czy shell poprawnie kończy pracę po 'exit'
    inputs = iter(["exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    interactive.interactive_shell()

def test_shell_import_requests(monkeypatch):
    # Testuje automatyczną instalację i import paczki requests
    inputs = iter(["import requests", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    interactive.interactive_shell()

def test_shell_zadanie_plot(monkeypatch):
    # Testuje zadanie z heurystyką LLM (wykres)
    inputs = iter(["zadanie narysuj wykres", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    interactive.interactive_shell()
