@echo off
echo Audio to Text Converter
echo =======================
echo.
echo Starting the audio to text converter...
echo.

cd /d "c:\Sateesh\Projects\AutoToText"

echo Checking if Python is available...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found in PATH. Trying full path...
    "C:/Users/Boggarapu/AppData/Local/Programs/Python/Python313/python.exe" working_converter.py
) else (
    echo ✅ Python found. Starting converter...
    python working_converter.py
)

pause
