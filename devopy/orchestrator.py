from devopy.registry.pypi import PyPIRegistry
from devopy.sandbox.venv import VenvSandbox
from devopy.sandbox.docker import DockerSandbox
from devopy.llm import analyze_task_llm

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
            print("[SUCCESS] Środowisko gotowe do użycia!")
            return True

if __name__ == "__main__":
    orch = Orchestrator()
    print("VENVSANDBOX:")
    orch.process_task("pobierz dane z api i zapisz do excela")
    print("\nDOCKERSANDBOX:")
    orch.process_task("pobierz dane z api i zapisz do excela", docker=True)
