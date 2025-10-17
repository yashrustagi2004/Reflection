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
from services.enhanced_file_parser import EnhancedFileParser

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
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No resume file provided'
            }), 400
        
        file = request.files['resume']
        user_id = 'anonymous'  # Temporary fix for authentication
        
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
        
        # Save original file temporarily
        temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', f"temp_{safe_filename}")
        file.save(temp_file_path)
        
        # Parse resume and remove PII
        try:
            # Validate file for parsing
            is_valid, validation_message = EnhancedFileParser.validate_file_for_parsing(temp_file_path)
            if not is_valid:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return jsonify({
                    'success': False,
                    'error': f'File parsing validation failed: {validation_message}'
                }), 400
            
            # Parse and clean the resume content
            cleaned_text = EnhancedFileParser.parse_file(temp_file_path, remove_pii=True)
            
            if cleaned_text is None:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                return jsonify({
                    'success': False,
                    'error': 'Failed to parse resume content'
                }), 500
            
            # Save the cleaned content as a new text file
            final_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', safe_filename.rsplit('.', 1)[0] + '_cleaned.txt')
            
            with open(final_file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            # Update the file path to point to cleaned version
            file_path = final_file_path
            
        except Exception as e:
            # Clean up temp file in case of error
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return jsonify({
                'success': False,
                'error': f'Resume parsing failed: {str(e)}'
            }), 500
        
        # Get file metadata for the cleaned file
        file_metadata = file_security.get_file_metadata(file_path)
        
        # Notify login service to update user record
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        upload_record = {
            'file_type': 'resume',
            'filename': os.path.basename(file_path),
            'original_name': file.filename,
            'file_path': file_path,
            'file_size': file_metadata['size'],
            'mime_type': 'text/plain'  # Always text after processing
        }
        
        service_client.post(
            'login-management',
            '/api/users/uploads',
            upload_record,
            user_token=token
        )
        
        return jsonify({
            'success': True,
            'message': 'Resume uploaded and processed successfully. Personal information has been removed for privacy.',
            'file': {
                'filename': os.path.basename(file_path),
                'original_name': file.filename,
                'size': file_metadata['size'],
                'mime_type': 'text/plain',  # Always text after processing
                'processed': True,
                'pii_removed': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/files/upload/job-description', methods=['POST'])
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
        if 'job_description' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No job description file provided'
            }), 400
        
        file = request.files['job_description']
        user_id = 'anonymous'  # Temporary fix for authentication
        
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
                'mime_type': file_metadata['mime_type'],
                'processed': False,  # Not processed, original file saved
                'pii_removed': False
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/files/text/job-description', methods=['POST'])
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
        user_id = 'anonymous'  # Temporary fix for authentication
        
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
                'size': len(sanitized_text.encode('utf-8')),
                'processed': False,  # Not processed, original text saved
                'pii_removed': False
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Save failed: {str(e)}'
        }), 500


# ==================== Combined Upload ====================

