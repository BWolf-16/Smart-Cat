@echo off
echo Smart Cat AI Assistant - Install from Repository
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.6+ and try again
    pause
    exit /b 1
)

echo Installing Smart Cat AI Assistant from GitHub repository...
echo.

REM Create temporary setup script if not available locally
if not exist setup.py (
    echo Downloading setup script...
    curl -o setup.py https://raw.githubusercontent.com/BWolf-16/Smart-Cat/main/setup.py
)

REM Run the installation
python setup.py install-repo

echo.
echo Installation completed!
echo Please restart KiCad to use the Smart Cat AI Assistant.
echo.
pause
