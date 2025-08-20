"""
Create a sample audio file using Windows Speech API (SAPI)
This creates a test audio file that you can use to test the converter.
"""

import os

def create_windows_speech_audio():
    """Create a sample audio file using Windows Speech API."""
    sample_text = (
        "Hello, this is a test of the Audio to Text Converter. "
        "This sample audio file should be converted back to text "
        "successfully using the Whisper speech recognition engine. "
        "The quick brown fox jumps over the lazy dog. "
        "Testing one, two, three, four, five. "
        "This is the end of the test audio file."
    )
    
    # Use Windows SAPI to create audio file
    powershell_command = f'''
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SetOutputToWaveFile("sample_test_audio.wav")
    $synth.Speak("{sample_text}")
    $synth.Dispose()
    '''
    
    # Write PowerShell script to file
    with open('create_audio.ps1', 'w') as f:
        f.write(powershell_command)
    
    # Execute PowerShell script
    os.system('powershell -ExecutionPolicy Bypass -File create_audio.ps1')
    
    # Clean up
    if os.path.exists('create_audio.ps1'):
        os.remove('create_audio.ps1')
    
    if os.path.exists('sample_test_audio.wav'):
        print("✅ Sample audio file created successfully!")
        print(f"📁 File: sample_test_audio.wav")
        print(f"📝 Original text: {sample_text}")
        return True
    else:
        print("❌ Failed to create sample audio file")
        return False

if __name__ == "__main__":
    print("🎵 Creating Sample Audio File")
    print("=" * 40)
    
    success = create_windows_speech_audio()
    
    if success:
        print("\n🎯 Ready to test!")
        print("1. Go to http://localhost:8080")
        print("2. Upload 'sample_test_audio.wav'")
        print("3. Click 'Convert with Whisper'")
        print("4. Compare the result with the original text above")
    else:
        print("\n📝 Manual alternatives:")
        print("1. Record a voice memo on your phone and transfer it")
        print("2. Download a sample audio from YouTube or other sources")
        print("3. Use the live transcription feature instead")
        print("4. Search for 'sample audio files' online")
