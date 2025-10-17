"""
Resources Microservice
Manages vector storage, embeddings, and document retrieval
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
service_client = ServiceClient('resources')


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'resources',
        'status': 'healthy'
    }), 200



if __name__ == '__main__':
    port = int(os.getenv('RESOURCES_PORT', 5005))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
