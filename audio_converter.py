import os
import sys
import wave
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import which
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AudioToTextConverter:
    """
    A comprehensive audio-to-text converter that supports multiple audio formats
    and speech recognition engines.
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_formats = {
            '.mp3', '.wav', '.flac', '.m4a', '.ogg', 
            '.aac', '.wma', '.aiff', '.au', '.3gp'
        }
        self.whisper_model = None
        
    def load_whisper_model(self, model_name: str = "base") -> bool:
        """
        Load OpenAI Whisper model for offline transcription.
        
        Args:
            model_name: Model size (tiny, base, small, medium, large)
            
        Returns:
            bool: True if model loaded successfully
        """
        try:
            import whisper
            self.whisper_model = whisper.load_model(model_name)
            logger.info(f"Whisper model '{model_name}' loaded successfully")
            return True
        except ImportError:
            logger.warning("Whisper not installed. Install with: pip install openai-whisper")
            return False
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            return False
    
    def is_supported_format(self, file_path: str) -> bool:
        """
        Check if the audio file format is supported.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            bool: True if format is supported
        """
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def convert_to_wav(self, input_path: str, output_path: str = None) -> str:
        """
        Convert audio file to WAV format for speech recognition.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output WAV file (optional)
            
        Returns:
            str: Path to the converted WAV file
        """
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.wav'))
            
        try:
            # Load audio file
            audio = AudioSegment.from_file(input_path)
            
            # Convert to mono and set sample rate to 16kHz for better recognition
            audio = audio.set_channels(1).set_frame_rate(16000)
            
            # Export as WAV
            audio.export(output_path, format="wav")
            logger.info(f"Converted {input_path} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error converting {input_path} to WAV: {str(e)}")
            raise
    
    def transcribe_with_google(self, audio_path: str, language: str = "en-US") -> str:
        """
        Transcribe audio using Google Speech Recognition.
        
        Args:
            audio_path: Path to audio file
            language: Language code for recognition
            
        Returns:
            str: Transcribed text
        """
        try:
            with sr.AudioFile(audio_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source)
                audio_data = self.recognizer.record(source)
                
            # Recognize speech using Google Web Speech API
            text = self.recognizer.recognize_google(audio_data, language=language)
            logger.info("Google Speech Recognition completed successfully")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return "Could not understand audio"
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service; {e}")
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error in Google transcription: {str(e)}")
            return f"Error: {str(e)}"
    
    def transcribe_with_whisper(self, audio_path: str, language: str = None) -> str:
        """
        Transcribe audio using OpenAI Whisper.
        
        Args:
            audio_path: Path to audio file
            language: Language code (optional)
            
        Returns:
            str: Transcribed text
        """
        if self.whisper_model is None:
            if not self.load_whisper_model():
                return "Error: Whisper model not available"
        
        try:
            result = self.whisper_model.transcribe(audio_path, language=language)
            logger.info("Whisper transcription completed successfully")
            return result["text"].strip()
            
        except Exception as e:
            logger.error(f"Error in Whisper transcription: {str(e)}")
            return f"Error: {str(e)}"
    
    def split_audio_for_recognition(self, audio_path: str, chunk_length_ms: int = 60000) -> List[str]:
        """
        Split long audio files into smaller chunks for better recognition.
        
        Args:
            audio_path: Path to audio file
            chunk_length_ms: Length of each chunk in milliseconds
            
        Returns:
            List[str]: Paths to audio chunks
        """
        try:
            audio = AudioSegment.from_wav(audio_path)
            chunks = []
            
            for i, chunk_start in enumerate(range(0, len(audio), chunk_length_ms)):
                chunk_end = min(chunk_start + chunk_length_ms, len(audio))
                chunk = audio[chunk_start:chunk_end]
                
                chunk_path = f"{audio_path}_chunk_{i:03d}.wav"
                chunk.export(chunk_path, format="wav")
                chunks.append(chunk_path)
                
            logger.info(f"Split audio into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error splitting audio: {str(e)}")
            return []
    
    def transcribe_file(self, 
                       input_path: str, 
                       engine: str = "google", 
                       language: str = "en-US",
                       chunk_audio: bool = False) -> Dict[str, Any]:
        """
        Main method to transcribe an audio file.
        
        Args:
            input_path: Path to input audio file
            engine: Recognition engine ('google' or 'whisper')
            language: Language code
            chunk_audio: Whether to split long audio into chunks
            
        Returns:
            Dict: Result containing transcribed text and metadata
        """
        result = {
            "file_path": input_path,
            "engine": engine,
            "language": language,
            "text": "",
            "success": False,
            "error": None,
            "chunks": []
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
                wav_path = self.convert_to_wav(input_path)
                temp_wav = True
            
            # Transcribe based on selected engine
            if engine.lower() == "whisper":
                if chunk_audio:
                    # Split audio into chunks and transcribe each
                    chunks = self.split_audio_for_recognition(wav_path)
                    transcriptions = []
                    
                    for i, chunk_path in enumerate(chunks):
                        chunk_text = self.transcribe_with_whisper(chunk_path, language)
                        transcriptions.append(chunk_text)
                        result["chunks"].append({
                            "chunk_index": i,
                            "file_path": chunk_path,
                            "text": chunk_text
                        })
                        # Clean up chunk file
                        try:
                            os.remove(chunk_path)
                        except:
                            pass
                    
                    result["text"] = " ".join(transcriptions)
                else:
                    result["text"] = self.transcribe_with_whisper(wav_path, language)
            
            else:  # Default to Google
                if chunk_audio:
                    # Split audio into chunks and transcribe each
                    chunks = self.split_audio_for_recognition(wav_path)
                    transcriptions = []
                    
                    for i, chunk_path in enumerate(chunks):
                        chunk_text = self.transcribe_with_google(chunk_path, language)
                        transcriptions.append(chunk_text)
                        result["chunks"].append({
                            "chunk_index": i,
                            "file_path": chunk_path,
                            "text": chunk_text
                        })
                        # Clean up chunk file
                        try:
                            os.remove(chunk_path)
                        except:
                            pass
                    
                    result["text"] = " ".join(transcriptions)
                else:
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
    
    def batch_transcribe(self, 
                        input_dir: str, 
                        output_dir: str = None,
                        engine: str = "google",
                        language: str = "en-US") -> List[Dict[str, Any]]:
        """
        Transcribe multiple audio files in a directory.
        
        Args:
            input_dir: Directory containing audio files
            output_dir: Directory to save transcription files
            engine: Recognition engine to use
            language: Language code
            
        Returns:
            List[Dict]: Results for each file
        """
        if output_dir is None:
            output_dir = os.path.join(input_dir, "transcriptions")
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        audio_files = []
        
        # Find all audio files
        for ext in self.supported_formats:
            audio_files.extend(Path(input_dir).glob(f"*{ext}"))
        
        logger.info(f"Found {len(audio_files)} audio files to transcribe")
        
        for audio_file in audio_files:
            result = self.transcribe_file(str(audio_file), engine, language)
            results.append(result)
            
            # Save transcription to file
            if result["success"]:
                output_file = Path(output_dir) / f"{audio_file.stem}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result["text"])
                logger.info(f"Saved transcription to {output_file}")
        
        # Save summary report
        summary_file = Path(output_dir) / "transcription_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results

def main():
    """Example usage of the AudioToTextConverter"""
    converter = AudioToTextConverter()
    
    # Example: Transcribe a single file
    audio_file = "example.wav"  # Replace with your audio file
    
    if os.path.exists(audio_file):
        result = converter.transcribe_file(audio_file, engine="google")
        
        if result["success"]:
            print("Transcription successful!")
            print(f"Text: {result['text']}")
            
            # Save to file
            with open("transcription.txt", 'w', encoding='utf-8') as f:
                f.write(result['text'])
        else:
            print(f"Transcription failed: {result['error']}")
    else:
        print("Please provide a valid audio file path")

if __name__ == "__main__":
    main()
