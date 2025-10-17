# File Parsing Service API Documentation

## Overview

The File Parsing Service handles all file upload operations, security validation, content extraction, and file management for the AI Interview Platform. It provides secure file processing capabilities for resumes, job descriptions, and other document types.

**Base URL**: `http://localhost:5002`  
**Port**: 5002  
**Technology**: Flask (Python) + File Processing Libraries  
**Authentication**: JWT tokens (validated via Login Management Service)  
**File Storage**: Local filesystem with organized directory structure

## Core Responsibilities

- **File Upload Security**: Virus scanning, file type validation, size limits
- **Content Extraction**: Text extraction from PDF, DOC, DOCX files
- **File Management**: Secure storage, organization, and cleanup
- **Metadata Processing**: File information and content analysis
- **Security Scanning**: Malware detection and content safety
- **Service Integration**: Coordinate with other services for file processing

---

## File Processing Flow

### Upload Flow Diagram
```
1. User uploads file → Frontend Service
2. Frontend → File Parsing: POST /api/upload/{type}
3. File Parsing: Security validation (size, type, virus scan)
4. File Parsing: Generate unique filename with timestamp
5. File Parsing: Save to appropriate directory (/uploads/{type}/)
6. File Parsing: Extract text content and metadata
7. File Parsing → Login Management: Record upload in user profile
8. File Parsing: Return success with file information
```

### Security Validation Process
```
1. File Extension Check: Verify allowed extensions (.pdf, .doc, .docx)
2. MIME Type Validation: Confirm actual file type matches extension
3. File Size Validation: Enforce 10MB limit
4. Content Security Scan: Check for malicious content
5. Filename Sanitization: Remove dangerous characters
6. Path Traversal Protection: Prevent directory manipulation
```

---

## API Endpoints

### Health Check

#### GET /health
**Description**: Service health check and file system status  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "service": "file-parsing",
  "status": "healthy",
  "file_system": {
    "uploads_accessible": true,
    "free_space_gb": 45.2,
    "total_files": 127
  },
  "security_scanner": {
    "enabled": true,
    "last_update": "2024-01-15T08:00:00Z"
  }
}
```
**Purpose**: Monitor service health and file system capacity

---

### Resume Upload

#### POST /api/upload/resume
**Description**: Upload and process resume files  
**Authentication**: Required (JWT token)  
**Content-Type**: `multipart/form-data`  
**Request**:
```
POST /api/upload/resume HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="resume"; filename="john_doe_resume.pdf"
Content-Type: application/pdf

[PDF file content]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully",
  "file_info": {
    "original_name": "john_doe_resume.pdf",
    "stored_filename": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
    "file_path": "/uploads/resumes/resume_507f1f77bcf86cd799439011_1634567890123.pdf",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "uploaded_at": "2024-01-15T10:30:00Z"
  },
  "content_info": {
    "text_extracted": true,
    "text_length": 2456,
    "detected_sections": [
      "personal_info",
      "work_experience", 
      "education",
      "skills",
      "projects"
    ],
    "keywords_found": [
      "Python", "JavaScript", "React", "Flask", 
      "MongoDB", "AWS", "Docker", "Git"
    ]
  },
  "processing_time": 2.3
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "File too large. Maximum size is 10MB",
  "error_code": "FILE_TOO_LARGE",
  "details": {
    "max_size_mb": 10,
    "received_size_mb": 15.2
  }
}
```

**Validation Rules**:
- **File Size**: Maximum 10MB (10,485,760 bytes)
- **File Types**: PDF (.pdf), Word Document (.doc, .docx)
- **MIME Types**: `application/pdf`, `application/msword`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- **Filename**: Sanitized, special characters removed
- **Content**: Scanned for malicious content

**Processing Steps**:
1. Validate file size and type
2. Generate unique filename: `resume_{user_id}_{timestamp}.{ext}`
3. Save to `/uploads/resumes/` directory
4. Extract text content using appropriate parser
5. Analyze content for sections and keywords
6. Record upload in user profile via Login Management Service
7. Return file information and content analysis

**Purpose**: Securely upload and process user resume files for interview preparation

---

### Job Description Upload (File)

#### POST /api/upload/job_description
**Description**: Upload and process job description files  
**Authentication**: Required (JWT token)  
**Content-Type**: `multipart/form-data`  
**Request**:
```
POST /api/upload/job_description HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="job_description"; filename="software_engineer_jd.pdf"
Content-Type: application/pdf

