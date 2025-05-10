# Narzędzia Docker

Ten katalog zawiera skrypty i narzędzia związane z konteneryzacją i piaskownicą Docker używane w projekcie Evopy.

## Dostępne narzędzia

- `docker_sandbox.py` - Główny moduł piaskownicy Docker do bezpiecznego wykonywania kodu
- `docker_task_register.py` - Rejestracja zadań Docker
- `test_docker_sandbox.py` - Testy dla piaskownicy Docker
- `test_docker_integration.py` - Testy integracyjne dla Dockera
- `docker-compose.yml` - Konfiguracja usług Docker Compose

## Przeznaczenie

Narzędzia w tym katalogu służą do:

1. Uruchamiania izolowanych środowisk Docker do bezpiecznego wykonywania kodu
2. Zarządzania kontenerami Docker używanymi przez projekt Evopy
3. Konfiguracji i monitorowania usług uruchamianych w kontenerach

## Użycie

```python
from tools.docker.docker_sandbox import DockerSandbox

# Tworzenie instancji piaskownicy
sandbox = DockerSandbox()

# Uruchamianie kodu w piaskownicy
result = sandbox.run("print('Hello from Docker!')")
print(result)
```
