#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service Sandbox - Moduł do uruchamiania serwisów webowych w kontenerach Docker

Ten moduł zapewnia bezpieczne środowisko do uruchamiania serwisów webowych
generowanych na podstawie kodu Python użytkownika.
"""

import os
import uuid
import json
import time
import shutil
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Import menedżera zależności
from dependency_manager import fix_code_dependencies

logger = logging.getLogger("evo-assistant.service-sandbox")


class ServiceSandbox:
    """Klasa do zarządzania piaskownicami Docker dla serwisów webowych"""

    def __init__(self, base_dir: Path, docker_image: str = "python:3.9-slim", timeout: int = 30):
        """
        Inicjalizacja piaskownicy serwisu

        Args:
            base_dir: Katalog bazowy dla plików piaskownicy
            docker_image: Obraz Docker do użycia
            timeout: Limit czasu wykonania w sekundach
        """
        self.base_dir = base_dir
        self.docker_image = docker_image
        self.timeout = timeout
        self.container_id = None
        self.sandbox_id = str(uuid.uuid4())
        self.sandbox_dir = base_dir / self.sandbox_id
        self.service_port = self._find_available_port()
        self.service_url = f"http://localhost:{self.service_port}"

        # Utwórz katalog dla piaskownicy
        os.makedirs(self.sandbox_dir, exist_ok=True)
        
        # Utwórz katalogi dla serwisu
        os.makedirs(self.sandbox_dir / "templates", exist_ok=True)
        os.makedirs(self.sandbox_dir / "static", exist_ok=True)

    def _find_available_port(self) -> int:
        """
        Znajduje dostępny port dla serwisu

        Returns:
            int: Numer dostępnego portu
        """
        # Znajdź dostępny port w zakresie 8000-9000
        for port in range(8000, 9000):
            try:
                # Sprawdź, czy port jest dostępny
                result = subprocess.run(
                    ["lsof", "-i", f":{port}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if result.returncode != 0:
                    return port
            except:
                # Jeśli wystąpił błąd, zakładamy, że port jest dostępny
                return port
        
        # Jeśli nie znaleziono dostępnego portu, użyj losowego
        return 8000 + (uuid.uuid4().int % 1000)

    def prepare_service(self, code: str, name: str = "Evopy Service", description: str = "", version: str = "1.0.0") -> Path:
        """
        Przygotowuje kod serwisu do uruchomienia w piaskownicy

        Args:
            code: Kod Python do wykonania
            name: Nazwa serwisu
            description: Opis serwisu
            version: Wersja serwisu

        Returns:
            Path: Ścieżka do pliku z kodem
        """
        # Napraw brakujące zależności w kodzie użytkownika
        code = fix_code_dependencies(code)

        # Przygotuj katalog dla serwisu
        service_dir = self.sandbox_dir
        
        # Kopiuj szablon serwisu
        template_path = Path(__file__).parent / "service_template.py"
        if template_path.exists():
            shutil.copy(template_path, service_dir / "service_template.py")
        else:
            logger.warning(f"Nie znaleziono szablonu serwisu: {template_path}")
            # Tutaj można by dodać kod do pobrania szablonu z repozytorium
        
        # Utwórz plik serwisu
        service_file = service_dir / "service.py"
        
        # Przygotuj kod serwisu
        service_code = f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
Serwis wygenerowany przez Evopy
\"\"\"

import os
import sys
import json
import time
import logging
from pathlib import Path

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("evopy-service")

# Importuj szablon serwisu
from service_template import (
    app, api_endpoint, web_page, run_service, set_service_info,
    generate_api_docs
)

# Ustaw informacje o serwisie
set_service_info(
    name="{name}",
    description="{description}",
    version="{version}"
)

# Kod użytkownika
{code}

# Uruchom serwis
if __name__ == "__main__":
    run_service(host="0.0.0.0", port={self.service_port}, debug=False)
"""

        # Zapisz kod serwisu
        with open(service_file, "w") as f:
            f.write(service_code)
        
        # Utwórz plik requirements.txt
        requirements_file = service_dir / "requirements.txt"
        with open(requirements_file, "w") as f:
            f.write("flask==2.0.1\\n")
        
        # Utwórz plik Dockerfile
        dockerfile = service_dir / "Dockerfile"
        with open(dockerfile, "w") as f:
            f.write(f"""FROM {self.docker_image}

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE {self.service_port}

CMD ["python", "service.py"]
""")

        return service_file

    def build_and_run(self, code: str, name: str = "Evopy Service", description: str = "", version: str = "1.0.0") -> Dict[str, Any]:
        """
        Buduje i uruchamia serwis w kontenerze Docker

        Args:
            code: Kod Python do wykonania
            name: Nazwa serwisu
            description: Opis serwisu
            version: Wersja serwisu

        Returns:
            Dict: Informacje o uruchomionym serwisie
        """
        try:
            # Przygotuj kod serwisu
            service_file = self.prepare_service(code, name, description, version)
            
            # Nazwa kontenera i obrazu
            container_name = f"evopy-service-{self.sandbox_id}"
            image_name = f"evopy-service-image-{self.sandbox_id}"
            
            # Zbuduj obraz Docker
            logger.info(f"Budowanie obrazu Docker: {image_name}")
            build_cmd = [
                "docker", "build",
                "-t", image_name,
                str(self.sandbox_dir)
            ]
            
            build_process = subprocess.Popen(
                build_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            build_stdout, build_stderr = build_process.communicate()
            
            if build_process.returncode != 0:
                logger.error(f"Błąd podczas budowania obrazu Docker: {build_stderr}")
                return {
                    "success": False,
                    "error": f"Błąd podczas budowania obrazu Docker: {build_stderr}",
                    "build_output": build_stdout
                }
            
            # Uruchom kontener
            logger.info(f"Uruchamianie kontenera Docker: {container_name}")
            run_cmd = [
                "docker", "run",
                "--name", container_name,
                "-d",  # Uruchom w tle
                "-p", f"{self.service_port}:{self.service_port}",
                "--memory", "512m",  # Limit pamięci
                "--cpus", "0.5",  # Limit CPU
                image_name
            ]
            
            run_process = subprocess.Popen(
                run_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            run_stdout, run_stderr = run_process.communicate()
            
            if run_process.returncode != 0:
                logger.error(f"Błąd podczas uruchamiania kontenera Docker: {run_stderr}")
                return {
                    "success": False,
                    "error": f"Błąd podczas uruchamiania kontenera Docker: {run_stderr}",
                    "run_output": run_stdout
                }
            
            # Zapisz ID kontenera
            self.container_id = run_stdout.strip()
            
            # Poczekaj na uruchomienie serwisu
            logger.info(f"Czekanie na uruchomienie serwisu na porcie {self.service_port}...")
            max_retries = 10
            retry_delay = 1
            
            for i in range(max_retries):
                try:
                    # Sprawdź, czy serwis jest dostępny
                    health_check_cmd = [
                        "docker", "exec", container_name,
                        "curl", "-s", f"http://localhost:{self.service_port}/api/info"
                    ]
                    
                    health_check_process = subprocess.Popen(
                        health_check_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    health_stdout, health_stderr = health_check_process.communicate(timeout=5)
                    
                    if health_check_process.returncode == 0:
                        logger.info(f"Serwis uruchomiony pomyślnie na porcie {self.service_port}")
                        break
                except:
                    pass
                
                time.sleep(retry_delay)
            
            # Pobierz informacje o serwisie
            service_info = {
                "success": True,
                "container_id": self.container_id,
                "image_name": image_name,
                "service_port": self.service_port,
                "service_url": self.service_url,
                "name": name,
                "description": description,
                "version": version,
                "sandbox_id": self.sandbox_id
            }
            
            # Zapisz informacje o serwisie
            with open(self.sandbox_dir / "service_info.json", "w") as f:
                json.dump(service_info, f, indent=2)
            
            return service_info
        
        except Exception as e:
            logger.error(f"Błąd podczas budowania i uruchamiania serwisu: {e}")
            return {
                "success": False,
                "error": f"Błąd podczas budowania i uruchamiania serwisu: {str(e)}"
            }

    def stop(self) -> Dict[str, Any]:
        """
        Zatrzymuje serwis

        Returns:
            Dict: Wynik zatrzymania serwisu
        """
        if not self.container_id:
            return {
                "success": False,
                "error": "Kontener nie został uruchomiony"
            }
        
        try:
            # Zatrzymaj kontener
            logger.info(f"Zatrzymywanie kontenera Docker: {self.container_id}")
            stop_cmd = ["docker", "stop", self.container_id]
            
            stop_process = subprocess.Popen(
                stop_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stop_stdout, stop_stderr = stop_process.communicate()
            
            if stop_process.returncode != 0:
                logger.error(f"Błąd podczas zatrzymywania kontenera Docker: {stop_stderr}")
                return {
                    "success": False,
                    "error": f"Błąd podczas zatrzymywania kontenera Docker: {stop_stderr}"
                }
            
            # Usuń kontener
            logger.info(f"Usuwanie kontenera Docker: {self.container_id}")
            rm_cmd = ["docker", "rm", self.container_id]
            
            rm_process = subprocess.Popen(
                rm_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            rm_stdout, rm_stderr = rm_process.communicate()
            
            if rm_process.returncode != 0:
                logger.warning(f"Błąd podczas usuwania kontenera Docker: {rm_stderr}")
            
            # Usuń obraz
            image_name = f"evopy-service-image-{self.sandbox_id}"
            logger.info(f"Usuwanie obrazu Docker: {image_name}")
            rmi_cmd = ["docker", "rmi", image_name]
            
            rmi_process = subprocess.Popen(
                rmi_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            rmi_stdout, rmi_stderr = rmi_process.communicate()
            
            if rmi_process.returncode != 0:
                logger.warning(f"Błąd podczas usuwania obrazu Docker: {rmi_stderr}")
            
            return {
                "success": True,
                "message": f"Serwis zatrzymany pomyślnie"
            }
        
        except Exception as e:
            logger.error(f"Błąd podczas zatrzymywania serwisu: {e}")
            return {
                "success": False,
                "error": f"Błąd podczas zatrzymywania serwisu: {str(e)}"
            }

    def cleanup(self):
        """Czyści zasoby piaskownicy"""
        # Zatrzymaj serwis, jeśli jest uruchomiony
        if self.container_id:
            self.stop()
        
        try:
            # Usuń katalog piaskownicy
            shutil.rmtree(self.sandbox_dir, ignore_errors=True)
            logger.info(f"Wyczyszczono piaskownicę: {self.sandbox_id}")
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia piaskownicy: {e}")

    def get_service_info(self) -> Dict[str, Any]:
        """
        Pobiera informacje o serwisie

        Returns:
            Dict: Informacje o serwisie
        """
        info_file = self.sandbox_dir / "service_info.json"
        
        if not info_file.exists():
            return {
                "success": False,
                "error": "Informacje o serwisie nie są dostępne"
            }
        
        try:
            with open(info_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Błąd podczas pobierania informacji o serwisie: {e}")
            return {
                "success": False,
                "error": f"Błąd podczas pobierania informacji o serwisie: {str(e)}"
            }

    def get_logs(self) -> Dict[str, Any]:
        """
        Pobiera logi serwisu

        Returns:
            Dict: Logi serwisu
        """
        if not self.container_id:
            return {
                "success": False,
                "error": "Kontener nie został uruchomiony"
            }
        
        try:
            # Pobierz logi kontenera
            logger.info(f"Pobieranie logów kontenera Docker: {self.container_id}")
            logs_cmd = ["docker", "logs", self.container_id]
            
            logs_process = subprocess.Popen(
                logs_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logs_stdout, logs_stderr = logs_process.communicate()
            
            if logs_process.returncode != 0:
                logger.error(f"Błąd podczas pobierania logów kontenera Docker: {logs_stderr}")
                return {
                    "success": False,
                    "error": f"Błąd podczas pobierania logów kontenera Docker: {logs_stderr}"
                }
            
            return {
                "success": True,
                "logs": logs_stdout
            }
        
        except Exception as e:
            logger.error(f"Błąd podczas pobierania logów serwisu: {e}")
            return {
                "success": False,
                "error": f"Błąd podczas pobierania logów serwisu: {str(e)}"
            }

    def get_api_docs(self) -> Dict[str, Any]:
        """
        Pobiera dokumentację API serwisu

        Returns:
            Dict: Dokumentacja API
        """
        if not self.container_id:
            return {
                "success": False,
                "error": "Kontener nie został uruchomiony"
            }
        
        try:
            # Pobierz dokumentację API
            logger.info(f"Pobieranie dokumentacji API serwisu")
            api_cmd = [
                "docker", "exec", self.container_id,
                "curl", "-s", f"http://localhost:{self.service_port}/api/info"
            ]
            
            api_process = subprocess.Popen(
                api_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            api_stdout, api_stderr = api_process.communicate()
            
            if api_process.returncode != 0:
                logger.error(f"Błąd podczas pobierania dokumentacji API: {api_stderr}")
                return {
                    "success": False,
                    "error": f"Błąd podczas pobierania dokumentacji API: {api_stderr}"
                }
            
            try:
                api_docs = json.loads(api_stdout)
                return {
                    "success": True,
                    "api_docs": api_docs
                }
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Nieprawidłowy format dokumentacji API",
                    "raw_output": api_stdout
                }
        
        except Exception as e:
            logger.error(f"Błąd podczas pobierania dokumentacji API serwisu: {e}")
            return {
                "success": False,
                "error": f"Błąd podczas pobierania dokumentacji API serwisu: {str(e)}"
            }


# Przykład użycia
if __name__ == "__main__":
    # Katalog bazowy dla piaskownic
    base_dir = Path("/tmp/evopy-services")
    
    # Przykładowy kod serwisu
    service_code = """
# Przykładowy endpoint API
@api_endpoint("/api/hello", methods=["GET"], description="Zwraca powitanie")
def hello(name="Świat"):
    return {"message": f"Witaj, {name}!"}

# Przykładowy endpoint API z metodą POST
@api_endpoint("/api/echo", methods=["POST"], description="Zwraca przesłane dane")
def echo(text):
    return {"echo": text}
"""
    
    # Utwórz piaskownicę serwisu
    sandbox = ServiceSandbox(base_dir)
    
    # Uruchom serwis
    result = sandbox.build_and_run(
        service_code,
        name="Przykładowy Serwis",
        description="Demonstracja możliwości piaskownicy serwisu",
        version="1.0.0"
    )
    
    print(json.dumps(result, indent=2))
    
    # Poczekaj na interakcję użytkownika
    input("Naciśnij Enter, aby zatrzymać serwis...")
    
    # Zatrzymaj serwis
    sandbox.stop()
    
    # Wyczyść piaskownicę
    sandbox.cleanup()