@app.route('/api/upload/submit', methods=['POST'])
def submit_resume_and_jd():
    """
    Combined endpoint to submit both resume and job description
    
    Flow:
    1. User submits both resume and JD files
    2. Resume gets parsed and PII removed
    3. Job description saved as-is (no parsing)
    4. Both files stored locally
    5. User sees success message
    """
    try:
        # Check if both files are provided
        if 'resume' not in request.files or 'job_description' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both resume and job description files are required'
            }), 400
        
        resume_file = request.files['resume']
        jd_file = request.files['job_description']
        user_id = 'anonymous'  # Temporary fix for authentication
        
        # Track results
        results = {
            'resume': None,
            'job_description': None
        }
        
        # Process Resume (with PII removal)
        try:
            # Validate resume file
            is_valid, message, validation_details = file_security.validate_upload(resume_file)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'error': f'Resume validation failed: {message}',
                    'details': validation_details
                }), 400
            
            # Generate secure filename for resume
            resume_filename = file_security.generate_secure_filename(
                resume_file.filename,
                user_id,
                'resume'
            )
            
            # Save resume temporarily
            temp_resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', f"temp_{resume_filename}")
            resume_file.save(temp_resume_path)
            
            # Parse and clean resume
            is_valid, validation_message = EnhancedFileParser.validate_file_for_parsing(temp_resume_path)
            if not is_valid:
                if os.path.exists(temp_resume_path):
                    os.remove(temp_resume_path)
                return jsonify({
                    'success': False,
                    'error': f'Resume parsing validation failed: {validation_message}'
                }), 400
            
            cleaned_text = EnhancedFileParser.parse_file(temp_resume_path, remove_pii=True)
            if cleaned_text is None:
                if os.path.exists(temp_resume_path):
                    os.remove(temp_resume_path)
                return jsonify({
                    'success': False,
                    'error': 'Failed to parse resume content'
                }), 500
            
            # Save cleaned resume
            resume_final_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', 
                                           resume_filename.rsplit('.', 1)[0] + '_cleaned.txt')
            with open(resume_final_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
            
            # Clean up temp file
            if os.path.exists(temp_resume_path):
                os.remove(temp_resume_path)
            
            resume_metadata = file_security.get_file_metadata(resume_final_path)
            results['resume'] = {
                'filename': os.path.basename(resume_final_path),
                'original_name': resume_file.filename,
                'size': resume_metadata['size'],
                'processed': True,
                'pii_removed': True
            }
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Resume processing failed: {str(e)}'
            }), 500
        
        # Process Job Description (no parsing, save as-is)
        try:
            # Validate JD file
            is_valid, message, validation_details = file_security.validate_upload(jd_file)
            if not is_valid:
                # Clean up resume file if JD validation fails
                if results['resume'] and os.path.exists(resume_final_path):
                    os.remove(resume_final_path)
                return jsonify({
                    'success': False,
                    'error': f'Job description validation failed: {message}',
                    'details': validation_details
                }), 400
            
            # Generate secure filename for JD
            jd_filename = file_security.generate_secure_filename(
                jd_file.filename,
                user_id,
                'job_description'
            )
            
            # Save JD as-is (no parsing)
            jd_final_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', jd_filename)
            jd_file.save(jd_final_path)
            
            jd_metadata = file_security.get_file_metadata(jd_final_path)
            results['job_description'] = {
                'filename': jd_filename,
                'original_name': jd_file.filename,
                'size': jd_metadata['size'],
                'processed': False,
                'pii_removed': False
            }
            
        except Exception as e:
            # Clean up resume file if JD processing fails
            if results['resume'] and os.path.exists(resume_final_path):
                os.remove(resume_final_path)
            return jsonify({
                'success': False,
                'error': f'Job description processing failed: {str(e)}'
            }), 500
        
        # Record uploads in login management service
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        # Record resume upload
        resume_upload_record = {
            'file_type': 'resume',
            'filename': results['resume']['filename'],
            'original_name': results['resume']['original_name'],
            'file_path': resume_final_path,
            'file_size': results['resume']['size'],
            'mime_type': 'text/plain'
        }
        
        # Record JD upload
        jd_upload_record = {
            'file_type': 'job_description',
            'filename': results['job_description']['filename'],
            'original_name': results['job_description']['original_name'],
            'file_path': jd_final_path,
            'file_size': results['job_description']['size'],
            'mime_type': jd_metadata['mime_type']
        }
        
        # Send both records to login management
        try:
            service_client.post(
                'login-management',
                '/api/users/uploads',
                resume_upload_record,
                user_token=token
            )
            
            service_client.post(
                'login-management',
                '/api/users/uploads',
                jd_upload_record,
                user_token=token
            )
        except Exception as e:
            # Files are saved but couldn't record in login service
            print(f"Warning: Failed to record uploads in login service: {e}")
        
        return jsonify({
            'success': True,
            'message': 'Files uploaded successfully! Resume processed with personal information removed. Job description saved as provided.',
            'files': results
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
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