[PDF file content]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Job description uploaded and processed successfully",
  "file_info": {
    "original_name": "software_engineer_jd.pdf",
    "stored_filename": "jd_507f1f77bcf86cd799439011_1634567890456.pdf",
    "file_path": "/uploads/job_descriptions/jd_507f1f77bcf86cd799439011_1634567890456.pdf",
    "file_size": 524288,
    "mime_type": "application/pdf",
    "uploaded_at": "2024-01-15T10:35:00Z"
  },
  "content_info": {
    "text_extracted": true,
    "text_length": 1842,
    "detected_sections": [
      "job_title",
      "company_info",
      "responsibilities",
      "requirements",
      "qualifications",
      "benefits"
    ],
    "required_skills": [
      "Python", "Django", "PostgreSQL",
      "REST APIs", "Docker", "AWS",
      "Agile", "Git"
    ],
    "experience_level": "3-5 years",
    "job_type": "Full-time"
  },
  "processing_time": 1.8
}
```

**Processing Steps**:
1. Validate file size and type (same rules as resume)
2. Generate unique filename: `jd_{user_id}_{timestamp}.{ext}`
3. Save to `/uploads/job_descriptions/` directory
4. Extract text content and analyze job requirements
5. Identify key skills, experience level, and job details
6. Record upload in user profile
7. Return detailed job description analysis

**Purpose**: Process job description files for interview question generation

---

### Job Description Upload (Text)

#### POST /api/upload/job_description_text
**Description**: Process job description from direct text input  
**Authentication**: Required (JWT token)  
**Content-Type**: `application/json`  
**Request**:
```json
{
  "job_description_text": "We are looking for a Senior Python Developer with 5+ years of experience...\n\nResponsibilities:\n- Develop scalable web applications using Django\n- Design and implement REST APIs\n- Work with PostgreSQL databases\n- Deploy applications on AWS\n\nRequirements:\n- Bachelor's degree in Computer Science\n- 5+ years Python development experience\n- Experience with Django, Flask\n- Knowledge of PostgreSQL, MongoDB\n- AWS cloud experience\n- Docker containerization\n- Git version control"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Job description text processed successfully",
  "file_info": {
    "original_name": "job_description_text",
    "stored_filename": "jd_text_507f1f77bcf86cd799439011_1634567890789.txt",
    "file_path": "/uploads/job_descriptions/jd_text_507f1f77bcf86cd799439011_1634567890789.txt",
    "file_size": 512,
    "mime_type": "text/plain",
    "uploaded_at": "2024-01-15T10:40:00Z"
  },
  "content_info": {
    "text_length": 512,
    "detected_sections": [
      "job_title",
      "responsibilities", 
      "requirements",
      "qualifications"
    ],
    "required_skills": [
      "Python", "Django", "Flask", "PostgreSQL",
      "MongoDB", "AWS", "Docker", "Git"
    ],
    "experience_level": "5+ years",
    "job_type": "Full-time",
    "education_required": "Bachelor's degree",
    "seniority_level": "Senior"
  },
  "processing_time": 0.5
}
```

**Validation Rules**:
- **Text Length**: Minimum 50 characters, maximum 10,000 characters
- **Content**: Must contain job-related keywords
- **Format**: Plain text, HTML tags stripped if present

**Processing Steps**:
1. Validate text length and content
2. Clean and sanitize text input
3. Generate filename: `jd_text_{user_id}_{timestamp}.txt`
4. Save to `/uploads/job_descriptions/` directory
5. Analyze text for job requirements and structure
6. Extract skills, experience level, and other metadata
7. Record upload in user profile
8. Return content analysis

**Purpose**: Process job descriptions provided as direct text input

---

### File Management

#### GET /api/files/list
**Description**: List user's uploaded files with metadata  
**Authentication**: Required (JWT token)  
**Parameters**:
- `type`: Filter by file type (`resume`, `job_description`, `all`) - optional
- `limit`: Maximum number of files to return (default: 50) - optional  
- `offset`: Number of files to skip (default: 0) - optional

**Response**:
```json
{
  "success": true,
  "files": {
    "resumes": [
      {
        "filename": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
        "original_name": "john_doe_resume.pdf",
        "uploaded_at": "2024-01-15T10:30:00Z",
        "file_size": 1048576,
        "mime_type": "application/pdf",
        "status": "processed",
        "content_preview": "John Doe\nSoftware Engineer\n5 years experience in Python development..."
      }
    ],
    "job_descriptions": [
      {
        "filename": "jd_507f1f77bcf86cd799439011_1634567890456.pdf", 
        "original_name": "software_engineer_jd.pdf",
        "uploaded_at": "2024-01-15T10:35:00Z",
        "file_size": 524288,
        "mime_type": "application/pdf",
        "status": "processed",
        "content_preview": "Senior Python Developer Position\nWe are seeking an experienced developer..."
      }
    ],
    "statistics": {
      "total_files": 2,
      "total_size": 1572864,
      "resumes_count": 1,
      "job_descriptions_count": 1
    }
  }
}
```
**Purpose**: Allow users to view their uploaded file history and metadata

#### GET /api/files/{filename}/content
**Description**: Retrieve extracted text content from uploaded file  
**Authentication**: Required (JWT token + file ownership validation)  
**Parameters**:
- `filename`: Name of the stored file

**Response**:
```json
{
  "success": true,
  "file_info": {
    "filename": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
    "original_name": "john_doe_resume.pdf", 
    "uploaded_at": "2024-01-15T10:30:00Z",
    "mime_type": "application/pdf"
  },
  "content": {
    "raw_text": "John Doe\nEmail: john.doe@email.com\nPhone: (555) 123-4567\n\nPROFESSIONAL EXPERIENCE\n\nSenior Software Engineer | TechCorp Inc. | 2020-2024\n- Developed scalable web applications using Python and Django\n- Led a team of 4 developers on multiple projects\n- Implemented CI/CD pipelines using Docker and AWS\n\nSoftware Engineer | StartupXYZ | 2018-2020\n- Built REST APIs using Flask and PostgreSQL\n- Worked on frontend development with React and JavaScript\n\nEDUCATION\n\nBachelor of Science in Computer Science\nUniversity of Technology | 2014-2018\n\nSKILLS\n\nProgramming Languages: Python, JavaScript, Java, C++\nFrameworks: Django, Flask, React, Node.js\nDatabases: PostgreSQL, MongoDB, MySQL\nCloud: AWS, Azure, Docker, Kubernetes\nTools: Git, Jenkins, JIRA, Confluence",
    "structured_data": {
      "personal_info": {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(555) 123-4567"
      },
      "experience": [
        {
          "title": "Senior Software Engineer",
          "company": "TechCorp Inc.",
          "duration": "2020-2024",
          "responsibilities": [
            "Developed scalable web applications using Python and Django",
            "Led a team of 4 developers on multiple projects", 
            "Implemented CI/CD pipelines using Docker and AWS"
          ]
        },
        {
          "title": "Software Engineer",
          "company": "StartupXYZ",
          "duration": "2018-2020",
          "responsibilities": [
            "Built REST APIs using Flask and PostgreSQL",
            "Worked on frontend development with React and JavaScript"
          ]
        }
      ],
      "education": [
        {
          "degree": "Bachelor of Science in Computer Science",
          "institution": "University of Technology",
          "duration": "2014-2018"
        }
      ],
      "skills": {
        "programming_languages": ["Python", "JavaScript", "Java", "C++"],
        "frameworks": ["Django", "Flask", "React", "Node.js"],
        "databases": ["PostgreSQL", "MongoDB", "MySQL"],
        "cloud": ["AWS", "Azure", "Docker", "Kubernetes"],
        "tools": ["Git", "Jenkins", "JIRA", "Confluence"]
      }
    }
  }
}
```

**Security**: File ownership validated - users can only access their own files

**Purpose**: Provide extracted and structured content for other services

#### DELETE /api/files/{filename}
**Description**: Delete uploaded file and its metadata  
**Authentication**: Required (JWT token + file ownership validation)  
**Parameters**:
- `filename`: Name of the stored file to delete

**Response**:
```json
{
  "success": true,
  "message": "File deleted successfully",
  "deleted_file": {
    "filename": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
    "original_name": "john_doe_resume.pdf",
    "file_size": 1048576
  }
}
```

**Process**:
1. Validate user owns the file
2. Remove file from filesystem
3. Remove upload record from Login Management Service
4. Return confirmation

**Purpose**: Allow users to delete their uploaded files

---

### Content Analysis (Internal Service Use)

#### POST /api/internal/analyze
**Description**: Analyze file content for other services (Question-Answer Generation, etc.)  
**Authentication**: Required (Service token)  
**Request Body**:
```json
{
  "filename": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
  "analysis_type": "skills_extraction",
  "options": {
    "include_experience_level": true,
    "include_keywords": true,
    "include_sections": true
  }
}
```

**Response**:
```json
{
  "success": true,
  "analysis": {
    "skills_analysis": {
      "technical_skills": [
        {"skill": "Python", "confidence": 0.95, "mentions": 3},
        {"skill": "Django", "confidence": 0.88, "mentions": 2},
        {"skill": "PostgreSQL", "confidence": 0.82, "mentions": 2},
        {"skill": "AWS", "confidence": 0.90, "mentions": 2}
      ],
      "soft_skills": [
        {"skill": "Leadership", "confidence": 0.75, "evidence": "Led a team of 4 developers"},
        {"skill": "Project Management", "confidence": 0.70, "evidence": "multiple projects"}
      ]
    },
    "experience_analysis": {
      "total_years": 6,
      "seniority_level": "Senior",
      "domain_experience": ["Web Development", "Backend Development", "Team Leadership"]
    },
    "keyword_density": {
      "python": 0.12,
      "django": 0.08,
      "aws": 0.06,
      "postgresql": 0.05
    }
  }
}
```
**Purpose**: Provide detailed content analysis for question generation and matching

---

## File Security & Validation

### Security Measures

#### File Type Validation
```python
ALLOWED_EXTENSIONS = {'.pdf', '.doc', '.docx'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
}
```

#### Size Limits
- **Maximum File Size**: 10MB (10,485,760 bytes)
- **Minimum File Size**: 1KB (prevents empty uploads)
- **Text Content Limits**: 50-10,000 characters for text uploads

#### Content Security Scanning
```python
def security_scan(file_content, filename):
    """
    Perform security validation on uploaded files
    - Check for malicious patterns
    - Validate file headers match extension
    - Scan for embedded executables
    - Check for suspicious metadata
    """
