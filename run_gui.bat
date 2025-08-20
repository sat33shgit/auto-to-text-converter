@echo off
REM Windows batch file to run the Audio to Text Converter GUI

echo Starting Audio to Text Converter...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if the GUI script exists
if not exist "audio_to_text_gui.py" (
    echo Error: audio_to_text_gui.py not found
    echo Make sure you're running this from the correct directory
    pause
    exit /b 1
)

REM Run the GUI application
echo Launching GUI application...
python audio_to_text_gui.py

REM Keep the window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Please check the error messages above.
    pause
)
