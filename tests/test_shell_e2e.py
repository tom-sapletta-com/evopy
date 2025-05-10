import builtins
import pytest
from devopy.shell import interactive

def test_shell_zadanie_suggest(monkeypatch):
    # Symulacja wejścia: zadanie pobierz dane z api i narysuj wykres
    inputs = iter(["zadanie pobierz dane z api i narysuj wykres", "exit"])
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    # Sprawdzenie, czy shell nie rzuca wyjątków
    interactive.interactive_shell()
# Możesz rozbudować testy o sprawdzanie efektów ubocznych (np. czy paczki zostały zainstalowane)
