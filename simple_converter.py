"""
Simple and compatible Audio to Text Converter.
Works with various Python versions and handles missing dependencies gracefully.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleAudioToTextConverter:
    """
    A simplified audio-to-text converter that handles missing dependencies gracefully.
    """
    
    def __init__(self):
        self.supported_formats = {
            '.mp3', '.wav', '.flac', '.m4a', '.ogg', 
            '.aac', '.wma', '.aiff', '.au', '.3gp'
        }
        self.speech_recognition = None
        self.pydub = None
        self.whisper = None
        
        # Try to import dependencies
        self._import_dependencies()
    
    def _import_dependencies(self):
        """Import available dependencies."""
        try:
            import speech_recognition as sr
            self.speech_recognition = sr
            self.recognizer = sr.Recognizer()
            logger.info("SpeechRecognition loaded successfully")
        except ImportError as e:
            logger.warning(f"SpeechRecognition not available: {e}")
        
        try:
            from pydub import AudioSegment
            self.pydub = AudioSegment
            logger.info("PyDub loaded successfully")
        except ImportError as e:
            logger.warning(f"PyDub not available: {e}")
        
        try:
            import whisper
            self.whisper = whisper
            logger.info("Whisper available")
        except ImportError as e:
            logger.info(f"Whisper not available: {e}")
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the audio file format is supported."""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def convert_to_wav(self, input_path: str, output_path: str = None) -> str:
        """Convert audio file to WAV format."""
        if self.pydub is None:
            raise ImportError("PyDub is required for audio format conversion")
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))
        
        try:
            audio = self.pydub.from_file(input_path)
            audio = audio.set_channels(1).set_frame_rate(16000)
            audio.export(output_path, format="wav")
            logger.info(f"Converted {input_path} to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting {input_path} to WAV: {str(e)}")
            raise
    
    def transcribe_with_google(self, audio_path: str, language: str = "en-US") -> str:
        """Transcribe audio using Google Speech Recognition."""
        if self.speech_recognition is None:
            raise ImportError("SpeechRecognition is required for Google transcription")
        
        try:
            with self.speech_recognition.AudioFile(audio_path) as source:
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
            
            text = self.recognizer.recognize_google(audio_data, language=language)
            logger.info("Google Speech Recognition completed successfully")
            return text
            
        except self.speech_recognition.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return "Could not understand audio"
        except self.speech_recognition.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error in Google transcription: {str(e)}")
            return f"Error: {str(e)}"
    
    def transcribe_with_whisper(self, audio_path: str, model_name: str = "base") -> str:
        """Transcribe audio using OpenAI Whisper."""
        if self.whisper is None:
            raise ImportError("Whisper is required for offline transcription")
        
        try:
            model = self.whisper.load_model(model_name)
            result = model.transcribe(audio_path)
            logger.info("Whisper transcription completed successfully")
            return result["text"].strip()
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {str(e)}")
            return f"Error: {str(e)}"
    
    def transcribe_file(self, input_path: str, engine: str = "google", 
                       language: str = "en-US") -> Dict[str, Any]:
        """Main method to transcribe an audio file."""
        result = {
            "file_path": input_path,
            "engine": engine,
            "language": language,
            "text": "",
            "success": False,
            "error": None
        }
        
        try:
            # Check if file exists and is supported
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"File not found: {input_path}")
            
            if not self.is_supported_format(input_path):
                raise ValueError(f"Unsupported audio format: {Path(input_path).suffix}")
            
            # Convert to WAV if necessary
            wav_path = input_path
            temp_wav = False
            
            if Path(input_path).suffix.lower() != '.wav':
                if self.pydub is None:
                    result["error"] = "PyDub is required for format conversion. Please install it or use WAV files."
                    return result
                
                wav_path = self.convert_to_wav(input_path)
                temp_wav = True
            
            # Transcribe based on selected engine
            if engine.lower() == "whisper":
                result["text"] = self.transcribe_with_whisper(wav_path)
            else:  # Default to Google
                result["text"] = self.transcribe_with_google(wav_path, language)
            
            # Clean up temporary WAV file
            if temp_wav and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except:
                    pass
            
            result["success"] = True
            logger.info(f"Successfully transcribed {input_path}")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"Error transcribing {input_path}: {str(e)}")
        
        return result
    
    def get_available_engines(self) -> List[str]:
        """Get list of available transcription engines."""
        engines = []
        if self.speech_recognition is not None:
            engines.append("google")
        if self.whisper is not None:
            engines.append("whisper")
        return engines
    
    def get_status(self) -> Dict[str, bool]:
        """Get status of available components."""
        return {
            "speech_recognition": self.speech_recognition is not None,
            "pydub": self.pydub is not None,
            "whisper": self.whisper is not None
        }

def main():
    """Example usage of the SimpleAudioToTextConverter"""
    print("Simple Audio to Text Converter")
    print("=" * 40)
    
    converter = SimpleAudioToTextConverter()
    
    # Show status
    status = converter.get_status()
    print("Available components:")
    for component, available in status.items():
        print(f"  {component}: {'✓' if available else '✗'}")
    
    engines = converter.get_available_engines()
    print(f"\nAvailable engines: {', '.join(engines) if engines else 'None'}")
    
    if not engines:
        print("\nNo transcription engines available!")
        print("Please install dependencies:")
        print("  - For Google: pip install speechrecognition")
        print("  - For Whisper: pip install openai-whisper")
        print("  - For format conversion: pip install pydub")
        return
    
    # Example usage
    print("\nTo use this converter:")
    print("1. Place an audio file in this directory")
    print("2. Run:")
    print("   result = converter.transcribe_file('your_audio.wav')")
    print("   print(result['text'])")

if __name__ == "__main__":
    main()
