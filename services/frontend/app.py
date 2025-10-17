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
def upload_resume():
    """Upload resume file"""
    try:
        token = get_user_token()
        
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Forward file to file-parsing service
        files = {'file': (file.filename, file.stream, file.mimetype)}
        
        response = service_client.post(
            'file-parsing',
            '/api/files/upload/resume',
            files=files,
            user_token=token
        )
        
        if response and response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'Resume uploaded successfully'),
                'original_filename': file.filename,
                'file': response.get('file')
            })
        else:
            return jsonify({
                'success': False,
                'error': response.get('error', 'Upload failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/upload/job-description', methods=['POST'])
@login_required
def upload_job_description():
    """Upload job description file"""
    try:
        token = get_user_token()
        
        if 'jd_file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['jd_file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Forward file to file-parsing service
        files = {'file': (file.filename, file.stream, file.mimetype)}
        
        response = service_client.post(
            'file-parsing',
            '/api/files/upload/job-description',
            files=files,
            user_token=token
        )
        
        if response and response.get('success'):
            return jsonify({
                'success': True,
                'message': response.get('message', 'Job description uploaded successfully'),
                'original_filename': file.filename,
                'file': response.get('file')
            })
        else:
            return jsonify({
                'success': False,
                'error': response.get('error', 'Upload failed')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@app.route('/api/upload/text/job-description', methods=['POST'])
@login_required
def upload_text_job_description():
    """Submit text job description"""
    token = get_user_token()
    data = request.get_json()
    
    response = service_client.post(
        'file-parsing',
        '/api/files/text/job-description',
        data,
        user_token=token
    )
    
    return jsonify(response)


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
