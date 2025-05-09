@echo off
REM Evopy Sandbox CLI for Windows
REM This batch file runs the cross-platform sandbox CLI on Windows

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Docker is not installed or not in PATH.
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Run the Python script with all arguments passed to this batch file
python "%~dp0sandbox_cli.py" %*

REM If there was an error, pause to show the message
if %ERRORLEVEL% neq 0 (
    echo.
    echo An error occurred while running the sandbox.
    pause
)
