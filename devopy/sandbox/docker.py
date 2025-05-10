import subprocess
import uuid
from pathlib import Path

class DockerSandbox:
    def __init__(self, base_dir="docker_sandbox_envs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    def create_env(self, packages):
        env_id = str(uuid.uuid4())[:8]
        dockerfile = self.base_dir / f"Dockerfile_{env_id}"
        requirements = self.base_dir / f"requirements_{env_id}.txt"
        # Zapisz requirements.txt
        with open(requirements, "w") as f:
            for pkg in packages:
                f.write(pkg + "\n")
        # Zapisz Dockerfile
        dockerfile.write_text(f"""
FROM python:3.12-slim
WORKDIR /app
COPY requirements_{env_id}.txt ./
RUN pip install --upgrade pip && pip install -r requirements_{env_id}.txt
CMD [\"python3\", \"-c\", \"print('Docker sandbox ready')\"]
""")
        # Build image
        image_tag = f"devopy_sandbox:{env_id}"
        subprocess.check_call([
            "docker", "build", "-f", str(dockerfile), "-t", image_tag, str(self.base_dir)
        ])
        return image_tag, env_id

    def test_package(self, image_tag, package_name):
        # Uruchom kontener i sprawdź import paczki
        code = f"import {package_name}"
        try:
            subprocess.check_call([
                "docker", "run", "--rm", image_tag, "python3", "-c", code
            ])
            return True
        except Exception as e:
            print(f"[ERROR] Docker sandbox test import {package_name}: {e}")
            return False
