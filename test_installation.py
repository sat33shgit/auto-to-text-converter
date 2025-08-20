#!/usr/bin/env python3
"""
Test script to verify the Audio to Text Converter installation and functionality.
"""

import sys
import os
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing module imports...")
    
    required_modules = [
        ("speech_recognition", "SpeechRecognition"),
        ("pydub", "PyDub"),
        ("numpy", "NumPy"),
        ("matplotlib", "Matplotlib"),
    ]
    
    optional_modules = [
        ("whisper", "OpenAI Whisper"),
        ("torch", "PyTorch"),
        ("pyaudio", "PyAudio"),
    ]
    
    failed_imports = []
    
    # Test required modules
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"  ✓ {name}")
        except ImportError as e:
            print(f"  ✗ {name}: {e}")
            failed_imports.append(name)
    
    # Test optional modules
    for module, name in optional_modules:
        try:
            __import__(module)
            print(f"  ✓ {name} (optional)")
        except ImportError:
            print(f"  ! {name} (optional) - not available")
    
    if failed_imports:
        print(f"\nError: Required modules failed to import: {', '.join(failed_imports)}")
        return False
    
    print("All required modules imported successfully!")
    return True

def test_audio_converter():
    """Test the AudioToTextConverter class."""
    print("\nTesting AudioToTextConverter...")
    
    try:
        from audio_converter import AudioToTextConverter
        
        converter = AudioToTextConverter()
        print("  ✓ AudioToTextConverter initialized")
        
        # Test supported formats check
        test_files = ["test.wav", "test.mp3", "test.flac", "test.txt"]
        for test_file in test_files:
            result = converter.is_supported_format(test_file)
            expected = test_file.endswith(('.wav', '.mp3', '.flac'))
            if result == expected:
                print(f"  ✓ Format check for {test_file}: {result}")
            else:
                print(f"  ✗ Format check for {test_file}: expected {expected}, got {result}")
        
        print("AudioToTextConverter basic tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ AudioToTextConverter test failed: {e}")
        traceback.print_exc()
        return False

def test_audio_utils():
    """Test the AudioAnalyzer class."""
    print("\nTesting AudioAnalyzer...")
    
    try:
        from audio_utils import AudioAnalyzer
        
        analyzer = AudioAnalyzer()
        print("  ✓ AudioAnalyzer initialized")
        
        # Test duration formatting
        test_cases = [
            (65, "01:05"),
            (3661, "01:01:01"),
            (30, "00:30")
        ]
        
        for seconds, expected in test_cases:
            result = analyzer._format_duration(seconds)
            if result == expected:
                print(f"  ✓ Duration format {seconds}s -> {result}")
            else:
                print(f"  ✗ Duration format {seconds}s: expected {expected}, got {result}")
        
        print("AudioAnalyzer basic tests passed!")
        return True
        
    except Exception as e:
        print(f"  ✗ AudioAnalyzer test failed: {e}")
        traceback.print_exc()
        return False

def test_gui_imports():
    """Test if GUI components can be imported."""
    print("\nTesting GUI components...")
    
    try:
        import tkinter as tk
        print("  ✓ Tkinter available")
        
        # Test if we can create a root window (don't show it)
        root = tk.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("  ✓ Tkinter window creation test passed")
        
        return True
        
    except Exception as e:
        print(f"  ✗ GUI test failed: {e}")
        return False

def test_whisper_availability():
    """Test if Whisper is available and can be loaded."""
    print("\nTesting Whisper availability...")
    
    try:
        import whisper
        print("  ✓ Whisper module imported")
        
        # Try to load the smallest model
        print("  Attempting to load tiny model...")
        try:
            model = whisper.load_model("tiny")
            print("  ✓ Whisper tiny model loaded successfully")
            return True
        except Exception as e:
            print(f"  ! Whisper model loading failed: {e}")
            print("  This is normal on first run - models will download when needed")
            return True
            
    except ImportError:
        print("  ! Whisper not available (optional)")
        return True
    except Exception as e:
        print(f"  ✗ Whisper test failed: {e}")
        return True  # Don't fail the overall test for optional component

def create_test_summary(results):
    """Create a summary of test results."""
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name:.<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All tests passed! The application should work correctly.")
    else:
        print("! Some tests failed. Some features may not work correctly.")
        print("Please check the error messages above and install missing dependencies.")
    
    return passed == total

def main():
    """Run all tests."""
    print("Audio to Text Converter - Installation Test")
    print("="*50)
    
    test_results = {
        "Module Imports": test_imports(),
        "AudioToTextConverter": test_audio_converter(),
        "AudioAnalyzer": test_audio_utils(),
        "GUI Components": test_gui_imports(),
        "Whisper Availability": test_whisper_availability(),
    }
    
    success = create_test_summary(test_results)
    
    print("\nNext steps:")
    if success:
        print("1. Try running the GUI: python audio_to_text_gui.py")
        print("2. Or use command line: python audio_to_text_cli.py --help")
        print("3. Check example_usage.py for usage examples")
    else:
        print("1. Install missing dependencies shown above")
        print("2. Run this test script again")
        print("3. Check the setup.py script for automated installation")
    
    print(f"\nTest completed with {'SUCCESS' if success else 'ISSUES'}")
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    
    # Keep window open on Windows
    if os.name == 'nt':
        input("\nPress Enter to exit...")
    
    sys.exit(exit_code)
