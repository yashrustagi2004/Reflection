"""
Frontend Microservice
Serves web interface and coordinates with backend microservices
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.service_client import ServiceClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Configure session settings
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.getenv('JWT_EXPIRY_HOURS', '24')))

# Initialize service client
service_client = ServiceClient('frontend')


# ==================== Helper Functions ====================

def get_user_token():
    """Get user token from session"""
    return session.get('auth_token')


def is_authenticated():
    """Check if user is authenticated"""
    token = get_user_token()
    if not token:
        return False
    
    # Verify token with login service
    response = service_client.post(
        'login-management',
        '/api/users/verify',
        {'token': token}
    )
    
    return response.get('success', False)


def login_required(f):
    """Decorator to require authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== Public Routes ====================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.route('/testimonials')
def testimonials():
    """Testimonials page"""
    return render_template('testimonials.html')


@app.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        return jsonify({'success': True, 'message': 'Message received'})
    return render_template('contact.html')


# ==================== Authentication Routes ====================

@app.route('/debug/session')
@login_required
def debug_session():
    """Debug endpoint to inspect session contents (remove in production!)"""
    return jsonify({
        'session_data': {
            'has_auth_token': 'auth_token' in session,
            'auth_token': session.get('auth_token'),  # The actual JWT
            'user': session.get('user'),
            'session_keys': list(session.keys())
        },
        'cookies': dict(request.cookies),
        'note': 'This is the JWT token used for backend API calls'
    })


@app.route('/login')
def login():
    """Login page"""
    if is_authenticated():
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/api/auth/google/login')
def google_login():
    """Initiate Google OAuth"""
    response = service_client.get('login-management', '/api/auth/google/login')
    
    if response.get('success') and response.get('auth_url'):
        # Redirect user to Google OAuth page
        return redirect(response['auth_url'])
    
    return redirect(url_for('login', error='auth_failed'))


@app.route('/api/auth/github/login')
def github_login():
    """Initiate GitHub OAuth"""
    response = service_client.get('login-management', '/api/auth/github/login')
    
    if response.get('success') and response.get('auth_url'):
        # Redirect user to GitHub OAuth page
        return redirect(response['auth_url'])
    
    return redirect(url_for('login', error='auth_failed'))


@app.route('/api/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return redirect(url_for('login', error='auth_failed'))
    
    # Forward to login-management service
    response = service_client.get(
        'login-management',
        f'/api/auth/google/callback?code={code}&state={state}'
    )
    
    if response.get('success'):
        # Store token in session and make it permanent
        session.permanent = True
        session['auth_token'] = response.get('token')
        session['user'] = response.get('user')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login', error='auth_failed'))


@app.route('/api/auth/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    code = request.args.get('code')
    state = request.args.get('state')
    
    if not code:
        return redirect(url_for('login', error='auth_failed'))
    
    # Forward to login-management service
    response = service_client.get(
        'login-management',
        f'/api/auth/github/callback?code={code}&state={state}'
    )
    
    if response.get('success'):
        # Store token in session and make it permanent
        session.permanent = True
        session['auth_token'] = response.get('token')
        session['user'] = response.get('user')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('login', error='auth_failed'))


@app.route('/logout')
def logout():
    """Logout user"""
    token = get_user_token()
    if token:
        service_client.post(
            'login-management',
            '/api/auth/logout',
            {},
            user_token=token
        )
    
    session.clear()
    return redirect(url_for('index'))


# ==================== Protected Routes ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    token = get_user_token()
    
    # Get user profile
    user_response = service_client.get(
        'login-management',
        '/api/users/profile',
        user_token=token
    )
    
    # Get upload requirements
    requirements_response = service_client.get(
        'file-parsing',
        '/api/files/requirements'
    )
    
    return render_template(
        'home.html',
        user=user_response.get('user', {}),
        upload_requirements=requirements_response.get('requirements', {})
    )


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    token = get_user_token()
    
    if request.method == 'POST':
        # Update profile settings
        settings = {
            'theme': request.form.get('theme', 'light'),
            'notifications': request.form.get('notifications') == 'on',
            'data_sharing': request.form.get('data_sharing') == 'on'
        }
        
        update_response = service_client.put(
            'login-management',
            '/api/users/profile',
            {'settings': settings},
            user_token=token
        )
        
        if update_response.get('success'):
            # Redirect to profile with success message
            return redirect(url_for('profile', updated='true'))
    
    # Get user profile
    response = service_client.get(
        'login-management',
        '/api/users/profile',
        user_token=token
    )
    
    return render_template('profile.html', user=response.get('user', {}), updated=request.args.get('updated'))


@app.route('/delete-account', methods=['GET'])
@login_required
def delete_account_page():
    """Account deletion page"""
    return render_template('delete_account.html')


@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    """Delete user account"""
    token = get_user_token()
    confirmation = request.form.get('confirmation', '').strip().lower()
    
    # Verify confirmation text
    if confirmation != 'delete my account':
        return redirect(url_for('delete_account_page', error='invalid_confirmation'))
    
    # Delete account via login-management service
    response = service_client.delete(
        'login-management',
        '/api/users/delete',
        user_token=token
    )
    
    if response.get('success'):
        # Clear session and redirect to home
        session.clear()
        return redirect(url_for('index'))
    
    return redirect(url_for('delete_account_page', error='delete_failed'))


# ==================== File Upload Routes ====================

@app.route('/api/upload/resume', methods=['POST'])
@login_required
def validate_resume():
    """Validate resume file for upload readiness"""
    try:
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Basic validation
        allowed_extensions = {'.pdf', '.doc', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Check file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)     # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'success': False,
                'error': 'File too large. Maximum size is 10MB'
            }), 400
        
        if file_size == 0:
            return jsonify({
                'success': False,
                'error': 'File is empty'
            }), 400
        
        # File is valid
        return jsonify({
            'success': True,
            'message': 'Resume file is valid and ready for submission',
            'original_filename': file.filename,
            'file_size': file_size
        }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Validation failed: {str(e)}'}), 500


@app.route('/api/upload/job-description', methods=['POST'])
@login_required
def upload_job_description():
    """Validate job description file for upload readiness"""
    try:
        if 'jd_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['jd_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Basic validation
        allowed_extensions = {'.pdf', '.doc', '.docx'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False, 
                'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'
            }), 400
        
        # Check file size (10MB limit)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)     # Reset to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({
                'success': False,
                'error': 'File too large. Maximum size is 10MB'
            }), 400
        
        if file_size == 0:
            return jsonify({
                'success': False,
                'error': 'File is empty'
            }), 400
        
        # File is valid
        return jsonify({
            'success': True,
            'message': 'Job description file is valid and ready for submission',
            'original_filename': file.filename,
            'file_size': file_size
        }), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': f'Validation failed: {str(e)}'}), 500


