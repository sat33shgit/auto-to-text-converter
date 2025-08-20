# 🎤 Enhanced Audio to Text Converter

A powerful web-based application that converts audio files to text using OpenAI Whisper, with support for both file upload and live real-time transcription.

## ✨ Features

### 📁 File Upload Transcription
- **Drag & Drop Interface**: Simply drag audio files onto the upload area
- **Multiple Format Support**: MP3, WAV, FLAC, M4A, OGG, WEBM
- **Background Processing**: Transcription happens in the background with progress indicators
- **Audio Preview**: Listen to uploaded files before transcription
- **Download Results**: Save transcribed text as .txt files
- **Copy to Clipboard**: One-click copying functionality

### 🎙️ Live Real-time Transcription
- **Real-time Speech Recognition**: Speak into your microphone for instant transcription
- **Continuous Recording**: Processes audio in 3-second chunks for near real-time results
- **Live Display**: See your words appear as you speak
- **Browser-based**: No additional software needed - works directly in your web browser
- **Noise Cancellation**: Built-in echo cancellation and noise suppression
- **Save Live Transcripts**: Download or copy live transcription results

### 🛠️ Technical Features
- **OpenAI Whisper Integration**: Uses state-of-the-art speech recognition
- **Offline Processing**: No internet required after initial setup
- **Cross-browser Compatible**: Works in Chrome, Firefox, Edge, and other modern browsers
- **Responsive Design**: Beautiful interface that works on desktop and mobile
- **Zero External Dependencies**: Only uses Python standard library + Whisper

## 🚀 Quick Start

### Option 1: Use the Batch File (Easiest)
1. Double-click `start_enhanced_converter.bat`
2. Open http://localhost:8080 in your browser
3. Start transcribing!

### Option 2: Manual Start
```bash
cd "c:\Sateesh\Projects\AutoToText"
python enhanced_web_converter.py
```

Then open http://localhost:8080 in your browser.

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Modern web browser with microphone access support
- At least 2GB RAM (for Whisper model)
- Internet connection (for initial Whisper model download)

### Python Dependencies
The application will automatically check for requirements. If needed, install:
```bash
pip install openai-whisper
```

Optional (for creating test audio files):
```bash
pip install pyttsx3
```

## 🎯 How to Use

### File Upload Transcription
1. **Start the Application**: Run the batch file or Python script
2. **Open Web Interface**: Navigate to http://localhost:8080
3. **Select File Upload Tab**: Click on the "📁 File Upload" tab
4. **Upload Audio**: 
   - Drag and drop an audio file onto the upload area, OR
   - Click the upload area to browse and select a file
5. **Preview Audio**: Use the audio player to preview your file
6. **Transcribe**: Click "🎵 Convert with Whisper"
7. **Wait for Processing**: Watch the progress bar as transcription completes
8. **Get Results**: 
   - View transcribed text in the text area
   - Download as .txt file using "💾 Download as TXT"
   - Copy to clipboard with "📋 Copy to Clipboard"

### Live Real-time Transcription
1. **Select Live Tab**: Click on the "🎙️ Live Transcription" tab
2. **Start Recording**: Click "🎤 Start Live Transcription"
3. **Grant Permissions**: Allow microphone access when prompted
4. **Speak Clearly**: Talk into your microphone - text will appear in real-time
5. **Stop Recording**: Click "⏸️ Stop Recording" when finished
6. **Save Results**:
   - Clear transcript with "🗑️ Clear Transcript"
   - Save with "💾 Save Transcript" 
   - Copy with "📋 Copy to Clipboard"

## 🎵 Supported Audio Formats

- **MP3** (.mp3) - Most common format
- **WAV** (.wav) - Uncompressed audio
- **FLAC** (.flac) - Lossless compression
- **M4A** (.m4a) - iTunes/Apple format
- **OGG** (.ogg) - Open source format
- **WEBM** (.webm) - Web-optimized format

## 🔧 Technical Details

### Architecture
- **Backend**: Python HTTP server with threading for background processing
- **Frontend**: Vanilla HTML/CSS/JavaScript with modern Web APIs
- **Speech Recognition**: OpenAI Whisper (offline processing)
- **Audio Handling**: Browser MediaRecorder API for live capture
- **Data Transfer**: JSON with base64 encoding for audio data

### File Structure
```
AutoToText/
├── enhanced_web_converter.py      # Main application
├── simple_web_converter.py        # Simplified version (backup)
├── start_enhanced_converter.bat   # Quick start batch file
├── enhanced_requirements.txt      # Dependencies list
├── create_test_audio.py          # Test file generator
├── ENHANCED_README.md            # This file
└── example_usage.py              # CLI examples
```

### Performance Notes
- **First Use**: Whisper will download its model (~39MB for base model) on first use
- **Processing Speed**: Depends on audio length and computer performance
- **Memory Usage**: ~500MB-2GB depending on audio file size and model
- **Live Transcription**: Processes in 3-second chunks with ~500ms delay

## 🆚 Version Comparison

| Feature | Simple Version | Enhanced Version |
|---------|---------------|------------------|
| File Upload | ✅ | ✅ |
| Background Processing | ✅ | ✅ |
| Download Results | ✅ | ✅ |
| Live Transcription | ❌ | ✅ |
| Real-time Audio | ❌ | ✅ |
| Tabbed Interface | ❌ | ✅ |
| Enhanced UI | ❌ | ✅ |
| Microphone Integration | ❌ | ✅ |

## 🛠️ Troubleshooting

### Common Issues

**Whisper Not Available**
- Install with: `pip install openai-whisper`
- Ensure you're using the correct Python environment

**Microphone Access Denied**
- Check browser permissions for microphone access
- Try using HTTPS (some browsers require secure connection)
- Ensure no other applications are using the microphone

**Server Won't Start**
- Check if port 8080 is already in use
- Try stopping with `taskkill /f /im python.exe` and restart
- Verify Python installation and path

**Live Transcription Not Working**
- Use a modern browser (Chrome, Firefox, Edge)
- Ensure microphone permissions are granted
- Check that WebRTC/MediaRecorder is supported

**Poor Transcription Quality**
- Use better quality audio files
- Speak clearly and reduce background noise
- Consider using a higher quality Whisper model (edit the code to use "small", "medium", or "large")

### Browser Compatibility
- ✅ **Chrome 60+**: Full support
- ✅ **Firefox 70+**: Full support  
- ✅ **Edge 79+**: Full support
- ✅ **Safari 14+**: Full support
- ❌ **Internet Explorer**: Not supported

## 🎨 Customization

### Using Different Whisper Models
Edit `enhanced_web_converter.py` and change the model size:
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
Modify the server address in the `main()` function:
```python
server_address = ('localhost', 8080)  # Change 8080 to your preferred port
```

### Recording Chunk Size
Modify the live recording duration in the JavaScript:
```javascript
setTimeout(() => {
    // Change 3000 to your preferred milliseconds
}, 3000);
```

## 📈 Future Enhancements

Possible future features:
- Multiple language support
- Custom vocabulary/domain-specific models
- Batch file processing
- Integration with cloud storage
- Advanced audio preprocessing
- Speaker identification
- Timestamps and word-level timing
- Export to various formats (SRT, VTT, etc.)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all requirements are installed
3. Ensure your browser supports the required features
4. Check the terminal output for error messages

## 📄 License

This project is for educational and personal use. OpenAI Whisper is subject to its own license terms.

---

**Enjoy your enhanced audio to text conversion experience!** 🎉
