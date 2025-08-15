@echo off
echo Audio to Text Converter - Setup
echo ===============================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found. Installing required packages...
echo.

pip install openai-whisper
echo.

if %errorlevel% == 0 (
    echo.
    echo ✅ Setup completed successfully!
    echo.
    echo To start the converter:
    echo 1. Double-click: start_working_converter.bat
    echo 2. Or run: python working_converter.py
    echo 3. Then open: http://localhost:8081
    echo.
    echo Optional: Install pyttsx3 for test audio creation
    echo pip install pyttsx3
    echo.
) else (
    echo.
    echo ❌ Setup failed. Please check your internet connection.
    echo.
)

pause
