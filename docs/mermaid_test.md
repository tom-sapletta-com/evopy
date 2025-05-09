---
layout: default
title: Mermaid Diagram Test
---

# Mermaid Diagram Test

This page demonstrates that Mermaid diagrams are properly rendering on the GitHub Pages site.

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

## Workflow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Evopy
    participant LLM
    participant Sandbox
    
    User->>Evopy: Request code generation
    Evopy->>LLM: Send prompt
    LLM-->>Evopy: Return generated code
    Evopy->>Sandbox: Execute code
    Sandbox-->>Evopy: Return execution results
    Evopy->>User: Display results
    
    Note over Evopy,Sandbox: Cross-platform execution
```

## Component Relationships

```mermaid
classDiagram
    class EvopyCore {
        +run_tests()
        +generate_report()
        +cleanup()
    }
    
    class SandboxManager {
        +execute_in_private_sandbox()
        +execute_in_public_sandbox()
        +execute_with_dependency_repair()
    }
    
    class DockerSandbox {
        -image: string
        -timeout: int
        -memory_limit: string
        +execute(code, input_data)
    }
    
    class ReportGenerator {
        +generate_markdown_report()
        +generate_html_report()
        +generate_pdf_report()
    }
    
    EvopyCore --> SandboxManager: uses
    EvopyCore --> ReportGenerator: uses
    SandboxManager --> DockerSandbox: manages
