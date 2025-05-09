---
layout: default
title: Architektura Sandbox
---


<!-- MENU_START -->
<div class="navigation-menu">
  <ul>
    <li><a href="index.md">📚 Główna dokumentacja</a></li>
    <li><a href="reports/index.md">📊 Raporty testów</a></li>
    <li><a href="TESTING.md">🧪 Instrukcja testowania</a></li>
    <li class="current"><a href="sandbox_architecture.md">🏗️ Architektura piaskownic</a></li>
    <li><a href="junior_programmer_skills.md">💻 Umiejętności programistyczne</a></li>
    <li><a href="project_guidelines.md">📝 Wytyczne projektu</a></li>
    <li><a href="cross_platform.md">🖥️ Wsparcie cross-platform</a></li>
    <li><a href="mermaid_test.md">📊 Testy diagramów Mermaid</a></li>
  </ul>
</div>
<!-- MENU_END -->
# Architektura Sandbox w Evopy

## Przegląd

Evopy implementuje dwa rodzaje środowisk sandbox:

1. **Private Sandbox** - Dla wewnętrznych usług systemu
2. **Public Sandbox** - Dla projektów zleconych przez użytkownika

Ta architektura pozwala na bezpieczne uruchamianie kodu, izolację zasobów i efektywne zarządzanie usługami.

## Private Sandbox

### Cel

Private Sandbox służy do uruchamiania wewnętrznych usług systemu, które implementują różne umiejętności programistyczne. Te usługi są wykorzystywane przez system do realizacji zadań użytkownika.

### Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                       Evopy Core                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Private Sandbox Manager                   │
└───────┬───────────┬───────────┬───────────┬────────────┬────┘
        │           │           │           │            │
        ▼           ▼           ▼           ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Service 1 │ │ Service 2 │ │ Service 3 │ │ Service 4 │ │ Service N │
│ Container │ │ Container │ │ Container │ │ Container │ │ Container │
└───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### Komponenty

1. **Private Sandbox Manager**
   - Zarządza cyklem życia usług
   - Monitoruje zasoby
   - Zapewnia komunikację między usługami
   - Implementuje mechanizmy bezpieczeństwa

2. **Service Containers**
   - Każda usługa działa w oddzielnym kontenerze Docker
   - Implementują konkretne umiejętności programistyczne
   - Mają ograniczony dostęp do zasobów i sieci
   - Komunikują się przez standardowe API

### Implementacja

```python
class PrivateSandboxManager:
    """Zarządza piaskownicami dla wewnętrznych usług systemu"""
    
    def __init__(self, base_dir, config):
        self.base_dir = base_dir
        self.config = config
        self.services = {}
        self.running_services = {}
    
    def start_service(self, service_name):
        """Uruchamia usługę w piaskownicy"""
        # Implementacja uruchamiania kontenera Docker
        pass
    
    def stop_service(self, service_name):
        """Zatrzymuje usługę"""
        # Implementacja zatrzymywania kontenera Docker
        pass
    
    def call_service(self, service_name, method, params):
        """Wywołuje metodę usługi"""
        # Implementacja komunikacji z usługą
        pass
    
    def list_services(self):
        """Zwraca listę dostępnych usług"""
        # Implementacja listowania usług
        pass
```

## Public Sandbox

### Cel

Public Sandbox służy do uruchamiania projektów zleconych przez użytkownika. Te projekty są tworzone jako rezultat żądań użytkownika i mogą być bardziej złożone niż pojedyncze funkcje.

### Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                       Evopy Core                            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Public Sandbox Manager                    │
└───────┬───────────┬───────────┬───────────┬────────────┬────┘
        │           │           │           │            │
        ▼           ▼           ▼           ▼            ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Project 1 │ │ Project 2 │ │ Project 3 │ │ Project 4 │ │ Project N │
│ Container │ │ Container │ │ Container │ │ Container │ │ Container │
└───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘
```

### Komponenty

1. **Public Sandbox Manager**
   - Zarządza cyklem życia projektów
   - Monitoruje zasoby
   - Zapewnia dostęp do projektów dla użytkownika
   - Implementuje mechanizmy bezpieczeństwa

2. **Project Containers**
   - Każdy projekt działa w oddzielnym kontenerze Docker
   - Zawierają kod wygenerowany na podstawie żądań użytkownika
   - Mają ograniczony dostęp do zasobów i sieci
   - Mogą być udostępniane użytkownikowi

### Implementacja

```python
class PublicSandboxManager:
    """Zarządza piaskownicami dla projektów użytkownika"""
    
    def __init__(self, base_dir, config):
        self.base_dir = base_dir
        self.config = config
        self.projects = {}
        self.running_projects = {}
    
    def create_project(self, project_name, description):
        """Tworzy nowy projekt"""
        # Implementacja tworzenia projektu
        pass
    
    def build_project(self, project_name, code):
        """Buduje projekt na podstawie kodu"""
        # Implementacja budowania projektu
        pass
    
    def start_project(self, project_name):
        """Uruchamia projekt w piaskownicy"""
        # Implementacja uruchamiania kontenera Docker
        pass
    
    def stop_project(self, project_name):
        """Zatrzymuje projekt"""
        # Implementacja zatrzymywania kontenera Docker
        pass
    
    def list_projects(self):
        """Zwraca listę dostępnych projektów"""
        # Implementacja listowania projektów
        pass
