#!/bin/bash

echo "Starting OCR to PDF Converter..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python is not installed or not in the PATH."
    echo "Please install Python 3.8 or higher from https://www.python.org/downloads/"
    echo
    read -p "Press Enter to exit..."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment and installing requirements..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install requirements."
        read -p "Press Enter to exit..."
        exit 1
    fi
else
    source venv/bin/activate
fi

# Run the application
python3 gui_app.py
if [ $? -ne 0 ]; then
    echo "Application exited with an error."
    read -p "Press Enter to exit..."
fi

deactivate
exit 0 