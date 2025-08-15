# 🎵 Audio to Text Converter

A simple, clean web-based application that converts audio files to text using OpenAI Whisper.

## ✨ Features

- **🎵 File Upload**: Drag & drop or click to select audio files
- **🎧 Audio Preview**: Listen to files before converting
- **⚡ Background Processing**: Conversion happens in the background with progress tracking
- **📁 Multiple Formats**: Supports MP3, WAV, FLAC, M4A, OGG, WEBM
- **💾 Smart Download**: Save transcripts with timestamps (e.g., `transcript_2025-08-15T10-30-45.txt`)
- **📋 Copy to Clipboard**: One-click copying functionality
- **🗑️ Clear Text**: Easy transcript clearing with confirmation
- **🌐 Web Interface**: Clean, responsive design that works in any modern browser
- **🔒 Offline Processing**: Uses Whisper locally - no internet required after setup

## 🚀 Quick Start

### Option 1: Use the Batch File (Easiest)
```bash
Double-click: start_working_converter.bat
```

### Option 2: Manual Start
```bash
python working_converter.py
```

Then open **http://localhost:8081** in your browser.

## 📋 Requirements

- **Python 3.8+**
- **OpenAI Whisper** (automatically installed)
- **Modern web browser**
- **2GB+ RAM** (for Whisper model)

### Installation
```bash
pip install openai-whisper
```

Optional (for creating test files):
```bash
pip install pyttsx3
```

## 🎯 How to Use

1. **Start the Application**
   - Run `start_working_converter.bat` or `python working_converter.py`
   - Open http://localhost:8081 in your browser

2. **Upload Audio File**
   - Drag and drop a file onto the upload area, OR
   - Click the upload area to browse and select a file

3. **Preview Audio** (Optional)
   - Use the audio player to preview your file

4. **Convert**
   - Click "🎵 Convert with Whisper"
   - Watch the progress bar as conversion completes

5. **Get Results**
   - View transcribed text in the text area
   - **💾 Download as TXT**: Save with automatic timestamp
   - **📋 Copy to Clipboard**: Copy text for use elsewhere
   - **🗑️ Clear Text**: Clear to start fresh

## 📁 Supported Audio Formats

- **MP3** (.mp3) - Most common format
- **WAV** (.wav) - Uncompressed audio  
- **FLAC** (.flac) - Lossless compression
- **M4A** (.m4a) - iTunes/Apple format
- **OGG** (.ogg) - Open source format
- **WEBM** (.webm) - Web-optimized format

## 🔧 Project Structure

```
AutoToText/
├── working_converter.py          # Main application
├── start_working_converter.bat   # Quick start batch file
├── requirements.txt              # Python dependencies  
├── README.md                    # This file
├── setup.bat                    # Setup script
├── create_test_audio.py         # Test audio file generator
└── sample_test_audio.wav        # Sample audio for testing
```

## 🛠️ Technical Details

- **Backend**: Python HTTP server with threading
- **Frontend**: Clean HTML/CSS/JavaScript interface
- **Speech Engine**: OpenAI Whisper (base model by default)
- **Audio Processing**: Browser-native + Whisper transcription
- **File Handling**: Base64 encoding for secure transfer

## 🎨 Customization

### Using Different Whisper Models
Edit `working_converter.py` and change the model:
```python
model = whisper.load_model("base")  # Options: tiny, base, small, medium, large
```

**Model Comparison:**
- `tiny`: Fastest, least accurate (~39 MB)
- `base`: Good balance (~74 MB) - **Default**
- `small`: Better accuracy (~244 MB) 
- `medium`: High accuracy (~769 MB)
- `large`: Best accuracy (~1550 MB)

### Changing Port
Modify the server address:
```python
server_address = ('localhost', 8081)  # Change 8081 to your preferred port
```

## 🔍 Troubleshooting

**Whisper Not Available**
```bash
pip install openai-whisper
```

**Server Won't Start**
- Check if port 8081 is in use
- Try `taskkill /f /im python.exe` then restart

**Poor Transcription Quality**
- Use higher quality audio files
- Speak clearly with less background noise
- Consider using a larger Whisper model

**First-time Slow**
- Whisper downloads its model (~74MB) on first use
- Subsequent uses are much faster

## 📈 Performance Notes

- **First Use**: Downloads Whisper model (one-time ~74MB)
- **Processing Speed**: Depends on audio length and hardware
- **Memory Usage**: ~500MB-2GB depending on file size
- **Accuracy**: Very high with clear audio

## 📄 License

This project is for educational and personal use. OpenAI Whisper is subject to its own license terms.

---

