@echo off
REM Windows batch file to run the Web-based Audio to Text Converter

echo Starting Web-based Audio to Text Converter...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if the simple web converter script exists
if not exist "simple_web_converter.py" (
    echo Error: simple_web_converter.py not found
    echo Make sure you're running this from the correct directory
    pause
    exit /b 1
)

echo Python found. Starting web server...
echo.
echo This version uses OpenAI Whisper for accurate offline transcription!
echo The application will open automatically in your browser.
echo If it doesn't, manually open: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when you're done.
echo.

REM Run the simplified web converter (works with Python 3.13)
python simple_web_converter.py

REM Keep the window open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo An error occurred. Please check the error messages above.
    pause
)
