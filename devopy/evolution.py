import json
from devopy.config import APP_DIR

HISTORY_FILE = APP_DIR / "evolution_history.json"

# Logowanie wykonanych zadań i użytych paczek

def log_task(task, packages):
    history = []
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append({"task": task, "packages": packages})
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def suggest_packages_for_task(task):
    if not HISTORY_FILE.exists():
        return []
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    for entry in reversed(history):
        if entry["task"] in task:
            return entry["packages"]
    return []
