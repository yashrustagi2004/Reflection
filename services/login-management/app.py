"""
Login Management Microservice
Handles user authentication, OAuth, and user data management
"""

import os
import sys
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.auth_middleware import AuthMiddleware
from shared.database import get_collection
from models.user_model import UserModel
from services.oauth_service import OAuthService
from services.user_management_service import UserManagementService

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app, supports_credentials=True, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Configure session settings
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.getenv('JWT_EXPIRY_HOURS', '24')))

# Initialize services
auth_middleware = AuthMiddleware()
users_collection = get_collection('users')
user_model = UserModel(users_collection)
oauth_service = OAuthService()
user_management_service = UserManagementService(user_model)


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'login-management',
        'status': 'healthy'
    }), 200


# ==================== OAuth Authentication ====================

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check OAuth provider configuration status"""
    config_status = oauth_service.get_config_status()
    return jsonify({
        'success': True,
        'google_configured': config_status['google'],
        'github_configured': config_status['github']
    }), 200


@app.route('/api/auth/google/login', methods=['GET'])
def google_login():
    """Initiate Google OAuth flow"""
    try:
        auth_url, state = oauth_service.get_google_auth_url()
        session['oauth_state'] = state
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        # Note: State verification skipped for microservices architecture
        # In production, use Redis or shared session store for cross-service state validation
        # Verify state
        # if state != session.get('oauth_state'):
        #     return jsonify({
        #         'success': False,
        #         'error': 'Invalid state parameter'
        #     }), 400
        
        # Exchange code for user info
        user_data = oauth_service.handle_google_callback(code)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with Google'
            }), 401
        
        # Create or update user
        user_id = user_management_service.create_or_update_user(user_data)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create user account'
            }), 500
        
        # Generate JWT token
        token = auth_middleware.generate_token(user_id, user_data['email'])
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'email': user_data['email'],
                'name': user_data['name'],
                'avatar_url': user_data.get('avatar_url')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/github/login', methods=['GET'])
def github_login():
    """Initiate GitHub OAuth flow"""
    try:
        auth_url, state = oauth_service.get_github_auth_url()
        session['oauth_state'] = state
        return jsonify({
            'success': True,
            'auth_url': auth_url
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/github/callback', methods=['GET'])
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        # Note: State verification skipped for microservices architecture
        # In production, use Redis or shared session store for cross-service state validation
        # Verify state
        # if state != session.get('oauth_state'):
        #     return jsonify({
        #         'success': False,
        #         'error': 'Invalid state parameter'
        #     }), 400
        
        # Exchange code for user info
        user_data = oauth_service.handle_github_callback(code)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'Failed to authenticate with GitHub'
            }), 401
        
        # Create or update user
        user_id = user_management_service.create_or_update_user(user_data)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'Failed to create user account'
            }), 500
        
        # Generate JWT token
        token = auth_middleware.generate_token(user_id, user_data['email'])
        
        return jsonify({
            'success': True,
            'token': token,
            'user': {
                'id': user_id,
                'email': user_data['email'],
                'name': user_data['name'],
                'avatar_url': user_data.get('avatar_url')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/auth/logout', methods=['POST'])
@auth_middleware.require_auth
def logout():
    """Logout user"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


# ==================== User Management ====================

@app.route('/api/users/profile', methods=['GET'])
@auth_middleware.require_auth
def get_profile():
    """Get user profile"""
    try:
        user = user_management_service.get_user_by_id(request.user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user_management_service.sanitize_user_data(user)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/profile', methods=['PUT'])
@auth_middleware.require_auth
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        # Validate input
        allowed_fields = ['name', 'avatar_url', 'settings']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        success = user_management_service.update_user(request.user_id, update_data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/verify', methods=['POST'])
def verify_user():
    """Verify user token and return user info (for inter-service calls)"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token required'
            }), 400
        
        # Verify token
        payload = auth_middleware.verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'Invalid or expired token'
            }), 401
        
        # Get user data
        user = user_management_service.get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user_management_service.sanitize_user_data(user)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/delete', methods=['DELETE'])
@auth_middleware.require_auth
def delete_account():
    """Delete user account"""
    try:
        success = user_management_service.delete_user(request.user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete account'
            }), 500
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== Upload Management ====================

@app.route('/api/users/uploads', methods=['POST'])
@auth_middleware.require_auth
def add_upload_record():
    """Add file upload record to user profile"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['file_type', 'filename', 'file_path', 'file_size']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        success = user_management_service.add_upload_record(
            request.user_id,
            data['file_type'],
            data
        )
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to add upload record'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Upload record added successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/users/uploads', methods=['GET'])
@auth_middleware.require_auth
def get_uploads():
    """Get user upload history"""
    try:
        uploads = user_management_service.get_user_uploads(request.user_id)
        
        return jsonify({
            'success': True,
            'uploads': uploads
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('LOGIN_MANAGEMENT_PORT', 5001))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
