# Frontend to File Parsing Microservice API Documentation

## Overview
This document provides detailed mapping of API calls between the Frontend service and File Parsing microservice, including authentication flow, request/response formats, and security measures.

---

## Table of Contents
1. [Authentication Flow](#authentication-flow)
2. [API Endpoints](#api-endpoints)
   - [Upload Resume](#1-upload-resume)
   - [Upload Job Description File](#2-upload-job-description-file)
   - [Upload Job Description Text](#3-upload-job-description-text)
   - [Combined Upload (Resume + Job Description)](#4-combined-upload-resume--job-description)
   - [Get Parsed Content](#5-get-parsed-content)
   - [Get Content Status](#6-get-content-status)
   - [Get Upload Requirements](#7-get-upload-requirements)
   - [Get Questions](#8-get-questions)
   - [Clear Parsed Content](#9-clear-parsed-content)
3. [Error Handling](#error-handling)
4. [Security Measures](#security-measures)

---

## Authentication Flow

### Overview
The authentication between Frontend and File Parsing microservice uses a multi-layered approach:

1. **User Authentication** (Frontend → Login Management)
   - User logs in via OAuth (Google/GitHub)
   - Login Management service generates JWT token
   - JWT token stored in frontend session

2. **Service-to-Service Authentication** (Frontend → File Parsing)
   - Frontend includes user JWT in `Authorization` header
   - ServiceClient adds service token in `X-Service-Token` header
   - File Parsing validates both tokens (where required)

### Authentication Headers

```http
Authorization: Bearer <user_jwt_token>
X-Service-Name: frontend
X-Service-Token: <service_jwt_token>
Content-Type: application/json
```

### JWT Token Structure

**User Token Payload:**
```json
{
  "user_id": "user123",
  "email": "user@example.com",
  "exp": 1730901234,
  "iat": 1730814834
}
```

**Service Token Payload:**
```json
{
  "service": "frontend",
  "exp": 1730901234,
  "iat": 1730814834
}
```

### Authentication Steps by Endpoint

| Endpoint | Requires User Auth | Service Auth | Validation Point |
|----------|-------------------|--------------|------------------|
| `/api/files/upload/resume` | Optional* | Yes | File Parsing receives token |
| `/api/files/upload/job-description` | Optional* | Yes | File Parsing receives token |
| `/api/files/text/job-description` | Optional* | Yes | File Parsing receives token |
| `/api/upload/submit` | Optional* | Yes | File Parsing receives token |
| `/api/files/parsed-content` | No | Yes | No auth validation |
| `/api/files/content-status` | No | Yes | No auth validation |
| `/api/files/requirements` | No | No | Public endpoint |
| `/api/questions` | No | Yes | No auth validation |

*Note: Currently uses 'anonymous' user_id as temporary fix. Full authentication implemented but not enforced.

---

## API Endpoints

### 1. Upload Resume

**Endpoint:** `POST /api/files/upload/resume`

**Flow:**
1. User uploads resume via frontend
2. Frontend validates file on client-side
3. Frontend sends file to File Parsing service
4. File Parsing performs security validation
5. Resume is parsed and PII is removed
6. Cleaned content stored in global storage
7. File saved as `.txt` with cleaned content
8. Login Management notified of upload

**Frontend Request:**

```http
POST http://localhost:5002/api/files/upload/resume
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="resume"; filename="resume.pdf"
Content-Type: application/pdf

<binary file data>
--boundary--
```

**File Parsing Response (Success):**

```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully. Personal information has been removed for privacy.",
  "file": {
    "filename": "resume_anonymous_1730814834_cleaned.txt",
    "original_name": "resume.pdf",
    "size": 2048,
    "mime_type": "text/plain",
    "processed": true,
    "pii_removed": true
  }
}
```

**File Parsing Response (Error):**

```json
{
  "success": false,
  "error": "No resume file provided"
}
```

**Security Checks Performed:**
1. File presence validation
2. File size validation (max 10MB)
3. File type validation (extension, MIME type, magic numbers)
4. Filename sanitization
5. Path traversal prevention
6. PII removal during parsing

**Processing Steps:**
1. Validate file upload security
2. Generate secure filename with timestamp
3. Save to temporary location
4. Parse file and extract text
5. Remove PII (names, emails, phone numbers, addresses)
6. Save cleaned content to final location
7. Delete temporary file
8. Store content in `parsed_content_storage['resume_file_content']`
9. Notify login-management service

---

### 2. Upload Job Description File

**Endpoint:** `POST /api/files/upload/job-description`

**Flow:**
1. User uploads JD file via frontend
2. Frontend validates file
3. Frontend sends to File Parsing service
4. File Parsing validates and saves file
5. Content parsed and stored (PII NOT removed)
6. Login Management notified

**Frontend Request:**

```http
POST http://localhost:5002/api/files/upload/job-description
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="job_description"; filename="job.pdf"
Content-Type: application/pdf

<binary file data>
--boundary--
```

**File Parsing Response (Success):**

```json
{
  "success": true,
  "message": "Job description uploaded successfully",
  "file": {
    "filename": "job_anonymous_1730814834.pdf",
    "original_name": "job.pdf",
    "size": 3072,
    "mime_type": "application/pdf",
    "processed": false,
    "pii_removed": false
  }
}
```

**Security Checks Performed:**
1. File presence validation
2. File size validation (max 10MB)
3. File type validation
4. Filename sanitization
5. Path traversal prevention

**Processing Steps:**
1. Validate file upload
2. Generate secure filename
3. Save file to job_descriptions folder
4. Parse content (no PII removal)
5. Store in `parsed_content_storage['jd_file_content']`
6. Notify login-management service

---

### 3. Upload Job Description Text

**Endpoint:** `POST /api/files/text/job-description`

**Flow:**
1. User enters JD text in frontend
2. Frontend sends text data
3. File Parsing validates and sanitizes text
4. Text saved as .txt file
5. Content stored in global storage

**Frontend Request:**

```http
POST http://localhost:5002/api/files/text/job-description
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "text": "We are looking for a Senior Software Engineer with 5+ years of experience in Python, React, and cloud technologies..."
}
```

**File Parsing Response (Success):**

```json
{
  "success": true,
  "message": "Job description saved successfully",
  "file": {
    "filename": "jd_text_anonymous_1730814834.txt",
    "size": 512,
    "processed": false,
    "pii_removed": false
  }
}
```

**File Parsing Response (Error):**

```json
{
  "success": false,
  "error": "Job description text is required"
}
```

**Security Checks Performed:**
1. Text presence validation
2. Text length validation (min/max limits)
3. XSS prevention via sanitization
4. Content filtering

**Processing Steps:**
1. Extract and trim text from request
2. Validate text content
3. Sanitize text to prevent XSS
4. Generate unique filename
5. Save to file
6. Store in `parsed_content_storage['jd_text_content']`
7. Notify login-management service

---

### 4. Combined Upload (Resume + Job Description)

**Endpoint:** `POST /api/upload/submit`

**Flow:**
1. User submits both files simultaneously
2. Frontend sends both files in single request
3. File Parsing processes resume with PII removal
4. File Parsing processes JD without PII removal
5. Both contents stored in global storage
6. Q&A generation service called automatically
7. Questions generated and stored

**Frontend Request:**

```http
POST http://localhost:5002/api/upload/submit
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="resume"; filename="resume.pdf"
Content-Type: application/pdf

<resume binary data>
--boundary
Content-Disposition: form-data; name="job_description"; filename="job.pdf"
Content-Type: application/pdf

<job description binary data>
--boundary--
```

**File Parsing Response (Success):**

```json
{
  "success": true,
  "message": "Files uploaded successfully and Q&A generated!",
  "files": {
    "resume": {
      "filename": "resume_anonymous_1730814834_cleaned.txt",
      "original_name": "resume.pdf",
      "size": 2048,
      "processed": true,
      "pii_removed": true
    },
    "job_description": {
      "filename": "job_anonymous_1730814834.txt",
      "original_name": "job.pdf",
      "size": 3072,
      "processed": false,
      "pii_removed": false
    }
  },
  "redirect_url": "/practice"
}
```

**File Parsing Response (Error):**

```json
{
  "success": false,
  "error": "Both resume and job description files are required"
}
```

**Processing Steps:**
1. **Resume Processing:**
   - Validate file
   - Save to temporary location
   - Parse and extract text
   - Remove PII
   - Save cleaned content
   - Store in `parsed_content_storage['resume_file_content']`

2. **Job Description Processing:**
   - Validate file
   - Save to temporary location
   - Parse content (no PII removal)
   - Convert to .txt format
   - Store in `parsed_content_storage['jd_file_content']`

3. **Upload Recording:**
   - Notify login-management for both files
   - Record metadata in user profile

4. **Q&A Generation:**
   - Extract resume and JD text from storage
   - Send to question-answer-generation service
   - Store generated questions in `qa_data` global variable

**Q&A Service Integration:**

```http
POST http://127.0.0.1:5003/api/questions/generate
Authorization: Bearer <API_AUTH_TOKEN>
Content-Type: application/json

{
  "resume_text": "Software Engineer with 5 years...",
  "jd_text": "We are looking for..."
}
```

---

### 5. Get Parsed Content

**Endpoint:** `GET /api/files/parsed-content`

**Flow:**
1. Frontend requests stored parsed content
2. File Parsing returns all stored content
3. No authentication required (public within service network)

**Frontend Request:**

```http
GET http://localhost:5002/api/files/parsed-content
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**File Parsing Response:**

```json
{
  "success": true,
  "parsed_content": {
    "resume_file_content": "Software Engineer with 5 years of experience...",
    "jd_file_content": "We are seeking a talented Senior Software Engineer...",
    "jd_text_content": null
  }
}
```

**Content Storage:**
- `resume_file_content`: Parsed resume text with PII removed
- `jd_file_content`: Parsed JD from uploaded file
- `jd_text_content`: JD entered as text (if applicable)

**Use Cases:**
- Practice page needs content for context
- Q&A generation service needs text
- Analysis services need original content

---

### 6. Get Content Status

**Endpoint:** `GET /api/files/content-status`

**Flow:**
1. Frontend checks what content is available
2. File Parsing returns boolean status for each type
3. Used for UI state management

**Frontend Request:**

```http
GET http://localhost:5002/api/files/content-status
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**File Parsing Response:**

```json
{
  "success": true,
  "status": {
    "resume_file_uploaded": true,
    "jd_file_uploaded": true,
    "jd_text_uploaded": false
  },
  "any_content_available": true
}
```

**Use Cases:**
- Check if files are uploaded before proceeding
- Enable/disable UI elements
- Show appropriate user messages

---

### 7. Get Upload Requirements

**Endpoint:** `GET /api/files/requirements`

**Flow:**
1. Frontend requests file upload constraints
2. File Parsing returns allowed formats, sizes, etc.
3. Public endpoint - no authentication

**Frontend Request:**

```http
GET http://localhost:5002/api/files/requirements
```

**File Parsing Response:**

```json
{
  "success": true,
  "requirements": {
    "max_file_size": 10485760,
    "max_file_size_mb": 10,
    "allowed_extensions": [".pdf", ".doc", ".docx", ".txt"],
    "allowed_mime_types": [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain"
    ],
    "text_max_length": 50000,
    "text_min_length": 50
  }
}
```

**Use Cases:**
- Display upload requirements to user
- Client-side validation before upload
- Error message generation

---

### 8. Get Questions

**Endpoint:** `GET /api/questions`

**Flow:**
1. Frontend requests generated Q&A data
2. File Parsing returns stored questions from Q&A service
3. Used by practice page to display questions

**Frontend Request:**

```http
GET http://localhost:5002/api/questions
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**File Parsing Response:**

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "Describe your experience with microservices architecture",
      "category": "Technical",
      "difficulty": "Medium",
      "suggested_answer": "Based on your resume, you have experience with...",
      "keywords": ["microservices", "architecture", "scalability"]
    },
    {
      "id": 2,
      "question": "How do you ensure code quality in your projects?",
      "category": "Process",
      "difficulty": "Medium",
      "suggested_answer": "Code quality can be ensured through...",
      "keywords": ["testing", "code review", "CI/CD"]
    }
  ]
}
```

**Data Source:**
- Questions generated by Q&A service during combined upload
- Stored in `qa_data` global variable
- Persists for session duration

---

### 9. Clear Parsed Content

**Endpoint:** `POST /api/files/clear-content`

**Flow:**
1. Frontend requests to clear all stored content
2. File Parsing resets global storage
3. Used when user wants to start fresh

**Frontend Request:**

```http
POST http://localhost:5002/api/files/clear-content
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
```

**File Parsing Response:**

```json
{
  "success": true,
  "message": "All parsed content cleared successfully"
}
```

**Effect:**
- Sets all `parsed_content_storage` values to `null`
- Does not delete physical files
- Clears in-memory storage only

---

## Error Handling

### Common Error Responses

**Authentication Error:**
```json
{
  "success": false,
  "error": "Invalid or expired token"
}
```
Status Code: `401 Unauthorized`

**File Validation Error:**
```json
{
  "success": false,
  "error": "File type not allowed",
  "details": {
    "allowed_types": [".pdf", ".doc", ".docx"],
    "received_type": ".exe"
  }
}
```
Status Code: `400 Bad Request`

**File Size Error:**
```json
{
  "success": false,
  "error": "File size exceeds maximum limit of 10MB"
}
```
Status Code: `400 Bad Request`

**Missing File Error:**
```json
{
  "success": false,
  "error": "No resume file provided"
}
```
Status Code: `400 Bad Request`

**Parsing Error:**
```json
{
  "success": false,
  "error": "Failed to parse resume content"
}
```
Status Code: `500 Internal Server Error`

**Service Communication Error:**
```json
{
  "success": false,
  "error": "Service communication error: Connection refused"
}
```
Status Code: `500 Internal Server Error`

### Error Handling Flow

1. **Client-Side Validation** (Frontend)
   - File size check
   - File type check
   - Required field validation

2. **Transport Layer** (ServiceClient)
   - Network error handling
   - Timeout handling
   - Connection error handling

3. **Service-Side Validation** (File Parsing)
   - Security validation
   - Business logic validation
   - File parsing validation

4. **Error Response** (Back to Frontend)
   - Structured error format
   - User-friendly messages
   - Debug information (in dev mode)

---

## Security Measures

### 1. File Upload Security

**File Type Validation:**
- Extension checking (`.pdf`, `.doc`, `.docx`, `.txt`)
- MIME type verification
- Magic number validation (file signature)

**File Size Validation:**
- Maximum 10MB per file
- Prevents DoS attacks
- Configurable via environment

**Filename Sanitization:**
- Removes dangerous characters
- Prevents path traversal attacks
- Adds timestamp for uniqueness
- Format: `{type}_{user_id}_{timestamp}_{original_name}`

**Path Security:**
- Restricts to upload directories only
- Validates absolute paths
- Prevents directory traversal

### 2. Authentication & Authorization

**JWT Token Validation:**
- Token signature verification
- Expiration checking
- Payload validation

**Service-to-Service Auth:**
- X-Service-Token header
- Service name validation
- Short-lived tokens (1 hour)

**User Token Forwarding:**
- Authorization header passthrough
- User context preservation
- Session management

### 3. Content Security

**PII Removal (Resume):**
- Email addresses removed
- Phone numbers removed
- Physical addresses removed
- Names anonymized
- Preserves professional content

**Text Sanitization:**
- XSS prevention
- SQL injection prevention
- HTML entity encoding
- Script tag removal

**Input Validation:**
- Length limits enforced
- Character encoding validation
- Content type verification

### 4. Network Security

**CORS Configuration:**
- Allowed origins from environment
- Credential support
- Method restrictions

**Timeout Configuration:**
- 30-second request timeout
- Prevents hanging connections
- Configurable per service

**Error Information:**
- Production mode hides details
- Debug mode shows stack traces
- Sanitized error messages to client

### 5. File Storage Security

**Secure Storage:**
- Files stored outside web root
- Restricted file permissions
- Organized by type (resumes/job_descriptions)

**Temporary File Handling:**
- Temp files deleted after processing
- Cleanup on error conditions
- Prevents disk space exhaustion

**File Metadata:**
- Size tracking
- MIME type recording
- Upload timestamp
- Original filename preservation

---

## Complete Request/Response Example

### Scenario: User Uploads Resume and Job Description

**Step 1: Frontend Login Check**
```javascript
// Frontend checks authentication
if (!is_authenticated()) {
    redirect('/login');
}
```

**Step 2: Frontend Sends Combined Upload**
```http
POST http://localhost:5002/api/upload/submit
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidXNlcjEyMyIsImVtYWlsIjoidXNlckBleGFtcGxlLmNvbSIsImV4cCI6MTczMDkwMTIzNCwiaWF0IjoxNzMwODE0ODM0fQ.signature
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzZXJ2aWNlIjoiZnJvbnRlbmQiLCJleHAiOjE3MzA4MTg0MzQsImlhdCI6MTczMDgxNDgzNH0.signature
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="resume"; filename="john_doe_resume.pdf"
Content-Type: application/pdf

<binary resume data>
------WebKitFormBoundary
Content-Disposition: form-data; name="job_description"; filename="senior_engineer_jd.pdf"
Content-Type: application/pdf

<binary job description data>
------WebKitFormBoundary--
```

**Step 3: File Parsing Validates & Processes**
```python
# 1. Validate resume file
is_valid, message, details = file_security.validate_upload(resume_file)

# 2. Generate secure filename
safe_filename = file_security.generate_secure_filename(
    "john_doe_resume.pdf", "user123", "resume"
)
# Result: "resume_user123_1730814834_john_doe_resume.pdf"

# 3. Parse and remove PII
cleaned_text = EnhancedFileParser.parse_file(temp_path, remove_pii=True)
# Original: "John Doe\njohn.doe@email.com\n+1-555-1234\nSoftware Engineer..."
# Cleaned: "Software Engineer with 5 years of experience..."

# 4. Store in global variable
parsed_content_storage['resume_file_content'] = cleaned_text

# 5. Process job description (no PII removal)
jd_text = EnhancedFileParser.parse_file(jd_temp_path, remove_pii=False)
parsed_content_storage['jd_file_content'] = jd_text
```

**Step 4: File Parsing Calls Q&A Service**
```http
POST http://127.0.0.1:5003/api/questions/generate
Authorization: Bearer my-secret-token
Content-Type: application/json

{
  "resume_text": "Software Engineer with 5 years of experience in Python, React, and microservices...",
  "jd_text": "We are seeking a Senior Software Engineer with expertise in cloud technologies..."
}
```

**Step 5: File Parsing Returns Success**
```json
{
  "success": true,
  "message": "Files uploaded successfully and Q&A generated!",
  "files": {
    "resume": {
      "filename": "resume_user123_1730814834_cleaned.txt",
      "original_name": "john_doe_resume.pdf",
      "size": 2048,
      "processed": true,
      "pii_removed": true
    },
    "job_description": {
      "filename": "job_user123_1730814834.txt",
      "original_name": "senior_engineer_jd.pdf",
      "size": 3072,
      "processed": false,
      "pii_removed": false
    }
  },
  "redirect_url": "/practice"
}
```

**Step 6: Frontend Redirects to Practice Page**
```javascript
// Frontend receives response
if (response.success && response.redirect_url) {
    window.location.href = response.redirect_url;
}
```

**Step 7: Practice Page Fetches Questions**
```http
GET http://localhost:5002/api/questions
X-Service-Name: frontend
X-Service-Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Step 8: File Parsing Returns Questions**
```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "Describe your experience with microservices architecture",
      "category": "Technical",
      "difficulty": "Medium",
      "suggested_answer": "Based on your resume, you have experience with distributed systems...",
      "keywords": ["microservices", "architecture", "scalability"]
    }
  ]
}
```

---

## Service Configuration

### Environment Variables

**Frontend Service:**
```bash
FILE_PARSING_URL=http://localhost:5002
JWT_SECRET=your-jwt-secret-change-this-in-production
JWT_EXPIRY_HOURS=24
FLASK_SECRET_KEY=your-secret-key-change-this-in-production
```

**File Parsing Service:**
```bash
FILE_PARSING_PORT=5002
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=10485760
JWT_SECRET=your-jwt-secret-change-this-in-production
FLASK_DEBUG=False
API_AUTH_TOKEN=my-secret-token
```

### Service URLs

| Service | Default URL | Environment Variable |
|---------|-------------|---------------------|
| Frontend | http://localhost:5000 | FRONTEND_PORT |
| Login Management | http://localhost:5001 | LOGIN_MANAGEMENT_URL |
| File Parsing | http://localhost:5002 | FILE_PARSING_URL |
| Q&A Generation | http://localhost:5003 | QA_GENERATION_URL |

---

## Appendix

### File Storage Structure

```
uploads/
├── resumes/
│   ├── resume_user123_1730814834_cleaned.txt
│   └── temp_resume_user123_1730814834.pdf (deleted after processing)
└── job_descriptions/
    ├── job_user123_1730814834.txt
    └── jd_text_user123_1730814834.txt
```

### Global Storage Variables

```python
parsed_content_storage = {
    'resume_file_content': str | None,  # Cleaned resume text
    'jd_file_content': str | None,      # JD from file upload
    'jd_text_content': str | None       # JD from text input
}

qa_data = {
    'success': bool,
    'questions': List[Dict]
}
```

### Supported File Types

| Extension | MIME Type | Notes |
|-----------|-----------|-------|
| .pdf | application/pdf | Most common |
| .doc | application/msword | Legacy Word |
| .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Modern Word |
| .txt | text/plain | Plain text |

---

**Document Version:** 1.0  
**Last Updated:** November 6, 2025  
**Maintained By:** Development Team
