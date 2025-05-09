@echo off
:: Run script for Evopy Assistant on Windows

set SCRIPT_DIR=%~dp0
set VENV_DIR=%SCRIPT_DIR%.venv

:: Activate virtual environment
if exist "%VENV_DIR%\Scripts\activate.bat" (
    call "%VENV_DIR%\Scripts\activate.bat"
    set PYTHON_CMD=python
) else (
    :: Choose available Python command
    where python > nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set PYTHON_CMD=python
    ) else (
        where python3 > nul 2>&1
        if %ERRORLEVEL% equ 0 (
            set PYTHON_CMD=python3
        ) else (
            echo Python not found. Please install Python 3.8 or newer.
            exit /b 1
        )
    )
)

:: Run assistant
%PYTHON_CMD% "%SCRIPT_DIR%evo.py" %*
