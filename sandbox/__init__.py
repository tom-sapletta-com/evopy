"""
Evopy Sandbox Module
===================

This module provides sandbox functionality for Evopy, ensuring secure code execution
across different platforms (Linux, Windows, macOS).

The sandbox uses Docker to isolate code execution and provides:
- Resource limitations (CPU, memory, time)
- Network isolation
- Automatic dependency management

Copyright 2025 Tom Sapletta

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
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
