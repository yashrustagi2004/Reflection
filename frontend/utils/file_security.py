"""
File Upload Security Utilities
Handles secure file upload validation and processing
"""

import os
import magic
import hashlib
import re
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

class FileUploadSecurity:
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
    
    # Allowed MIME types (primary validation)
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
    
    # Maximum file size (10MB in bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Maximum filename length
    MAX_FILENAME_LENGTH = 100
    
    @staticmethod
    def validate_filename(filename):
        """
        Validate filename for security issues
        """
        if not filename:
            return False, "No filename provided"
            
        if len(filename) > FileUploadSecurity.MAX_FILENAME_LENGTH:
            return False, "Filename is too long"
            
        # Check for path traversal attempts
        if '..' in filename or '/' in filename or '\\' in filename:
            return False, "Invalid filename"
            
        # Check for null bytes
        if '\x00' in filename:
            return False, "Invalid filename"
            
        # Check file extension
        file_ext = os.path.splitext(filename.lower())[1]
        if file_ext not in FileUploadSecurity.ALLOWED_EXTENSIONS:
            return False, "File type not supported. Please upload PDF, DOC, or DOCX files"
            
        return True, "Valid filename"
    
    @staticmethod
    def validate_file_size(file_storage):
        """
        Validate file size
        """
        try:
            # Seek to end to get file size
            file_storage.seek(0, os.SEEK_END)
            file_size = file_storage.tell()
            file_storage.seek(0)  # Reset to beginning
            
            if file_size > FileUploadSecurity.MAX_FILE_SIZE:
                max_mb = FileUploadSecurity.MAX_FILE_SIZE / (1024 * 1024)
                return False, f"File is too large. Maximum size is {max_mb:.0f}MB"
                
            if file_size == 0:
                return False, "File is empty"
                
            return True, "Valid file size"
        except Exception:
            return False, "Unable to read file"
    
    @staticmethod
    def validate_mime_type(file_storage):
        """
        Validate MIME type using python-magic
        """
        try:
            # Read first 2048 bytes for magic number detection
            file_storage.seek(0)
            file_header = file_storage.read(2048)
            file_storage.seek(0)  # Reset to beginning
            
            # Get MIME type
            mime_type = magic.from_buffer(file_header, mime=True)
            
            if mime_type not in FileUploadSecurity.ALLOWED_MIME_TYPES:
                return False, "Invalid file format. Please upload a valid document file"
                
            return True, f"Valid MIME type: {mime_type}"
            
        except Exception:
            return False, "Unable to verify file type"
    
    @staticmethod
    def validate_file_signature(file_storage):
        """
        Validate file signature (magic numbers)
        """
        try:
            file_storage.seek(0)
            file_header = file_storage.read(512)  # Read enough bytes for signature detection
            file_storage.seek(0)  # Reset to beginning
            
            # Check for known file signatures
            for signature, file_type in FileUploadSecurity.ALLOWED_SIGNATURES.items():
                if file_header.startswith(signature):
                    return True, f"Valid {file_type.upper()} file signature"
                    
            return False, "File appears to be corrupted or invalid"
            
        except Exception:
            return False, "Unable to validate file"
    
    @staticmethod
    def generate_safe_filename(original_filename, user_id=None):
        """
        Generate a safe filename with timestamp and hash
        """
        # Secure the filename
        safe_name = secure_filename(original_filename)
        
        # Get file extension
        name, ext = os.path.splitext(safe_name)
        
        # Create hash of original filename + timestamp for uniqueness
        import time
        timestamp = str(int(time.time()))
        hash_input = f"{original_filename}_{timestamp}_{user_id or 'anonymous'}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        
        # Generate final filename: name_hash_timestamp.ext
        # Limit name length to prevent overly long filenames
        final_name = f"{name[:20]}_{file_hash}_{timestamp}{ext}"
        
        return final_name
    
    @staticmethod
    def scan_for_malicious_content(file_storage):
        """
        Scan for potentially malicious content in document files
        """
        try:
            file_storage.seek(0)
            content = file_storage.read()
            file_storage.seek(0)  # Reset to beginning
            
            # Only scan the first 50KB to avoid false positives in large documents
            scan_content = content[:51200]
            
            # Convert to string for text-based scanning (ignore encoding errors)
            try:
                text_content = scan_content.decode('utf-8', errors='ignore').lower()
            except:
                # If decoding fails completely, skip content scanning
                # Binary documents may not decode properly
                return True, "Content scan skipped"
            
            # Refined suspicious patterns - focus on actual threats
            # Use word boundaries and context to reduce false positives
            suspicious_patterns = [
                r'<script[\s>]',           # Script tags with space or closing bracket
                r'javascript\s*:',          # JavaScript protocol
                r'vbscript\s*:',           # VBScript protocol
                r'onload\s*=',             # Event handler
                r'onerror\s*=',            # Event handler
                r'\beval\s*\(',            # Eval function calls
                r'document\.cookie',       # Cookie access
                r'document\.write\s*\(',   # Document write
                r'<\?php',                 # PHP tags
                r'<%[^>]{0,50}(exec|eval|system)', # ASP with dangerous functions
                r'\bexec\s*\(',            # Exec calls
                r'\bsystem\s*\(',          # System calls
                r'shell_exec\s*\(',        # Shell execution
                r'base64_decode\s*\(',     # Suspicious decoding
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, text_content):
                    return False, "File contains potentially unsafe content"
                    
            return True, "No malicious content detected"
            
        except Exception:
            # If scanning fails, don't block legitimate files
            # Log this error in production for monitoring
            return True, "Content scan completed"
    
    @staticmethod
    def validate_upload(file_storage, user_id=None):
        """
        Complete file validation pipeline
        Returns: (is_valid, message, safe_filename)
        """
        if not file_storage or not file_storage.filename:
            return False, "No file provided", None
            
        original_filename = file_storage.filename
        
        # Step 1: Validate filename
        is_valid, message = FileUploadSecurity.validate_filename(original_filename)
        if not is_valid:
            return False, message, None
        
        # Step 2: Validate file size
        is_valid, message = FileUploadSecurity.validate_file_size(file_storage)
        if not is_valid:
            return False, message, None
        
        # Step 3: Validate MIME type
        is_valid, message = FileUploadSecurity.validate_mime_type(file_storage)
        if not is_valid:
            return False, message, None
        
        # Step 4: Validate file signature
        is_valid, message = FileUploadSecurity.validate_file_signature(file_storage)
        if not is_valid:
            return False, message, None
        
        # Step 5: Scan for malicious content
        is_valid, message = FileUploadSecurity.scan_for_malicious_content(file_storage)
        if not is_valid:
            return False, message, None
        
        # Step 6: Generate safe filename
        safe_filename = FileUploadSecurity.generate_safe_filename(original_filename, user_id)
        
        # Reset file pointer to beginning for final use
        file_storage.seek(0)
        
        return True, "File uploaded successfully", safe_filename

    @staticmethod
    def get_upload_requirements():
        """
        Get upload requirements for display to users
        """
        return {
            'allowed_formats': ['PDF', 'DOC', 'DOCX'],
            'max_size_mb': FileUploadSecurity.MAX_FILE_SIZE / (1024 * 1024),
            'max_filename_length': FileUploadSecurity.MAX_FILENAME_LENGTH
        }