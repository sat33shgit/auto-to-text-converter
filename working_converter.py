"""
Simple Audio to Text Converter - File Upload Only
Clean, working version focused on file upload and background conversion
"""

import json
import base64
import threading
import time
import os
import tempfile
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Try to import Whisper
try:
    import whisper
    WHISPER_AVAILABLE = True
    print("✓ Whisper loaded successfully")
except ImportError:
    WHISPER_AVAILABLE = False
    print("❌ Whisper not available")

# Global variables for managing transcription jobs
transcription_jobs = {}
job_counter = 0
job_lock = threading.Lock()

class SimpleAudioHandler(BaseHTTPRequestHandler):
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
            else:
                self.send_error(404)
        except Exception as e:
            print(f"GET Error: {e}")
            traceback.print_exc()
            self.send_error(500)

    def do_POST(self):
        """Handle POST requests."""
        try:
            parsed_url = urlparse(self.path)
            path = parsed_url.path
            
            if path == '/api/transcribe':
                self.handle_file_transcription()
            else:
                self.send_error(404)
        except Exception as e:
            print(f"POST Error: {e}")
            traceback.print_exc()
            self.send_error(500)

    def handle_file_transcription(self):
        """Handle file upload and transcription."""
        global job_counter
        
        try:
            # Read the JSON data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(post_data)
            
            # Extract audio data
            audio_data = base64.b64decode(data['audio'])
            filename = data.get('filename', 'audio.wav')
            
            print(f"Received file: {filename}, size: {len(audio_data)} bytes")
            
            # Create job
            with job_lock:
                job_counter += 1
                job_id = str(job_counter)
                transcription_jobs[job_id] = {
                    'status': 'processing',
                    'progress': 0,
                    'filename': filename
                }
            
            print(f"Created job {job_id} for file {filename}")
            
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
            
        except Exception as e:
            print(f"File transcription error: {e}")
            traceback.print_exc()
            response = {'status': 'error', 'error': str(e)}
            self.send_json_response(response)

    def transcribe_audio_file(self, job_id, audio_data, filename):
        """Transcribe audio file in background thread."""
        temp_path = None
        try:
            print(f"[Job {job_id}] Starting transcription for: {filename}")
            
            # Check if Whisper is available
            if not WHISPER_AVAILABLE:
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = 'Whisper not available. Please install: pip install openai-whisper'
                print(f"[Job {job_id}] Error: Whisper not available")
                return
            
            # Update progress
            transcription_jobs[job_id]['progress'] = 10
            print(f"[Job {job_id}] Progress: 10%")
            
            # Save audio data to temporary file
            file_ext = '.wav'
            if filename:
                _, ext = os.path.splitext(filename.lower())
                if ext in ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.webm']:
                    file_ext = ext
            
            with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            print(f"[Job {job_id}] Saved to temporary file: {temp_path}")
            transcription_jobs[job_id]['progress'] = 30
            print(f"[Job {job_id}] Progress: 30%")
            
            # Load Whisper model
            print(f"[Job {job_id}] Loading Whisper model...")
            transcription_jobs[job_id]['progress'] = 50
            print(f"[Job {job_id}] Progress: 50%")
            
            try:
                model = whisper.load_model("base")
                print(f"[Job {job_id}] Whisper model loaded successfully")
            except Exception as model_error:
                print(f"[Job {job_id}] Failed to load Whisper model: {model_error}")
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = f'Failed to load Whisper model: {model_error}'
                return
            
            transcription_jobs[job_id]['progress'] = 70
            print(f"[Job {job_id}] Progress: 70%")
            
            # Transcribe audio
            print(f"[Job {job_id}] Starting transcription...")
            try:
                result = model.transcribe(temp_path, fp16=False)
                text = result["text"].strip()
                
                if not text:
                    text = "No speech detected in the audio file."
                
                print(f"[Job {job_id}] Transcription completed: {len(text)} characters")
                    
            except Exception as transcribe_error:
                print(f"[Job {job_id}] Transcription failed: {transcribe_error}")
                traceback.print_exc()
                transcription_jobs[job_id]['status'] = 'error'
                transcription_jobs[job_id]['error'] = f'Transcription failed: {transcribe_error}'
                return
            
            transcription_jobs[job_id]['progress'] = 90
            print(f"[Job {job_id}] Progress: 90%")
            
            # Update job with result
            transcription_jobs[job_id]['status'] = 'completed'
            transcription_jobs[job_id]['result'] = text
            transcription_jobs[job_id]['progress'] = 100
            
            print(f"[Job {job_id}] Job completed successfully!")
            
        except Exception as e:
            print(f"[Job {job_id}] Error: {e}")
            traceback.print_exc()
            transcription_jobs[job_id]['status'] = 'error'
            transcription_jobs[job_id]['error'] = f'Transcription failed: {str(e)}'
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    print(f"[Job {job_id}] Cleaned up temporary file: {temp_path}")
                except Exception as cleanup_error:
                    print(f"[Job {job_id}] Warning: Could not clean up temporary file: {cleanup_error}")

    def send_json_response(self, data):
        """Send JSON response."""
        response_json = json.dumps(data)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_json.encode())

    def generate_html(self):
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
            font-weight: 300;
        }
        
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
        
        input[type="file"] {
            display: none;
        }
        
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
        
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }
        
        .btn-secondary {
            background: linear-gradient(145deg, #a0aec0, #718096);
            color: white;
            box-shadow: 0 4px 15px rgba(160, 174, 192, 0.4);
        }
        
        .btn-secondary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(160, 174, 192, 0.6);
        }
        
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none !important;
        }
        
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
        <h1>🎵 Audio to Text Converter</h1>
        
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
                <button id="downloadBtn" class="btn btn-secondary" onclick="downloadTranscript()">
                    💾 Download as TXT
                </button>
                <button class="btn btn-secondary" onclick="copyToClipboard()">
                    📋 Copy to Clipboard
                </button>
                <button class="btn btn-secondary" onclick="clearTranscript()">
                    🗑️ Clear Text
                </button>
            </div>
        </div>
    </div>

    <script>
        let currentJobId = null;
        let selectedFile = null;
        
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
            
            console.log('Starting transcription for:', selectedFile.name);
            
            // Read file as base64
            const reader = new FileReader();
            reader.onload = function(e) {
                const audioData = e.target.result.split(',')[1]; // Remove data:audio/...;base64, prefix
                
                console.log('Sending audio data, size:', audioData.length, 'characters');
                
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
                    console.log('Server response:', result);
                    if (result.job_id) {
                        currentJobId = result.job_id;
                        showProgress();
                        pollJobStatus();
                    } else {
                        showError('Failed to start transcription: ' + (result.error || 'Unknown error'));
                    }
                })
                .catch(error => {
                    console.error('Network error:', error);
                    showError('Network error occurred: ' + error.message);
                });
            };
            
            reader.readAsDataURL(selectedFile);
        }
        
        function pollJobStatus() {
            if (!currentJobId) return;
            
            fetch(`/api/job_status?job_id=${currentJobId}`)
                .then(response => response.json())
                .then(result => {
                    console.log('Job status:', result);
                    updateProgress(result.progress || 0, result.status);
                    
                    if (result.status === 'completed') {
                        hideProgress();
                        document.getElementById('resultText').value = result.result;
                        showSuccess('Transcription completed successfully!');
                        console.log('Transcription completed!');
                    } else if (result.status === 'error') {
                        hideProgress();
                        showError(`Transcription failed: ${result.error}`);
                        console.error('Transcription error:', result.error);
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
            }, 8000);
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
            if (text && text.trim() !== '') {
                // Create filename with timestamp
                const now = new Date();
                const timestamp = now.toISOString().slice(0, 19).replace(/[:.]/g, '-');
                const filename = `transcript_${timestamp}.txt`;
                
                const blob = new Blob([text], { type: 'text/plain' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                showSuccess(`Downloaded as ${filename}`);
            } else {
                showError('No transcript text to download. Please transcribe an audio file first.');
            }
        }
        
        function clearTranscript() {
            if (confirm('Are you sure you want to clear the transcript text?')) {
                document.getElementById('resultText').value = '';
                showSuccess('Transcript cleared!');
            }
        }
        
        function copyToClipboard() {
            const text = document.getElementById('resultText').value;
            if (text && text.trim() !== '') {
                navigator.clipboard.writeText(text).then(() => {
                    showSuccess('Text copied to clipboard!');
                }).catch(() => {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    showSuccess('Text copied to clipboard!');
                });
            } else {
                showError('No transcript text to copy. Please transcribe an audio file first.');
            }
        }
    </script>
</body>
</html>
        """

def main():
    """Main function to start the server."""
    if WHISPER_AVAILABLE:
        print("✅ Ready for transcription!")
    else:
        print("❌ Whisper not available - please install: pip install openai-whisper")
        return
    
    # Start server
    server_address = ('localhost', 8081)
    httpd = HTTPServer(server_address, SimpleAudioHandler)
    
    print(f"\n🎵 Simple Audio to Text Converter started!")
    print(f"🌐 Open your browser and go to: http://localhost:8081")
    print(f"\nFeatures:")
    print(f"  📁 File Upload & Background Transcription")
    print(f"  💾 Download transcripts as text files")
    print(f"  📋 Copy to clipboard functionality")
    print(f"\nPress Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == "__main__":
    main()
