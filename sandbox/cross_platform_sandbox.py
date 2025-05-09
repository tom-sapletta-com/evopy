#!/usr/bin/env python3
"""
Cross-Platform Sandbox for Evopy
================================

This module provides a cross-platform implementation of the Evopy sandbox architecture,
ensuring compatibility across Linux (including Fedora), Windows, and macOS.

It handles platform-specific differences in:
- Docker command execution
- Path handling
- Resource limitations
- Network isolation

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

import os
import sys
import json
import platform
import subprocess
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cross_platform_sandbox")

# Platform detection
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"
IS_FEDORA = IS_LINUX and os.path.exists("/etc/fedora-release")
IS_MACOS = platform.system() == "Darwin"

# Base directory
BASE_DIR = Path(__file__).parent.parent.absolute()

class DockerSandbox:
    """Cross-platform implementation of Docker sandbox for code execution."""
    
    def __init__(
        self,
        image: str = "python:3.9-slim",
        timeout: int = 30,
        memory_limit: str = "512m",
        cpu_limit: float = 1.0,
        network_enabled: bool = False,
        auto_remove: bool = True
    ):
        """
        Initialize the Docker sandbox with platform-specific settings.
        
        Args:
            image: Docker image to use
            timeout: Maximum execution time in seconds
            memory_limit: Memory limit for the container
            cpu_limit: CPU limit for the container
            network_enabled: Whether to enable network access
            auto_remove: Whether to automatically remove the container after execution
        """
        self.image = image
        self.timeout = timeout
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.network_enabled = network_enabled
        self.auto_remove = auto_remove
        
        # Check if Docker is available
        self._check_docker()
    
    def _check_docker(self) -> None:
        """Check if Docker is available and running."""
        try:
            docker_cmd = "docker.exe" if IS_WINDOWS else "docker"
            result = subprocess.run(
                [docker_cmd, "info"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.warning("Docker is not running or not accessible.")
                logger.warning(f"Error: {result.stderr}")
                
                if IS_WINDOWS:
                    logger.info("On Windows, make sure Docker Desktop is running.")
                elif IS_FEDORA:
                    logger.info("On Fedora, run: sudo systemctl start docker")
                elif IS_LINUX:
                    logger.info("On Linux, run: sudo systemctl start docker")
                elif IS_MACOS:
                    logger.info("On macOS, make sure Docker Desktop is running.")
        except FileNotFoundError:
            logger.error("Docker is not installed.")
            
            if IS_WINDOWS:
                logger.info("Install Docker Desktop from: https://www.docker.com/products/docker-desktop")
            elif IS_FEDORA:
                logger.info("Install Docker on Fedora: sudo dnf install docker-ce")
            elif IS_LINUX:
                logger.info("Install Docker on Linux: https://docs.docker.com/engine/install/")
            elif IS_MACOS:
                logger.info("Install Docker on macOS: https://docs.docker.com/desktop/install/mac-install/")
    
    def _prepare_docker_command(
        self,
        code: str,
        input_data: Optional[str] = None,
        working_dir: Optional[Path] = None
    ) -> Tuple[List[str], Path]:
        """
        Prepare the Docker command for execution.
        
        Args:
            code: Python code to execute
            input_data: Input data for the code
            working_dir: Working directory for the code
        
        Returns:
            Tuple of Docker command and temporary directory
        """
        # Create temporary directory for code and input
        temp_dir = Path(tempfile.mkdtemp())
        
        # Write code to file
        code_file = temp_dir / "code.py"
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        # Write input to file if provided
        if input_data:
            input_file = temp_dir / "input.txt"
            with open(input_file, "w", encoding="utf-8") as f:
                f.write(input_data)
        
        # Prepare Docker command
        docker_cmd = "docker.exe" if IS_WINDOWS else "docker"
        
        # Base command
        cmd = [
            docker_cmd, "run",
            "--rm" if self.auto_remove else "",
            f"--memory={self.memory_limit}",
            f"--cpus={self.cpu_limit}",
            f"--timeout={self.timeout}s",
            "--network=none" if not self.network_enabled else "",
        ]
        
        # Remove empty elements
        cmd = [c for c in cmd if c]
        
        # Mount volumes
        if IS_WINDOWS:
            # Windows paths need special handling
            mount_path = temp_dir.as_posix().replace("C:", "/c").replace("D:", "/d")
            cmd.extend(["-v", f"{mount_path}:/code"])
        else:
            # Unix paths
            cmd.extend(["-v", f"{temp_dir}:/code"])
        
        # Working directory
        cmd.extend(["-w", "/code"])
        
        # Image and command
        cmd.extend([self.image, "python", "/code/code.py"])
        
        # Input redirection if provided
        if input_data:
            cmd.extend(["<", "/code/input.txt"])
        
        return cmd, temp_dir
    
    def execute(
        self,
        code: str,
        input_data: Optional[str] = None,
        working_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Execute code in the Docker sandbox.
        
        Args:
            code: Python code to execute
            input_data: Input data for the code
            working_dir: Working directory for the code
        
        Returns:
            Dictionary with execution results
        """
        cmd, temp_dir = self._prepare_docker_command(code, input_data, working_dir)
        
        try:
            # Execute the command
            logger.info(f"Executing command: {' '.join(cmd)}")
            
            # Handle input redirection differently on Windows
            if IS_WINDOWS and input_data:
                # Windows doesn't handle < redirection well in subprocess
                # Remove the redirection from command
                cmd = [c for c in cmd if c != "<" and not c.startswith("/code/input.txt")]
                
                # Use shell=True and full command string with redirection
                cmd_str = " ".join(cmd) + " < " + str(temp_dir / "input.txt")
                process = subprocess.run(
                    cmd_str,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout
                )
            else:
                # Unix systems can use the command list directly
                process = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=self.timeout
                )
            
            # Prepare result
            result = {
                "stdout": process.stdout,
                "stderr": process.stderr,
                "exit_code": process.returncode,
                "timeout": False,
                "error": None
            }
            
        except subprocess.TimeoutExpired:
            result = {
                "stdout": "",
                "stderr": "Execution timed out",
                "exit_code": -1,
                "timeout": True,
                "error": "Timeout"
            }
        except Exception as e:
            result = {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "timeout": False,
                "error": str(e)
            }
        finally:
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
        
        return result

