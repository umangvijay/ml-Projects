@echo off
echo Installing Speech and Image to PDF Converter...

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.8 or higher.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Detected Python version: %PYTHON_VERSION%

:: Create virtual environment
echo Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo Installing dependencies...
pip install -e .
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

:: Remind about Tesseract OCR
echo.
echo IMPORTANT: You need to install Tesseract OCR for image text extraction.
echo Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
echo.

:: Remind about FFmpeg
echo IMPORTANT: You need to install FFmpeg for audio processing.
echo Download and install from: https://ffmpeg.org/download.html
echo.

echo Installation completed successfully!
echo.
echo To use the application:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Run the application: python src\main.py --help
echo.

pause 