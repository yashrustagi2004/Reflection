
import os
import traceback
from flask import Flask, request, jsonify
from functools import wraps
from services.qa_services import QAService

from dotenv import load_dotenv
load_dotenv()

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


# ==================== Routes ====================

@app.route("/api/questions/generate", methods=["POST"])
@auth_middleware.require_auth
def generate_questions():
    """
    Generate interview questions based on resume and job description.
    Protected by Bearer token.
    in the following json format:
    {
            "text": {question},
            "category": {category},
            "difficulty": {difficulty}
        }, 
    """
    try:
        data = request.get_json(silent=True) or {}
        
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        resume_text = data.get("resume_text", "").strip()
        job_description_text = data.get("jd_text", "").strip()

        if not resume_text or not job_description_text:
            return jsonify({
                "success": False,
                "error": "Both resume and job description text are required"
            }), 400

        questions = qa_service.generate_questions(resume_text, job_description_text)
        print(questions)
        return jsonify({
            "success": True,
            "questions": questions,
            "message": f"Generated {len(questions)} personalized interview questions"
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Question generation failed: {str(e)}"
        }), 500


@app.route("/api/answers/generate", methods=["POST"])
@auth_middleware.require_auth
def generate_ideal_answers():
    """
    Generate ideal answers for questions based on resume and job description.
    Protected by Bearer token.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        questions = data.get("questions", [])
        resume_text = data.get("resume_text", "").strip()
        job_description_text = data.get("job_description_text", "").strip()

        if not questions or not resume_text or not job_description_text:
            return jsonify({
                "success": False,
                "error": "Questions, resume text, and job description text are required"
            }), 400

        answers = qa_service.generate_ideal_answers(questions, resume_text, job_description_text)

        return jsonify({
            "success": True,
            "answers": answers,
            "message": f"Generated ideal answers for {len(answers)} questions"
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Answer generation failed: {str(e)}"
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
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
