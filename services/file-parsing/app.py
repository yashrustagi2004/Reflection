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
from services.pinecone_service import get_pinecone_service
from services.job_category_detector import JobCategoryDetector
from flask import session
import traceback, requests, time
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
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

# Initialize Pinecone service (lazy loading to handle missing env vars gracefully)
pinecone_service = None
try:
    pinecone_service = get_pinecone_service()
    print("[FILE PARSING] ✅ Pinecone service initialized")
except Exception as e:
    print(f"[FILE PARSING] ⚠️ Pinecone service not available: {e}")
    print("[FILE PARSING] Will fall back to local storage if needed")

# Deprecated: Global storage for parsed content - now using Pinecone
# Keep for backward compatibility with existing endpoints
parsed_content_storage = {
    'resume_file_content': None,
    'jd_file_content': None,
    'jd_text_content': None
}


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'file-parsing',
        'status': 'healthy'
    }), 200


# ==================== Debug Endpoints ====================

@app.route('/debug/request-headers', methods=['GET', 'POST'])
def debug_request_headers():
    """Debug endpoint to inspect incoming request headers and tokens (remove in production!)"""
    import jwt
    
    # Get all headers
    headers_dict = dict(request.headers)
    
    # Extract tokens
    auth_header = request.headers.get('Authorization', '')
    service_token = request.headers.get('X-Service-Token', '')
    service_name = request.headers.get('X-Service-Name', '')
    
    # Try to decode tokens
    user_token_payload = None
    service_token_payload = None
    
    if auth_header.startswith('Bearer '):
        user_token = auth_header.replace('Bearer ', '')
        try:
            user_token_payload = jwt.decode(
                user_token, 
                auth_middleware.jwt_secret, 
                algorithms=[auth_middleware.jwt_algorithm]
            )
        except Exception as e:
            user_token_payload = f"Decode error: {str(e)}"
    
    if service_token:
        try:
            service_token_payload = jwt.decode(
                service_token,
                auth_middleware.jwt_secret,
                algorithms=[auth_middleware.jwt_algorithm]
            )
        except Exception as e:
            service_token_payload = f"Decode error: {str(e)}"
    
    return jsonify({
        'received_headers': headers_dict,
        'extracted_tokens': {
            'user_token': {
                'header': auth_header,
                'raw_token': auth_header.replace('Bearer ', '') if auth_header else None,
                'decoded_payload': user_token_payload
            },
            'service_token': {
                'header': service_token,
                'decoded_payload': service_token_payload,
                'service_name': service_name
            }
        },
        'request_info': {
            'method': request.method,
            'url': request.url,
            'endpoint': request.endpoint,
            'remote_addr': request.remote_addr
        },
        'note': 'This shows what file-parsing service receives from frontend',
        'warning': 'This endpoint exposes sensitive tokens - remove in production!'
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
            
            # Store parsed content in global variable
            global parsed_content_storage
            parsed_content_storage['resume_file_content'] = cleaned_text
            print(f"[FILE PARSING] Resume file content stored: {len(cleaned_text)} characters")
            print(f"[FILE PARSING] Resume preview: {cleaned_text[:200]}...")
            
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
        
        # Parse job description content and store in variable
        try:
            # Parse the job description to extract text content
            jd_text_content = EnhancedFileParser.parse_file(file_path, remove_pii=False)
            if jd_text_content:
                # Store parsed content in global variable
                global parsed_content_storage
                parsed_content_storage['jd_file_content'] = jd_text_content
                print(f"[FILE PARSING] JD file content stored: {len(jd_text_content)} characters")
                print(f"[FILE PARSING] JD preview: {jd_text_content[:200]}...")
        except Exception as e:
            print(f"Warning: Failed to parse job description for storage: {e}")
            # Continue execution even if parsing fails
        
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
        
        # Store text content in global variable
        global parsed_content_storage
        parsed_content_storage['jd_text_content'] = sanitized_text
        print(f"[FILE PARSING] JD text content stored: {len(sanitized_text)} characters")
        print(f"[FILE PARSING] JD text preview: {sanitized_text[:200]}...")
        
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


# (make sure `requests` is imported)

@app.route('/api/upload/submit', methods=['POST'])
def submit_resume_and_jd():
    """
    Combined endpoint to submit both resume and job description
    
    Flow:
    1. User submits both resume and JD files
    2. Resume gets parsed and PII removed
    3. Job description parsed (no PII removal)
    4. Embeddings generated and stored in Pinecone (no local storage)
    5. Text and embedding IDs sent to Q&A microservice
    6. Q&A service generates questions and saves to MongoDB with user association
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
        
        # Extract user_id from JWT token
        user_id = 'anonymous'  # Default fallback
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            try:
                payload = auth_middleware.verify_token(token)
                if payload and 'user_id' in payload:
                    user_id = payload['user_id']
                    print(f"[FILE PARSING] Authenticated user: {user_id}")
                else:
                    print("[FILE PARSING] ⚠️ Token valid but no user_id, using anonymous")
            except Exception as e:
                print(f"[FILE PARSING] ⚠️ Token verification failed: {e}, using anonymous")
        else:
            print("[FILE PARSING] ⚠️ No token provided, using anonymous")
        
        results = {'resume': None, 'job_description': None}
        timestamp = int(time.time())
        
        # ================== Resume Processing ==================
        resume_text = None
        try:
            is_valid, message, validation_details = file_security.validate_upload(resume_file)
            if not is_valid:
                return jsonify({'success': False, 'error': f'Resume validation failed: {message}'}), 400
            
            resume_filename = file_security.generate_secure_filename(
                resume_file.filename, user_id, 'resume'
            )
            temp_resume_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', f"temp_{resume_filename}")
            resume_file.save(temp_resume_path)
            
            is_valid, validation_message = EnhancedFileParser.validate_file_for_parsing(temp_resume_path)
            if not is_valid:
                os.remove(temp_resume_path)
                return jsonify({'success': False, 'error': f'Resume parsing validation failed: {validation_message}'}), 400
            
            # Parse and remove PII
            cleaned_text = EnhancedFileParser.parse_file(temp_resume_path, remove_pii=True)
            if cleaned_text is None:
                os.remove(temp_resume_path)
                return jsonify({'success': False, 'error': 'Failed to parse resume content'}), 500
            
            resume_text = cleaned_text
            
            # Clean up temp file
            os.remove(temp_resume_path)
            
            # Set metadata for response
            results['resume'] = {
                'filename': resume_filename.rsplit('.', 1)[0] + '_cleaned.txt',
                'original_name': resume_file.filename,
                'size': len(cleaned_text),
                'processed': True,
                'pii_removed': True
            }
            
            print(f"[FILE PARSING] ✅ Resume parsed: {len(cleaned_text)} characters")
            
        except Exception as e:
            print(f"[FILE PARSING] ❌ Resume processing error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Resume processing failed: {str(e)}'}), 500
        
        # ================== Job Description Processing ==================
        jd_text = None
        try:
            is_valid, message, validation_details = file_security.validate_upload(jd_file)
            if not is_valid:
                return jsonify({'success': False, 'error': f'Job description validation failed: {message}'}), 400

            jd_filename = file_security.generate_secure_filename(jd_file.filename, user_id, 'job_description')
            temp_jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', f"temp_{jd_filename}")
            jd_file.save(temp_jd_path)

            # Parse JD (no PII removal)
            jd_text_content = EnhancedFileParser.parse_file(temp_jd_path, remove_pii=False)
            
            if not jd_text_content:
                # Fallback to raw text if parsing fails
                with open(temp_jd_path, 'rb') as rb:
                    raw = rb.read()
                jd_text_content = raw.decode('utf-8', errors='replace')
            
            jd_text = jd_text_content
            
            # Clean up temp file
            os.remove(temp_jd_path)

            # Set metadata for response
            results['job_description'] = {
                'filename': jd_filename.rsplit('.', 1)[0] + '.txt',
                'original_name': jd_file.filename,
                'size': len(jd_text_content),
                'processed': True,
                'pii_removed': False
            }
            
            print(f"[FILE PARSING] ✅ JD parsed: {len(jd_text_content)} characters")
            
        except Exception as e:
            print(f"[FILE PARSING] ❌ JD processing error: {e}")
            traceback.print_exc()
            return jsonify({'success': False, 'error': f'Job description processing failed: {str(e)}'}), 500
        
        # ================== Store Embeddings in Pinecone ==================
        resume_embedding_id = None
        jd_embedding_id = None
        
        if pinecone_service and resume_text and jd_text:
            try:
                # Replace old embeddings with new ones (one resume + one JD per user)
                resume_embedding_id, jd_embedding_id = pinecone_service.replace_user_documents(
                    user_id=user_id,
                    resume_text=resume_text,
                    jd_text=jd_text,
                    timestamp=timestamp,
                    resume_metadata={
                        'original_filename': resume_file.filename,
                        'processed': True,
                        'pii_removed': True
                    },
                    jd_metadata={
                        'original_filename': jd_file.filename,
                        'processed': True,
                        'pii_removed': False
                    }
                )
                
                if resume_embedding_id and jd_embedding_id:
                    print(f"[FILE PARSING] ✅ Documents replaced for user {user_id}")
                    print(f"[FILE PARSING]    Resume ID: {resume_embedding_id}")
                    print(f"[FILE PARSING]    JD ID: {jd_embedding_id}")
                else:
                    print(f"[FILE PARSING] ⚠️ Failed to store embeddings in Pinecone")
                
            except Exception as e:
                print(f"[FILE PARSING] ⚠️ Pinecone storage failed: {e}")
                traceback.print_exc()
                # Continue without failing the request
                # We'll still send text to QA service
        else:
            if not pinecone_service:
                print("[FILE PARSING] ⚠️ Pinecone service not available, skipping embedding storage")
        
        # ================== Record Uploads in Login Management ==================
        resume_upload_record = {
            'file_type': 'resume',
            'filename': results['resume']['filename'],
            'original_name': results['resume']['original_name'],
            'file_path': results['resume']['filename'],  # Added missing field
            'file_size': results['resume']['size'],
            'mime_type': 'text/plain',
            'pinecone_id': resume_embedding_id
        }
        jd_upload_record = {
            'file_type': 'job_description',
            'filename': results['job_description']['filename'],
            'original_name': results['job_description']['original_name'],
            'file_path': results['job_description']['filename'],  # Added missing field
            'file_size': results['job_description']['size'],
            'mime_type': 'text/plain',
            'pinecone_id': jd_embedding_id
        }
        try:
            service_client.post('login-management', '/api/users/uploads', resume_upload_record, user_token=token)
            service_client.post('login-management', '/api/users/uploads', jd_upload_record, user_token=token)
        except Exception as e:
            print(f"[FILE PARSING] ⚠️ Failed to record uploads in login service: {e}")
        
        # ================== Send to Q&A Microservice for Question Generation ==================
        try:
            qa_payload = {
                "user_id": user_id,
                "resume_text": resume_text,
                "jd_text": jd_text,
                "resume_embedding_id": resume_embedding_id,
                "jd_embedding_id": jd_embedding_id
            }

            qa_response = requests.post(
                "http://127.0.0.1:5003/api/questions/generate",
                headers={
                    "Authorization": f"Bearer {os.getenv('API_AUTH_TOKEN', 'my-secret-token')}",
                    "Content-Type": "application/json"
                },
                json=qa_payload,
                timeout=30
            )

            if qa_response.status_code != 200:
                print(f"[FILE PARSING] ⚠️ Q&A service failed with status {qa_response.status_code}: {qa_response.text}")
                return jsonify({
                    "success": False, 
                    "message": "File processing succeeded but Q&A generation failed"
                }), 500
            
            qa_result = qa_response.json()
            print(f"[FILE PARSING] ✅ Q&A generation successful for user {user_id}")

        except Exception as e:
            print(f"[FILE PARSING] ❌ Error contacting Q&A microservice: {e}")
            traceback.print_exc()
            return jsonify({
                "success": False, 
                "error": f"File processing succeeded but Q&A generation failed: {str(e)}"
            }), 500
        
        # ================== Job Category Detection ==================
        job_categories_result = {}
        detected_categories_list = []
        try:
            # Perform regex-based category detection on both resume and JD
            detection_results = JobCategoryDetector.detect_categories_from_both(resume_text, jd_text)
            job_categories_result = JobCategoryDetector.format_results_for_response(detection_results)
            
            detected_categories_list = job_categories_result.get('detected_categories', [])
            if detected_categories_list:
                print(f"[FILE PARSING] ✅ Detected job categories: {', '.join(detected_categories_list)}")
            else:
                print("[FILE PARSING] ℹ️ No specific job categories detected")
                
        except Exception as e:
            print(f"[FILE PARSING] ⚠️ Category detection failed: {e}")
            traceback.print_exc()
            # Don't fail the request if category detection fails
            job_categories_result = {
                'detected_categories': [],
                'details': {}
            }
        
        # ================== Store Categories in User Profile ==================
        if detected_categories_list:
            try:
                categories_payload = {
                    'detected_categories': detected_categories_list
                }
                service_client.post('login-management', '/api/users/categories', categories_payload, user_token=token)
                print(f"[FILE PARSING] ✅ Stored categories in user profile for user {user_id}")
            except Exception as e:
                print(f"[FILE PARSING] ⚠️ Failed to store categories in login service: {e}")
        
        # ================== Final Success Response ==================
        return jsonify({
            'success': True,
            'message': 'Files uploaded successfully, embeddings stored, and questions generated!',
            'files': results,
            'embeddings': {
                'resume_id': resume_embedding_id,
                'jd_id': jd_embedding_id
            },
            'job_categories': job_categories_result,
            'user_id': user_id,
            'redirect_url': '/practice'
        }), 200

    except Exception as e:
        print(f"[FILE PARSING] ❌ Upload failed: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500



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


@app.route('/api/files/parsed-content', methods=['GET'])
def get_parsed_content():
    """
    Get the stored parsed content for resume and job description
    
    Returns:
        Dictionary containing parsed content for both resume and JD
    """
    try:
        global parsed_content_storage
        
        print(f"[FILE PARSING] Parsed content requested. Current storage:")
        for key, value in parsed_content_storage.items():
            if value:
                print(f"  - {key}: {len(value)} characters")
            else:
                print(f"  - {key}: None")
        
        return jsonify({
            'success': True,
            'parsed_content': {
                'resume_file_content': parsed_content_storage.get('resume_file_content'),
                'jd_file_content': parsed_content_storage.get('jd_file_content'),
                'jd_text_content': parsed_content_storage.get('jd_text_content')
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve parsed content: {str(e)}'
        }), 500


@app.route('/api/files/clear-content', methods=['POST'])
def clear_parsed_content():
    """
    Clear all stored parsed content
    
    Returns:
        Success message
    """
    try:
        global parsed_content_storage
        parsed_content_storage = {
            'resume_file_content': None,
            'jd_file_content': None,
            'jd_text_content': None
        }
        print("[FILE PARSING] All parsed content cleared")
        
        return jsonify({
            'success': True,
            'message': 'All parsed content cleared successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to clear content: {str(e)}'
        }), 500


@app.route('/api/files/content-status', methods=['GET'])
def get_content_status():
    """
    Get status of what content is currently stored
    
    Returns:
        Status of each content type (whether it exists or not)
    """
    try:
        global parsed_content_storage
        
        status = {
            'resume_file_uploaded': parsed_content_storage.get('resume_file_content') is not None,
            'jd_file_uploaded': parsed_content_storage.get('jd_file_content') is not None,
            'jd_text_uploaded': parsed_content_storage.get('jd_text_content') is not None
        }
        
        return jsonify({
            'success': True,
            'status': status,
            'any_content_available': any(status.values())
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get content status: {str(e)}'
        }), 500

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """
    Get questions for the authenticated user from QA service.
    Fetches user-specific questions from MongoDB.
    """
    try:
        # Extract user_id from JWT token
        user_id = 'anonymous'  # Default fallback
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            try:
                payload = auth_middleware.verify_token(token)
                if payload and 'user_id' in payload:
                    user_id = payload['user_id']
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Invalid token: user_id not found'
                    }), 401
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Token verification failed: {str(e)}'
                }), 401
        else:
            return jsonify({
                'success': False,
                'error': 'Authorization token required'
            }), 401
        
        # Fetch questions from QA service
        qa_service_url = f"http://127.0.0.1:5003/api/questions/user/{user_id}"
        
        qa_response = requests.get(
            qa_service_url,
            headers={
                "Authorization": f"Bearer {os.getenv('API_AUTH_TOKEN', 'my-secret-token')}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        if qa_response.status_code == 404:
            return jsonify({
                'success': False,
                'error': 'No questions found',
                'message': 'Please upload resume and job description first',
                'questions': []
            }), 404
        
        if qa_response.status_code != 200:
            return jsonify({
                'success': False,
                'error': f'QA service error: {qa_response.status_code}',
                'questions': []
            }), 500
        
        qa_data = qa_response.json()
        return jsonify(qa_data), 200
        
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'QA service timeout',
            'questions': []
        }), 504
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'QA service unavailable',
            'questions': []
        }), 503
    except Exception as e:
        print(f"[FILE PARSING] ❌ Error fetching questions: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to fetch questions: {str(e)}',
            'questions': []
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('FILE_PARSING_PORT', 5002))
    print(f"[FILE PARSING] Starting service on port {port}")
    print(f"[FILE PARSING] Initial parsed content storage: {parsed_content_storage}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
