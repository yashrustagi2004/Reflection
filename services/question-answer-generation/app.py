"""
Question-Answer Generation Microservice
Handles interview question generation and ideal answer creation
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
service_client = ServiceClient('question-answer-generation')


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'question-answer-generation',
        'status': 'healthy'
    }), 200


# ==================== Question Generation ====================

@app.route('/api/questions/generate', methods=['POST'])
@auth_middleware.require_auth
def generate_questions():
    """
    Generate interview questions based on resume and job description
    
    Expected input:
    {
        "resume_text": "...",
        "job_description_text": "..."
    }
    """


@app.route('/api/answers/generate', methods=['POST'])
@auth_middleware.require_auth
def generate_ideal_answers():
    """
    Generate ideal answers for questions based on resume and job description
    
    Expected input:
    {
        "questions": [...],
        "resume_text": "...",
        "job_description_text": "..."
    }
    """


if __name__ == '__main__':
    port = int(os.getenv('QA_GENERATION_PORT', 5003))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