```

## Integracja z Evopy Core

### Przepływ pracy

1. Użytkownik formułuje żądanie w języku naturalnym
2. Evopy Core konwertuje żądanie na kod Python
3. Evopy Core identyfikuje potrzebne usługi z Private Sandbox
4. Evopy Core uruchamia kod w odpowiednim środowisku:
   - Jeśli to proste zadanie, używa Private Sandbox
   - Jeśli to złożony projekt, tworzy nowy projekt w Public Sandbox
5. Evopy Core zwraca wynik i wyjaśnienie do użytkownika
6. Użytkownik potwierdza czy wynik spełnia jego oczekiwania

### Implementacja

```python
class SandboxIntegration:
    """Integruje Private i Public Sandbox z Evopy Core"""
    
    def __init__(self, config):
        self.config = config
        self.private_sandbox = PrivateSandboxManager(
            base_dir=Path(config["private_sandbox_dir"]),
            config=config["private_sandbox_config"]
        )
        self.public_sandbox = PublicSandboxManager(
            base_dir=Path(config["public_sandbox_dir"]),
            config=config["public_sandbox_config"]
        )
    
    def execute_code(self, code, context):
        """Wykonuje kod w odpowiednim środowisku"""
        if self._is_simple_task(code, context):
            return self._execute_in_private_sandbox(code, context)
        else:
            return self._execute_in_public_sandbox(code, context)
    
    def _is_simple_task(self, code, context):
        """Określa czy zadanie jest proste czy złożone"""
        # Implementacja heurystyki
        pass
    
    def _execute_in_private_sandbox(self, code, context):
        """Wykonuje kod w Private Sandbox"""
        # Identyfikacja potrzebnych usług
        services = self._identify_required_services(code, context)
        
        # Uruchomienie usług
        for service in services:
            self.private_sandbox.start_service(service)
        
        # Wykonanie kodu
        result = self._run_code_with_services(code, services)
        
        # Zatrzymanie usług
        for service in services:
            self.private_sandbox.stop_service(service)
        
        return result
    
    def _execute_in_public_sandbox(self, code, context):
        """Wykonuje kod w Public Sandbox"""
        # Utworzenie projektu
        project_name = f"project_{uuid.uuid4()}"
        self.public_sandbox.create_project(project_name, context["description"])
        
        # Budowanie projektu
        self.public_sandbox.build_project(project_name, code)
        
        # Uruchomienie projektu
        self.public_sandbox.start_project(project_name)
        
        # Pobranie wyniku
        result = self._get_project_result(project_name)
        
        # Zatrzymanie projektu (opcjonalnie)
        if not context.get("keep_running", False):
            self.public_sandbox.stop_project(project_name)
        
        return result
```

## Bezpieczeństwo

### Ograniczenia zasobów

- Limity CPU i pamięci dla każdego kontenera
- Limity czasu wykonania
- Limity przestrzeni dyskowej

### Izolacja sieciowa

- Brak dostępu do sieci zewnętrznej dla większości usług
- Kontrolowany dostęp do sieci dla wybranych usług
- Izolacja między kontenerami

### Monitorowanie

- Stałe monitorowanie zużycia zasobów
- Wykrywanie anomalii
- Automatyczne zatrzymywanie podejrzanych kontenerów

## Zarządzanie zasobami

### Automatyczne skalowanie

- Dynamiczne przydzielanie zasobów w zależności od obciążenia
- Automatyczne uruchamianie i zatrzymywanie usług
- Priorytetyzacja zadań

### Czyszczenie

- Automatyczne usuwanie nieużywanych kontenerów
- Cykliczne czyszczenie przestrzeni dyskowej
- Zarządzanie wersjami usług

## Wdrożenie

### Wymagania

- Docker Engine
- Docker Compose
- Python 3.8+
- Minimum 8GB RAM
- 50GB przestrzeni dyskowej

### Kroki wdrożenia

1. Instalacja zależności
2. Konfiguracja środowiska
3. Budowanie obrazów bazowych
4. Inicjalizacja Private Sandbox
5. Inicjalizacja Public Sandbox
6. Integracja z Evopy Core
7. Testowanie i walidacja
