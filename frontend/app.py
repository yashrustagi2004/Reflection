from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from utils.file_security import FileUploadSecurity

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions'), exist_ok=True)

@app.route('/')
def home():
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

@app.route('/home')
def dashboard():
    requirements = FileUploadSecurity.get_upload_requirements()
    return render_template('home.html', upload_requirements=requirements)

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    try:
        if 'resume_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['resume_file']
        user_id = request.form.get('user_id', 'anonymous')  # You'll get this from session later
        
        # Validate file using security utility
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', safe_filename)
        file.save(file_path)
        
        return jsonify({
            'success': True, 
            'message': 'Resume uploaded successfully!',
            'filename': safe_filename,
            'original_filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/upload_job_description', methods=['POST'])
def upload_job_description():
    try:
        if 'jd_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file selected'})
        
        file = request.files['jd_file']
        user_id = request.form.get('user_id', 'anonymous')  # You'll get this from session later
        
        # Validate file using security utility
        is_valid, message, safe_filename = FileUploadSecurity.validate_upload(file, user_id)
        
        if not is_valid:
            return jsonify({'success': False, 'message': message})
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', safe_filename)
        file.save(file_path)
        
        return jsonify({
            'success': True, 
            'message': 'Job description uploaded successfully!',
            'filename': safe_filename,
            'original_filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/submit_job_description', methods=['POST'])
def submit_job_description():
    try:
        job_description = request.form.get('job_description', '').strip()
        
        if not job_description:
            return jsonify({'success': False, 'message': 'Job description cannot be empty'})
        
        if len(job_description) < 50:
            return jsonify({'success': False, 'message': 'Job description too short (minimum 50 characters)'})
        
        if len(job_description) > 5000:
            return jsonify({'success': False, 'message': 'Job description too long (maximum 5000 characters)'})
        
        # Here you would save the job description to database or file
        # For now, we'll just return success
        user_id = request.form.get('user_id', 'anonymous')
        
        # Save to file (in production, use database)
        jd_filename = f"jd_text_{user_id}_{int(__import__('time').time())}.txt"
        jd_path = os.path.join(app.config['UPLOAD_FOLDER'], 'job_descriptions', jd_filename)
        
        with open(jd_path, 'w', encoding='utf-8') as f:
            f.write(job_description)
        
        return jsonify({
            'success': True,
            'message': 'Job description saved successfully!',
            'filename': jd_filename
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving job description: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)