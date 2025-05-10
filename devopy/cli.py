import argparse
from devopy.orchestrator import Orchestrator

def main():
    parser = argparse.ArgumentParser(description="devopy CLI: automatyczne środowiska dla zadań Python")
    parser.add_argument("run", metavar="TASK", type=str, nargs=1, help="Opis zadania do wykonania (np. 'pobierz dane z api i zapisz do excela')")
    parser.add_argument("--docker", action="store_true", help="Użyj sandboxa Docker zamiast venv")
    args = parser.parse_args()

    task = args.run[0]
    orch = Orchestrator()
    print("[INFO] Uruchamiam zadanie:", task)
    orch.process_task(task, docker=args.docker)

if __name__ == "__main__":
    main()
