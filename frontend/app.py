from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import os
import sys
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.file_security import FileUploadSecurity

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Add backend to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.routes.auth_routes import auth_bp, login_required
from backend.services.user_service import UserService
from backend.config.database import init_database

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Register authentication blueprint
app.register_blueprint(auth_bp)

# Initialize database
try:
    init_database()
    print("✅ Database connected successfully")
except Exception as e:
    print(f"⚠️ Database connection failed: {e}")
    print("The app will run but authentication features will be limited")

# Initialize services
try:
    user_service = UserService()
    if user_service.user_model is not None:
        print("✅ User service initialized")
    else:
        print("⚠️ User service initialized but database connection failed")
except Exception as e:
    print(f"⚠️ User service initialization failed: {e}")
    user_service = None

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    requirements = FileUploadSecurity.get_upload_requirements()
    user_profile = None
    if user_service and user_service.user_model:
        user_profile = user_service.get_user_profile(session['user_id'])
    return render_template('home.html', upload_requirements=requirements, user=user_profile)

@app.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    try:
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['resume_file']
        user_id = session['user_id']
        
        # Validate file using security utility
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', safe_filename)
        file.save(file_path)
        
        # Add upload record to user profile
        if user_service and user_service.user_model:
            file_info = {
                'filename': safe_filename,
                'original_name': file.filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_type': 'resume'
            }
            user_service.add_user_upload(user_id, 'resumes', file_info)
        
        return jsonify({
            'success': True, 
            'message': 'Resume uploaded successfully!',
            'filename': safe_filename,
            'original_filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/upload_job_description', methods=['POST'])
@login_required
def upload_job_description():
    try:
        if 'jd_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['jd_file']
        user_id = session['user_id']
        
        # Validate file using security utility
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', safe_filename)
        file.save(file_path)
        
        # Add upload record to user profile
        if user_service and user_service.user_model:
            file_info = {
                'filename': safe_filename,
                'original_name': file.filename,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'file_type': 'job_description'
            }
            user_service.add_user_upload(user_id, 'job_descriptions', file_info)
        
        return jsonify({
            'success': True, 
            'message': 'Job description uploaded successfully!',
            'filename': safe_filename,
            'original_filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/submit_job_description', methods=['POST'])
@login_required
def submit_job_description():
    try:
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({'success': False, 'message': 'Job description cannot be empty'})
        
        if len(job_description) < 50:
            return jsonify({'success': False, 'message': 'Job description too short (minimum 50 characters)'})
        
        if len(job_description) > 5000:
            return jsonify({'success': False, 'message': 'Job description too long (maximum 5000 characters)'})
        
        user_id = session['user_id']
        
        # Save to file
        jd_filename = f"jd_text_{user_id}_{int(__import__('time').time())}.txt"
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', jd_filename)
        
        with open(jd_path, 'w', encoding='utf-8') as f:
            f.write(job_description)
        
        # Add upload record to user profile
        if user_service and user_service.user_model:
            file_info = {
                'filename': jd_filename,
                'original_name': 'Text Job Description',
                'file_path': jd_path,
                'file_size': len(job_description.encode('utf-8')),
                'file_type': 'job_description_text'
            }
            user_service.add_user_upload(user_id, 'job_descriptions', file_info)
        
        return jsonify({
            'success': True,
            'message': 'Job description saved successfully!',
            'filename': jd_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving job description: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)