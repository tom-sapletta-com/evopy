---
layout: default
title: Evopy Documentation
---

# Evopy Documentation

Evopy to kompleksowy, ale minimalny system asystenta, który jest w stanie ewoluować z prostego skryptu konsolowego do pełnego środowiska z wieloma piaskownicami Docker. Asystent wspiera konwersję tekstu na kod Python i zarządzanie projektami w kontenerach Docker.

## System Architecture

```mermaid
graph TD
    A[User] -->|Input| B(Evopy Core)
    B --> C{Processing Type}
    C -->|Code Generation| D[LLM Model]
    C -->|Code Execution| E[Sandbox]
    D --> F[Generated Code]
    F --> E
    E --> G[Execution Results]
    G --> B
    B --> H[Report Generator]
    H --> I[HTML/Markdown Reports]
    
    subgraph "Cross-Platform Support"
    J[Linux/Fedora]
    K[Windows]
    L[macOS]
    end
    
    E --- J
    E --- K
    E --- L
```

## Cross-Platform Support

Evopy now works seamlessly across different operating systems:

### Linux (including Fedora)
- Full support for all features
- Automatic dependency management
- Docker integration
- Shell script automation

### Windows 11
- PowerShell and batch file support
- Windows-specific path handling
- Docker Desktop integration
- Automatic dependency repair

### macOS
- Compatible with macOS environments
- Terminal integration
- Docker for Mac support

## Documentation Sections

- [Testing Guide](TESTING.md)
- [Sandbox Architecture](sandbox_architecture.md)
- [Mermaid Diagram Test](mermaid_test.md)

## Installation

### Cross-Platform Installation

```bash
# On Linux/macOS
python install.py

# On Windows (PowerShell)
python install.py
```

### Fedora-Specific Installation

```bash
sudo ./setup_fedora.sh
```

### Windows-Specific Installation

```powershell
# Using PowerShell
.\evopy.ps1 --install
```

## Usage

```bash
# Run tests for a specific model
./evopy.py test --model=llama3

# Generate a comparison report
./evopy.py report --all

# Clean intermediate files
./evopy.py cleanup
```

## Sandbox Usage

```bash
# Execute code in private sandbox
./sandbox_cli.py my_script.py

# Execute code with network access
./sandbox_cli.py --public my_script.py
```
