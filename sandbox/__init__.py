"""
Evopy Sandbox Module
===================

This module provides sandbox functionality for Evopy, ensuring secure code execution
across different platforms (Linux, Windows, macOS).

The sandbox uses Docker to isolate code execution and provides:
- Resource limitations (CPU, memory, time)
- Network isolation
- Automatic dependency management
"""

from .cross_platform_sandbox import (
    DockerSandbox,
    SandboxManager,
    execute_code,
    sandbox_manager
)

__all__ = [
    'DockerSandbox',
    'SandboxManager',
    'execute_code',
    'sandbox_manager'
]
