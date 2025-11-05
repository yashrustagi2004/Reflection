import os
import random
import json
import traceback
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
# from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv

load_dotenv()

try:
    import pinecone
except Exception:
    pinecone = None


# -------------------------
# Utility: Mock / Local generation (used as fallback)
# -------------------------
def _mock_select_questions_from_templates(resume_text: str, job_description_text: str, n: int = 8) -> List[Dict]:
    base_questions = [
        {"text": "Tell me about a challenging project you worked on and how you overcame the obstacles.", "category": "Behavioral", "difficulty": "Medium"},
        {"text": "Describe a time you had to learn a new technology quickly to complete a project. What was your approach?", "category": "Behavioral", "difficulty": "Medium"},
        {"text": "Explain the architecture you used for a recent project and why you chose it.", "category": "Technical", "difficulty": "Hard"},
        {"text": "How do you ensure code quality and maintainability in your projects?", "category": "Technical", "difficulty": "Medium"},
        {"text": "Describe a time you had conflict on a team. How did you resolve it?", "category": "Behavioral", "difficulty": "Medium"},
        {"text": "What's a performance optimization you implemented and how did you measure its impact?", "category": "Technical", "difficulty": "Hard"},
        {"text": "How do you prioritize your work when you have multiple deadlines?", "category": "Behavioral", "difficulty": "Easy"},
        {"text": "Explain a bug you diagnosed and fixed. How did you approach debugging?", "category": "Technical", "difficulty": "Medium"},
        {"text": "What motivates you in your engineering/career path?", "category": "General", "difficulty": "Easy"},
        {"text": "How do you stay current with new technologies and trends?", "category": "General", "difficulty": "Easy"},
    ]

    jd_lower = job_description_text.lower()
    resume_lower = resume_text.lower()

    if any(k in jd_lower for k in ["cloud", "aws", "gcp", "azure"]):
        base_questions.append({
            "text": "Describe your experience with cloud platforms (AWS/GCP/Azure) and an architecture you deployed to the cloud.",
            "category": "Technical",
            "difficulty": "Hard"
        })

    if "lead" in resume_lower or "manager" in resume_lower:
        base_questions.append({
            "text": "Describe a time you mentored or led a team. What was the outcome?",
            "category": "Behavioral",
            "difficulty": "Medium"
        })

    return random.sample(base_questions, min(n, len(base_questions)))