**Enjoy your simple, powerful audio-to-text converter!** 🎉
2. Open your browser and go to: `http://localhost:8080`
3. Upload audio files or record directly in the browser
4. Click "Convert to Text" to get transcription

### **Windows Users**
Double-click `run_web.bat` to start the web application automatically.

## 📋 Features

### Web-based Interface
- ✅ **Works with any Python version** (no dependency issues)
- ✅ Upload audio files (MP3, WAV, M4A, OGG, WEBM)
- ✅ Record audio directly in browser
- ✅ Real-time speech recognition
- ✅ Download transcriptions as text files
- ✅ Modern, responsive interface
- ✅ Works in Chrome, Edge, Firefox, Safari

### Advanced Features (requires additional setup)
- 🔧 Multiple speech recognition engines (Google, Whisper)
- 🔧 Batch processing of multiple files
- 🔧 Audio analysis and quality assessment
- 🔧 Command-line interface
- 🔧 GUI desktop application

## 📦 Installation

### Method 1: Web-based (Recommended)
**No additional packages required!** Just Python 3.7+

```bash
git clone <this-repository>
cd AutoToText
python web_converter.py
```

### Method 2: Full Installation
For advanced features, install additional dependencies:

```bash
# Windows
setup.bat

# Or manually
pip install speechrecognition pydub numpy matplotlib openai-whisper
```

## 🎯 Usage

### Web Interface
1. **Start the server:**
   ```bash
   python web_converter.py
   ```

2. **Upload audio or record:**
   - Drag & drop audio files
   - Or click "Choose Audio Files"
   - Or use "Start Recording" for live audio

3. **Transcribe:**
   - Click "Convert to Text"
   - Wait for transcription to complete
   - Edit and download the result

### Command Line (Advanced)
```bash
# Single file
python audio_to_text_cli.py --input "audio.mp3" --output "transcription.txt"

# Batch processing
python audio_to_text_cli.py --input "audio_folder/" --output "transcriptions/"

# Using Whisper
python audio_to_text_cli.py --input "audio.wav" --engine whisper
```

### Desktop GUI (Advanced)
```bash
python audio_to_text_gui.py
```

## 🎵 Supported Formats

- **MP3** - Most common format
- **WAV** - Uncompressed, best quality
- **M4A** - Apple format
- **OGG** - Open source format
- **WEBM** - Web format
- **FLAC** - Lossless compression
- **AAC** - Advanced Audio Coding

## 🔧 Troubleshooting

### Web Version Issues
- **"Speech Recognition not supported"**: Use Chrome or Edge browser
- **Microphone access denied**: Allow microphone permissions in browser
- **Port already in use**: Try different port: `python web_converter.py --port 8081`

### Python Version Issues
If you get import errors with older Python installations:
1. Use the web version (`python web_converter.py`)
2. Or update to Python 3.9+
3. Or use the simple converter (`python simple_converter.py`)

### Audio Quality Tips
- Use mono audio for better recognition
- 16kHz sample rate is optimal
- Clear speech with minimal background noise
- Shorter clips (< 5 minutes) work better

## 📁 Project Structure

```
AutoToText/
├── web_converter.py          # 🌟 Web-based converter (recommended)
├── simple_converter.py       # Basic converter for any Python version
├── audio_converter.py        # Full-featured converter
├── audio_to_text_gui.py     # Desktop GUI application
├── audio_to_text_cli.py     # Command-line interface
├── audio_utils.py           # Audio analysis utilities
├── example_usage.py         # Usage examples
├── setup.py                 # Installation script
├── test_installation.py     # Test script
├── run_web.bat             # Windows launcher for web version
├── setup.bat               # Windows setup script
└── requirements.txt        # Dependencies list
```

## 🆘 Support

### Getting Help
1. **For web version**: Check browser console (F12) for errors
2. **For desktop version**: Run `python test_installation.py`
3. **For setup issues**: Run `python setup.py`

### Common Solutions
- **Import errors**: Use web version or update Python
- **Audio not recognized**: Check audio quality and format
- **Server won't start**: Check if port 8080 is available

## 🔐 Privacy

- **Web version**: All processing happens in your browser
- **Desktop version**: All processing happens on your computer
- **No data is sent to external servers** (except Google Speech API if used)

## 📄 License

MIT License - feel free to use and modify!

---

## 🎉 Quick Test

1. Run: `python web_converter.py`
2. Open: `http://localhost:8080`
3. Click "Start Recording"
4. Say: "Hello, this is a test"
5. Click "Stop Recording"
6. Click "Convert to Text"
7. See your text appear!

**That's it! You now have a working audio-to-text converter!** 🎊
