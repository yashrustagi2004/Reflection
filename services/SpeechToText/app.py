"""
SpeechToText Microservice
Handles audio uploads, converts to WAV (via FFmpeg + pydub),
and performs transcription using Google Speech Recognition.
"""

import os
import sys
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import time
import psutil

# Add parent directory for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.service_client import ServiceClient
from shared.auth_middleware import AuthMiddleware
# Load environment variables
load_dotenv()

# Initialize Flask app
auth_middleware = AuthMiddleware()
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize service client and recognizer
service_client = ServiceClient('speech-to-text')
recognizer = sr.Recognizer()

# ==================== Health Check ====================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'speech-to-text',
        'status': 'healthy'
    }), 200

# Monitoring
# Custom metrics
REQUEST_COUNT = Counter('http_request_total', 'Total HTTP Requests', ['method', 'status', 'path'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'status', 'path'])
REQUEST_IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP Requests in progress', ['method', 'path'])

# System metrics
CPU_USAGE = Gauge('process_cpu_usage', 'Current CPU usage in percent')
MEMORY_USAGE = Gauge('process_memory_usage_bytes', 'Current memory usage in bytes')

def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)

@app.before_request
def before_request():
    request.start_time = time.time()
    REQUEST_IN_PROGRESS.labels(method=request.method, path=request.path).inc()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_COUNT.labels(method=request.method, status=response.status_code, path=request.path).inc()
    REQUEST_LATENCY.labels(method=request.method, status=response.status_code, path=request.path).observe(request_latency)
    REQUEST_IN_PROGRESS.labels(method=request.method, path=request.path).dec()
    return response


@app.route('/metrics')
def metrics():
    update_system_metrics()
    return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Modify the middleware to return bytes
def metrics_app(environ, start_response):
    update_system_metrics()
    data = generate_latest(REGISTRY)
    status = '200 OK'
    headers = [('Content-Type', CONTENT_TYPE_LATEST), ('Content-Length', str(len(data)))]
    start_response(status, headers)
    return [data]

# Use the modified middleware
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': metrics_app
})

# ==================== Speech-to-Text Endpoint ====================
@app.route('/SpeechToText', methods=['POST'])
@auth_middleware.require_auth
def speech_to_text():
    """
    Converts uploaded audio (any common format) into text.
    Requires:
        - Form-data: file=<audio_blob>
    Returns:
        JSON: { 'transcript': "<recognized text>" }
    """

    # 1️⃣ Validate audio file
    if 'file' not in request.files:
        return jsonify({"error": "No audio file uploaded"}), 400

    audio_file = request.files['file']

    try:
        # 2️⃣ Save and convert uploaded file to WAV
        with tempfile.NamedTemporaryFile(delete=False) as temp_in, \
             tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:

            audio_file.save(temp_in.name)

            # Convert to WAV (handles .webm, .ogg, .m4a, etc.)
            AudioSegment.from_file(temp_in.name).export(temp_wav.name, format="flac")

            # 3️⃣ Recognize speech using Google STT
            with sr.AudioFile(temp_wav.name) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)

        # 4️⃣ Cleanup temporary files
        os.remove(temp_in.name)
        os.remove(temp_wav.name)

        # 5️⃣ Return transcript
        return jsonify({"transcript": text}), 200

    except sr.UnknownValueError:
        return jsonify({"error": "Could not understand the audio"}), 400
    except sr.RequestError as e:
        return jsonify({"error": f"Google STT service error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


# ==================== Main App Runner ====================
if __name__ == '__main__':
    port = int(os.getenv('SPEECHTOTEXT_PORT', 5004))
    
    use_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    try:
        # run_simple(hostname, port, application, use_reloader=False, use_debugger=False, threaded=False)
        run_simple('0.0.0.0', port, app_dispatch, use_reloader=use_debug, use_debugger=use_debug)
    except Exception:
        # Fallback to Flask's development server if run_simple isn't available or fails
        app.run(host='0.0.0.0', port=port, debug=use_debug)
