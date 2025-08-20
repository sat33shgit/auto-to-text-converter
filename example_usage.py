"""
Simple example script demonstrating how to use the Audio to Text Converter.
"""

from audio_converter import AudioToTextConverter
from audio_utils import AudioAnalyzer
import os
from pathlib import Path

def example_basic_usage():
    """Basic usage example."""
    print("=== Basic Usage Example ===")
    
    # Initialize converter
    converter = AudioToTextConverter()
    
    # Example audio file (you'll need to replace this with an actual file)
    audio_file = "example_audio.wav"  # Replace with your audio file
    
    if not os.path.exists(audio_file):
        print(f"Audio file '{audio_file}' not found.")
        print("Please place an audio file named 'example_audio.wav' in this directory,")
        print("or modify this script to use your own audio file.")
        return
    
    # Transcribe using Google Speech Recognition
    print(f"Transcribing '{audio_file}' using Google Speech Recognition...")
    result = converter.transcribe_file(audio_file, engine="google")
    
    if result["success"]:
        print("Transcription successful!")
        print(f"Text: {result['text']}")
        
        # Save to file
        output_file = "transcription_example.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"Transcription saved to: {output_file}")
    else:
        print(f"Transcription failed: {result['error']}")

def example_whisper_usage():
    """Example using Whisper for offline transcription."""
    print("\n=== Whisper (Offline) Example ===")
    
    # Initialize converter
    converter = AudioToTextConverter()
    
    # Load Whisper model
    print("Loading Whisper model...")
    if not converter.load_whisper_model("base"):
        print("Failed to load Whisper model. Make sure it's installed:")
        print("pip install openai-whisper")
        return
    
    audio_file = "example_audio.wav"  # Replace with your audio file
    
    if not os.path.exists(audio_file):
        print(f"Audio file '{audio_file}' not found.")
        return
    
    # Transcribe using Whisper
    print(f"Transcribing '{audio_file}' using Whisper...")
    result = converter.transcribe_file(audio_file, engine="whisper")
    
    if result["success"]:
        print("Transcription successful!")
        print(f"Text: {result['text']}")
        
        # Save to file
        output_file = "transcription_whisper.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        print(f"Transcription saved to: {output_file}")
    else:
        print(f"Transcription failed: {result['error']}")

def example_audio_analysis():
    """Example of audio analysis features."""
    print("\n=== Audio Analysis Example ===")
    
    analyzer = AudioAnalyzer()
    
    audio_file = "example_audio.wav"  # Replace with your audio file
    
    if not os.path.exists(audio_file):
        print(f"Audio file '{audio_file}' not found.")
        return
    
    # Get audio information
    print("Getting audio information...")
    info = analyzer.get_audio_info(audio_file)
    
    if "error" not in info:
        print("\nAudio Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Analyze audio quality
    print("\nAnalyzing audio quality...")
    quality = analyzer.analyze_audio_quality(audio_file)
    
    if "error" not in quality:
        print(f"Quality Score: {quality['quality_score']}/100")
        print(f"Quality Rating: {quality['quality_rating']}")
        print("Recommendations:")
        for rec in quality['recommendations']:
            print(f"  - {rec}")
    
    # Create waveform plot
    try:
        print("\nCreating waveform plot...")
        plot_path = analyzer.create_waveform_plot(audio_file, "waveform_example.png")
        print(f"Waveform plot saved to: {plot_path}")
    except Exception as e:
        print(f"Could not create waveform plot: {e}")

def example_batch_processing():
    """Example of batch processing multiple files."""
    print("\n=== Batch Processing Example ===")
    
    # Create a sample directory structure
    audio_dir = "sample_audio_files"
    output_dir = "batch_transcriptions"
    
    if not os.path.exists(audio_dir):
        print(f"Creating sample directory: {audio_dir}")
        os.makedirs(audio_dir, exist_ok=True)
        print(f"Please add audio files to '{audio_dir}' directory and run this example again.")
        return
    
    # Check if there are audio files
    audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(Path(audio_dir).glob(f"*{ext}"))
    
    if not audio_files:
        print(f"No audio files found in '{audio_dir}' directory.")
        print("Please add some audio files and try again.")
        return
    
    print(f"Found {len(audio_files)} audio files for batch processing...")
    
    # Initialize converter
    converter = AudioToTextConverter()
    
    # Batch transcribe
    results = converter.batch_transcribe(
        input_dir=audio_dir,
        output_dir=output_dir,
        engine="google",
        language="en-US"
    )
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nBatch processing completed:")
    print(f"Total files: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Results saved to: {output_dir}")

def create_sample_audio():
    """Create a simple sample audio file for testing (requires text-to-speech)."""
    print("\n=== Creating Sample Audio ===")
    
    try:
        import pyttsx3
        
        # Initialize text-to-speech engine
        engine = pyttsx3.init()
        
        # Sample text
        sample_text = ("Hello, this is a sample audio file for testing the "
                      "Audio to Text Converter application. This text should "
                      "be converted back to text successfully.")
        
        # Save as audio file
        output_file = "sample_audio.wav"
        engine.save_to_file(sample_text, output_file)
        engine.runAndWait()
        
        print(f"Sample audio file created: {output_file}")
        print("You can use this file to test the transcription.")
        
    except ImportError:
        print("pyttsx3 not installed. Cannot create sample audio.")
        print("You can install it with: pip install pyttsx3")
    except Exception as e:
        print(f"Could not create sample audio: {e}")

def main():
    """Run all examples."""
    print("Audio to Text Converter - Examples")
    print("=" * 50)
    
    # Check if we have an example audio file
    example_files = ["example_audio.wav", "sample_audio.wav", "test_audio.wav"]
    available_file = None
    
    for file in example_files:
        if os.path.exists(file):
            available_file = file
            break
    
    if not available_file:
        print("No sample audio file found.")
        print("Creating a sample audio file...")
        create_sample_audio()
        
        # Check again
        for file in example_files:
            if os.path.exists(file):
                available_file = file
                break
    
    if available_file:
        # Update examples to use the available file
        globals()['audio_file'] = available_file
        
        # Run examples
        example_basic_usage()
        # example_whisper_usage()  # Uncomment if Whisper is installed
        # example_audio_analysis()  # Uncomment if matplotlib is working
        # example_batch_processing()  # Uncomment for batch processing test
    else:
        print("\nTo run the examples, you need an audio file.")
        print("Please:")
        print("1. Place an audio file named 'example_audio.wav' in this directory, OR")
        print("2. Install pyttsx3 (pip install pyttsx3) to create a sample file")
        
        print("\nAlternatively, you can modify this script to use your own audio files.")

if __name__ == "__main__":
    main()
