
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
        Decorator to enforce Bearer token authentication on Flask routes.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({
                    "success": False,
                    "error": "Missing or invalid authorization header"
                }), 401

            token = auth_header.split("Bearer ")[-1]

            if token != self.api_token:
                return jsonify({
                    "success": False,
                    "error": "Invalid or expired token"
                }), 403

            # Token is valid → proceed to the view
            return f(*args, **kwargs)

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


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


# ==================== App Runner ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
