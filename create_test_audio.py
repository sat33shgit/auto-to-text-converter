"""
Create a sample audio file for testing the audio to text converter.
This creates a simple audio file using text-to-speech if available,
or provides instructions for testing with your own audio files.
"""

import os
import sys
from pathlib import Path

def create_sample_audio_with_tts():
    """Try to create a sample audio file using text-to-speech."""
    try:
        import pyttsx3
        
        # Initialize text-to-speech engine
        engine = pyttsx3.init()
        
        # Sample text for testing
        sample_text = ("Hello, this is a test of the Audio to Text Converter. "
                      "This sample audio file should be converted back to text "
                      "successfully using the Whisper speech recognition engine. "
                      "The quick brown fox jumps over the lazy dog. "
                      "Testing one, two, three, four, five.")
        
        # Save as audio file
        output_file = "sample_test_audio.wav"
        engine.save_to_file(sample_text, output_file)
        engine.runAndWait()
        
        if os.path.exists(output_file):
            print(f"✓ Sample audio file created: {output_file}")
            print(f"Original text: {sample_text}")
            return output_file
        else:
            print("! Failed to create sample audio file")
            return None
            
    except ImportError:
        print("! pyttsx3 not installed. Cannot create sample audio.")
        print("Install it with: pip install pyttsx3")
        return None
    except Exception as e:
        print(f"! Error creating sample audio: {e}")
        return None

def check_existing_audio_files():
    """Check for existing audio files in the current directory."""
    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac']
    current_dir = Path('.')
    
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(list(current_dir.glob(f"*{ext}")))
    
    return audio_files

def main():
    """Main function to set up test audio files."""
    print("Audio to Text Converter - Test Setup")
    print("=" * 40)
    
    # Check for existing audio files
    existing_files = check_existing_audio_files()
    
    if existing_files:
        print("Found existing audio files:")
        for file in existing_files:
            print(f"  • {file.name}")
        print("\nYou can use these files to test the converter!")
    else:
        print("No audio files found in the current directory.")
    
    # Try to create a sample file
    print("\nAttempting to create a sample audio file...")
    sample_file = create_sample_audio_with_tts()
    
    if sample_file:
        print(f"\n✓ Test setup complete!")
        print(f"Sample file: {sample_file}")
    elif not existing_files:
        print("\n! No sample audio file could be created.")
        print("\nTo test the converter:")
        print("1. Download a sample audio file (MP3, WAV, etc.)")
        print("2. Place it in this directory")
        print("3. Run the web converter: python simple_web_converter.py")
        print("4. Upload the file and test the conversion")
    
    # Instructions for testing
    print(f"\n🎯 How to test:")
    print("1. Start the web converter:")
    print("   python simple_web_converter.py")
    print("2. Open http://localhost:8080 in your browser")
    print("3. Upload an audio file")
    print("4. Click 'Convert with Whisper'")
    print("5. Wait for the transcription to complete")
    print("6. Download the result!")
    
    print(f"\nNote: The first time you use Whisper, it will download the model")
    print("which may take a few minutes depending on your internet connection.")

if __name__ == "__main__":
    main()
