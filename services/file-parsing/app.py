"""
File Parsing Microservice
Handles secure file upload, validation, and parsing
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.auth_middleware import AuthMiddleware
from shared.service_client import ServiceClient
from services.file_security_service import FileSecurityService
from services.file_parser_service import FileParserService

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Configuration
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Create upload directories
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)

# Initialize services
auth_middleware = AuthMiddleware()
service_client = ServiceClient('file-parsing')
file_security = FileSecurityService()
file_parser = FileParserService()


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'file-parsing',
        'status': 'healthy'
    }), 200


# ==================== File Upload ====================

@app.route('/api/files/upload/resume', methods=['POST'])
@auth_middleware.require_auth
def upload_resume():
    """
    Upload and validate resume file
    
    Security checks:
    - File size validation
    - File type validation (extension, MIME type, magic numbers)
    - Filename sanitization
    - Path traversal prevention
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        user_id = request.user_id
        
        # Validate file security
        is_valid, message, validation_details = file_security.validate_upload(file)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'details': validation_details
            }), 400
        
        # Generate secure filename
        safe_filename = file_security.generate_secure_filename(
            file.filename,
            user_id,
            'resume'
        )
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', safe_filename)
        file.save(file_path)
        
        # Get file metadata
        file_metadata = file_security.get_file_metadata(file_path)
        
        # Notify login service to update user record
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        upload_record = {
            'file_type': 'resume',
            'filename': safe_filename,
            'original_name': file.filename,
            'file_path': file_path,
            'file_size': file_metadata['size'],
            'mime_type': file_metadata['mime_type']
        }
        
        service_client.post(
            'login-management',
            '/api/users/uploads',
            upload_record,
            user_token=token
        )
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded successfully',
            'file': {
                'filename': safe_filename,
                'original_name': file.filename,
                'size': file_metadata['size'],
                'mime_type': file_metadata['mime_type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/files/upload/job-description', methods=['POST'])
@auth_middleware.require_auth
def upload_job_description():
    """
    Upload and validate job description file
    
    Security checks:
    - File size validation
    - File type validation (extension, MIME type, magic numbers)
    - Filename sanitization
    - Path traversal prevention
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        user_id = request.user_id
        
        # Validate file security
        is_valid, message, validation_details = file_security.validate_upload(file)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message,
                'details': validation_details
            }), 400
        
        # Generate secure filename
        safe_filename = file_security.generate_secure_filename(
            file.filename,
            user_id,
            'job_description'
        )
        
        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', safe_filename)
        file.save(file_path)
        
        # Get file metadata
        file_metadata = file_security.get_file_metadata(file_path)
        
        # Notify login service to update user record
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        upload_record = {
            'file_type': 'job_description',
            'filename': safe_filename,
            'original_name': file.filename,
            'file_path': file_path,
            'file_size': file_metadata['size'],
            'mime_type': file_metadata['mime_type']
        }
        
        service_client.post(
            'login-management',
            '/api/users/uploads',
            upload_record,
            user_token=token
        )
        
        return jsonify({
            'success': True,
            'message': 'Job description uploaded successfully',
            'file': {
                'filename': safe_filename,
                'original_name': file.filename,
                'size': file_metadata['size'],
                'mime_type': file_metadata['mime_type']
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/files/text/job-description', methods=['POST'])
@auth_middleware.require_auth
def save_text_job_description():
    """
    Save text-based job description
    
    Security checks:
    - Input validation
    - Length validation
    - XSS prevention
    """
    try:
        data = request.get_json()
        text_content = data.get('text', '').strip()
        
        if not text_content:
            return jsonify({
                'success': False,
                'error': 'Job description text is required'
            }), 400
        
        # Validate text content
        is_valid, message = file_security.validate_text_content(text_content)
        
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Sanitize and save
        sanitized_text = file_security.sanitize_text(text_content)
        user_id = request.user_id
        
        # Generate filename
        filename = f"jd_text_{user_id}_{int(__import__('time').time())}.txt"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', filename)
        
        # Save file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(sanitized_text)
        
        # Notify login service
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        upload_record = {
            'file_type': 'job_description_text',
            'filename': filename,
            'original_name': 'Text Job Description',
            'file_path': file_path,
            'file_size': len(sanitized_text.encode('utf-8')),
            'mime_type': 'text/plain'
        }
        
        service_client.post(
            'login-management',
            '/api/users/uploads',
            upload_record,
            user_token=token
        )
        
        return jsonify({
            'success': True,
            'message': 'Job description saved successfully',
            'file': {
                'filename': filename,
                'size': len(sanitized_text.encode('utf-8'))
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Save failed: {str(e)}'
        }), 500


# ==================== File Parsing ====================

@app.route('/api/files/parse', methods=['POST'])
@auth_middleware.require_auth
def parse_file():
    """
    Parse document file (PDF, DOC, DOCX) and extract text
    
    Args (JSON):
        file_path: Path to the file to parse
        
    Returns:
        Extracted text content
    """
    try:
        data = request.get_json()
        file_path = data.get('file_path')
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': 'File path is required'
            }), 400
        
        # Security check: Ensure file exists and is in allowed directory
        if not file_security.is_safe_path(file_path, app.config['UPLOAD_FOLDER']):
            return jsonify({
                'success': False,
                'error': 'Invalid file path'
            }), 403
        
        # Parse file
        text_content = file_parser.parse_document(file_path)
        
        if text_content is None:
            return jsonify({
                'success': False,
                'error': 'Failed to parse file'
            }), 500
        
        return jsonify({
            'success': True,
            'text': text_content,
            'length': len(text_content)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Parse failed: {str(e)}'
        }), 500


@app.route('/api/files/requirements', methods=['GET'])
def get_upload_requirements():
    """Get file upload requirements and constraints"""
    return jsonify({
        'success': True,
        'requirements': file_security.get_upload_requirements()
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('FILE_PARSING_PORT', 5002))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
