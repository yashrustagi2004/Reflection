"""
Enhanced File Parser with PII Removal
Handles secure document parsing and personal information removal
"""

import re
import os
from typing import Optional
import pdfplumber
from docx import Document


class EnhancedFileParser:
    """Enhanced file parser with PII removal capabilities"""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Remove emails, phone numbers, and other PII from text.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text with PII removed
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove email addresses (improved regex)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REMOVED]', text)
        
        # Remove phone numbers (various formats)
        # US formats: (xxx) xxx-xxxx, xxx-xxx-xxxx, xxx.xxx.xxxx, xxxxxxxxxx
        text = re.sub(r'\b\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})\b', '[PHONE_REMOVED]', text)
        
        # International formats: +xx xxx xxx xxxx
        text = re.sub(r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_REMOVED]', text)
        
        # Remove standalone 10+ digit numbers that might be phone numbers
        text = re.sub(r'\b\d{10,}\b', '[NUMBER_REMOVED]', text)
        
        # Remove URLs (optional - might contain personal domains)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '[URL_REMOVED]', text)
        
        # Remove common address patterns (basic)
        # Street addresses with numbers
        text = re.sub(r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b', '[ADDRESS_REMOVED]', text, flags=re.IGNORECASE)
        
        # Remove extra whitespace and clean up
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove multiple consecutive removed markers
        text = re.sub(r'(\[.*?_REMOVED\]\s*){2,}', '[PII_REMOVED] ', text)
        
        return text

    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        Extract text from PDF file using pdfplumber.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not os.path.exists(file_path):
            return None
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            return None
        
        return text.strip() if text else None

    @staticmethod
    def extract_text_from_docx(file_path: str) -> Optional[str]:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not os.path.exists(file_path):
            return None
        
        text = ""
        try:
            doc = Document(file_path)
            paragraphs = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    paragraphs.append(paragraph.text.strip())
            
            text = "\n".join(paragraphs)
            
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {e}")
            return None
        
        return text.strip() if text else None

    @staticmethod
    def extract_text_from_txt(file_path: str) -> Optional[str]:
        """
        Extract text from TXT file with encoding handling.
        
        Args:
            file_path: Path to TXT file
            
        Returns:
            Extracted text or None if extraction fails
        """
        if not os.path.exists(file_path):
            return None
        
        # Try different encodings
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    text = f.read()
                return text.strip() if text else None
            except Exception:
                continue
        
        print(f"Error reading TXT file {file_path}: Could not decode with any encoding")
        return None

    @staticmethod
    def parse_file(file_path: str, remove_pii: bool = False) -> Optional[str]:
        """
        Main function to parse files and optionally remove PII.
        
        Args:
            file_path: Path to the file to parse
            remove_pii: Whether to remove PII from the extracted text
            
        Returns:
            Parsed text content (with PII removed if requested)
        """
        if not file_path or not os.path.exists(file_path):
            return None
        
        # Validate file path for security
        if '..' in file_path or file_path.startswith('/'):
            print(f"Security warning: Potentially unsafe file path {file_path}")
            return None
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Extract text based on file type
        text = None
        if ext == ".pdf":
            text = EnhancedFileParser.extract_text_from_pdf(file_path)
        elif ext == ".docx":
            text = EnhancedFileParser.extract_text_from_docx(file_path)
        elif ext in [".txt", ".text"]:
            text = EnhancedFileParser.extract_text_from_txt(file_path)
        else:
            # Try as text file for unknown extensions
            text = EnhancedFileParser.extract_text_from_txt(file_path)
        
        if text and remove_pii:
            text = EnhancedFileParser.clean_text(text)
        
        return text

    @staticmethod
    def validate_file_for_parsing(file_path: str) -> tuple[bool, str]:
        """
        Validate if file can be safely parsed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path:
            return False, "File path is required"
        
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file size (max 50MB for parsing)
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:  # 50MB
                return False, "File too large for parsing"
        except Exception:
            return False, "Cannot access file"
        
        # Check file extension
        _, ext = os.path.splitext(file_path)
        allowed_extensions = {'.pdf', '.docx', '.txt', '.text'}
        if ext.lower() not in allowed_extensions:
            return False, f"Unsupported file type: {ext}"
        
        return True, "File is valid for parsing"