"""
File Security Service
Handles file upload validation and security checks
"""

import os
import re
import hashlib
import magic
from typing import Tuple, Dict, Any, Optional
from werkzeug.utils import secure_filename
import html


class FileSecurityService:
    """Service for secure file upload handling"""
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    
    # Allowed MIME types
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # Magic number signatures for file type validation
    ALLOWED_SIGNATURES = {
        b'%PDF': 'pdf',
        b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1': 'doc',  # MS Office compound document
        b'PK\x03\x04': 'docx'  # ZIP-based format (DOCX)
    }
    
    # File size limits
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_FILENAME_LENGTH = 100
    
    # Text content limits
    MIN_TEXT_LENGTH = 50
    MAX_TEXT_LENGTH = 5000
    
    def validate_upload(self, file) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive file upload validation
        
        Args:
            file: FileStorage object from Flask request
            
        Returns:
            Tuple of (is_valid, message, validation_details)
        """
        validation_details = {}
        
        # Check if file exists
        if not file or not file.filename:
            return False, "No file provided", validation_details
        
        # Validate filename
        is_valid, message = self._validate_filename(file.filename)
        validation_details['filename'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            return False, message, validation_details
        
        # Validate file extension
        is_valid, message = self._validate_extension(file.filename)
        validation_details['extension'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            return False, message, validation_details
        
        # Read file content for further validation
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Validate file size
        is_valid, message = self._validate_size(len(file_content))
        validation_details['size'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            return False, message, validation_details
        
        # Validate magic numbers (file signature)
        is_valid, message = self._validate_magic_numbers(file_content)
        validation_details['magic_numbers'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            return False, message, validation_details
        
        # Validate MIME type using python-magic
        is_valid, message = self._validate_mime_type(file_content)
        validation_details['mime_type'] = {'valid': is_valid, 'message': message}
        if not is_valid:
            return False, message, validation_details
        
        return True, "File validation successful", validation_details
    
    def _validate_filename(self, filename: str) -> Tuple[bool, str]:
        """Validate filename for security issues"""
        if not filename:
            return False, "No filename provided"
        
        if len(filename) > self.MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {self.MAX_FILENAME_LENGTH} characters)"
        
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename: path traversal detected"
        
        # Check for null bytes
        if '\x00' in filename:
            return False, "Invalid filename: null byte detected"
        
        # Check for control characters
        if any(ord(c) < 32 for c in filename):
            return False, "Invalid filename: control characters detected"
        
        return True, "Filename valid"
    
    def _validate_extension(self, filename: str) -> Tuple[bool, str]:
        """Validate file extension"""
        ext = os.path.splitext(filename)[1].lower()
        
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"File type not allowed. Allowed types: {', '.join(self.ALLOWED_EXTENSIONS)}"
        
        return True, "Extension valid"
    
    def _validate_size(self, size: int) -> Tuple[bool, str]:
        """Validate file size"""
        if size == 0:
            return False, "File is empty"
        
        if size > self.MAX_FILE_SIZE:
            max_mb = self.MAX_FILE_SIZE / (1024 * 1024)
            return False, f"File too large (max {max_mb}MB)"
        
        return True, "Size valid"
    
    def _validate_magic_numbers(self, content: bytes) -> Tuple[bool, str]:
        """Validate file type using magic numbers (file signature)"""
        if len(content) < 8:
            return False, "File too small to validate"
        
        # Check against known signatures
        for signature, file_type in self.ALLOWED_SIGNATURES.items():
            if content.startswith(signature):
                return True, f"Valid {file_type} file signature"
        
        return False, "Invalid file signature"
    
    def _validate_mime_type(self, content: bytes) -> Tuple[bool, str]:
        """Validate MIME type using python-magic"""
        try:
            mime = magic.from_buffer(content, mime=True)
            
            if mime not in self.ALLOWED_MIME_TYPES:
                return False, f"Invalid MIME type: {mime}"
            
            return True, f"Valid MIME type: {mime}"
            
        except Exception as e:
            return False, f"MIME type validation failed: {str(e)}"
    
    def generate_secure_filename(self, original_filename: str, user_id: str, 
                                 file_type: str) -> str:
        """
        Generate a secure, unique filename
        
        Args:
            original_filename: Original uploaded filename
            user_id: User identifier
            file_type: Type of file (resume, job_description, etc.)
            
        Returns:
            Secure filename with hash
        """
        # Get safe base filename
        base = secure_filename(original_filename)
        name, ext = os.path.splitext(base)
        
        # Create hash from original name and timestamp
        timestamp = str(int(__import__('time').time() * 1000))
        hash_input = f"{name}{user_id}{timestamp}".encode('utf-8')
        file_hash = hashlib.sha256(hash_input).hexdigest()[:8]
        
        # Construct secure filename
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)[:50]
        secure_name = f"{safe_name}_{file_hash}_{timestamp}{ext}"
        
        return secure_name
    
    def get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Get file metadata
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file metadata
        """
        try:
            stat = os.stat(file_path)
            mime_type = magic.from_file(file_path, mime=True)
            
            return {
                'size': stat.st_size,
                'mime_type': mime_type,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
        except Exception:
            return {}
    
    def validate_text_content(self, text: str) -> Tuple[bool, str]:
        """
        Validate text content for job descriptions
        
        Args:
            text: Text content to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not text or not text.strip():
            return False, "Text content is empty"
        
        text_length = len(text.strip())
        
        if text_length < self.MIN_TEXT_LENGTH:
            return False, f"Text too short (minimum {self.MIN_TEXT_LENGTH} characters)"
        
        if text_length > self.MAX_TEXT_LENGTH:
            return False, f"Text too long (maximum {self.MAX_TEXT_LENGTH} characters)"
        
        return True, "Text content valid"
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """
        Sanitize text content to prevent XSS and injection attacks
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # HTML escape
        sanitized = html.escape(text)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    @staticmethod
    def is_safe_path(path: str, base_directory: str) -> bool:
        """
        Check if a file path is safe (within allowed directory)
        
        Args:
            path: File path to check
            base_directory: Allowed base directory
            
        Returns:
            True if path is safe, False otherwise
        """
        try:
            # Resolve to absolute paths
            base = os.path.abspath(base_directory)
            target = os.path.abspath(path)
            
            # Check if target is within base directory
            return target.startswith(base) and os.path.exists(target)
            
        except Exception:
            return False
    
    @staticmethod
    def get_upload_requirements() -> Dict[str, Any]:
        """Get upload requirements for client"""
        return {
            'max_file_size': FileSecurityService.MAX_FILE_SIZE,
            'max_file_size_mb': FileSecurityService.MAX_FILE_SIZE / (1024 * 1024),
            'allowed_extensions': list(FileSecurityService.ALLOWED_EXTENSIONS),
            'allowed_mime_types': list(FileSecurityService.ALLOWED_MIME_TYPES),
            'max_filename_length': FileSecurityService.MAX_FILENAME_LENGTH,
            'text_min_length': FileSecurityService.MIN_TEXT_LENGTH,
            'text_max_length': FileSecurityService.MAX_TEXT_LENGTH
        }