class SandboxManager:
    """
    Cross-platform manager for Evopy sandboxes.
    Handles both private and public sandboxes.
    """
    
    def __init__(self):
        """Initialize the sandbox manager."""
        self.private_sandbox = DockerSandbox(
            image="python:3.9-slim",
            network_enabled=False,
            memory_limit="512m"
        )
        
        self.public_sandbox = DockerSandbox(
            image="python:3.9-slim",
            network_enabled=True,
            memory_limit="1g"
        )
    
    def execute_in_private_sandbox(
        self,
        code: str,
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code in the private sandbox.
        
        Args:
            code: Python code to execute
            input_data: Input data for the code
        
        Returns:
            Dictionary with execution results
        """
        return self.private_sandbox.execute(code, input_data)
    
    def execute_in_public_sandbox(
        self,
        code: str,
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code in the public sandbox.
        
        Args:
            code: Python code to execute
            input_data: Input data for the code
        
        Returns:
            Dictionary with execution results
        """
        return self.public_sandbox.execute(code, input_data)
    
    def execute_with_dependency_repair(
        self,
        code: str,
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute code with automatic dependency repair.
        
        Args:
            code: Python code to execute
            input_data: Input data for the code
        
        Returns:
            Dictionary with execution results
        """
        # First try in private sandbox
        result = self.execute_in_private_sandbox(code, input_data)
        
        # Check if there are import errors
        if result["exit_code"] != 0 and "ModuleNotFoundError" in result["stderr"]:
            # Try to repair imports
            try:
                # Import dependency manager dynamically
                sys.path.append(str(BASE_DIR))
                from dependency_manager import repair_imports
                
                # Repair imports
                repaired_code = repair_imports(code)
                
                # Execute repaired code
                result = self.execute_in_private_sandbox(repaired_code, input_data)
                
                # Add repair info to result
                result["repaired"] = True
                result["original_code"] = code
                result["repaired_code"] = repaired_code
            except ImportError:
                logger.warning("Could not import dependency_manager module")
            except Exception as e:
                logger.error(f"Error repairing imports: {e}")
        
        return result

# Singleton instance
sandbox_manager = SandboxManager()

def execute_code(
    code: str,
    input_data: Optional[str] = None,
    sandbox_type: str = "private",
    auto_repair: bool = True
) -> Dict[str, Any]:
    """
    Execute code in the specified sandbox.
    
    Args:
        code: Python code to execute
        input_data: Input data for the code
        sandbox_type: Type of sandbox to use ("private" or "public")
        auto_repair: Whether to automatically repair dependencies
    
    Returns:
        Dictionary with execution results
    """
    if auto_repair:
        return sandbox_manager.execute_with_dependency_repair(code, input_data)
    
    if sandbox_type == "public":
        return sandbox_manager.execute_in_public_sandbox(code, input_data)
    else:
        return sandbox_manager.execute_in_private_sandbox(code, input_data)

# Example usage
if __name__ == "__main__":
    # Example code
    example_code = """
import time
import os

print(f"Platform: {os.name}")
print(f"Current time: {time.time()}")
print(f"Current directory: {os.getcwd()}")

# Try to access network
try:
    import urllib.request
    response = urllib.request.urlopen("https://www.google.com")
    print(f"Network access: Success ({response.status})")
except Exception as e:
    print(f"Network access: Failed ({str(e)})")
"""
    
    # Execute in private sandbox
    print("=== Executing in private sandbox ===")
    result = execute_code(example_code, sandbox_type="private")
    print(f"Exit code: {result['exit_code']}")
    print(f"Output:\n{result['stdout']}")
    if result['stderr']:
        print(f"Error:\n{result['stderr']}")
    
    # Execute in public sandbox
    print("\n=== Executing in public sandbox ===")
    result = execute_code(example_code, sandbox_type="public")
    print(f"Exit code: {result['exit_code']}")
    print(f"Output:\n{result['stdout']}")
    if result['stderr']:
        print(f"Error:\n{result['stderr']}")
