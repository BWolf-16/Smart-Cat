#!/bin/bash

echo "Smart Cat AI Assistant - Install from Repository"
echo "================================================"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.6+ and try again"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

echo "Installing Smart Cat AI Assistant from GitHub repository..."
echo

# Check if setup.py exists locally, if not download it
if [ ! -f "setup.py" ]; then
    echo "Downloading setup script..."
    curl -o setup.py https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/setup.py
fi

# Run the installation
$PYTHON_CMD setup.py install-repo

echo
echo "Installation completed!"
echo "Please restart KiCad to use the Smart Cat AI Assistant."
echo

# Wait for user input on macOS/Linux
read -p "Press Enter to continue..."
