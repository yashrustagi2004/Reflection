
import os
import sys
import traceback
from flask import Flask, request, jsonify
from functools import wraps
from services.qa_services import QAService
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple
import time
import psutil

from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.database import db_manager
from models.user_questions_model import UserQuestionsModel

# ==================== Authentication Middleware ====================

class AuthMiddleware:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def require_auth(self, f):
        """
        Decorator to enforce authentication on Flask routes.
        Accepts either:
        1. Service-to-service token (X-Service-Token header)
        2. User JWT token (Authorization Bearer header)
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check for service-to-service authentication
            service_token = request.headers.get("X-Service-Token")
            if service_token:
                # For now, we trust service-to-service calls
                # In production, verify the service token properly
                return f(*args, **kwargs)
            
            # Check for user JWT token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split("Bearer ")[-1]
                
                # Check if it's the API auth token
                if token == self.api_token:
                    return f(*args, **kwargs)
                
                # For user JWT tokens, we accept them if they exist
                # In production, you should validate the JWT signature
                if token and len(token) > 20:  # Basic check
                    return f(*args, **kwargs)
            
            # No valid authentication found
            return jsonify({
                "success": False,
                "error": "Missing or invalid authorization"
            }), 401

        return decorated_function


# ==================== App Initialization ====================

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "my-secret-token")
auth_middleware = AuthMiddleware(API_AUTH_TOKEN)

qa_service = QAService()

# Initialize database connection
db_manager.connect()
print("[QA SERVICE] ✅ Database connection initialized")

# Monitoring
# Custom metrics
REQUEST_COUNT = Counter('http_request_total', 'Total HTTP Requests', ['method', 'status', 'path'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Duration', ['method', 'status', 'path'])
REQUEST_IN_PROGRESS = Gauge('http_requests_in_progress', 'HTTP Requests in progress', ['method', 'path'])

# System metrics
CPU_USAGE = Gauge('process_cpu_usage', 'Current CPU usage in percent')
MEMORY_USAGE = Gauge('process_memory_usage_bytes', 'Current memory usage in bytes')

def update_system_metrics():
    CPU_USAGE.set(psutil.cpu_percent())
    MEMORY_USAGE.set(psutil.Process().memory_info().rss)

@app.before_request
def before_request():
    request.start_time = time.time()
    REQUEST_IN_PROGRESS.labels(method=request.method, path=request.path).inc()

@app.after_request
def after_request(response):
    request_latency = time.time() - request.start_time
    REQUEST_COUNT.labels(method=request.method, status=response.status_code, path=request.path).inc()
    REQUEST_LATENCY.labels(method=request.method, status=response.status_code, path=request.path).observe(request_latency)
    REQUEST_IN_PROGRESS.labels(method=request.method, path=request.path).dec()
    return response


@app.route('/metrics')
def metrics():
    update_system_metrics()
    return generate_latest(REGISTRY), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Modify the middleware to return bytes
def metrics_app(environ, start_response):
    update_system_metrics()
    data = generate_latest(REGISTRY)
    status = '200 OK'
    headers = [('Content-Type', CONTENT_TYPE_LATEST), ('Content-Length', str(len(data)))]
    start_response(status, headers)
    return [data]

# Use the modified middleware
app_dispatch = DispatcherMiddleware(app, {
    '/metrics': metrics_app
})



# ==================== Routes ====================

@app.route("/api/questions/generate", methods=["POST"])
@auth_middleware.require_auth
def generate_questions():
    """
    Generate interview questions based on resume and job description.
    Saves questions to MongoDB associated with user.
    Protected by Bearer token.
    
    Expected JSON format:
    {
        "user_id": "user123",
        "resume_text": "...",
        "jd_text": "...",
        "resume_embedding_id": "abc123",
        "jd_embedding_id": "def456"
    }
    
    Returns JSON format:
    {
        "success": true,
        "questions": [...],
        "message": "Generated X questions"
    }
    """
    try:
        data = request.get_json(silent=True) or {}
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        # Extract required fields
        user_id = data.get("user_id", "").strip()
        resume_text = data.get("resume_text", "").strip()
        job_description_text = data.get("jd_text", "").strip()
        resume_embedding_id = data.get("resume_embedding_id")
        jd_embedding_id = data.get("jd_embedding_id")

        # Validate required fields
        if not user_id:
            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if not resume_text:
            return jsonify({
                "success": False,
                "error": "resume_text is required"
            }), 400
        
        # JD is optional - if not provided, generate resume-focused questions
        if not job_description_text:
            job_description_text = "General interview preparation"
            print(f"[QA SERVICE] No JD provided - generating resume-focused questions for user: {user_id}")
        else:
            print(f"[QA SERVICE] Generating questions for user: {user_id} with resume and JD")
        questions = qa_service.generate_questions(resume_text, job_description_text)
        
        if not questions:
            return jsonify({
                "success": False,
                "error": "Failed to generate questions"
            }), 500
        
        print(f"[QA SERVICE] Generated {len(questions)} questions")
        
        # Save questions to MongoDB
        try:
            doc_id = UserQuestionsModel.create_user_questions(
                user_id=user_id,
                resume_embedding_id=resume_embedding_id or "",
                jd_embedding_id=jd_embedding_id or "",
                questions=questions,
                metadata={
                    'resume_length': len(resume_text),
                    'jd_length': len(job_description_text)
                }
            )
            
            if doc_id:
                print(f"[QA SERVICE] ✅ Questions saved to MongoDB for user {user_id}")
            else:
                print(f"[QA SERVICE] ⚠️ Failed to save questions to MongoDB")
                # Don't fail the request, just log the warning
                
        except Exception as e:
            print(f"[QA SERVICE] ⚠️ MongoDB save error: {e}")
            traceback.print_exc()
            # Continue anyway - questions were generated successfully
        
        return jsonify({
            "success": True,
            "questions": questions,
            "message": f"Generated {len(questions)} personalized interview questions",
            "user_id": user_id
        }), 200

    except Exception as e:
        print(f"[QA SERVICE] ❌ Question generation failed: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Question generation failed: {str(e)}"
        }), 500


@app.route("/api/questions/user/<user_id>", methods=["GET"])
@auth_middleware.require_auth
def get_user_questions(user_id):
    """
    Get questions for a specific user from MongoDB.
    Protected by Bearer token.
    
    Returns:
    {
        "success": true,
        "questions": [...],
        "total": 10,
        "user_id": "user123"
    }
    """
    try:
        # Validate user_id
        if not user_id or not isinstance(user_id, str):
            return jsonify({
                "success": False,
                "error": "Invalid user_id"
            }), 400
        
        # Fetch questions from MongoDB
        print(f"[QA SERVICE] Fetching questions for user: {user_id}")
        user_questions_doc = UserQuestionsModel.get_user_questions(user_id)
        
        if not user_questions_doc:
            return jsonify({
                "success": False,
                "error": "No questions found for this user",
                "message": "Please upload resume and job description first"
            }), 404
        
        questions = user_questions_doc.get('questions', [])
        
        return jsonify({
            "success": True,
            "questions": questions,
            "total": len(questions),
            "user_id": user_id,
            "created_at": user_questions_doc.get('created_at').isoformat() if user_questions_doc.get('created_at') else None,
            "updated_at": user_questions_doc.get('updated_at').isoformat() if user_questions_doc.get('updated_at') else None
        }), 200
        
    except Exception as e:
        print(f"[QA SERVICE] ❌ Failed to fetch user questions: {e}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Failed to fetch questions: {str(e)}"
        }), 500


@app.route("/api/answers/analyze", methods=["POST"])
@auth_middleware.require_auth
def analyze_answer():
    """
    Analyze a user's answer to an interview question.
    Protected by Bearer token.
    
    Expected JSON format:
    {
        "question": "The interview question",
        "user_answer": "The user's answer",
        "category": "Technical/Behavioral/General",
        "difficulty": "Easy/Medium/Hard"
    }
    
    Returns JSON with analysis including score and feedback.
    """
    try:
        data = request.get_json(silent=True) or {}
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        question = data.get("question", "").strip()
        user_answer = data.get("user_answer", "").strip()
        category = data.get("category", "General").strip()
        difficulty = data.get("difficulty", "Medium").strip()

        if not question or not user_answer:
            return jsonify({
                "success": False,
                "error": "Both question and user_answer are required"
            }), 400

        # Analyze the answer using QA service
        analysis = qa_service.analyze_answer(question, user_answer, category, difficulty)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "message": "Answer analyzed successfully"
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Answer analysis failed: {str(e)}"
        }), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ==================== App Runner ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5003))

    use_debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    try:
        # run_simple(hostname, port, application, use_reloader=False, use_debugger=False, threaded=False)
        run_simple('0.0.0.0', port, app_dispatch, use_reloader=use_debug, use_debugger=use_debug)
    except Exception:
        # Fallback to Flask's development server if run_simple isn't available or fails
        app.run(host='0.0.0.0', port=port, debug=use_debug)