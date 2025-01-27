@echo off
setlocal enabledelayedexpansion

:: Check Python version
python -c "import sys; assert sys.version_info >= (3,8)" 2>nul
if errorlevel 1 (
    echo Error: Python 3.8 or higher is required
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Error: Could not find virtual environment activation script
    exit /b 1
)

:: Install requirements
echo Installing requirements...
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Run the app if --run flag is provided
if "%1"=="--run" (
    echo Starting Rhystic.io server...
    python -m server.api
) else (
    echo Setup complete! To run the server, use: setup.bat --run
)

endlocal 