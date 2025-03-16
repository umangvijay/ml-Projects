#!/bin/bash

echo "Installing Speech and Image to PDF Converter..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    echo "You can download Python from https://www.python.org/downloads/"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Detected Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

# Remind about Tesseract OCR
echo
echo "IMPORTANT: You need to install Tesseract OCR for image text extraction."
echo "On Ubuntu/Debian: sudo apt install tesseract-ocr"
echo "On macOS: brew install tesseract"
echo

# Remind about FFmpeg
echo "IMPORTANT: You need to install FFmpeg for audio processing."
echo "On Ubuntu/Debian: sudo apt install ffmpeg"
echo "On macOS: brew install ffmpeg"
echo

echo "Installation completed successfully!"
echo
echo "To use the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python src/main.py --help"
echo

# Make the script executable
chmod +x install_unix.sh 