"""
Simplified web-based Audio to Text Converter that works with Python 3.13.
Uses only Whisper for background processing to avoid compatibility issues.
"""

import http.server
import socketserver
import json
import os
import tempfile
import threading
import webbrowser
import time
import uuid
import shutil
import base64
from pathlib import Path

class SimpleAudioToTextWebServer:
    """
    A simplified web-based audio to text converter that uses Whisper for background processing.
    """
    
    def __init__(self, port=8080):
        self.port = port
        self.server = None
        self.html_content = self._get_html_content()
        self.processing_jobs = {}
        self.temp_dir = tempfile.mkdtemp()
        
        # Try to import Whisper
        self.whisper_available = False
        try:
            import whisper
            self.whisper = whisper
            self.whisper_available = True
            print("✓ Whisper available for background processing")
        except ImportError:
            print("! Whisper not available - install with: pip install openai-whisper")
    
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
    <title>Simple Audio to Text Converter</title>
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
        
        .processing {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
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
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #667eea;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .info-box {
            background: #f7fafc;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Simple Audio to Text Converter</h1>
        
        <div class="info-box">
            <h3>How it works:</h3>
            <p>• Upload an audio file (MP3, WAV, M4A, etc.)</p>
            <p>• Click "Convert with Whisper" for offline processing</p>
            <p>• Wait for the conversion to complete</p>
            <p>• Download your transcription as a text file</p>
            <p><strong>Note:</strong> This uses OpenAI Whisper for accurate offline transcription</p>
        </div>
        
        <!-- File Upload Section -->
        <div class="upload-area" id="uploadArea">
            <p>📁 Drop audio files here or click to browse</p>
            <input type="file" id="audioFile" accept="audio/*">
            <button class="upload-btn" onclick="document.getElementById('audioFile').click()">
                Choose Audio File
            </button>
        </div>
        
        <!-- Audio Player -->
        <div class="audio-player" id="audioPlayer" style="display: none;">
            <audio controls id="audioElement"></audio>
            <p id="fileName"></p>
        </div>
        
        <!-- Control Buttons -->
        <div class="controls">
            <button class="btn btn-primary" id="convertBtn" onclick="convertAudio()" disabled>
                ⚡ Convert with Whisper
            </button>
            <button class="btn btn-secondary" onclick="clearAll()">
                Clear All
            </button>
            <button class="btn btn-secondary" onclick="downloadText()" id="downloadBtn" disabled>
                📥 Download Text
            </button>
        </div>
        
        <!-- Status Display -->
        <div id="status"></div>
        
        <!-- Processing Progress -->
        <div id="processingProgress" style="display: none;">
            <div class="status info processing">
                <span id="progressText">Processing...</span>
                <div class="spinner"></div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        
        <!-- Transcription Area -->
        <div class="transcription-area">
            <h3>Transcription Result:</h3>
            <textarea id="transcriptionText" placeholder="Transcribed text will appear here..."></textarea>
        </div>
    </div>

    <script>
        let currentAudioFile = null;
        let pollInterval = null;
        
        const uploadArea = document.getElementById('uploadArea');
        const audioFile = document.getElementById('audioFile');
        const audioPlayer = document.getElementById('audioPlayer');
        const audioElement = document.getElementById('audioElement');
        const fileName = document.getElementById('fileName');
        const convertBtn = document.getElementById('convertBtn');
        const transcriptionText = document.getElementById('transcriptionText');
        
        // File upload handling
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
            convertBtn.disabled = false;
            currentAudioFile = file;
            
            showStatus(`Audio file "${file.name}" loaded successfully!`, 'success');
        }
        
        async function convertAudio() {
            if (!currentAudioFile) {
                showStatus('Please select an audio file first.', 'error');
                return;
            }
            
            showStatus('Starting conversion...', 'info');
            showProgress('Uploading file...', 10);
            
            convertBtn.disabled = true;
            
            try {
                // Convert file to base64 for simple transfer
                const reader = new FileReader();
                reader.onload = async function(e) {
                    const audioData = e.target.result.split(',')[1]; // Remove data URL prefix
                    
                    // Send to server
                    const response = await fetch('/api/convert', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            audio_data: audioData,
                            filename: currentAudioFile.name
                        })
                    });
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const jobId = result.job_id;
                        showProgress('Processing with Whisper...', 25);
                        pollForResults(jobId);
                    } else {
                        throw new Error(result.error || 'Unknown error');
                    }
                };
                
                reader.readAsDataURL(currentAudioFile);
                
            } catch (error) {
                showStatus(`Conversion failed: ${error.message}`, 'error');
                hideProgress();
                convertBtn.disabled = false;
            }
        }
        
        async function pollForResults(jobId) {
            let progress = 25;
            
            pollInterval = setInterval(async () => {
                try {
                    const response = await fetch(`/api/status/${jobId}`);
                    const result = await response.json();
                    
                    if (result.status === 'completed') {
                        clearInterval(pollInterval);
                        hideProgress();
                        
                        if (result.success) {
                            transcriptionText.value = result.text;
                            showStatus('Conversion completed successfully!', 'success');
                            document.getElementById('downloadBtn').disabled = false;
                        } else {
                            showStatus(`Conversion failed: ${result.error}`, 'error');
                        }
                        
                        convertBtn.disabled = false;
                        
                    } else if (result.status === 'error') {
                        clearInterval(pollInterval);
                        hideProgress();
                        showStatus(`Conversion failed: ${result.error}`, 'error');
                        convertBtn.disabled = false;
                        
                    } else {
                        // Still processing
                        progress = Math.min(progress + 10, 90);
                        showProgress('Processing with Whisper...', progress);
                    }
                    
                } catch (error) {
                    clearInterval(pollInterval);
                    hideProgress();
                    showStatus(`Error checking conversion status: ${error.message}`, 'error');
                    convertBtn.disabled = false;
                }
            }, 2000); // Poll every 2 seconds
        }
        
        function showProgress(message, percent) {
            const progressDiv = document.getElementById('processingProgress');
            const progressText = document.getElementById('progressText');
            const progressFill = document.getElementById('progressFill');
            
            progressDiv.style.display = 'block';
            progressText.textContent = message;
            progressFill.style.width = `${percent}%`;
        }
        
        function hideProgress() {
            const progressDiv = document.getElementById('processingProgress');
            progressDiv.style.display = 'none';
            
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
            convertBtn.disabled = true;
            document.getElementById('downloadBtn').disabled = true;
            currentAudioFile = null;
            audioFile.value = '';
            document.getElementById('status').innerHTML = '';
            hideProgress();
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
            showStatus('Simple Audio to Text Converter loaded successfully!', 'success');
        });
    </script>
