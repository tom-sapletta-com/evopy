# Wsparcie Cross-Platform dla Evopy

## Wprowadzenie

Evopy został zaprojektowany z myślą o działaniu na różnych systemach operacyjnych, zapewniając spójne doświadczenie niezależnie od platformy. Ten dokument zawiera informacje o wsparciu cross-platform oraz instrukcje instalacji i uruchamiania Evopy na różnych systemach operacyjnych.

## Wspierane Systemy Operacyjne

Evopy oficjalnie wspiera następujące systemy operacyjne:

| System Operacyjny | Wersja | Status wsparcia |
|-------------------|--------|-----------------|
| Linux             | Ubuntu 20.04+ | Pełne wsparcie |
| Linux             | Debian 10+ | Pełne wsparcie |
| Linux             | Inne dystrybucje | Powinno działać, ale nie jest oficjalnie testowane |
| Windows           | 10/11 | Wsparcie przez WSL lub natywnie z pewnymi ograniczeniami |
| macOS             | 10.15+ (Catalina) | Podstawowe wsparcie |

## Wymagania Systemowe

Minimalne wymagania systemowe dla Evopy:

- Python 3.8 lub nowszy
- 4GB RAM (zalecane 8GB dla większych zadań)
- 2GB wolnego miejsca na dysku
- Dostęp do internetu (dla niektórych funkcji)

## Instalacja na Różnych Platformach

### Linux

Na systemach Linux, instalacja Evopy jest najprostsza i w pełni wspierana:

```bash
# Sklonuj repozytorium
git clone https://github.com/tom-sapletta-com/evopy.git
cd evopy

# Utwórz i aktywuj wirtualne środowisko
python -m venv .venv
source .venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom Evopy
python evo.py
```

### Windows

Na systemie Windows zalecamy korzystanie z Windows Subsystem for Linux (WSL):

1. Zainstaluj WSL zgodnie z [oficjalną dokumentacją Microsoft](https://docs.microsoft.com/en-us/windows/wsl/install)
2. Zainstaluj dystrybucję Ubuntu z Microsoft Store
3. Uruchom terminal Ubuntu i wykonaj kroki instalacji dla Linuxa

Alternatywnie, można zainstalować Evopy natywnie na Windows:

```powershell
# Sklonuj repozytorium
git clone https://github.com/tom-sapletta-com/evopy.git
cd evopy

# Utwórz i aktywuj wirtualne środowisko
python -m venv .venv
.\.venv\Scripts\activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom Evopy
python evo.py
```

**Uwaga**: Niektóre funkcje związane z Docker mogą nie działać poprawnie na natywnej instalacji Windows. Zalecamy korzystanie z WSL dla pełnej funkcjonalności.

### macOS

Instalacja na macOS:

```bash
# Sklonuj repozytorium
git clone https://github.com/tom-sapletta-com/evopy.git
cd evopy

# Utwórz i aktywuj wirtualne środowisko
python -m venv .venv
source .venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom Evopy
python evo.py
```

**Uwaga**: Na macOS mogą wystąpić problemy z niektórymi zależnościami. W przypadku problemów, sprawdź sekcję rozwiązywania problemów.

## Uruchamianie Skryptów

### Linux i macOS

Na systemach Unix-podobnych (Linux, macOS), skrypty można uruchamiać bezpośrednio:

```bash
# Upewnij się, że skrypt ma uprawnienia do wykonania
chmod +x run.sh

# Uruchom skrypt
./run.sh
```

### Windows

Na Windows, skrypty powłoki można uruchamiać za pomocą PowerShell lub WSL:

```powershell
# PowerShell
python run.py

# Lub za pomocą WSL (zalecane)
wsl ./run.sh
```

## Piaskownica Docker

Evopy wykorzystuje Docker do uruchamiania kodu w bezpiecznym środowisku. Aby korzystać z tej funkcji:

1. Zainstaluj Docker na swoim systemie:
   - [Docker dla Linux](https://docs.docker.com/engine/install/)
   - [Docker Desktop dla Windows](https://docs.docker.com/desktop/install/windows-install/)
   - [Docker Desktop dla macOS](https://docs.docker.com/desktop/install/mac-install/)

2. Upewnij się, że Docker jest uruchomiony przed korzystaniem z funkcji piaskownicy.

3. Na Windows, jeśli korzystasz z natywnej instalacji (nie WSL), może być konieczne dostosowanie ścieżek w konfiguracji.

## Znane Problemy i Rozwiązania

### Windows

- **Problem**: Błąd SyntaxError przy uruchamianiu skryptów shell.
  **Rozwiązanie**: Używaj WSL do uruchamiania skryptów shell lub konwertuj je na skrypty PowerShell.

- **Problem**: Problemy z Docker na natywnym Windows.
  **Rozwiązanie**: Zainstaluj Docker Desktop i upewnij się, że integracja WSL jest włączona.

### macOS

- **Problem**: Problemy z zależnościami na nowszych wersjach macOS.
  **Rozwiązanie**: Zainstaluj wymagane biblioteki za pomocą Homebrew:
  ```bash
  brew install python@3.9 openssl readline sqlite3 xz zlib
  ```

### Linux

- **Problem**: Brak uprawnień do uruchamiania Docker.
  **Rozwiązanie**: Dodaj swojego użytkownika do grupy docker:
  ```bash
  sudo usermod -aG docker $USER
  newgrp docker
  ```

## Wsparcie dla Różnych Wersji Pythona

Evopy jest testowany głównie na Python 3.8-3.10, ale powinien działać również na nowszych wersjach. W przypadku problemów z konkretną wersją Pythona, zalecamy użycie Python 3.9, który jest najbardziej stabilną wersją dla tego projektu.

## Kontakt i Zgłaszanie Problemów

Jeśli napotkasz problemy związane z konkretną platformą, zgłoś je w sekcji Issues na GitHubie:
https://github.com/tom-sapletta-com/evopy/issues

Proszę dołącz następujące informacje:
- System operacyjny i jego wersja
- Wersja Pythona
- Pełny komunikat błędu
- Kroki do odtworzenia problemu

## Przyszłe Plany Wsparcia Cross-Platform

W przyszłych wersjach planujemy:
- Dodanie instalatorów dla poszczególnych platform
- Lepsze wsparcie dla natywnego Windows
- Rozszerzone wsparcie dla macOS
- Wersja webowa dostępna przez przeglądarkę
