from devopy.shell.modules import ensure_module
from devopy.logger import info
from devopy.llm import analyze_task

def interactive_shell():
    info("Witaj w devopy shell! Wpisz 'użyj <moduł>', 'zadanie <nazwa>' lub 'exit'.")
    while True:
        cmd = input("devopy> ").strip()
        if cmd.startswith("użyj "):
            mod = cmd.split(" ", 1)[1].strip()
            ensure_module(mod)
            continue
        if cmd.startswith("zadanie "):
            task_name = cmd.split(" ", 1)[1].strip()
            # Analiza zadania przez LLM/heurystykę
            suggested_pkgs = analyze_task(task_name)
            for pkg in suggested_pkgs:
                ensure_module(pkg)
            info(f"Sugerowane i zainstalowane paczki: {', '.join(suggested_pkgs)}")
            continue
        if cmd in ("exit", "quit"):
            info("Kończę pracę shellu devopy.")
            break
        else:
            info(f"Nieznane polecenie: {cmd}")
