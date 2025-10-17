"""
File Parser Service
Handles document parsing and text extraction
"""

import os
from typing import Optional
import PyPDF2
import docx


class FileParserService:
    """Service for parsing and extracting text from documents"""
    
    def parse_document(self, file_path: str) -> Optional[str]:
        """
        Parse document and extract text content
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Extracted text content or None if parsing fails
        """
        if not os.path.exists(file_path):
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.pdf':
                return self._parse_pdf(file_path)
            elif ext == '.docx':
                return self._parse_docx(file_path)
            elif ext == '.doc':
                return self._parse_doc(file_path)
            elif ext == '.txt':
                return self._parse_txt(file_path)
            else:
                return None
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}")
            return None
    
    def _parse_pdf(self, file_path: str) -> Optional[str]:
        """Extract text from PDF file"""
        try:
            text_content = []
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            return '\n'.join(text_content)
            
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return None
    
    def _parse_docx(self, file_path: str) -> Optional[str]:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(file_path)
            text_content = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_content.append(paragraph.text)
            
            return '\n'.join(text_content)
            
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return None
    
    def _parse_doc(self, file_path: str) -> Optional[str]:
        """
        Extract text from DOC file
        Note: Parsing .doc files is more complex and may require additional libraries
        like python-docx or antiword. For now, return a placeholder.
        """
        # TODO: Implement DOC parsing using appropriate library
        # For production, consider using antiword or python-docx with compatibility mode
        try:
            # Placeholder: attempt to read as text
            with open(file_path, 'rb') as file:
                content = file.read()
                # Basic text extraction (may not work well for all .doc files)
                text = content.decode('latin-1', errors='ignore')
                return text
        except Exception as e:
            print(f"Error parsing DOC: {e}")
            return None
    
    def _parse_txt(self, file_path: str) -> Optional[str]:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error parsing TXT: {e}")
            return None
