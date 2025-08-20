"""
Enhanced Audio to Text Converter with Live Transcription
Combines file upload functionality with real-time microphone transcription
"""

import json
import base64
import threading
import queue
import time
import os
import tempfile
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Try to import Whisper at module level
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✓ Whisper imported successfully")
except ImportError:
    WHISPER_AVAILABLE = False
    print("⚠ Warning: Whisper not available")

# Global variables for managing transcription jobs and live audio
transcription_jobs = {}
job_counter = 0
job_lock = threading.Lock()

# Live transcription variables
live_transcription_active = False
live_transcript_buffer = []
live_audio_queue = queue.Queue()

class AudioTranscriptionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/' or path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(self.generate_html().encode())
            elif path == '/api/job_status':
                # Get job status
                query_params = parse_qs(parsed_url.query)
                job_id = query_params.get('job_id', [None])[0]
                
                if job_id and job_id in transcription_jobs:
                    job = transcription_jobs[job_id]
                    response = {
                        'status': job['status'],
                        'progress': job.get('progress', 0),
                        'result': job.get('result', ''),
                        'error': job.get('error', '')
                    }
                else:
                    response = {'status': 'not_found', 'error': 'Job not found'}
                
                self.send_json_response(response)
            elif path == '/api/live_status':
                # Get live transcription status
                global live_transcription_active, live_transcript_buffer
                response = {
                    'active': live_transcription_active,
                    'transcript': ' '.join(live_transcript_buffer)
                }
                self.send_json_response(response)
            else:
                self.send_error(404)
        except Exception as e:
            print(f"GET Error: {e}")
            self.send_error(500)

    def do_POST(self):
        """Handle POST requests."""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/api/transcribe':
                self.handle_file_transcription()
            elif path == '/api/live_start':
                self.handle_live_start()
            elif path == '/api/live_stop':
                self.handle_live_stop()
            elif path == '/api/live_audio':
                self.handle_live_audio()
            else:
                self.send_error(404)
        except Exception as e:
            print(f"POST Error: {e}")
            traceback.print_exc()
            self.send_error(500)

    def handle_file_transcription(self):
        """Handle file upload and transcription."""
        global job_counter
        
        # Read the JSON data
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = json.loads(post_data)
        
        # Extract audio data
        audio_data = base64.b64decode(data['audio'])
        filename = data.get('filename', 'audio.wav')
        
        # Create job
        with job_lock:
            job_counter += 1
            job_id = str(job_counter)
            transcription_jobs[job_id] = {
                'status': 'processing',
                'progress': 0,
                'filename': filename
            }
        
        # Start transcription in background
        thread = threading.Thread(
            target=self.transcribe_audio_file,
            args=(job_id, audio_data, filename)
        )
        thread.daemon = True
        thread.start()
        
        # Return job ID
        response = {'job_id': job_id, 'status': 'started'}
        self.send_json_response(response)

    def handle_live_start(self):
        """Start live transcription."""
        global live_transcription_active, live_transcript_buffer
        
        try:
            live_transcription_active = True
            live_transcript_buffer = []
            
            # Note: In a real implementation, you would start audio capture here
            # For now, we'll simulate it
            print("Live transcription started")
            
            response = {'status': 'started', 'message': 'Live transcription activated'}
            self.send_json_response(response)
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            self.send_json_response(response)

    def handle_live_stop(self):
        """Stop live transcription."""
        global live_transcription_active
        
        try:
            live_transcription_active = False
            print("Live transcription stopped")
            
            response = {'status': 'stopped', 'message': 'Live transcription deactivated'}
            self.send_json_response(response)
        except Exception as e:
            response = {'status': 'error', 'message': str(e)}
            self.send_json_response(response)

    def handle_live_audio(self):
        """Handle live audio data from browser."""
        global live_transcript_buffer
        
        try:
            # Read the JSON data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # Extract audio data
            audio_data = base64.b64decode(data['audio'])
            
            # Process audio with Whisper
            if WHISPER_AVAILABLE:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_file.write(audio_data)
                    temp_path = temp_file.name
                
                try:
                    # Load model and transcribe
                    model = whisper.load_model("base")
                    result = model.transcribe(temp_path)
                    text = result["text"].strip()
                    
                    if text:
                        live_transcript_buffer.append(text)
                        # Keep only last 50 segments to avoid memory issues
                        if len(live_transcript_buffer) > 50:
                            live_transcript_buffer = live_transcript_buffer[-50:]
                    
                    response = {'status': 'success', 'text': text}
                    
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_path)
                    except:
                        pass
            else:
                response = {'status': 'error', 'message': 'Whisper not available'}
            
            self.send_json_response(response)
            
        except Exception as e:
            print(f"Live audio processing error: {e}")
            response = {'status': 'error', 'message': str(e)}
            self.send_json_response(response)

    def transcribe_audio_file(self, job_id, audio_data, filename):
        """Transcribe audio file in background thread."""
        temp_path = None
        try:
            print(f"Starting transcription for job {job_id}, file: {filename}")
            
            # Update progress
            transcription_jobs[job_id]['progress'] = 10
            
            # Check if Whisper is available at module level
            if not WHISPER_AVAILABLE:
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = 'Whisper not available. Please install with: pip install openai-whisper'
                return
            
            # Save audio data to temporary file with appropriate extension
            file_ext = '.wav'  # Default to wav
            if filename:
                _, ext = os.path.splitext(filename.lower())
                if ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.webm']:
                    file_ext = ext
            
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            print(f"Saved audio to temporary file: {temp_path}")
            transcription_jobs[job_id]['progress'] = 30
            
            # Load Whisper model
            transcription_jobs[job_id]['progress'] = 50
            
            print(f"Loading Whisper model for job {job_id}...")
            try:
                model = whisper.load_model("base")  # Using the already imported whisper module
            except Exception as model_error:
                print(f"Failed to load Whisper model: {model_error}")
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = f'Failed to load Whisper model: {model_error}'
                return
            
            transcription_jobs[job_id]['progress'] = 70
            
            # Transcribe audio
            print(f"Transcribing audio for job {job_id}...")
            try:
                result = model.transcribe(temp_path, fp16=False)  # Disable fp16 for better compatibility
                text = result["text"].strip()
                
                if not text:
                    text = "No speech detected in the audio file."
                    
            except Exception as transcribe_error:
                print(f"Transcription failed: {transcribe_error}")
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = f'Transcription failed: {transcribe_error}'
                return
            
            transcription_jobs[job_id]['progress'] = 90
            
            # Clean up temporary file
            if temp_path:
                try:
                    os.unlink(temp_path)
                    print(f"Cleaned up temporary file: {temp_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file: {cleanup_error}")
            
            # Update job with result
            transcription_jobs[job_id]['status'] = 'completed'
            transcription_jobs[job_id]['result'] = text
            transcription_jobs[job_id]['progress'] = 100
            
            print(f"Transcription completed for job {job_id}: {len(text)} characters")
            
        except Exception as e:
            print(f"Transcription error for job {job_id}: {e}")
            import traceback
            traceback.print_exc()
            transcription_jobs[job_id]['status'] = 'error'
            transcription_jobs[job_id]['error'] = f'Transcription failed: {str(e)}'
            
            # Clean up temporary file on error
            if temp_path:
                try:
                    os.unlink(temp_path)
                except Exception as cleanup_error:
                    print(f"Warning: Could not clean up temporary file on error: {cleanup_error}")

    def send_json_response(self, data):
        """Send JSON response."""
        response_json = json.dumps(data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_json.encode())

    def generate_html(self):
        """Generate the HTML content for the web interface with tabs."""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Audio to Text Converter</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
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
            font-weight: 300;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #e2e8f0;
            background-color: #f7fafc;
            border-radius: 10px 10px 0 0;
            overflow: hidden;
        }
        
        .tab {
            flex: 1;
            padding: 20px;
            text-align: center;
            cursor: pointer;
            border: none;
            background: transparent;
            font-size: 16px;
            color: #4a5568;
            transition: all 0.3s ease;
            border-bottom: 3px solid transparent;
        }
        
        .tab:hover {
            background-color: #edf2f7;
            color: #2d3748;
        }
        
        .tab.active {
            background-color: #667eea;
            color: white;
            border-bottom-color: #4c51bf;
        }
        
        .tab-content {
            display: none;
            animation: fadeIn 0.3s ease-in;
        }
        
        .tab-content.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* File Upload Styles */
        .upload-area {
            border: 2px dashed #cbd5e0;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            margin-bottom: 20px;
            background: linear-gradient(145deg, #f7fafc, #edf2f7);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: linear-gradient(145deg, #edf2f7, #e2e8f0);
            transform: translateY(-2px);
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: linear-gradient(145deg, #ebf8ff, #bee3f8);
            transform: scale(1.02);
        }
        
        .file-label {
            cursor: pointer;
            color: #4a5568;
            font-size: 16px;
            font-weight: 500;
        }
        
        .file-info {
            margin-top: 15px;
            padding: 15px;
            background: linear-gradient(145deg, #e6fffa, #b2f5ea);
            border-radius: 8px;
            display: none;
            border-left: 4px solid #38b2ac;
        }
        
        /* Live Transcription Styles */
        .live-controls {
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: linear-gradient(145deg, #f7fafc, #edf2f7);
            border-radius: 15px;
        }
        
        .record-btn {
            background: linear-gradient(145deg, #fc8181, #f56565);
            color: white;
            font-size: 18px;
            padding: 20px 40px;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
        }
        
        .record-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 101, 101, 0.6);
        }
        
        .record-btn.recording {
            background: linear-gradient(145deg, #ed8936, #dd6b20);
            animation: pulse 1.5s infinite;
            box-shadow: 0 4px 15px rgba(237, 137, 54, 0.6);
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
        
        .microphone-status {
            margin-top: 15px;
            font-size: 14px;
            color: #718096;
            font-weight: 500;
        }
        
        .live-transcript {
            min-height: 200px;
            background: linear-gradient(145deg, #f7fafc, #edf2f7);
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Segoe UI', sans-serif;
            line-height: 1.8;
            font-size: 16px;
            color: #2d3748;
            overflow-y: auto;
            max-height: 300px;
        }
        
        .live-transcript.listening {
            border-color: #48bb78;
            background: linear-gradient(145deg, #f0fff4, #c6f6d5);
            box-shadow: 0 0 20px rgba(72, 187, 120, 0.2);
        }
        
        /* Button Styles */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            margin: 8px 4px;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .btn-primary {
            background: linear-gradient(145deg, #667eea, #764ba2);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn-secondary {
            background: linear-gradient(145deg, #a0aec0, #718096);
            color: white;
            box-shadow: 0 4px 15px rgba(160, 174, 192, 0.4);
        }
        
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(160, 174, 192, 0.6);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
        /* Progress Bar */
        .progress-container {
            display: none;
            margin: 20px 0;
            padding: 20px;
            background: linear-gradient(145deg, #f7fafc, #edf2f7);
            border-radius: 12px;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e2e8f0;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .progress-text {
            text-align: center;
            color: #4a5568;
            font-weight: 500;
        }
        
        /* Text Areas */
        textarea {
            width: 100%;
            min-height: 200px;
            padding: 20px;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            font-family: 'Segoe UI', sans-serif;
            font-size: 16px;
            line-height: 1.6;
            resize: vertical;
            background: linear-gradient(145deg, #ffffff, #f7fafc);
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        /* Status Messages */
        .error {
            color: #e53e3e;
            background: linear-gradient(145deg, #fed7d7, #feb2b2);
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
            border-left: 4px solid #e53e3e;
        }
        
        .success {
            color: #38a169;
            background: linear-gradient(145deg, #c6f6d5, #9ae6b4);
            padding: 15px 20px;
            border-radius: 8px;
            margin: 15px 0;
            display: none;
            border-left: 4px solid #38a169;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .audio-player {
            margin: 20px 0;
            text-align: center;
        }
        
        audio {
            width: 100%;
            max-width: 400px;
            border-radius: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎤 Enhanced Audio to Text Converter</h1>
        
        <!-- Tab Navigation -->
        <div class="tabs">
            <button class="tab active" onclick="showTab('file-upload')">📁 File Upload</button>
            <button class="tab" onclick="showTab('live-transcription')">🎙️ Live Transcription</button>
        </div>
        
        <!-- File Upload Tab -->
        <div id="file-upload" class="tab-content active">
            <div class="upload-area" id="uploadArea">
                <label for="audioFile" class="file-label">
                    📤 Click to select an audio file or drag and drop here<br>
                    <small>Supported formats: MP3, WAV, FLAC, M4A, OGG, WEBM</small>
                </label>
                <input type="file" id="audioFile" accept="audio/*">
                <div id="fileInfo" class="file-info"></div>
            </div>
            
            <div class="audio-player" id="audioPlayerContainer" style="display: none;">
                <audio id="audioPlayer" controls></audio>
            </div>
            
            <div style="text-align: center;">
                <button id="transcribeBtn" class="btn btn-primary" onclick="transcribeAudio()" disabled>
                    🎵 Convert with Whisper
                </button>
            </div>
            
            <div id="progressContainer" class="progress-container">
                <div class="progress-bar">
                    <div id="progressFill" class="progress-fill"></div>
                </div>
                <div id="progressText" class="progress-text">Processing...</div>
            </div>
            
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
            
            <div class="result-container">
                <h3>📝 Transcribed Text:</h3>
                <textarea id="resultText" placeholder="Transcribed text will appear here..."></textarea>
                <div style="text-align: center; margin-top: 20px;">
                    <button id="downloadBtn" class="btn btn-secondary" onclick="downloadTranscript()" disabled>
                        💾 Download as TXT
                    </button>
                    <button class="btn btn-secondary" onclick="copyToClipboard()">
                        📋 Copy to Clipboard
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Live Transcription Tab -->
        <div id="live-transcription" class="tab-content">
            <div class="live-controls">
                <button id="recordBtn" class="record-btn" onclick="toggleLiveTranscription()">
                    🎤 Start Live Transcription
                </button>
                <div id="microphoneStatus" class="microphone-status">
                    Click the button to start recording and transcribing in real-time
                </div>
            </div>
            
            <div>
                <h3>📝 Live Transcript:</h3>
                <div id="liveTranscript" class="live-transcript">
                    Live transcription will appear here as you speak...
                </div>
                
                <div style="text-align: center; margin-top: 20px;">
                    <button id="clearLiveBtn" class="btn btn-secondary" onclick="clearLiveTranscript()">
                        🗑️ Clear Transcript
                    </button>
                    <button id="saveLiveBtn" class="btn btn-secondary" onclick="saveLiveTranscript()">
                        💾 Save Transcript
                    </button>
                    <button class="btn btn-secondary" onclick="copyLiveToClipboard()">
                        📋 Copy to Clipboard
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let currentJobId = null;
        let selectedFile = null;
        let isRecording = false;
        let mediaRecorder = null;
        let audioStream = null;
        let recordingChunks = [];
        
        // Tab functionality
        function showTab(tabId) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabId).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
        }
        
        // File Upload Functionality
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('audioFile');
        const fileInfo = document.getElementById('fileInfo');
        const transcribeBtn = document.getElementById('transcribeBtn');
        const audioPlayerContainer = document.getElementById('audioPlayerContainer');
        const audioPlayer = document.getElementById('audioPlayer');
        
        // Drag and drop handlers
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
                handleFileSelect(files[0]);
            }
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
        
        function handleFileSelect(file) {
            selectedFile = file;
            
            // Show file info
            const fileSize = (file.size / 1024 / 1024).toFixed(2);
            fileInfo.innerHTML = `
                <strong>Selected File:</strong> ${file.name}<br>
                <strong>Size:</strong> ${fileSize} MB<br>
                <strong>Type:</strong> ${file.type}
            `;
            fileInfo.style.display = 'block';
            
            // Show audio player
            const audioURL = URL.createObjectURL(file);
            audioPlayer.src = audioURL;
            audioPlayerContainer.style.display = 'block';
            
            // Enable transcribe button
            transcribeBtn.disabled = false;
        }
        
        function transcribeAudio() {
            if (!selectedFile) {
                showError('Please select an audio file first');
                return;
            }
            
            // Read file as base64
            const reader = new FileReader();
            reader.onload = function(e) {
                const audioData = e.target.result.split(',')[1]; // Remove data:audio/...;base64, prefix
                
                // Send to server
                const data = {
                    audio: audioData,
                    filename: selectedFile.name
                };
                
                fetch('/api/transcribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                })
                .then(response => response.json())
                .then(result => {
                    if (result.job_id) {
                        currentJobId = result.job_id;
                        showProgress();
                        pollJobStatus();
                    } else {
                        showError('Failed to start transcription');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showError('Network error occurred');
                });
            };
            
            reader.readAsDataURL(selectedFile);
        }
        
        function pollJobStatus() {
            if (!currentJobId) return;
            
            fetch(`/api/job_status?job_id=${currentJobId}`)
                .then(response => response.json())
                .then(result => {
                    updateProgress(result.progress || 0, result.status);
                    
                    if (result.status === 'completed') {
                        hideProgress();
                        document.getElementById('resultText').value = result.result;
                        document.getElementById('downloadBtn').disabled = false;
                        showSuccess('Transcription completed successfully!');
                    } else if (result.status === 'error') {
                        hideProgress();
                        showError(`Transcription failed: ${result.error}`);
                    } else if (result.status === 'processing') {
                        // Continue polling
                        setTimeout(pollJobStatus, 1000);
                    }
                })
                .catch(error => {
                    console.error('Polling error:', error);
                    hideProgress();
                    showError('Error checking transcription status');
                });
        }
        
        // Live Transcription Functionality
        const recordBtn = document.getElementById('recordBtn');
        const microphoneStatus = document.getElementById('microphoneStatus');
        const liveTranscript = document.getElementById('liveTranscript');
        
        async function toggleLiveTranscription() {
            if (isRecording) {
                stopLiveTranscription();
            } else {
                await startLiveTranscription();
            }
        }
        
        async function startLiveTranscription() {
            try {
                // Request microphone access
                audioStream = await navigator.mediaDevices.getUserMedia({ 
                    audio: {
                        sampleRate: 16000,
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: true
                    } 
                });
                
                // Create MediaRecorder
                mediaRecorder = new MediaRecorder(audioStream, {
                    mimeType: 'audio/webm;codecs=opus'
                });
                
                recordingChunks = [];
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        recordingChunks.push(event.data);
                    }
                };
                
                mediaRecorder.onstop = () => {
                    processRecordingChunk();
                };
                
                // Start recording
                isRecording = true;
                recordBtn.classList.add('recording');
                recordBtn.textContent = '⏸️ Stop Recording';
                microphoneStatus.textContent = 'Recording... Speak now!';
                liveTranscript.classList.add('listening');
                
                // Start live transcription on server
                fetch('/api/live_start', { method: 'POST' })
                    .then(response => response.json())
                    .then(result => {
                        console.log('Live transcription started:', result);
                    });
                
                // Start recording in chunks
                startRecordingChunks();
                
            } catch (error) {
                console.error('Error starting live transcription:', error);
                showError('Could not access microphone. Please allow microphone access.');
            }
        }
        
        function stopLiveTranscription() {
            isRecording = false;
            
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            
            if (audioStream) {
                audioStream.getTracks().forEach(track => track.stop());
            }
            
            recordBtn.classList.remove('recording');
            recordBtn.textContent = '🎤 Start Live Transcription';
            microphoneStatus.textContent = 'Live transcription stopped';
            liveTranscript.classList.remove('listening');
            
            // Stop live transcription on server
            fetch('/api/live_stop', { method: 'POST' })
                .then(response => response.json())
                .then(result => {
                    console.log('Live transcription stopped:', result);
                });
        }
        
        function startRecordingChunks() {
            if (!isRecording) return;
            
            recordingChunks = [];
            mediaRecorder.start();
            
            // Stop recording after 3 seconds and process
            setTimeout(() => {
                if (isRecording && mediaRecorder.state === 'recording') {
                    mediaRecorder.stop();
                }
            }, 3000);
        }
        
        function processRecordingChunk() {
            if (recordingChunks.length === 0) return;
            
            const audioBlob = new Blob(recordingChunks, { type: 'audio/webm' });
            const reader = new FileReader();
            
            reader.onload = function(e) {
                const audioData = e.target.result.split(',')[1];
                
                // Send audio chunk to server for transcription
                fetch('/api/live_audio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ audio: audioData })
                })
                .then(response => response.json())
                .then(result => {
                    if (result.status === 'success' && result.text) {
                        // Add new text to transcript
                        const currentTranscript = liveTranscript.textContent;
                        if (currentTranscript === 'Live transcription will appear here as you speak...') {
                            liveTranscript.textContent = result.text;
                        } else {
                            liveTranscript.textContent = currentTranscript + ' ' + result.text;
                        }
                        
                        // Auto-scroll to bottom
                        liveTranscript.scrollTop = liveTranscript.scrollHeight;
                    }
                })
                .catch(error => {
                    console.error('Live transcription error:', error);
                });
            };
            
            reader.readAsDataURL(audioBlob);
            
            // Start next chunk if still recording
            if (isRecording) {
                setTimeout(startRecordingChunks, 500);
            }
        }
        
        function clearLiveTranscript() {
            liveTranscript.textContent = 'Live transcription will appear here as you speak...';
        }
        
        function saveLiveTranscript() {
            const text = liveTranscript.textContent;
            if (text && text !== 'Live transcription will appear here as you speak...') {
                downloadText(text, 'live-transcript.txt');
            }
        }
        
        function copyLiveToClipboard() {
            const text = liveTranscript.textContent;
            if (text && text !== 'Live transcription will appear here as you speak...') {
                navigator.clipboard.writeText(text).then(() => {
                    showSuccess('Live transcript copied to clipboard!');
                });
            }
        }
        
        // Utility functions
        function showProgress() {
            document.getElementById('progressContainer').style.display = 'block';
            transcribeBtn.disabled = true;
        }
        
        function hideProgress() {
            document.getElementById('progressContainer').style.display = 'none';
            transcribeBtn.disabled = false;
        }
        
        function updateProgress(progress, status) {
            document.getElementById('progressFill').style.width = progress + '%';
            document.getElementById('progressText').textContent = 
                `${status.charAt(0).toUpperCase() + status.slice(1)}... ${progress}%`;
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
        
        function showSuccess(message) {
            const successDiv = document.getElementById('success');
            successDiv.textContent = message;
            successDiv.style.display = 'block';
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 5000);
        }
        
        function downloadTranscript() {
            const text = document.getElementById('resultText').value;
            if (text) {
                downloadText(text, 'transcript.txt');
            }
        }
        
        function downloadText(text, filename) {
            const blob = new Blob([text], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        
        function copyToClipboard() {
            const text = document.getElementById('resultText').value;
            if (text) {
                navigator.clipboard.writeText(text).then(() => {
                    showSuccess('Text copied to clipboard!');
                });
            }
        }
        
        // Check if browser supports required features
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            document.getElementById('live-transcription').innerHTML = 
                '<div style="text-align: center; padding: 40px; color: #e53e3e;">' +
                '<h3>⚠️ Live Transcription Not Supported</h3>' +
                '<p>Your browser does not support live audio recording. Please use a modern browser like Chrome, Firefox, or Edge.</p>' +
                '</div>';
        }
    </script>
</body>
</html>
        """

def check_whisper_available():
    """Check if OpenAI Whisper is available."""
    return WHISPER_AVAILABLE

def main():
    """Main function to start the server."""
    # Check if Whisper is available
    if WHISPER_AVAILABLE:
        print("✓ Whisper available for transcription")
    else:
        print("⚠ Warning: Whisper not installed. Install with: pip install openai-whisper")
    
    # Start server
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, AudioTranscriptionHandler)
    
    print(f"\nEnhanced Audio to Text Converter started!")
    print(f"🌐 Open your browser and go to: http://localhost:8080")
    print(f"Features:")
    print(f"  📁 File Upload & Background Transcription")
    print(f"  🎙️ Live Real-time Transcription") 
    print(f"  💾 Download transcripts as text files")
    print(f"  📋 Copy to clipboard functionality")
    print(f"\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
