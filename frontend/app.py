from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
import os
import sys
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ✅ Add this — make sure Python can find backend
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from utils.file_security import FileUploadSecurity
from backend.utils.parser import FileParser


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

# Global variable to store parsed text data
docs = {
    "resumes": {},
    "job_descriptions": {}
}

# Create directories if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)

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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        if not name or not email or not message:
            flash("All fields are required!", "error")
            return redirect(url_for('contact'))

        print(f"📩 New message received:\nFrom: {name} ({email})\nMessage: {message}\n")

        flash("Thank you for contacting us! We’ll get back to you soon.", "success")
        return redirect(url_for('contact'))

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

        # Validate file
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        if not is_valid:
            return jsonify({'success': False, 'message': message})

        # Save original file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', safe_filename)
        file.save(file_path)

        #  Parse and clean resume text (store in variable, not file)
        parsed_text = FileParser.extract_text(file_path)
        docs["resumes"][user_id] = parsed_text  # Store in global variable

        # Add upload record
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
            'message': 'Resume uploaded and parsed successfully!',
            'filename': safe_filename,
            'parsed_text_preview': parsed_text[:300]  # preview first 300 chars
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

        # Validate file
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        if not is_valid:
            return jsonify({'success': False, 'message': message})

        # Save JD
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', safe_filename)
        file.save(file_path)

        # Parse and clean JD text (store in variable)
        parsed_text = FileParser.extract_text(file_path)
        docs["job_descriptions"][user_id] = parsed_text

        # Add upload record
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
            'message': 'Job description uploaded and parsed successfully!',
            'filename': safe_filename,
            'parsed_text_preview': parsed_text[:300]
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
        jd_filename = f"jd_text_{user_id}_{int(__import__('time').time())}.txt"
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', jd_filename)

        with open(jd_path, 'w', encoding='utf-8') as f:
            f.write(job_description)

        # Clean text and store in docs
        parsed_text = FileParser.clean_text(job_description)
        docs["job_descriptions"][user_id] = parsed_text

        # Add upload record
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
            'message': 'Job description saved and parsed successfully!',
            'parsed_text_preview': parsed_text[:300]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving job description: {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)