```

#### Filename Sanitization
```python
def sanitize_filename(filename):
    """
    Remove dangerous characters and path traversal attempts
    - Remove: ../ .\ < > : " | ? * 
    - Limit length to 255 characters
    - Ensure safe character set
    """
```

### Directory Structure
```
/uploads/
├── resumes/
│   ├── resume_507f1f77bcf86cd799439011_1634567890123.pdf
│   └── resume_507f1f77bcf86cd799439011_1634567890456.pdf
├── job_descriptions/
│   ├── jd_507f1f77bcf86cd799439011_1634567890789.pdf
│   └── jd_text_507f1f77bcf86cd799439011_1634567890012.txt
└── temp/
    └── (temporary processing files)
```

### Access Control
- **File Ownership**: Users can only access files they uploaded
- **Path Validation**: Prevents directory traversal attacks
- **Service Authentication**: Internal APIs require service tokens
- **JWT Validation**: All user operations validate JWT tokens

---

## Content Processing

### Text Extraction Capabilities

#### PDF Processing
- **Library**: PyPDF2, pdfplumber
- **Features**: Multi-page support, table extraction, metadata
- **Limitations**: OCR not included (text-based PDFs only)

#### Word Document Processing  
- **Library**: python-docx, python-docx2txt
- **Features**: Full text extraction, formatting preservation
- **Supported**: .doc and .docx formats

#### Text Analysis Features
- **Section Detection**: Automatic identification of resume/JD sections
- **Keyword Extraction**: Technical and soft skill identification  
- **Experience Parsing**: Job titles, companies, duration extraction
- **Skills Matching**: Technology stack and competency analysis

### Content Structure Analysis

#### Resume Analysis
```python
def analyze_resume_content(text):
    """
    Analyze resume content and extract structured information
    Returns:
    - Personal information (name, contact)
    - Work experience (companies, roles, dates)
    - Education (degrees, institutions)  
    - Skills (technical, soft skills)
    - Projects and achievements
    """
