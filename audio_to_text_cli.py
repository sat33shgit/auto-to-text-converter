#!/usr/bin/env python3
"""
Command-line interface for Audio to Text Converter.
Provides batch processing capabilities and command-line arguments.
"""

import argparse
import os
import sys
from pathlib import Path
import json
from audio_converter import AudioToTextConverter

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert audio files to text using speech recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audio_to_text_cli.py --input audio.mp3 --output transcription.txt
  python audio_to_text_cli.py --input ./audio_files/ --output ./transcriptions/ --engine whisper
  python audio_to_text_cli.py --input audio.wav --engine google --language es-ES --chunk
        """
    )
    
    # Input/Output arguments
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Input audio file or directory containing audio files"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output text file or directory (default: same as input with .txt extension)"
    )
    
    # Engine options
    parser.add_argument(
        "--engine", "-e",
        choices=["google", "whisper"],
        default="google",
        help="Speech recognition engine to use (default: google)"
    )
    
    parser.add_argument(
        "--language", "-l",
        default="en-US",
        help="Language code for recognition (default: en-US)"
    )
    
    # Processing options
    parser.add_argument(
        "--chunk",
        action="store_true",
        help="Split long audio files into chunks for better recognition"
    )
    
    parser.add_argument(
        "--whisper-model",
        choices=["tiny", "base", "small", "medium", "large"],
        default="base",
        help="Whisper model size to use (default: base)"
    )
    
    # Output options
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate JSON summary report"
    )
    
    parser.add_argument(
        "--format",
        choices=["txt", "json", "both"],
        default="txt",
        help="Output format (default: txt)"
    )
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = AudioToTextConverter()
    
    # Load Whisper model if needed
    if args.engine == "whisper":
        print(f"Loading Whisper model '{args.whisper_model}'...")
        if not converter.load_whisper_model(args.whisper_model):
            print("Error: Failed to load Whisper model. Make sure it's installed.")
            sys.exit(1)
        print("Whisper model loaded successfully.")
    
    # Determine input type (file or directory)
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"Error: Input path '{args.input}' does not exist.")
        sys.exit(1)
    
    results = []
    
    if input_path.is_file():
        # Single file processing
        if args.verbose:
            print(f"Processing file: {input_path}")
        
        result = converter.transcribe_file(
            str(input_path),
            engine=args.engine,
            language=args.language,
            chunk_audio=args.chunk
        )
        
        results.append(result)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix('.txt')
        
        # Save results
        if result["success"]:
            # Save text output
            if args.format in ["txt", "both"]:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['text'])
                print(f"Transcription saved to: {output_path}")
            
            # Save JSON output
            if args.format in ["json", "both"]:
                json_path = output_path.with_suffix('.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Result data saved to: {json_path}")
            
            if args.verbose:
                print(f"Transcribed text: {result['text'][:200]}...")
        else:
            print(f"Error processing {input_path}: {result['error']}")
    
    else:
        # Directory processing
        if args.verbose:
            print(f"Processing directory: {input_path}")
        
        # Determine output directory
        if args.output:
            output_dir = Path(args.output)
        else:
            output_dir = input_path / "transcriptions"
        
        output_dir.mkdir(exist_ok=True)
        
        # Find all audio files
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(input_path.glob(f"*{ext}"))
            audio_files.extend(input_path.glob(f"*{ext.upper()}"))
        
        if not audio_files:
            print(f"No audio files found in {input_path}")
            sys.exit(1)
        
        print(f"Found {len(audio_files)} audio files to process...")
        
        # Process each file
        for i, audio_file in enumerate(audio_files, 1):
            if args.verbose:
                print(f"Processing {i}/{len(audio_files)}: {audio_file.name}")
            else:
                print(f"Progress: {i}/{len(audio_files)}")
            
            result = converter.transcribe_file(
                str(audio_file),
                engine=args.engine,
                language=args.language,
                chunk_audio=args.chunk
            )
            
            results.append(result)
            
            # Save individual results
            if result["success"]:
                # Save text output
                if args.format in ["txt", "both"]:
                    output_file = output_dir / f"{audio_file.stem}.txt"
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(result['text'])
                
                # Save JSON output
                if args.format in ["json", "both"]:
                    json_file = output_dir / f"{audio_file.stem}.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                
                if args.verbose:
                    print(f"  Success: {result['text'][:100]}...")
            else:
                if args.verbose:
                    print(f"  Error: {result['error']}")
    
    # Generate summary report
    if args.summary or len(results) > 1:
        summary = {
            "total_files": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "engine": args.engine,
            "language": args.language,
            "results": results
        }
        
        if input_path.is_file():
            summary_file = Path(args.output or input_path.with_suffix('.json'))
            if summary_file.suffix != '.json':
                summary_file = summary_file.with_name(f"{summary_file.stem}_summary.json")
        else:
            summary_file = output_dir / "transcription_summary.json"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Summary report saved to: {summary_file}")
    
    # Print final statistics
    successful = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nConversion completed!")
    print(f"Total files: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    
    if successful < total:
        print("\nFailed files:")
        for result in results:
            if not result["success"]:
                print(f"  {Path(result['file_path']).name}: {result['error']}")

if __name__ == "__main__":
    main()
