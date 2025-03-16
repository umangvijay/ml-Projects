@echo off
echo Starting OCR to PDF Converter...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if requirements are installed
if not exist venv (
    echo Creating virtual environment and installing requirements...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed to install requirements.
        pause
        exit /b 1
    )
) else (
    call venv\Scripts\activate
)

REM Run the application
python gui_app.py
if %errorlevel% neq 0 (
    echo Application exited with an error.
    pause
)

deactivate
exit /b 0 