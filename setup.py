#!/usr/bin/env python3
"""
Setup script for Audio to Text Converter.
Installs all required dependencies and sets up the environment.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7 or higher is required!")
        return False
    
    print("✓ Python version is compatible")
    return True

def install_system_dependencies():
    """Install system dependencies based on the operating system."""
    system = platform.system().lower()
    
    print(f"\nDetected operating system: {system}")
    
    if system == "windows":
        print("On Windows, you may need to install:")
        print("  - Microsoft Visual C++ Build Tools")
        print("  - FFmpeg (for audio format support)")
        print("  - portaudio (for PyAudio)")
        print("\nPlease install these manually if you encounter errors.")
        return True
    
    elif system == "linux":
        # Try to install system dependencies on Linux
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y python3-dev",
            "sudo apt-get install -y portaudio19-dev",
            "sudo apt-get install -y ffmpeg",
            "sudo apt-get install -y libasound2-dev"
        ]
        
        for cmd in commands:
            if not run_command(cmd, f"Running: {cmd}"):
                print("Some system dependencies may not have been installed.")
                break
    
    elif system == "darwin":  # macOS
        print("On macOS, you may need to install:")
        print("  - Homebrew")
        print("  - portaudio: brew install portaudio")
        print("  - ffmpeg: brew install ffmpeg")
        print("\nTrying to install via Homebrew...")
        
        commands = [
            "brew install portaudio",
            "brew install ffmpeg"
        ]
        
        for cmd in commands:
            run_command(cmd, f"Running: {cmd}")
    
    return True

def install_python_packages():
    """Install Python packages from requirements.txt."""
    print("\nInstalling Python packages...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", 
                      "Upgrading pip"):
        print("Warning: Could not upgrade pip")
    
    # Install packages from requirements.txt
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        cmd = f"{sys.executable} -m pip install -r {requirements_file}"
        if run_command(cmd, "Installing packages from requirements.txt"):
            return True
    
    # Fallback: install packages individually
    print("\nFallback: Installing packages individually...")
    
    packages = [
        "speechrecognition==3.10.0",
        "pydub==0.25.1",
        "numpy==1.24.3",
        "matplotlib==3.7.2",
    ]
    
    # Try to install PyAudio (can be problematic)
    print("\nInstalling PyAudio (this might take a while or fail)...")
    if not run_command(f"{sys.executable} -m pip install pyaudio", "Installing PyAudio"):
        print("Warning: PyAudio installation failed. Real-time audio features may not work.")
        print("You can try installing it later with: pip install pyaudio")
    
    # Install other packages
    for package in packages:
        run_command(f"{sys.executable} -m pip install {package}", 
                   f"Installing {package}")
    
    # Try to install Whisper (optional)
    print("\nInstalling OpenAI Whisper (optional, for offline transcription)...")
    if run_command(f"{sys.executable} -m pip install openai-whisper", 
                  "Installing OpenAI Whisper"):
        print("✓ Whisper installed successfully")
    else:
        print("Warning: Whisper installation failed. Offline transcription may not work.")
    
    return True

def test_installation():
    """Test if the installation was successful."""
    print("\nTesting installation...")
    
    test_imports = [
        ("speech_recognition", "Speech Recognition"),
        ("pydub", "PyDub (audio processing)"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
    ]
    
    all_good = True
    
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✓ {description} imported successfully")
        except ImportError as e:
            print(f"✗ {description} import failed: {e}")
            all_good = False
    
    # Test optional imports
    optional_imports = [
        ("pyaudio", "PyAudio (real-time audio)"),
        ("whisper", "OpenAI Whisper (offline transcription)"),
    ]
    
    for module, description in optional_imports:
        try:
            __import__(module)
            print(f"✓ {description} imported successfully")
        except ImportError:
            print(f"! {description} not available (optional)")
    
    return all_good

def create_sample_files():
    """Create sample configuration and usage files."""
    print("\nCreating sample files...")
    
    # Create a sample configuration file
    config_content = """# Audio to Text Converter Configuration
# You can modify these settings as needed

[DEFAULT]
engine = google
language = en-US
chunk_audio = false
output_format = txt

[GOOGLE]
# Google Speech Recognition settings
# No API key required for basic usage

[WHISPER]
# OpenAI Whisper settings
model = base
# Available models: tiny, base, small, medium, large
"""
    
    config_path = Path(__file__).parent / "config.ini"
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✓ Created sample configuration: {config_path}")
    
    # Create a quick start guide
    quickstart_content = """# Quick Start Guide

## GUI Mode (Recommended for beginners)
Run the graphical interface:
```
python audio_to_text_gui.py
```

## Command Line Mode
Convert a single file:
```
python audio_to_text_cli.py --input "audio.mp3" --output "transcription.txt"
```

Convert multiple files in a folder:
```
python audio_to_text_cli.py --input "audio_folder/" --output "transcriptions/"
```

Use Whisper for offline transcription:
```
python audio_to_text_cli.py --input "audio.wav" --engine whisper
```

## Supported Audio Formats
- MP3, WAV, FLAC, M4A, OGG, AAC, WMA

## Troubleshooting
- If you get import errors, make sure all dependencies are installed
- For PyAudio issues on Windows, try installing it separately
- For better accuracy, use mono audio at 16kHz sample rate
- Internet connection required for Google Speech Recognition
"""
    
    quickstart_path = Path(__file__).parent / "QUICKSTART.md"
    with open(quickstart_path, 'w') as f:
        f.write(quickstart_content)
    
    print(f"✓ Created quick start guide: {quickstart_path}")

def main():
    """Main setup function."""
    print("=" * 60)
    print("Audio to Text Converter - Setup Script")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install system dependencies
    install_system_dependencies()
    
    # Install Python packages
    if not install_python_packages():
        print("\nWarning: Some packages may not have been installed correctly.")
    
    # Test installation
    if test_installation():
        print("\n✓ Installation completed successfully!")
    else:
        print("\n! Installation completed with some issues.")
        print("Some features may not work correctly.")
    
    # Create sample files
    create_sample_files()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Read the QUICKSTART.md file for usage instructions")
    print("2. Try running: python audio_to_text_gui.py")
    print("3. Or use command line: python audio_to_text_cli.py --help")
    print("\nFor issues, check the README.md file or the project documentation.")

if __name__ == "__main__":
    main()
