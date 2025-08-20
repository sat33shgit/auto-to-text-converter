"""
Web-based Audio to Text Converter using HTML5 and modern web APIs.
This solution works with any Python version and doesn't require problematic audio libraries.
"""

import http.server
import socketserver
import json
import base64
import os
import tempfile
import threading
import webbrowser
import time
import uuid
import shutil
from pathlib import Path
from urllib.parse import parse_qs, urlparse

class AudioToTextWebServer:
    """
    A web-based audio to text converter that uses the browser's built-in capabilities
    and online services for transcription.
    """
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.html_content = self._get_html_content()
        self.processing_jobs = {}  # Store background processing jobs
        self.temp_dir = tempfile.mkdtemp()
        
        # Try to import speech recognition for background processing
        self.speech_recognition_available = False
        self.whisper_available = False
        
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.speech_recognition_available = True
            print("✓ SpeechRecognition available for background processing")
        except ImportError:
            print("! SpeechRecognition not available - using browser-only mode")
        
        try:
            import whisper
            self.whisper = whisper
            self.whisper_available = True
            print("✓ Whisper available for background processing")
        except ImportError:
            print("! Whisper not available - using browser-only mode")
    
    def cleanup(self):
        """Clean up temporary files and resources."""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
    
    def _get_html_content(self):
        """Generate the HTML content for the web interface."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Audio to Text Converter</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        h1 {
            color: #4a5568;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }
        
        .upload-area {
            border: 3px dashed #cbd5e0;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            transition: all 0.3s ease;
            background: #f7fafc;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #e6fffa;
        }
        
        .upload-area input[type="file"] {
            display: none;
        }
        
        .upload-btn {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .upload-btn:hover {
            background: #5a67d8;
            transform: translateY(-2px);
        }
        
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #38a169;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2f855a;
        }
        
        .btn-secondary {
            background: #718096;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4a5568;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .audio-player {
            margin: 20px 0;
            text-align: center;
        }
        
        audio {
            width: 100%;
            max-width: 400px;
        }
        
        .transcription-area {
            margin: 20px 0;
        }
        
        .transcription-area textarea {
            width: 100%;
            min-height: 200px;
            padding: 15px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 16px;
            line-height: 1.5;
            resize: vertical;
        }
        
        .transcription-area textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .status {
            margin: 10px 0;
            padding: 10px;
            border-radius: 6px;
            text-align: center;
        }
        
        .status.success {
            background: #c6f6d5;
            color: #22543d;
        }
        
        .status.error {
            background: #fed7d7;
            color: #742a2a;
        }
        
        .status.info {
            background: #bee3f8;
            color: #2c5282;
        }
        
        .recording-controls {
            text-align: center;
            margin: 20px 0;
        }
        
        .record-btn {
            background: #e53e3e;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 50px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .record-btn.recording {
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .format-info {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
        }
        
        .format-info h3 {
            margin-top: 0;
            color: #4a5568;
        }
        
        .format-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        
        .format-tag {
            background: #667eea;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #667eea;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .engine-selector {
            margin: 15px 0;
            padding: 15px;
            background: #f7fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .engine-selector h4 {
            margin: 0 0 10px 0;
            color: #4a5568;
        }
        
        .radio-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        
        .radio-option {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .radio-option input[type="radio"] {
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Audio to Text Converter</h1>
        
        <div class="format-info">
            <h3>Supported Features:</h3>
            <p>• Upload audio files and convert them to text</p>
            <p>• Record audio directly in your browser</p>
            <p>• 🆕 <strong>Background Processing:</strong> Upload files for server-side conversion</p>
            <p>• Live transcription using browser's Speech Recognition API</p>
            <p>• Multiple engines: Google Speech Recognition, OpenAI Whisper</p>
            <p>• Download transcriptions as text files</p>
            
            <div class="format-list">
                <span class="format-tag">MP3</span>
                <span class="format-tag">WAV</span>
                <span class="format-tag">M4A</span>
                <span class="format-tag">OGG</span>
                <span class="format-tag">WEBM</span>
                <span class="format-tag">FLAC</span>
            </div>
        </div>
        
        <!-- File Upload Section -->
        <div class="upload-area" id="uploadArea">
            <p>📁 Drop audio files here or click to browse</p>
            <input type="file" id="audioFile" accept="audio/*" multiple>
            <button class="upload-btn" onclick="document.getElementById('audioFile').click()">
                Choose Audio Files
            </button>
        </div>
        
        <!-- Audio Player -->
        <div class="audio-player" id="audioPlayer" style="display: none;">
            <audio controls id="audioElement"></audio>
            <p id="fileName"></p>
        </div>
        
        <!-- Recording Section -->
        <div class="recording-controls">
            <button class="record-btn" id="recordBtn" onclick="toggleRecording()">
                🎤 Start Recording
            </button>
            <p id="recordingStatus"></p>
        </div>
        
        <!-- Engine Selection for Background Processing -->
        <div class="engine-selector">
            <h4>Background Processing Engine:</h4>
            <div class="radio-group">
                <div class="radio-option">
                    <input type="radio" id="googleEngine" name="engine" value="google" checked>
                    <label for="googleEngine">Google Speech Recognition (Online)</label>
                </div>
                <div class="radio-option">
                    <input type="radio" id="whisperEngine" name="engine" value="whisper">
                    <label for="whisperEngine">OpenAI Whisper (Offline)</label>
                </div>
                <div class="radio-option">
                    <input type="radio" id="browserEngine" name="engine" value="browser">
                    <label for="browserEngine">Browser API (Live only)</label>
                </div>
            </div>
        </div>
        
        <!-- Control Buttons -->
        <div class="controls">
            <button class="btn btn-primary" id="transcribeBtn" onclick="transcribeAudio()" disabled>
                🔊 Live Transcribe (Browser)
            </button>
            <button class="btn btn-primary" id="backgroundTranscribeBtn" onclick="backgroundTranscribe()" disabled>
                ⚡ Background Convert
            </button>
            <button class="btn btn-secondary" onclick="clearAll()">
                Clear All
            </button>
            <button class="btn btn-secondary" onclick="downloadText()" id="downloadBtn" disabled>
                📥 Download Text
            </button>
        </div>
        
        <!-- Background Processing Status -->
        <div id="backgroundStatus" style="display: none;">
            <div class="status info">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span id="backgroundStatusText">Processing...</span>
                    <div class="spinner"></div>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
        </div>
        
        <!-- Status Display -->
        <div id="status"></div>
        
        <!-- Transcription Area -->
        <div class="transcription-area">
            <h3>Transcription Result:</h3>
            <textarea id="transcriptionText" placeholder="Transcribed text will appear here..."></textarea>
        </div>
    </div>

    <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let currentAudioBlob = null;
        
        // File upload handling
        const uploadArea = document.getElementById('uploadArea');
        const audioFile = document.getElementById('audioFile');
        const audioPlayer = document.getElementById('audioPlayer');
        const audioElement = document.getElementById('audioElement');
        const fileName = document.getElementById('fileName');
        const transcribeBtn = document.getElementById('transcribeBtn');
        const backgroundTranscribeBtn = document.getElementById('backgroundTranscribeBtn');
        const recordBtn = document.getElementById('recordBtn');
        const transcriptionText = document.getElementById('transcriptionText');
        
        let pollInterval = null;
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelection(files[0]);
            }
        });
        
        audioFile.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelection(e.target.files[0]);
            }
        });
        
        function handleFileSelection(file) {
            if (!file.type.startsWith('audio/')) {
                showStatus('Please select an audio file.', 'error');
                return;
            }
            
            const url = URL.createObjectURL(file);
            audioElement.src = url;
            fileName.textContent = file.name;
            audioPlayer.style.display = 'block';
            transcribeBtn.disabled = false;
            backgroundTranscribeBtn.disabled = false;
            currentAudioBlob = file;
            
            showStatus(`Audio file "${file.name}" loaded successfully!`, 'success');
        }
        
        // Recording functionality
        async function toggleRecording() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    
                    mediaRecorder.ondataavailable = (event) => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        const url = URL.createObjectURL(audioBlob);
                        
                        audioElement.src = url;
                        fileName.textContent = 'Recorded Audio';
                        audioPlayer.style.display = 'block';
                        transcribeBtn.disabled = false;
                        backgroundTranscribeBtn.disabled = false;
                        currentAudioBlob = audioBlob;
                        
                        showStatus('Recording completed successfully!', 'success');
                        document.getElementById('recordingStatus').textContent = '';
                    };
                    
                    mediaRecorder.start();
                    isRecording = true;
                    recordBtn.textContent = '⏹️ Stop Recording';
                    recordBtn.classList.add('recording');
                    document.getElementById('recordingStatus').textContent = 'Recording in progress...';
                    showStatus('Recording started...', 'info');
                    
                } catch (error) {
                    showStatus('Error accessing microphone: ' + error.message, 'error');
                }
            } else {
                mediaRecorder.stop();
                mediaRecorder.stream.getTracks().forEach(track => track.stop());
                isRecording = false;
                recordBtn.textContent = '🎤 Start Recording';
                recordBtn.classList.remove('recording');
            }
        }
        
        // Speech Recognition
        function transcribeAudio() {
            if (!currentAudioBlob) {
                showStatus('Please select or record an audio file first.', 'error');
                return;
            }
            
            // Check if browser supports Speech Recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (!SpeechRecognition) {
                showStatus('Speech Recognition is not supported in this browser. Try Chrome or Edge.', 'error');
                return;
            }
            
            showStatus('Starting transcription... Please wait.', 'info');
            transcribeBtn.disabled = true;
            
            // For live audio, we'll use the SpeechRecognition API
            // For uploaded files, we'll provide instructions
            if (currentAudioBlob instanceof File || audioChunks.length > 0) {
                // Play the audio and use speech recognition simultaneously
                transcribeWithSpeechRecognition();
            }
        }
        
        function transcribeWithSpeechRecognition() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            let finalTranscript = '';
            let interimTranscript = '';
            
            recognition.onresult = (event) => {
                interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                transcriptionText.value = finalTranscript + interimTranscript;
            };
            
            recognition.onerror = (event) => {
                showStatus('Speech recognition error: ' + event.error, 'error');
                transcribeBtn.disabled = false;
            };
            
            recognition.onend = () => {
                transcriptionText.value = finalTranscript;
                showStatus('Transcription completed!', 'success');
                transcribeBtn.disabled = false;
                document.getElementById('downloadBtn').disabled = false;
            };
            
            // Play audio and start recognition
            audioElement.play();
            recognition.start();
            
            // Stop recognition when audio ends
            audioElement.onended = () => {
                setTimeout(() => {
                    recognition.stop();
                }, 1000);
            };
            
            showStatus('Transcription in progress... Speak clearly for better results.', 'info');
        }
        
        // Background transcription using server-side processing
        async function backgroundTranscribe() {
            if (!currentAudioBlob) {
                showStatus('Please select or record an audio file first.', 'error');
                return;
            }
            
            const selectedEngine = document.querySelector('input[name="engine"]:checked').value;
            
            if (selectedEngine === 'browser') {
                // Fall back to live transcription
                transcribeAudio();
                return;
            }
            
            showStatus('Starting background transcription...', 'info');
            showBackgroundProgress('Uploading file...', 0);
            
            backgroundTranscribeBtn.disabled = true;
            transcribeBtn.disabled = true;
            
            try {
                // Create FormData for file upload
                const formData = new FormData();
                formData.append('audio', currentAudioBlob, 'audio.wav');
                formData.append('engine', selectedEngine);
                formData.append('language', 'en-US');
                
                // Upload and start processing
                const response = await fetch('/api/transcribe', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }
                
                const result = await response.json();
                
                if (result.success) {
                    const jobId = result.job_id;
                    showBackgroundProgress('Processing audio...', 25);
                    
                    // Start polling for results
                    pollForResults(jobId);
                } else {
                    throw new Error(result.error || 'Unknown error');
                }
                
            } catch (error) {
                showStatus(`Background transcription failed: ${error.message}`, 'error');
                hideBackgroundProgress();
                backgroundTranscribeBtn.disabled = false;
                transcribeBtn.disabled = false;
            }
        }
        
        // Poll server for transcription results
        async function pollForResults(jobId) {
            let progress = 25;
            
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/status/${jobId}`);
                    const result = await response.json();
                    
                    if (result.status === 'completed') {
                        clearInterval(pollInterval);
                        hideBackgroundProgress();
                        
                        if (result.success) {
                            transcriptionText.value = result.text;
                            showStatus('Background transcription completed successfully!', 'success');
                            document.getElementById('downloadBtn').disabled = false;
                        } else {
                            showStatus(`Transcription failed: ${result.error}`, 'error');
                        }
                        
                        backgroundTranscribeBtn.disabled = false;
                        transcribeBtn.disabled = false;
                        
                    } else if (result.status === 'error') {
                        clearInterval(pollInterval);
                        hideBackgroundProgress();
                        showStatus(`Transcription failed: ${result.error}`, 'error');
                        backgroundTranscribeBtn.disabled = false;
                        transcribeBtn.disabled = false;
                        
                    } else {
                        // Still processing
                        progress = Math.min(progress + 5, 90);
                        showBackgroundProgress('Processing audio...', progress);
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    hideBackgroundProgress();
                    showStatus(`Error checking transcription status: ${error.message}`, 'error');
                    backgroundTranscribeBtn.disabled = false;
                    transcribeBtn.disabled = false;
                }
            }, 2000); // Poll every 2 seconds
        }
        
        // Show background processing progress
        function showBackgroundProgress(message, percent) {
            const backgroundStatus = document.getElementById('backgroundStatus');
            const backgroundStatusText = document.getElementById('backgroundStatusText');
            const progressFill = document.getElementById('progressFill');
            
            backgroundStatus.style.display = 'block';
            backgroundStatusText.textContent = message;
            progressFill.style.width = `${percent}%`;
        }
        
        // Hide background processing progress
        function hideBackgroundProgress() {
            const backgroundStatus = document.getElementById('backgroundStatus');
            backgroundStatus.style.display = 'none';
            
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        }
        
        function clearAll() {
            transcriptionText.value = '';
            audioElement.src = '';
            audioPlayer.style.display = 'none';
            fileName.textContent = '';
            transcribeBtn.disabled = true;
            backgroundTranscribeBtn.disabled = true;
            document.getElementById('downloadBtn').disabled = true;
            currentAudioBlob = null;
            audioFile.value = '';
            document.getElementById('status').innerHTML = '';
            hideBackgroundProgress();
        }
        
        function downloadText() {
            const text = transcriptionText.value;
            if (!text.trim()) {
                showStatus('No text to download.', 'error');
                return;
            }
            
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'transcription.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showStatus('Transcription downloaded successfully!', 'success');
        }
        
        function showStatus(message, type) {
            const status = document.getElementById('status');
            status.innerHTML = `<div class="status ${type}">${message}</div>`;
            
            // Auto-hide after 5 seconds for success/info messages
            if (type === 'success' || type === 'info') {
                setTimeout(() => {
                    status.innerHTML = '';
                }, 5000);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            showStatus('Audio to Text Converter loaded successfully!', 'success');
        });
    </script>
</body>
</html>
        """
    
    def start_server(self):
        """Start the web server."""
        handler = self._create_handler()
        
        try:
            self.server = socketserver.TCPServer(("", self.port), handler)
            print(f"Audio to Text Converter started!")
            print(f"Open your browser and go to: http://localhost:{self.port}")
            print("Press Ctrl+C to stop the server")
            
            # Automatically open browser
            threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{self.port}")).start()
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            print("\nServer stopped.")
        except Exception as e:
            print(f"Error starting server: {e}")
        finally:
            if self.server:
                self.server.shutdown()
            self.cleanup()
    
    def _process_audio_background(self, job_id, audio_data, engine, language):
        """Process audio in background thread."""
        try:
            print(f"Starting background processing for job {job_id} with engine {engine}")
            
            # Save audio data to temporary file
            temp_file = os.path.join(self.temp_dir, f"{job_id}.wav")
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            print(f"Audio data saved to {temp_file}, size: {len(audio_data)} bytes")
            
            self.processing_jobs[job_id]['status'] = 'processing'
            self.processing_jobs[job_id]['progress'] = 50
            
            # Process based on engine
            if engine == 'whisper' and self.whisper_available:
                try:
                    print(f"Loading Whisper model for job {job_id}")
                    model = self.whisper.load_model("base")
                    print(f"Transcribing with Whisper for job {job_id}")
                    result = model.transcribe(temp_file)
                    text = result["text"].strip()
                    
                    print(f"Whisper transcription completed for job {job_id}: {text[:100]}...")
                    
                    self.processing_jobs[job_id].update({
                        'status': 'completed',
                        'success': True,
                        'text': text,
                        'progress': 100
                    })
                except Exception as e:
                    print(f"Whisper error for job {job_id}: {str(e)}")
                    self.processing_jobs[job_id].update({
                        'status': 'error',
                        'success': False,
                        'error': f"Whisper processing failed: {str(e)}"
                    })
            
            elif engine == 'google' and self.speech_recognition_available:
                try:
                    print(f"Processing with Google Speech Recognition for job {job_id}")
                    with self.sr.AudioFile(temp_file) as source:
                        self.recognizer.adjust_for_ambient_noise(source)
                        audio = self.recognizer.record(source)
                    
                    text = self.recognizer.recognize_google(audio, language=language)
                    print(f"Google transcription completed for job {job_id}: {text[:100]}...")
                    
                    self.processing_jobs[job_id].update({
                        'status': 'completed',
                        'success': True,
                        'text': text,
                        'progress': 100
                    })
                except self.sr.UnknownValueError:
                    print(f"Google Speech Recognition could not understand audio for job {job_id}")
                    self.processing_jobs[job_id].update({
                        'status': 'completed',
                        'success': False,
                        'error': "Could not understand audio - try speaking more clearly or use a different audio file"
                    })
                except self.sr.RequestError as e:
                    print(f"Google Speech Recognition error for job {job_id}: {str(e)}")
                    self.processing_jobs[job_id].update({
                        'status': 'error',
                        'success': False,
                        'error': f"Google Speech Recognition error: {str(e)}"
                    })
                except Exception as e:
                    print(f"Google processing error for job {job_id}: {str(e)}")
                    self.processing_jobs[job_id].update({
                        'status': 'error',
                        'success': False,
                        'error': f"Processing failed: {str(e)}"
                    })
            
            else:
                error_msg = f"Engine '{engine}' not available. Available engines: {', '.join([e for e, a in [('google', self.speech_recognition_available), ('whisper', self.whisper_available)] if a])}"
                print(f"Engine error for job {job_id}: {error_msg}")
                self.processing_jobs[job_id].update({
                    'status': 'error',
                    'success': False,
                    'error': error_msg
                })
            
            # Clean up temporary file
            try:
                os.remove(temp_file)
                print(f"Cleaned up temp file for job {job_id}")
            except Exception as e:
                print(f"Warning: Could not clean up temp file for job {job_id}: {e}")
                
        except Exception as e:
            print(f"Unexpected error in background processing for job {job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            self.processing_jobs[job_id].update({
                'status': 'error',
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            })
    def _create_handler(self):
        """Create the HTTP request handler."""
        html_content = self.html_content
        server_instance = self
        
        class AudioToTextHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/' or self.path == '':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(html_content.encode())
                    
                elif self.path.startswith('/api/status/'):
                    # Get job status
                    job_id = self.path.split('/')[-1]
                    
                    if job_id in server_instance.processing_jobs:
                        job_info = server_instance.processing_jobs[job_id]
                        response = json.dumps(job_info)
                    else:
                        response = json.dumps({
                            'status': 'error',
                            'error': 'Job not found'
                        })
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(response.encode())
                    
                else:
                    super().do_GET()
            
            def do_POST(self):
                if self.path == '/api/transcribe':
                    try:
                        # Parse multipart form data
                        content_type = self.headers.get('content-type', '')
                        if not content_type.startswith('multipart/form-data'):
                            self.send_error(400, "Expected multipart/form-data")
                            return
                        
                        # Get content length
                        content_length = int(self.headers.get('Content-Length', 0))
                        if content_length == 0:
                            self.send_error(400, "No content received")
                            return
                        
                        # Read the form data
                        form_data = self.rfile.read(content_length)
                        
                        # Parse boundary
                        boundary_match = content_type.split('boundary=')
                        if len(boundary_match) < 2:
                            self.send_error(400, "No boundary in content-type")
                            return
                        
                        boundary = boundary_match[1].split(';')[0].strip()
                        boundary = boundary.encode()
                        
                        # Split by boundary
                        parts = form_data.split(b'--' + boundary)
                        
                        audio_data = None
                        engine = 'google'
                        language = 'en-US'
                        
                        for part in parts:
                            if len(part) < 10:  # Skip empty parts
                                continue
                                
                            part_str = part.decode('utf-8', errors='ignore')
                            
                            if 'name="audio"' in part_str:
                                # Find the start of binary data
                                header_end = part.find(b'\r\n\r\n')
                                if header_end == -1:
                                    header_end = part.find(b'\n\n')
                                    if header_end != -1:
                                        header_end += 2
                                else:
                                    header_end += 4
                                
                                if header_end > 0:
                                    audio_data = part[header_end:].rstrip(b'\r\n').rstrip(b'\n')
                                    # Remove trailing boundary markers
                                    if audio_data.endswith(b'--'):
                                        audio_data = audio_data[:-2].rstrip(b'\r\n')
                            
                            elif 'name="engine"' in part_str:
                                # Extract engine value
                                lines = part_str.split('\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == '' and i < len(lines) - 1:
                                        engine = lines[i + 1].strip()
                                        break
                            
                            elif 'name="language"' in part_str:
                                # Extract language value
                                lines = part_str.split('\n')
                                for i, line in enumerate(lines):
                                    if line.strip() == '' and i < len(lines) - 1:
                                        language = lines[i + 1].strip()
                                        break
                        
                        if not audio_data or len(audio_data) < 100:
                            raise ValueError("No valid audio data received")
                        
                        # Create job ID
                        job_id = str(uuid.uuid4())
                        
                        # Initialize job
                        server_instance.processing_jobs[job_id] = {
                            'status': 'queued',
                            'progress': 0,
                            'engine': engine,
                            'language': language,
                            'created_at': time.time()
                        }
                        
                        # Start processing in background
                        thread = threading.Thread(
                            target=server_instance._process_audio_background,
                            args=(job_id, audio_data, engine, language)
                        )
                        thread.daemon = True
                        thread.start()
                        
                        # Return job ID
                        response = json.dumps({
                            'success': True,
                            'job_id': job_id,
                            'message': 'Processing started'
                        })
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(response.encode())
                        
                    except Exception as e:
                        # Log the full error for debugging
                        print(f"Error in /api/transcribe: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        
                        error_response = json.dumps({
                            'success': False,
                            'error': str(e)
                        })
                        
                        self.send_response(500)
                        self.send_header('Content-type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(error_response.encode())
                
                else:
                    self.send_error(404)
            
            def do_OPTIONS(self):
                # Handle CORS preflight requests
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def log_message(self, format, *args):
                # Suppress default logging except for errors
                if 'POST /api/' in format % args or 'GET /api/' in format % args:
                    print(f"API: {format % args}")
        
        return AudioToTextHandler

def main():
    """Main function to start the web server."""
    print("Web-based Audio to Text Converter")
    print("=" * 40)
    print("This version works in your web browser and doesn't require")
    print("any problematic Python audio libraries!")
    print()
    
    try:
        port = 8080
        server = AudioToTextWebServer(port)
        server.start_server()
    except Exception as e:
        print(f"Error: {e}")
        print("Try running on a different port or check if port 8080 is already in use.")

if __name__ == "__main__":
    main()
