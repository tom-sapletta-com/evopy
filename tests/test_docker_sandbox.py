#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Testy dla modułu DockerSandbox
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Dodaj katalog główny projektu do ścieżki Pythona
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importuj moduł DockerSandbox
from docker_sandbox import DockerSandbox

class TestDockerSandbox:
    """Testy dla klasy DockerSandbox"""
    
    @pytest.fixture
    def sandbox(self):
        """Tworzy instancję DockerSandbox do testów"""
        # Użyj katalogu tymczasowego dla testów
        base_dir = Path(os.path.dirname(__file__)) / "test_data" / "sandbox"
        os.makedirs(base_dir, exist_ok=True)
        
        # Utwórz instancję DockerSandbox z zamockowanymi metodami
        with patch('docker_sandbox.subprocess.run'), \
             patch('docker_sandbox.subprocess.Popen'):
            sandbox = DockerSandbox(
                base_dir=base_dir,
                docker_image="python:3.9-slim",
                timeout=10
            )
            yield sandbox
    
    def test_initialization(self, sandbox):
        """Test inicjalizacji DockerSandbox"""
        assert sandbox is not None
        assert sandbox.docker_image == "python:3.9-slim"
        assert sandbox.timeout == 10
        assert sandbox.base_dir.exists()
    
    def test_create_container(self, sandbox):
        """Test tworzenia kontenera Docker"""
        with patch('docker_sandbox.subprocess.run') as mock_run:
            # Mockuj wynik polecenia docker create
            mock_process = MagicMock()
            mock_process.stdout = b"container_id\n"
            mock_process.returncode = 0
            mock_run.return_value = mock_process
            
            container_id = sandbox._create_container()
            assert container_id == "container_id"
            
            # Sprawdź czy wywołano docker create z odpowiednimi parametrami
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "docker" in args
            assert "create" in args
            assert "--rm" in args
            assert "-v" in args  # Sprawdź czy użyto montowania woluminu
    
    def test_run_successful_code(self, sandbox):
        """Test uruchamiania poprawnego kodu"""
        with patch.object(sandbox, '_create_container', return_value="container_id"), \
             patch.object(sandbox, '_start_container'), \
             patch.object(sandbox, '_wait_for_container'), \
             patch.object(sandbox, '_get_container_logs', return_value="Hello, World!"), \
             patch.object(sandbox, '_remove_container'), \
             patch('docker_sandbox.time.time', side_effect=[0, 1]):  # Symuluj 1 sekundę wykonania
            
            code = "print('Hello, World!')"
            result = sandbox.run(code)
            
            assert result["success"] is True
            assert result["output"] == "Hello, World!"
            assert result["error"] == ""
            assert result["execution_time"] == 1.0
    
    def test_run_code_with_error(self, sandbox):
        """Test uruchamiania kodu z błędem"""
        with patch.object(sandbox, '_create_container', return_value="container_id"), \
             patch.object(sandbox, '_start_container'), \
             patch.object(sandbox, '_wait_for_container', return_value=1),  # Kod błędu
             patch.object(sandbox, '_get_container_logs', return_value=""), \
             patch.object(sandbox, '_get_container_stderr', return_value="NameError: name 'undefined_variable' is not defined"), \
             patch.object(sandbox, '_remove_container'), \
             patch('docker_sandbox.time.time', side_effect=[0, 1]):  # Symuluj 1 sekundę wykonania
            
            code = "print(undefined_variable)"
            result = sandbox.run(code)
            
            assert result["success"] is False
            assert result["output"] == ""
            assert "NameError" in result["error"]
            assert result["execution_time"] == 1.0
    
    def test_run_code_with_timeout(self, sandbox):
        """Test uruchamiania kodu z przekroczeniem czasu"""
        with patch.object(sandbox, '_create_container', return_value="container_id"), \
             patch.object(sandbox, '_start_container'), \
             patch.object(sandbox, '_wait_for_container', side_effect=TimeoutError("Timeout")), \
             patch.object(sandbox, '_kill_container'), \
             patch.object(sandbox, '_remove_container'), \
             patch('docker_sandbox.time.time', side_effect=[0, sandbox.timeout + 1]):
            
            code = "import time; time.sleep(100)"  # Kod, który będzie działał zbyt długo
            result = sandbox.run(code)
            
            assert result["success"] is False
            assert "Timeout" in result["error"]
            assert result["execution_time"] >= sandbox.timeout
    
    def test_cleanup(self, sandbox):
        """Test czyszczenia po wykonaniu kodu"""
        with patch.object(sandbox, '_remove_container') as mock_remove:
            sandbox.container_id = "container_id"
            sandbox.cleanup()
            
            # Sprawdź czy wywołano usunięcie kontenera
            mock_remove.assert_called_once_with("container_id")
            assert sandbox.container_id is None
    
    def test_dependency_auto_repair(self, sandbox):
        """Test automatycznej naprawy zależności"""
        # Ten test sprawdza funkcjonalność auto-naprawy zależności
        with patch.object(sandbox, '_create_container', return_value="container_id"), \
             patch.object(sandbox, '_start_container'), \
             patch.object(sandbox, '_wait_for_container', side_effect=[1, 0]),  # Najpierw błąd, potem sukces
             patch.object(sandbox, '_get_container_logs', return_value="Success"), \
             patch.object(sandbox, '_get_container_stderr', return_value="NameError: name 'time' is not defined"), \
             patch.object(sandbox, '_remove_container'), \
             patch('docker_sandbox.time.time', side_effect=[0, 0.5, 0.5, 1]):
            
            # Kod bez importu time
            code = "print(time.time())"
            
            # Mockuj dependency_manager
            with patch('docker_sandbox.dependency_manager.analyze_and_fix_imports', 
                      return_value="import time\nprint(time.time())"):
                result = sandbox.run(code)
                
                assert result["success"] is True
                assert result["output"] == "Success"
                assert result["error"] == ""
                assert result["execution_time"] == 0.5  # Tylko czas drugiego uruchomienia
