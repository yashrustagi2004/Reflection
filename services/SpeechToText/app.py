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
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True    # <-- force debug ON
    )
