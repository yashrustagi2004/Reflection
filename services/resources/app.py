"""
Resources Microservice
Manages vector storage, embeddings, document retrieval, and learning resources
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient

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

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["Reflection"]
resources_collection = db["resources"]

# ==================== Health Check ====================
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'resources',
        'status': 'healthy'
    }), 200

# ==================== Resource Endpoint ====================
@app.route('/resources', methods=['GET'])
def get_resource():
    """
    Returns requested parts of a resource category.
    - Category ID is sent in the request headers as 'Resource-ID'
    - JWT token must be sent in 'Authorization' header as Bearer token
    - Query parameters (optional):
        - courses=1 → include courses
        - certifications=1 → include certifications
        - projects=1 → include projects
    If no query params are provided, return the entire category.
    """
    # 1️⃣ Authenticate request using JWT
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    token = auth_header.split("Bearer ")[-1]  # Extract JWT
    user = auth_middleware.verify_token(token)
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    # 2️⃣ Get category ID from headers
    category = request.headers.get('Resource-ID')
    if not category:
        return jsonify({"error": "Missing Resource-ID in headers"}), 400

    # 3️⃣ Map query params to MongoDB projection
    projection = {}
    if 'courses' in request.args:
        projection['courses'] = 1
    if 'certifications' in request.args:
        projection['certifications'] = 1
    if 'projects' in request.args:
        projection['projects'] = 1

    # If no projection specified, return all fields
    if not projection:
        resource = resources_collection.find_one({"_id": category})
    else:
        projection['_id'] = 0  # hide MongoDB internal _id
        resource = resources_collection.find_one({"_id": category}, projection)

    if resource:
        return jsonify(resource)
    else:
        return jsonify({"error": "Resource category not found"}), 404

# ==================== List All Categories ====================
@app.route('/categories', methods=['GET'])
def list_categories():
    """Return all available resource categories (authenticated)"""
    # Authenticate request
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Missing Authorization header"}), 401

    token = auth_header.split("Bearer ")[-1]
    user = auth_middleware.verify_token(token)
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 401

    resources = list(resources_collection.find({}, {"_id": 1}))
    category_names = [r["_id"] for r in resources]
    return jsonify({"resources": category_names})

# ==================== Main App Runner ====================
if __name__ == '__main__':
    port = int(os.getenv('RESOURCES_PORT', 5005))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )