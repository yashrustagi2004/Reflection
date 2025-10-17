import re
from docx import Document
import pdfplumber

class FileParser:
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove emails, phone numbers, and unwanted info."""
        # Remove emails
        text = re.sub(r'\S+@\S+', '', text)
        # Remove phone numbers
        text = re.sub(r'\b\d{10}\b', '', text)
        text = re.sub(r'\+?\d[\d -]{8,}\d', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """Extract text from PDF."""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
        return text

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """Extract text from DOCX."""
        text = ""
        try:
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            print(f"Error reading DOCX: {e}")
        return text

    @staticmethod
    def parse_file(file_path: str) -> str:
        """Main function to parse and clean resume/JD files."""
        if file_path.lower().endswith(".pdf"):
            text = FileParser.extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(".docx"):
            text = FileParser.extract_text_from_docx(file_path)
        else:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception as e:
                print(f"Error reading text file: {e}")
                text = ""
        return FileParser.clean_text(text)
