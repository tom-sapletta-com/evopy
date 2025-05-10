from devopy.shell.interactive import interactive_shell
from devopy.dependency import ensure_package
from devopy.evolution import HISTORY_FILE
import json

DEFAULT_PACKAGES = ["requests", "matplotlib", "openpyxl", "json"]

def install_all_dependencies():
    # Najpierw domyślne paczki
    for pkg in DEFAULT_PACKAGES:
        ensure_package(pkg)
    # Potem z historii zadań
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        pkgs = set()
        for entry in history:
            pkgs.update(entry.get("packages", []))
        for pkg in pkgs:
            ensure_package(pkg)
    except Exception:
        pass

def main():
    install_all_dependencies()
    interactive_shell()

if __name__ == "__main__":
    main()