```

#### Job Description Analysis  
```python
def analyze_job_description(text):
    """
    Analyze job description content and extract requirements
    Returns:
    - Required skills and technologies
    - Experience level and seniority
    - Job responsibilities
    - Qualifications and education
    - Company information
    """
```

---

## Error Handling

### Upload Errors
```json
{
  "success": false,
  "error": "File validation failed",
  "error_code": "FILE_VALIDATION_ERROR",
  "details": {
    "validation_errors": [
      "File size exceeds 10MB limit",
      "Invalid file type. Only PDF, DOC, DOCX allowed"
    ]
  }
}
```

### Processing Errors
```json
{
  "success": false, 
  "error": "Content extraction failed",
  "error_code": "CONTENT_EXTRACTION_ERROR",
  "details": {
    "file_type": "pdf",
    "processing_stage": "text_extraction",
    "technical_error": "PDF appears to be corrupted or encrypted"
  }
}
```

### Security Errors
```json
{
  "success": false,
  "error": "Security scan detected potential threat",
  "error_code": "SECURITY_SCAN_FAILED", 
  "details": {
    "threat_type": "suspicious_content",
    "action_taken": "file_quarantined"
  }
}
```

### File System Errors
```json
{
  "success": false,
  "error": "File system operation failed",
  "error_code": "FILESYSTEM_ERROR",
  "details": {
    "operation": "save_file",
    "disk_space_available": "1.2GB",
    "suggested_action": "Contact administrator"
  }
}
```

---

## Performance & Monitoring

### Processing Metrics
- **Upload Speed**: Average processing time by file size
- **Content Extraction**: Success rates by file type
- **Security Scanning**: Scan time and threat detection rates
- **Storage Usage**: Disk space utilization and cleanup

### Health Monitoring
- **File System Health**: Disk space, read/write performance
- **Processing Queue**: Pending uploads and processing backlog
- **Security Status**: Scanner updates and threat detection
- **Service Integration**: Connection status with other services

### Cleanup Operations
- **Temporary Files**: Automatic cleanup after processing
- **Old Files**: Configurable retention policies
- **Failed Uploads**: Cleanup of incomplete operations
- **User Deletion**: Complete file removal when users delete accounts

---

## Configuration

### Environment Variables
```bash
# File Upload Configuration
MAX_FILE_SIZE_MB=10
UPLOAD_DIRECTORY=/uploads
TEMP_DIRECTORY=/uploads/temp
ALLOWED_EXTENSIONS=pdf,doc,docx

