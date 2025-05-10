from devopy.registry.pypi import PyPIRegistry
from devopy.sandbox.venv import VenvSandbox

class Orchestrator:
    def __init__(self):
        self.sandbox = VenvSandbox()

    def analyze_task(self, task):
        # Prosta heurystyka: zwraca listę paczek na podstawie słów kluczowych
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

    def process_task(self, task):
        needed_packages = self.analyze_task(task)
        env_path = self.sandbox.create_env("task_env")
        for pkg in needed_packages:
            print(f"[INFO] Instaluję {pkg} w sandboxie...")
            PyPIRegistry.install_package(pkg, venv_path=env_path)
            print(f"[INFO] Testuję {pkg} w sandboxie...")
            if not self.sandbox.test_package(env_path, pkg):
                print(f"[ERROR] Paczka {pkg} nie przeszła testu!")
                return False
        print("[SUCCESS] Środowisko gotowe do użycia!")
        return True

if __name__ == "__main__":
    orch = Orchestrator()
    orch.process_task("pobierz dane z api i zapisz do excela")