@app.route('/api/upload/text/job-description', methods=['POST'])
@login_required
def upload_text_job_description():
    """Submit text job description - requires resume to be uploaded first"""
    try:
        data = request.get_json()
        
        # Validate that job description text is provided
        if not data or 'job_description' not in data:
            return jsonify({
                'success': False,
                'error': 'No job description text provided'
            }), 400
        
        job_description = data['job_description'].strip()
        if not job_description:
            return jsonify({
                'success': False,
                'error': 'Job description cannot be empty'
            }), 400
        
        # Check minimum length
        if len(job_description) < 50:
            return jsonify({
                'success': False,
                'error': 'Job description must be at least 50 characters long'
            }), 400
        
        # For now, we'll accept text job descriptions without file validation
        # In a full implementation, you'd want to check if resume was uploaded
        # by the same user in the current session
        
        token = get_user_token()
        
        response = service_client.post(
            'file-parsing',
            '/api/files/text/job-description',
            data,
            user_token=token
        )
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Text job description submission failed: {str(e)}'
        }), 500


@app.route('/submit_job_description', methods=['POST'])
@login_required  
def submit_job_description():
    """Submit job description text - simpler endpoint for JS compatibility"""
    try:
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({
                'success': False,
                'error': 'Job description cannot be empty'
            }), 400
            
        if len(job_description) < 50:
            return jsonify({
                'success': False,
                'error': 'Job description must be at least 50 characters long'
            }), 400
        
        # For now, just return success to allow the JS to handle UI state
        # In a full implementation, you'd save this to a session or database
        return jsonify({
            'success': True,
            'message': 'Job description received and ready for submission'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Submission failed: {str(e)}'
        }), 500