# Security Configuration  
SECURITY_SCAN_ENABLED=true
VIRUS_SCANNER_PATH=/usr/bin/clamscan
QUARANTINE_DIRECTORY=/quarantine

# Content Processing
TEXT_EXTRACTION_TIMEOUT=30
MAX_TEXT_LENGTH=100000
PROCESSING_THREADS=4

# Service Integration
LOGIN_MANAGEMENT_URL=http://localhost:5001
SERVICE_AUTH_TOKEN=your-service-token

# File System
FILE_RETENTION_DAYS=365
CLEANUP_SCHEDULE=0 2 * * *  # Daily at 2 AM
BACKUP_ENABLED=true
```

### File Processing Configuration
```python
PROCESSING_CONFIG = {
    'pdf': {
        'max_pages': 50,
        'extract_images': False,
        'extract_tables': True
    },
    'docx': {
        'preserve_formatting': True,
        'extract_headers_footers': True
    },
    'security': {
        'scan_timeout': 30,
        'quarantine_threats': True,
        'log_all_scans': True
    }
}
```

---

## Development Notes

### Testing File Uploads
```bash
# Test resume upload
curl -X POST http://localhost:5002/api/upload/resume \
  -H "Authorization: Bearer your-jwt-token" \
  -F "resume=@test_resume.pdf"

# Test job description text
curl -X POST http://localhost:5002/api/upload/job_description_text \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"job_description_text": "Software Engineer position..."}'
```

### File Processing Libraries
```bash
# Required Python packages
pip install PyPDF2 pdfplumber python-docx python-docx2txt
pip install python-magic werkzeug flask
pip install nltk spacy  # For text analysis
```

### Security Tools Setup
```bash
# Install ClamAV for virus scanning
sudo apt-get install clamav clamav-daemon
sudo freshclam  # Update virus definitions
```

### File System Permissions
```bash
# Set up upload directories with proper permissions
mkdir -p /uploads/{resumes,job_descriptions,temp}
chmod 755 /uploads
chmod 777 /uploads/temp  # Temporary files need write access
```