</body>
</html>
        """
    
    def _process_audio_background(self, job_id, audio_data, filename):
        """Process audio in background thread using Whisper."""
        try:
            print(f"Starting Whisper processing for job {job_id}, file: {filename}")
            
            # Save audio data to temporary file
            file_ext = Path(filename).suffix.lower() or '.wav'
            temp_file = os.path.join(self.temp_dir, f"{job_id}{file_ext}")
            
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            
            print(f"Audio data saved to {temp_file}, size: {len(audio_data)} bytes")
            
            self.processing_jobs[job_id]['status'] = 'processing'
            self.processing_jobs[job_id]['progress'] = 50
            
            if self.whisper_available:
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
            else:
                error_msg = "Whisper not available. Please install with: pip install openai-whisper"
                print(f"Whisper not available for job {job_id}")
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
    
    def start_server(self):
        """Start the web server."""
        handler = self._create_handler()
        
        try:
            self.server = socketserver.TCPServer(("", self.port), handler)
            print(f"Simple Audio to Text Converter started!")
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
    
    def _create_handler(self):
        """Create the HTTP request handler."""
        html_content = self.html_content
        server_instance = self
        
        class SimpleAudioToTextHandler(http.server.SimpleHTTPRequestHandler):
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
                if self.path == '/api/convert':
                    try:
                        # Read JSON data
                        content_length = int(self.headers.get('Content-Length', 0))
                        if content_length == 0:
                            raise ValueError("No content received")
                        
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        
                        audio_data_b64 = data.get('audio_data')
                        filename = data.get('filename', 'audio.wav')
                        
                        if not audio_data_b64:
                            raise ValueError("No audio data received")
                        
                        # Decode base64 audio data
                        audio_data = base64.b64decode(audio_data_b64)
                        
                        # Create job ID
                        job_id = str(uuid.uuid4())
                        
                        # Initialize job
                        server_instance.processing_jobs[job_id] = {
                            'status': 'queued',
                            'progress': 0,
                            'filename': filename,
                            'created_at': time.time()
                        }
                        
                        # Start processing in background
                        thread = threading.Thread(
                            target=server_instance._process_audio_background,
                            args=(job_id, audio_data, filename)
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
                        print(f"Error in /api/convert: {str(e)}")
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
                # Only log API calls
                if 'POST /api/' in format % args or 'GET /api/' in format % args:
                    print(f"API: {format % args}")
        
        return SimpleAudioToTextHandler

def main():
    """Main function to start the simple web server."""
    print("Simple Audio to Text Converter (Whisper Only)")
    print("=" * 50)
    print("This version works with Python 3.13 and uses Whisper for")
    print("accurate offline transcription without compatibility issues!")
    print()
    
    try:
        port = 8080
        server = SimpleAudioToTextWebServer(port)
        server.start_server()
    except Exception as e:
        print(f"Error: {e}")
        print("Try running on a different port or check if port 8080 is already in use.")

if __name__ == "__main__":
    main()
