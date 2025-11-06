from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.0-flash",
    temperature=0.6
)

def generate_interview_questions(docs):
    # Combine all parsed content
    full_document_content = "\n\n".join([doc.page_content for doc in docs])

    # Prompt template
    question_gen_prompt_text = """
    Based on the provided resume and job description below, please act as a senior hiring manager.
    Your task is to generate a list of 5-7 insightful interview questions that thoroughly probe
    the candidate's suitability for the role. The questions should cover technical skills,
    behavioral competencies, and past project experiences mentioned in the resume.

    <context>
    {context}
    </context>

    Questions:
    """
    question_gen_prompt = ChatPromptTemplate.from_template(question_gen_prompt_text)
    question_generation_chain = question_gen_prompt | llm

    # Generate response
    response = question_generation_chain.invoke({"context": full_document_content})
    interview_questions = response.content.strip().split("\n")

    return interview_questions
