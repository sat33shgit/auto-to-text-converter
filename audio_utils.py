"""
Utility functions for audio processing and analysis.
Provides additional functionality for the audio-to-text converter.
"""

import os
import wave
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class AudioAnalyzer:
    """
    Utility class for analyzing audio files and providing insights.
    """
    
    def __init__(self):
        self.supported_formats = {'.wav', '.mp3', '.flac', '.m4a', '.ogg', '.aac'}
    
    def get_audio_info(self, file_path: str) -> Dict:
        """
        Get basic information about an audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict: Audio file information
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(file_path)
            
            info = {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size_mb": round(os.path.getsize(file_path) / (1024 * 1024), 2),
                "duration_seconds": len(audio) / 1000,
                "duration_formatted": self._format_duration(len(audio) / 1000),
                "channels": audio.channels,
                "sample_rate": audio.frame_rate,
                "sample_width": audio.sample_width,
                "frame_count": audio.frame_count(),
                "bitrate": audio.frame_rate * audio.channels * audio.sample_width * 8,
                "format": Path(file_path).suffix.lower()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting audio info for {file_path}: {str(e)}")
            return {"error": str(e)}
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in seconds to MM:SS or HH:MM:SS format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def analyze_audio_quality(self, file_path: str) -> Dict:
        """
        Analyze audio quality and provide recommendations for transcription.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dict: Quality analysis results
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(file_path)
            
            # Convert to numpy array for analysis
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
                samples = samples.mean(axis=1)  # Convert to mono for analysis
            
            # Normalize samples
            samples = samples.astype(np.float32)
            samples = samples / np.max(np.abs(samples))
            
            # Calculate various quality metrics
            rms_level = np.sqrt(np.mean(samples**2))
            peak_level = np.max(np.abs(samples))
            
            # Dynamic range (simplified)
            dynamic_range = peak_level / (rms_level + 1e-10)
            
            # Signal-to-noise ratio estimation (very basic)
            # Find quiet sections (bottom 10% of RMS values in chunks)
            chunk_size = len(samples) // 100
            if chunk_size > 0:
                chunks = [samples[i:i+chunk_size] for i in range(0, len(samples), chunk_size)]
                chunk_rms = [np.sqrt(np.mean(chunk**2)) for chunk in chunks if len(chunk) == chunk_size]
                noise_floor = np.percentile(chunk_rms, 10) if chunk_rms else 0.01
                snr_estimate = 20 * np.log10(rms_level / (noise_floor + 1e-10))
            else:
                snr_estimate = 0
            
            # Quality assessment
            quality_score = 0
            recommendations = []
            
            # Sample rate check
            if audio.frame_rate >= 16000:
                quality_score += 25
            else:
                recommendations.append("Consider using audio with sample rate >= 16kHz for better recognition")
            
            # Channels check
            if audio.channels == 1:
                quality_score += 15
                recommendations.append("Mono audio is optimal for speech recognition")
            else:
                quality_score += 10
                recommendations.append("Consider converting to mono for better speech recognition")
            
            # Duration check
            duration = len(audio) / 1000
            if duration < 300:  # Less than 5 minutes
                quality_score += 20
            elif duration < 1800:  # Less than 30 minutes
                quality_score += 15
                recommendations.append("Consider splitting long audio into smaller chunks")
            else:
                quality_score += 5
                recommendations.append("Long audio files may benefit from chunking for better accuracy")
            
            # Signal level check
            if 0.1 <= rms_level <= 0.7:
                quality_score += 25
            elif rms_level < 0.05:
                recommendations.append("Audio level is quite low - consider amplifying")
                quality_score += 10
            elif rms_level > 0.8:
                recommendations.append("Audio level is high - check for clipping")
                quality_score += 15
            else:
                quality_score += 20
            
            # SNR check
            if snr_estimate > 20:
                quality_score += 15
            elif snr_estimate > 10:
                quality_score += 10
            else:
                recommendations.append("Audio may be noisy - consider noise reduction")
                quality_score += 5
            
            # Overall quality rating
            if quality_score >= 80:
                quality_rating = "Excellent"
            elif quality_score >= 65:
                quality_rating = "Good"
            elif quality_score >= 50:
                quality_rating = "Fair"
            else:
                quality_rating = "Poor"
            
            if not recommendations:
                recommendations.append("Audio quality looks good for transcription")
            
            analysis = {
                "file_path": file_path,
                "quality_score": quality_score,
                "quality_rating": quality_rating,
                "recommendations": recommendations,
                "metrics": {
                    "rms_level": float(rms_level),
                    "peak_level": float(peak_level),
                    "dynamic_range": float(dynamic_range),
                    "snr_estimate_db": float(snr_estimate),
                    "duration_seconds": duration,
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing audio quality for {file_path}: {str(e)}")
            return {"error": str(e)}
    
    def create_waveform_plot(self, file_path: str, output_path: str = None) -> str:
        """
        Create a waveform visualization of the audio file.
        
        Args:
            file_path: Path to the audio file
            output_path: Path to save the plot image
            
        Returns:
            str: Path to the saved plot image
        """
        try:
            from pydub import AudioSegment
            
            if output_path is None:
                output_path = str(Path(file_path).with_suffix('.png'))
            
            # Load audio
            audio = AudioSegment.from_file(file_path)
            
            # Convert to numpy array
            samples = np.array(audio.get_array_of_samples())
            if audio.channels == 2:
                samples = samples.reshape((-1, 2))
            
            # Create time axis
            duration = len(audio) / 1000  # Duration in seconds
            time = np.linspace(0, duration, len(samples))
            
            # Create plot
            plt.figure(figsize=(12, 6))
            
            if audio.channels == 1:
                plt.plot(time, samples, color='blue', alpha=0.7)
                plt.title(f'Waveform - {os.path.basename(file_path)}')
                plt.ylabel('Amplitude')
            else:
                plt.subplot(2, 1, 1)
                plt.plot(time, samples[:, 0], color='blue', alpha=0.7)
                plt.title(f'Waveform - {os.path.basename(file_path)} (Left Channel)')
                plt.ylabel('Amplitude')
                
                plt.subplot(2, 1, 2)
                plt.plot(time, samples[:, 1], color='red', alpha=0.7)
                plt.title('Right Channel')
                plt.ylabel('Amplitude')
            
            plt.xlabel('Time (seconds)')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Waveform plot saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error creating waveform plot for {file_path}: {str(e)}")
            raise
    
    def detect_silence(self, file_path: str, min_silence_len: int = 1000, 
                      silence_thresh: int = -40) -> List[Tuple[float, float]]:
        """
        Detect silent sections in the audio file.
        
        Args:
            file_path: Path to the audio file
            min_silence_len: Minimum length of silence in milliseconds
            silence_thresh: Silence threshold in dBFS
            
        Returns:
            List[Tuple[float, float]]: List of (start, end) times of silent sections
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import detect_silence
            
            audio = AudioSegment.from_file(file_path)
            
            # Detect silence
            silent_ranges = detect_silence(
                audio, 
                min_silence_len=min_silence_len, 
                silence_thresh=silence_thresh
            )
            
            # Convert to seconds
            silent_ranges_sec = [(start/1000, end/1000) for start, end in silent_ranges]
            
            return silent_ranges_sec
            
        except Exception as e:
            logger.error(f"Error detecting silence in {file_path}: {str(e)}")
            return []
    
    def suggest_chunk_points(self, file_path: str, target_chunk_duration: int = 60) -> List[float]:
        """
        Suggest optimal points to split audio into chunks based on silence detection.
        
        Args:
            file_path: Path to the audio file
            target_chunk_duration: Target duration for each chunk in seconds
            
        Returns:
            List[float]: List of suggested split points in seconds
        """
        try:
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(file_path)
            duration = len(audio) / 1000  # Duration in seconds
            
            if duration <= target_chunk_duration:
                return []  # No need to split
            
            # Detect silent sections
            silent_ranges = self.detect_silence(file_path)
            
            # Find optimal split points
            split_points = []
            current_position = 0
            
            while current_position + target_chunk_duration < duration:
                target_split = current_position + target_chunk_duration
                
                # Find the closest silence to the target split point
                best_split = target_split
                min_distance = float('inf')
                
                for start, end in silent_ranges:
                    silence_center = (start + end) / 2
                    if current_position < silence_center < duration:
                        distance = abs(silence_center - target_split)
                        if distance < min_distance and distance < target_chunk_duration * 0.3:  # Within 30% of target
                            min_distance = distance
                            best_split = silence_center
                
                split_points.append(best_split)
                current_position = best_split
            
            return split_points
            
        except Exception as e:
            logger.error(f"Error suggesting chunk points for {file_path}: {str(e)}")
            return []

class AudioPreprocessor:
    """
    Utility class for preprocessing audio files before transcription.
    """
    
    def __init__(self):
        pass
    
    def normalize_audio(self, input_path: str, output_path: str = None, target_dBFS: float = -20.0) -> str:
        """
        Normalize audio levels to a target dBFS.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            target_dBFS: Target loudness in dBFS
            
        Returns:
            str: Path to normalized audio file
        """
        try:
            from pydub import AudioSegment
            
            if output_path is None:
                output_path = str(Path(input_path).with_stem(f"{Path(input_path).stem}_normalized"))
            
            audio = AudioSegment.from_file(input_path)
            
            # Normalize to target dBFS
            change_in_dBFS = target_dBFS - audio.dBFS
            normalized_audio = audio.apply_gain(change_in_dBFS)
            
            # Export normalized audio
            normalized_audio.export(output_path, format="wav")
            
            logger.info(f"Normalized audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error normalizing audio {input_path}: {str(e)}")
            raise
    
    def reduce_noise(self, input_path: str, output_path: str = None) -> str:
        """
        Apply basic noise reduction to audio file.
        Note: This is a simple implementation. For better results, consider using specialized tools.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            
        Returns:
            str: Path to noise-reduced audio file
        """
        try:
            from pydub import AudioSegment
            from pydub.effects import normalize
            
            if output_path is None:
                output_path = str(Path(input_path).with_stem(f"{Path(input_path).stem}_denoised"))
            
            audio = AudioSegment.from_file(input_path)
            
            # Simple noise reduction: high-pass filter and normalization
            # This removes very low frequencies that are often noise
            audio_filtered = audio.high_pass_filter(80)  # Remove frequencies below 80Hz
            audio_normalized = normalize(audio_filtered)
            
            # Export processed audio
            audio_normalized.export(output_path, format="wav")
            
            logger.info(f"Noise-reduced audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error reducing noise in {input_path}: {str(e)}")
            raise

def main():
    """Example usage of audio utilities."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audio_utils.py <audio_file>")
        sys.exit(1)
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"File not found: {audio_file}")
        sys.exit(1)
    
    # Initialize analyzer
    analyzer = AudioAnalyzer()
    
    # Get audio info
    print("Audio Information:")
    info = analyzer.get_audio_info(audio_file)
    for key, value in info.items():
        if key != "error":
            print(f"  {key}: {value}")
    
    print("\nQuality Analysis:")
    quality_analysis = analyzer.analyze_audio_quality(audio_file)
    if "error" not in quality_analysis:
        print(f"  Quality Score: {quality_analysis['quality_score']}/100")
        print(f"  Quality Rating: {quality_analysis['quality_rating']}")
        print("  Recommendations:")
        for rec in quality_analysis['recommendations']:
            print(f"    - {rec}")
    
    # Create waveform plot
    try:
        plot_path = analyzer.create_waveform_plot(audio_file)
        print(f"\nWaveform plot saved to: {plot_path}")
    except Exception as e:
        print(f"Could not create waveform plot: {e}")

if __name__ == "__main__":
    main()
