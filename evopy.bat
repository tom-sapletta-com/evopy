@echo off
REM Evopy Windows Launcher
REM This batch file runs the cross-platform Evopy Python script on Windows

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the Python script with all arguments passed to this batch file
python "%~dp0evopy.py" %*

REM If there was an error, pause to show the message
if %ERRORLEVEL% neq 0 (
    echo.
    echo An error occurred while running Evopy.
    pause
)
