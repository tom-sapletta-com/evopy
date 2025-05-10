import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.resolve()))
from registry.pypi import PyPIRegistry
from sandbox.venv import VenvSandbox
from sandbox.docker import DockerSandbox
from llm import analyze_task_llm

class Orchestrator:
    def __init__(self):
        self.sandbox = VenvSandbox()
        self.docker_sandbox = DockerSandbox()

    def analyze_task(self, task):
        # Użyj LLM/interfejsu heurystycznego do wyboru paczek
        return analyze_task_llm(task)

    def process_task(self, task, docker=False):
        needed_packages = self.analyze_task(task)
        if docker:
            print("[INFO] Tworzę sandbox Docker...")
            image_tag, env_id = self.docker_sandbox.create_env(needed_packages)
            for pkg in needed_packages:
                print(f"[INFO] Testuję {pkg} w Docker sandbox...")
                if not self.docker_sandbox.test_package(image_tag, pkg):
                    print(f"[ERROR] Paczka {pkg} nie przeszła testu w Docker!")
                    return False
            print("[SUCCESS] Docker sandbox gotowy do użycia!")
            return True
        else:
            env_path = self.sandbox.create_env("task_env")
            for pkg in needed_packages:
                print(f"[INFO] Instaluję {pkg} w sandboxie...")
                PyPIRegistry.install_package(pkg, venv_path=env_path)
                print(f"[INFO] Testuję {pkg} w sandboxie...")
                if not self.sandbox.test_package(env_path, pkg):
                    print(f"[ERROR] Paczka {pkg} nie przeszła testu!")
                    return False
            # Specjalna obsługa dla wykresów
            if "matplotlib" in needed_packages and "excel" in task.lower():
                import importlib.util
                import sys
                import os
                import openpyxl
                import matplotlib
                import matplotlib.pyplot as plt
                from devopy.output_utils import get_output_dir, unique_filename
                # Szukaj pliku Excel w katalogu roboczym (dla uproszczenia)
                files = [f for f in os.listdir(os.getcwd()) if f.endswith('.xlsx') or f.endswith('.xls')]
                if not files:
                    return {"error": "Brak pliku Excel w katalogu roboczym!", "status": "fail"}
                wb = openpyxl.load_workbook(files[0])
                ws = wb.active
                data = [row for row in ws.iter_rows(values_only=True)]
                if len(data) < 2:
                    return {"error": "Za mało danych w pliku Excel!", "status": "fail"}
                x, y = zip(*data[1:])
                plt.figure()
                plt.plot(x, y)
                plt.title("Wykres z Excela")
                out_dir = get_output_dir()
                fname = unique_filename()
                out_path = os.path.join(out_dir, fname)
                plt.savefig(out_path)
                plt.close()
                print(f"[SUCCESS] Wykres zapisany jako {fname}")
                return {"status": "ok", "plot_file": fname}
            print("[SUCCESS] Środowisko gotowe do użycia!")
            return True

if __name__ == "__main__":
    orch = Orchestrator()
    print("VENVSANDBOX:")
    orch.process_task("pobierz dane z api i zapisz do excela")
    print("\nDOCKERSANDBOX:")
    orch.process_task("pobierz dane z api i zapisz do excela", docker=True)
