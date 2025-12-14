#!/bin/bash
# Kollect-It Desktop App Launcher for macOS/Linux
# Run: chmod +x start_app.sh && ./start_app.sh

echo "============================================="
echo "   Kollect-It Product Automation System"
echo "============================================="
echo

# Change to script directory
cd "$(dirname "$0")"

# Check for virtual environment in parent directory
if [ -f "../.venv/bin/python" ]; then
    echo "Using virtual environment..."
    ../.venv/bin/python main.py
    exit 0
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9+ from https://python.org"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python version: $PYTHON_VERSION"

# Check if dependencies are installed
if ! python3 -c "import PyQt5" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install dependencies"
        exit 1
    fi
fi

# Launch the application
echo "Starting Kollect-It Desktop App..."
python3 main.py
