"""
Question-Answer Generation Microservice
Handles interview question generation and ideal answer creation
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Add parent directory to path for shared imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.auth_middleware import AuthMiddleware
from shared.service_client import ServiceClient

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=os.getenv('ALLOWED_ORIGINS', '*').split(','))

# Initialize services
auth_middleware = AuthMiddleware()
service_client = ServiceClient('question-answer-generation')


# ==================== Health Check ====================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'service': 'question-answer-generation',
        'status': 'healthy'
    }), 200


# ==================== Question Generation ====================

@app.route('/api/questions/generate', methods=['POST'])
# @auth_middleware.require_auth  # Temporarily disabled for testing
def generate_questions():
    """
    Generate interview questions based on resume and job description
    
    Expected input:
    {
        "resume_text": "...",
        "job_description_text": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        resume_text = data.get('resume_text', '')
        job_description_text = data.get('job_description_text', '')
        
        if not resume_text or not job_description_text:
            return jsonify({
                'success': False,
                'error': 'Both resume and job description text are required'
            }), 400
        
        # Generate questions using AI (mock implementation for now)
        # In a real implementation, this would use Google Gemini or similar AI service
        questions = generate_interview_questions(resume_text, job_description_text)
        
        return jsonify({
            'success': True,
            'questions': questions,
            'message': f'Generated {len(questions)} personalized interview questions'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Question generation failed: {str(e)}'
        }), 500


def generate_interview_questions(resume_text, job_description_text):
    """
    Generate personalized interview questions based on resume and job description
    This is a mock implementation - in production, this would use AI services
    """
    # Mock question templates that would be personalized by AI
    base_questions = [
        {
            "text": "Tell me about a challenging project you worked on and how you overcame the obstacles.",
            "category": "Behavioral",
            "difficulty": "Medium"
        },
        {
            "text": "How would you approach debugging a performance issue in a web application?",
            "category": "Technical",
            "difficulty": "Hard"
        },
        {
            "text": "Describe a time when you had to work with a difficult team member. How did you handle it?",
            "category": "Behavioral",
            "difficulty": "Medium"
        },
        {
            "text": "What design patterns would you use to build a scalable microservices architecture?",
            "category": "Technical",
            "difficulty": "Hard"
        },
        {
            "text": "How do you stay updated with the latest technologies in your field?",
            "category": "General",
            "difficulty": "Easy"
        },
        {
            "text": "Explain the difference between SQL and NoSQL databases and when you would use each.",
            "category": "Technical",
            "difficulty": "Medium"
        },
        {
            "text": "Tell me about a time when you had to learn a new technology quickly for a project.",
            "category": "Behavioral",
            "difficulty": "Medium"
        },
        {
            "text": "How would you handle a situation where your code broke in production?",
            "category": "Technical",
            "difficulty": "Hard"
        },
        {
            "text": "What is your approach to code review and ensuring code quality?",
            "category": "Technical",
            "difficulty": "Medium"
        },
        {
            "text": "Describe a time when you had to meet a tight deadline. How did you manage it?",
            "category": "Behavioral",
            "difficulty": "Medium"
        }
    ]
    
    # In a real implementation, this would analyze the resume and job description
    # to generate personalized questions using AI
    # For now, we'll return a mix of questions
    import random
    selected_questions = random.sample(base_questions, min(8, len(base_questions)))
    
    return selected_questions


@app.route('/api/answers/generate', methods=['POST'])
@auth_middleware.require_auth
def generate_ideal_answers():
    """
    Generate ideal answers for questions based on resume and job description
    
    Expected input:
    {
        "questions": [...],
        "resume_text": "...",
        "job_description_text": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        questions = data.get('questions', [])
        resume_text = data.get('resume_text', '')
        job_description_text = data.get('job_description_text', '')
        
        if not questions or not resume_text or not job_description_text:
            return jsonify({
                'success': False,
                'error': 'Questions, resume text, and job description text are required'
            }), 400
        
        # Generate ideal answers using AI (mock implementation for now)
        answers = generate_ideal_answers_for_questions(questions, resume_text, job_description_text)
        
        return jsonify({
            'success': True,
            'answers': answers,
            'message': f'Generated ideal answers for {len(answers)} questions'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Answer generation failed: {str(e)}'
        }), 500


def generate_ideal_answers_for_questions(questions, resume_text, job_description_text):
    """
    Generate ideal answers for interview questions based on resume and job description
    This is a mock implementation - in production, this would use AI services
    """
    answers = []
    
    for question in questions:
        question_text = question.get('text', '')
        category = question.get('category', 'General')
        
        # Generate a mock ideal answer based on question category
        if category == 'Behavioral':
            ideal_answer = f"Based on your experience, you should structure your answer using the STAR method (Situation, Task, Action, Result). For this question about '{question_text}', focus on a specific example from your background that demonstrates relevant skills mentioned in the job description."
        elif category == 'Technical':
            ideal_answer = f"For this technical question: '{question_text}', provide a clear, step-by-step explanation. Include relevant technologies from your resume and how they apply to the role. Be specific about tools, frameworks, or methodologies you've used."
        else:
            ideal_answer = f"Address this question: '{question_text}' by connecting your experience to the job requirements. Highlight relevant skills and achievements from your resume that align with what the company is looking for."
        
        answers.append({
            'question': question_text,
            'ideal_answer': ideal_answer,
            'category': category,
            'tips': [
                "Be specific and use examples from your experience",
                "Connect your answer to the job requirements",
                "Show enthusiasm and passion for the role",
                "Ask clarifying questions if needed"
            ]
        })
    
    return answers


if __name__ == '__main__':
    port = int(os.getenv('QA_GENERATION_PORT', 5003))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