@app.route('/api/upload/submit_mixed', methods=['POST'])
@login_required
def submit_mixed():
    """
    Mixed endpoint to submit resume file + job description text
    """
    try:
        # Check if resume file is provided
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Resume file is required'
            }), 400
        
        # Check if job description text is provided
        jd_text = request.form.get('job_description_text', '').strip()
        if not jd_text:
            return jsonify({
                'success': False,
                'error': 'Job description text is required'
            }), 400
        
        resume_file = request.files['resume']
        
        # Validate resume file
        if not resume_file or resume_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Resume file is required'
            }), 400
        
        # Process resume through file-parsing service
        resume_file.stream.seek(0)
        resume_files = {
            'resume': (resume_file.filename, resume_file.stream, resume_file.mimetype)
        }

        user_token = get_user_token()
        resume_response = service_client.post(
            'file-parsing',
            '/api/files/upload/resume',
            data={},
            files=resume_files,
            user_token=user_token
        )
        
        if not resume_response or not resume_response.get('success'):
            return jsonify({
                'success': False,
                'error': 'Resume processing failed'
            }), 500
        
        # Process job description text through file-parsing service
        jd_data = {'text': jd_text}
        jd_response = service_client.post(
            'file-parsing',
            '/api/files/text/job-description',
            jd_data,
            user_token=user_token
        )
        
        if not jd_response or not jd_response.get('success'):
            return jsonify({
                'success': False,
                'error': 'Job description processing failed'
            }), 500
        
        return jsonify({
            'success': True,
            'message': 'Files processed successfully! Resume processed with personal information removed. Job description saved as provided.',
            'resume': resume_response,
            'job_description': jd_response
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Mixed submission failed: {str(e)}'
        }), 500


# ==================== Combined Upload ====================

@app.route('/api/upload/submit', methods=['POST'])
@login_required
def submit_combined():
    """
    Combined endpoint to submit both resume and job description
    Proxies to file-parsing service's combined upload endpoint
    """
    try:
        # Check if both files are provided
        if 'resume' not in request.files or 'job_description' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Both resume and job description files are required'
            }), 400
        
        # Get files from request
        resume_file = request.files['resume']
        jd_file = request.files['job_description']
        
        # Validate files
        if not resume_file or resume_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Resume file is required'
            }), 400
            
        if not jd_file or jd_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Job description file is required'
            }), 400
        
        # Create files dict for service client
        files = {
            'resume': (resume_file.filename, resume_file.stream, resume_file.mimetype),
            'job_description': (jd_file.filename, jd_file.stream, jd_file.mimetype)
        }
        
        # Proxy request to file-parsing service
        user_token = get_user_token()
        response = service_client.post(
            'file-parsing',
            '/api/upload/submit',
            data={},
            files=files,
            user_token=user_token
        )
        
        if response and response.get('success'):
            return jsonify(response), 200
        else:
            error_msg = response.get('error', 'Combined upload failed') if response else 'Service unavailable'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Combined upload failed: {str(e)}'
        }), 500


# ==================== Individual File Processing ====================

@app.route('/process_resume', methods=['POST'])
@login_required
def process_resume():
    """
    Process uploaded resume with PII removal - expects file in request
    """
    try:
        # Check if resume file is in the request
        if 'resume' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No resume file provided. Please upload a resume first.'
            }), 400
        
        resume_file = request.files['resume']
        if not resume_file or resume_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Resume file is empty.'
            }), 400
        
        # Create files dict for service client - need to reset stream position
        resume_file.stream.seek(0)
        files = {
            'resume': (resume_file.filename, resume_file.stream, resume_file.mimetype)
        }
        
        # Send to file-parsing service for processing
        user_token = get_user_token()
        response = service_client.post(
            'file-parsing',
            '/api/files/upload/resume',
            data={},
            files=files,
            user_token=user_token
        )
        
        if response and response.get('success'):
            return jsonify({
                'success': True,
                'message': 'Resume processed successfully! Personal information has been removed.',
                'data': response
            }), 200
        else:
            error_msg = response.get('error', 'Resume processing failed') if response else 'Service unavailable'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Resume processing failed: {str(e)}'
        }), 500


@app.route('/process_job_description', methods=['POST'])
@login_required
def process_job_description():
    """
    Process uploaded job description (save as-is) - expects file in request
    """
    try:
        # Check if job description file is in the request
        if 'jd' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No job description file provided. Please upload a job description first.'
            }), 400
        
        jd_file = request.files['jd']
        if not jd_file or jd_file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Job description file is empty.'
            }), 400
        
        # Create files dict for service client - need to reset stream position
        jd_file.stream.seek(0)
        files = {
            'job_description': (jd_file.filename, jd_file.stream, jd_file.mimetype)
        }
        
        # Send to file-parsing service for processing
        user_token = get_user_token()
        response = service_client.post(
            'file-parsing',
            '/api/files/upload/job-description',
            data={},
            files=files,
            user_token=user_token
        )
        
        if response and response.get('success'):
            return jsonify({
                'success': True,
                'message': 'Job description saved successfully!',
                'data': response
            }), 200
        else:
            error_msg = response.get('error', 'Job description processing failed') if response else 'Service unavailable'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Job description processing failed: {str(e)}'
        }), 500


# ==================== Health Check ====================

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'frontend',
        'status': 'healthy'
    }), 200


if __name__ == '__main__':
    port = int(os.getenv('FRONTEND_PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
