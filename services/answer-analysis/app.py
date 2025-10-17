"""
Answer Analysis Microservice
Handles user answer evaluation and feedback generation
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.auth_middleware import AuthMiddleware
from shared.service_client import ServiceClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize services
auth_middleware = AuthMiddleware()
service_client = ServiceClient('answer-analysis')


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'answer-analysis',
        'status': 'healthy'
    }), 200


# ==================== Answer Analysis ====================

@app.route('/api/analyze/answer', methods=['POST'])
@auth_middleware.require_auth
def analyze_answer():
    """
    Analyze user's answer and provide feedback
    
    Expected input:
    {
        "question": "...",
        "user_answer": "...",
        "ideal_answer": "...",
        "context": {
            "resume_text": "...",
            "job_description_text": "..."
        }
    }
    """


@app.route('/api/analyze/session', methods=['POST'])
@auth_middleware.require_auth
def analyze_session():
    """
    Analyze entire interview practice session
    
    Expected input:
    {
        "questions": [...],
        "answers": [...],
        "session_metadata": {...}
    }
    """


if __name__ == '__main__':
    port = int(os.getenv('ANSWER_ANALYSIS_PORT', 5004))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