# -------------------------
# QAService class: integrates Gemini + embeddings + Pinecone
# -------------------------
class QAService:
    def __init__(self, index_name: Optional[str] = None):
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        self.pinecone_env = os.getenv("PINECONE_ENVIRONMENT")
        self.index_name = index_name or os.getenv("PINECONE_INDEX", "qa-index")

        self.embed_model = None
        self.vector_index = None
        self.in_memory_store = []

        # Initialize embeddings
        self._init_embedding_model()
        self._init_vector_store()

        # Initialize Gemini (Google Generative AI)
        google_api_key = os.getenv("GOOGLE_API_KEY")

        if google_api_key:
            self.genai = ChatGoogleGenerativeAI(model="models/gemini-2.0-flash", google_api_key=google_api_key)
        else:
            self.genai = None

        print(f"✅ Gemini client initialized: {bool(self.genai)} with key: {bool(google_api_key)}")


    # -------------------------
    # Vector/embedding setup
    # -------------------------
    def _init_embedding_model(self):
        try:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            self.embed_model = HuggingFaceEmbeddings(model_name=model_name)
        except Exception:
            self.embed_model = None

    def _init_vector_store(self):
        """
        Initializes Pinecone index (if configured), otherwise defaults to in-memory mode.
        """
        if self.pinecone_api_key and pinecone is not None:
            try:
                pc = Pinecone(api_key=self.pinecone_api_key)
                index_name = "interview-prep-assistant"
                embedding_dimension = 384  # Based on all-MiniLM-L6-v2

                # ✅ FIX: Safely handle .list_indexes() API change
                existing_indexes = [i["name"] for i in pc.list_indexes()]

                if index_name not in existing_indexes:
                    print(f"Creating new index: {index_name}")
                    pc.create_index(
                        name=index_name,
                        dimension=embedding_dimension,
                        metric="cosine",
                        spec=ServerlessSpec(cloud="aws", region="us-east-1")
                    )

                # ✅ FIX: Removed undefined `text_chunks` (was causing NameError)
                # This section just confirms index connection instead of uploading
                print(f"Pinecone index '{index_name}' is ready.")
                self.vector_index = "pinecone"
                return
            except Exception:
                traceback.print_exc()

        # Fallback
        self.vector_index = "in_memory"
        print("⚠️ Pinecone not initialized, using in-memory fallback.")
        return

    def _embedding_dim(self) -> int:
        if self.embed_model is not None:
            return self.embed_model.get_sentence_embedding_dimension()
        return 384


    # -------------------------
    # Core: Question Generation using Gemini
    # -------------------------
    def generate_questions(self, resume_text: str, job_description_text: str) -> List[Dict]:
        prompt = (
            f"You are an expert hiring manager. Based on the resume and job description, "
            f"generate 8 personalized interview questions. Return a JSON array of objects with fields: "
            f"'text', 'category' (Behavioral/Technical/General), and 'difficulty' (Easy/Medium/Hard). "
            f"Resume:\n{resume_text}\n\nJob Description:\n{job_description_text}"
        )

        if self.genai:
            try:
                response = self.genai.invoke(prompt)
                text = getattr(response, "content", None) or getattr(response, "text", None) or str(response)

                # ✅ Robust JSON parsing fallback
                try:
                    questions = json.loads(text)
                except json.JSONDecodeError:
                    print("⚠️ Gemini response not JSON, trying to extract JSON substring...")
                    start = text.find("[")
                    end = text.rfind("]") + 1
                    questions = json.loads(text[start:end])

                return questions
            except Exception:
                traceback.print_exc()
                return _mock_select_questions_from_templates(resume_text, job_description_text, n=8)
        else:
            return _mock_select_questions_from_templates(resume_text, job_description_text, n=8)


    # -------------------------
    # Core: Ideal Answer Generation using Gemini
    # -------------------------
    def generate_ideal_answers(self, questions: List[Dict], resume_text: str, job_description_text: str) -> List[Dict]:
        questions_json = json.dumps(questions, ensure_ascii=False)
        prompt = (
            f"You are an expert interviewer. For each question below, generate an ideal answer "
            f"and a list of 3-5 short actionable tips. Return a JSON array with objects having fields "
            f"'question', 'ideal_answer', 'category', and 'tips'.\n\n"
            f"Questions: {questions_json}\n\n"
            f"Resume:\n{resume_text}\n\nJob Description:\n{job_description_text}"
        )

        if self.genai:
            try:
                response = self.genai.invoke(prompt)
                text = getattr(response, "content", None) or getattr(response, "text", None) or str(response)

                try:
                    answers = json.loads(text)
                except json.JSONDecodeError:
                    print("⚠️ Gemini response not JSON, trying to extract JSON substring...")
                    start = text.find("[")
                    end = text.rfind("]") + 1
                    answers = json.loads(text[start:end])

                return answers
            except Exception:
                traceback.print_exc()

        # fallback
        answers = []
        for q in questions:
            question_text = q.get("text", "")
            category = q.get("category", "General")
            ideal_answer = (
                f"For the question '{question_text}', connect your answer to your achievements "
                f"and relate them to the job description."
            )
            answers.append({
                "question": question_text,
                "ideal_answer": ideal_answer,
                "category": category,
                "tips": [
                    "Be specific and use examples from your experience",
                    "Connect your answer to the job requirements",
                    "Show enthusiasm and clarity",
                ]
            })
        return answers
