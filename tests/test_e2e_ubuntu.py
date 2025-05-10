import builtins
import pytest
from devopy.shell import interactive

def run_shell_cmds(cmds):
    inputs = iter(cmds)
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(builtins, "input", lambda _: next(inputs))
    interactive.interactive_shell()
    monkeypatch.undo()

def test_shell_start_exit():
    run_shell_cmds(["exit"])

def test_import_requests():
    run_shell_cmds(["import requests", "exit"])

def test_zadanie_wykres():
    run_shell_cmds(["zadanie narysuj wykres", "exit"])

def test_zadanie_api():
    run_shell_cmds(["zadanie pobierz dane z api", "exit"])

def test_zadanie_excel():
    run_shell_cmds(["zadanie zapisz do pliku excel", "exit"])

def test_use_module():
    run_shell_cmds(["użyj requests", "exit"])

def test_unknown_command():
    run_shell_cmds(["nieznane_polecenie", "exit"])

def test_exit():
    run_shell_cmds(["exit"])
