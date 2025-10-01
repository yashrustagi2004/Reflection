"""
Authentication Routes
Handles OAuth login, logout, and user account management endpoints
"""

from flask import Blueprint, request, redirect, url_for, session, flash, jsonify, render_template
from backend.services.auth_service import AuthenticationService
from backend.services.user_service import UserService
from backend.config.database import init_database
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Initialize services
auth_service = AuthenticationService()
try:
    user_service = UserService()
except Exception as e:
    logger.error(f"Failed to initialize UserService: {e}")
    user_service = None


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Verify user is still active
        if user_service and not user_service.is_user_active(session['user_id']):
            session.clear()
            flash('Your account is no longer active', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/status')
def auth_status():
    """Check authentication configuration status"""
    config_status = auth_service.is_configured()
    return jsonify({
        'google_configured': config_status['google'],
        'github_configured': config_status['github'],
        'database_connected': user_service.user_model is not None
    })


@auth_bp.route('/login/google')
def google_login():
    """Initiate Google OAuth login"""
    try:
        if not auth_service.is_configured()['google']:
            flash('Google login is not configured', 'error')
            return redirect(url_for('login'))
        
        # Generate state parameter for security
        state = auth_service.generate_state()
        session['oauth_state'] = state
        
        # Get Google OAuth URL
        auth_url = auth_service.get_google_auth_url(state)
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating Google login: {e}")
        flash('Error starting Google login', 'error')
        return redirect(url_for('login'))


@auth_bp.route('/login/github')
def github_login():
    """Initiate GitHub OAuth login"""
    try:
        if not auth_service.is_configured()['github']:
            flash('GitHub login is not configured', 'error')
            return redirect(url_for('login'))
        
        # Generate state parameter for security
        state = auth_service.generate_state()
        session['oauth_state'] = state
        
        # Get GitHub OAuth URL
        auth_url = auth_service.get_github_auth_url(state)
        return redirect(auth_url)
        
    except Exception as e:
        logger.error(f"Error initiating GitHub login: {e}")
        flash('Error starting GitHub login', 'error')
        return redirect(url_for('login'))


@auth_bp.route('/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state parameter
        state = request.args.get('state')
        if not state or state != session.get('oauth_state'):
            flash('Invalid authentication state', 'error')
            return redirect(url_for('login'))
        
        # Clear state from session
        session.pop('oauth_state', None)
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'Unknown error')
            flash(f'Google authentication failed: {error}', 'error')
            return redirect(url_for('login'))
        
        # Authenticate with Google
        user_data = auth_service.authenticate_google(code)
        if not user_data:
            flash('Failed to authenticate with Google', 'error')
            return redirect(url_for('login'))
        
        # Create or update user
        if not user_service:
            flash('Authentication service unavailable - database connection issue', 'error')
            return redirect(url_for('login'))
            
        user_id = user_service.create_or_update_user_from_oauth(user_data)
        if not user_id:
            flash('Failed to create user account', 'error')
            return redirect(url_for('login'))
        
        # Create session
        session['user_id'] = user_id
        session['user_email'] = user_data['email']
        session['user_name'] = user_data['name']
        session['provider'] = 'google'
        
        flash('Successfully logged in with Google!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error in Google callback: {e}")
        flash('Authentication error occurred', 'error')
        return redirect(url_for('login'))


@auth_bp.route('/github/callback')
def github_callback():
    """Handle GitHub OAuth callback"""
    try:
        # Verify state parameter
        state = request.args.get('state')
        if not state or state != session.get('oauth_state'):
            flash('Invalid authentication state', 'error')
            return redirect(url_for('login'))
        
        # Clear state from session
        session.pop('oauth_state', None)
        
        # Get authorization code
        code = request.args.get('code')
        if not code:
            error = request.args.get('error', 'Unknown error')
            flash(f'GitHub authentication failed: {error}', 'error')
            return redirect(url_for('login'))
        
        # Authenticate with GitHub
        user_data = auth_service.authenticate_github(code)
        if not user_data:
            flash('Failed to authenticate with GitHub', 'error')
            return redirect(url_for('login'))
        
        # Create or update user
        if not user_service:
            flash('Authentication service unavailable - database connection issue', 'error')
            return redirect(url_for('login'))
            
        user_id = user_service.create_or_update_user_from_oauth(user_data)
        if not user_id:
            flash('Failed to create user account', 'error')
            return redirect(url_for('login'))
        
        # Create session
        session['user_id'] = user_id
        session['user_email'] = user_data['email']
        session['user_name'] = user_data['name']
        session['provider'] = 'github'
        
        flash('Successfully logged in with GitHub!', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error in GitHub callback: {e}")
        flash('Authentication error occurred', 'error')
        return redirect(url_for('login'))


@auth_bp.route('/logout')
def logout():
    """Logout user and clear session"""
    user_name = session.get('user_name', 'User')
    session.clear()
    flash(f'Goodbye {user_name}! You have been logged out.', 'info')
    return redirect(url_for('index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    try:
        user_profile = user_service.get_user_profile(session['user_id'])
        if not user_profile:
            flash('Unable to load profile', 'error')
            return redirect(url_for('dashboard'))
        
        # Get user statistics
        stats = user_service.get_user_statistics(session['user_id'])
        
        return render_template('profile.html', user=user_profile, stats=stats)
        
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        flash('Error loading profile', 'error')
        return redirect(url_for('dashboard'))


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile settings"""
    try:
        settings = {
            'theme': request.form.get('theme', 'light')
        }
        
        success = user_service.update_user_settings(session['user_id'], settings)
        if success:
            flash('Profile updated successfully!', 'success')
        else:
            flash('Failed to update profile', 'error')
        
        return redirect(url_for('auth.profile'))
        
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        flash('Error updating profile', 'error')
        return redirect(url_for('auth.profile'))


@auth_bp.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    """Delete user account"""
    if request.method == 'GET':
        return render_template('delete_account.html')
    
    try:
        # Verify user confirmation
        confirmation = request.form.get('confirmation', '').lower()
        if confirmation != 'delete my account':
            flash('Please type exactly "delete my account" to confirm', 'error')
            return render_template('delete_account.html')
        
        user_id = session['user_id']
        user_name = session.get('user_name', 'User')
        
        # Delete account (soft delete by default)
        hard_delete = request.form.get('permanent_delete') == 'on'
        success = user_service.delete_user_account(user_id, hard_delete=hard_delete)
        
        if success:
            # Clear session
            session.clear()
            
            delete_type = "permanently deleted" if hard_delete else "deactivated"
            flash(f'Your account has been {delete_type}. Thank you for using our service, {user_name}.', 'info')
            return redirect(url_for('index'))
        else:
            flash('Failed to delete account. Please try again.', 'error')
            return render_template('delete_account.html')
            
    except Exception as e:
        logger.error(f"Error deleting account: {e}")
        flash('Error processing account deletion', 'error')
        return render_template('delete_account.html')


@auth_bp.route('/api/user')
@login_required
def api_user_info():
    """API endpoint to get current user information"""
    try:
        user_profile = user_service.get_user_profile(session['user_id'])
        if user_profile:
            return jsonify({
                'success': True,
                'user': user_profile
            })
        else:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting user info: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@auth_bp.route('/api/uploads')
@login_required
def api_user_uploads():
    """API endpoint to get user's upload history"""
    try:
        uploads = user_service.get_user_uploads(session['user_id'])
        return jsonify({
            'success': True,
            'uploads': uploads or {'resumes': [], 'job_descriptions': []}
        })
        
    except Exception as e:
        logger.error(f"Error getting user uploads: {e}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500