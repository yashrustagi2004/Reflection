# Frontend Service API Documentation

## Overview

The Frontend Service is the main web interface for the AI Interview Platform. It serves HTML pages to users and acts as a gateway to coordinate with backend microservices. This service handles user sessions, OAuth authentication flows, file uploads, and provides the web-based user interface.

**Base URL**: `http://localhost:5000`  
**Port**: 5000  
**Technology**: Flask (Python)  
**Authentication**: Session-based with JWT tokens  

## Service Architecture

```
User Browser
     ↓
Frontend Service (Port 5000)
     ↓
├── Login Management (Port 5001)    - OAuth & User Management
├── File Parsing (Port 5002)        - File Upload & Processing  
├── Q&A Generation (Port 5003)      - Interview Question Generation
├── Answer Analysis (Port 5004)     - Answer Evaluation
└── Resources (Port 5005)           - Document Storage & Retrieval
```

## Authentication & Session Management

The frontend service manages user sessions and coordinates OAuth authentication with the Login Management service. JWT tokens are stored in Flask sessions and forwarded to backend services.

### Session Flow:
1. User initiates OAuth login via frontend
2. Frontend forwards request to Login Management service
3. Login Management handles OAuth flow with provider (Google/GitHub)
4. JWT token returned and stored in session
5. Subsequent requests include JWT token for backend authentication

---

## API Endpoints

### Public Web Pages

#### GET /
**Description**: Landing/home page of the application  
**Authentication**: None  
**Response**: HTML landing page  
**Purpose**: Introduces users to the platform and provides navigation to login

#### GET /about
**Description**: About page with platform information  
**Authentication**: None  
**Response**: HTML about page  
**Purpose**: Provides information about the platform, features, and team

#### GET /testimonials  
**Description**: User testimonials and success stories page  
**Authentication**: None  
**Response**: HTML testimonials page  
**Purpose**: Shows user reviews and platform success stories

#### GET /privacy
**Description**: Privacy policy page  
**Authentication**: None  
**Response**: HTML privacy policy page  
**Purpose**: Details data handling, privacy practices, and user rights

#### GET /contact
**Description**: Contact page with form  
**Authentication**: None  
**Response**: HTML contact page with form  
**Purpose**: Allows users to contact support or provide feedback

#### POST /contact
**Description**: Handle contact form submission  
**Authentication**: None  
**Request Body**: Form data
```html
name: string (required)
email: string (required) 
message: string (required)
```
**Response**: JSON with success/error message  
**Purpose**: Process contact form submissions and send to support team

---

### Authentication Endpoints

#### GET /login
**Description**: Login page with OAuth options  
**Authentication**: None (redirects to dashboard if already authenticated)  
**Response**: HTML login page with Google/GitHub OAuth buttons  
**Purpose**: Provides OAuth login interface for user authentication

#### GET /api/auth/google/login
**Description**: Initiate Google OAuth authentication flow  
**Authentication**: None  
**Response**: Redirect to Google OAuth authorization URL  
**Flow**:
1. Forwards request to Login Management service
2. Receives Google OAuth URL
3. Redirects user to Google for authorization
**Purpose**: Start Google OAuth login process

#### GET /api/auth/github/login  
**Description**: Initiate GitHub OAuth authentication flow  
**Authentication**: None  
**Response**: Redirect to GitHub OAuth authorization URL  
**Flow**:
1. Forwards request to Login Management service  
2. Receives GitHub OAuth URL
3. Redirects user to GitHub for authorization
**Purpose**: Start GitHub OAuth login process

#### GET /api/auth/google/callback
**Description**: Handle Google OAuth callback after user authorization  
**Authentication**: None  
**Parameters**:
- `code`: OAuth authorization code from Google
- `state`: CSRF protection token
**Response**: Redirect to dashboard on success, login page on failure  
**Flow**:
1. Receives OAuth callback from Google
2. Forwards to Login Management service for processing
3. Stores JWT token in session
4. Redirects to dashboard
**Purpose**: Complete Google OAuth flow and establish user session

#### GET /api/auth/github/callback
**Description**: Handle GitHub OAuth callback after user authorization  
**Authentication**: None  
**Parameters**:
- `code`: OAuth authorization code from GitHub  
- `state`: CSRF protection token
**Response**: Redirect to dashboard on success, login page on failure  
**Flow**:
1. Receives OAuth callback from GitHub
2. Forwards to Login Management service for processing  
3. Stores JWT token in session
4. Redirects to dashboard
**Purpose**: Complete GitHub OAuth flow and establish user session

#### POST /logout
**Description**: Logout user and clear session  
**Authentication**: Required  
**Response**: Redirect to home page  
**Purpose**: End user session and clear authentication data

---

### Protected Web Pages  

#### GET /dashboard
**Description**: Main user dashboard with file upload interface  
**Authentication**: Required (redirects to login if not authenticated)  
**Response**: HTML dashboard page with:
- File upload forms for resume and job description
- User statistics and upload history  
- Navigation to other platform features
**Purpose**: Primary interface for file uploads and platform navigation

#### GET /profile  
**Description**: User profile page (GET request)  
**Authentication**: Required  
**Response**: HTML profile page with user information and settings  
**Purpose**: Display user account information and preferences

#### POST /profile
**Description**: Update user profile information  
**Authentication**: Required  
**Request Body**: Form data with profile updates
```html
name: string (optional)
email: string (optional) 
preferences: object (optional)
```
**Response**: Updated profile page with success/error messages  
**Purpose**: Allow users to modify their profile information

#### GET /delete-account
**Description**: Account deletion confirmation page  
**Authentication**: Required  
**Response**: HTML confirmation page with deletion form  
**Purpose**: Provide secure interface for account deletion

#### POST /delete-account
**Description**: Delete user account after confirmation  
**Authentication**: Required  
**Request Body**: Form data
```html
confirmation: "delete my account" (exact string required)
```
**Response**: Redirect to home page with session cleared  
**Flow**:
1. Validates confirmation text
2. Forwards deletion request to Login Management service
3. Clears local session
4. Redirects to home page
**Purpose**: Permanently delete user account and all associated data

---

### File Upload Endpoints

#### POST /api/upload/resume
**Description**: Upload resume file for interview preparation  
**Authentication**: Required  
**Content-Type**: `multipart/form-data`  
**Request Body**:
- `resume_file`: File (PDF, DOC, DOCX, max 10MB)

**Response**:
```json
{
  "success": true,
  "message": "Resume uploaded successfully",
  "original_filename": "my_resume.pdf",
  "file": {
    "filename": "resume_user123_1634567890.pdf",
    "original_name": "my_resume.pdf", 
    "size": 1048576,
    "mime_type": "application/pdf"
  }
}
```

**Flow**:
1. Receives multipart file upload from browser
2. Forwards file to File Parsing service for validation and storage
3. File Parsing service stores file and updates user record
4. Returns upload confirmation to user
**Purpose**: Allow users to upload resumes for personalized interview questions

#### POST /api/upload/job-description  
**Description**: Upload job description file for role-specific questions  
**Authentication**: Required  
**Content-Type**: `multipart/form-data`  
**Request Body**:
- `jd_file`: File (PDF, DOC, DOCX, max 10MB)

**Response**:
```json
{
  "success": true,
  "message": "Job description uploaded successfully", 
  "original_filename": "job_posting.pdf",
  "file": {
    "filename": "jd_user123_1634567890.pdf",
    "original_name": "job_posting.pdf",
    "size": 2097152,
    "mime_type": "application/pdf" 
  }
}
```

**Flow**:
1. Receives multipart file upload from browser
2. Forwards file to File Parsing service for validation and storage  
3. File Parsing service stores file and updates user record
4. Returns upload confirmation to user
**Purpose**: Allow users to upload job descriptions for role-specific interview preparation

#### POST /api/upload/text/job-description
**Description**: Submit job description as text instead of file  
**Authentication**: Required  
**Content-Type**: `application/json`  
**Request Body**:
```json
{
  "text": "Software Developer position requiring Python, Flask, REST APIs, and database experience. Looking for someone with 3+ years experience..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Job description saved successfully",
  "file": {
    "filename": "jd_text_user123_1634567890.txt",
    "size": 512
  }
}
```

**Flow**:
1. Receives text job description from web form
2. Forwards to File Parsing service for text validation and storage
3. File Parsing service saves as text file and updates user record  
4. Returns confirmation to user
**Purpose**: Provide alternative to file upload for users who want to paste job description text

---

### Utility Endpoints

#### GET /health
**Description**: Service health check endpoint  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "service": "frontend", 
  "status": "healthy"
}
```
**Purpose**: Allow monitoring systems to verify service availability

#### GET /debug/session
**Description**: Debug endpoint to inspect session contents (development only)  
**Authentication**: Required  
**Response**: JSON with session information
```json
{
  "session_data": {
    "has_auth_token": true,
    "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "id": "user123",
      "name": "John Doe",
      "email": "john@example.com"
    },
    "session_keys": ["auth_token", "user"]
  },
  "cookies": {},
  "note": "This is the JWT token used for backend API calls"
}
```
**Purpose**: Development tool for debugging authentication and session issues
**⚠️ Security Note**: Should be removed in production environments

---

## Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common HTTP Status Codes
- **200**: Success
- **302**: Redirect (OAuth flows, post-login redirects)  
- **400**: Bad Request (missing file, invalid form data)
- **401**: Unauthorized (not logged in)
- **403**: Forbidden (insufficient permissions)
- **413**: Payload Too Large (file size exceeds 10MB)
- **500**: Internal Server Error (service communication failure)

### Authentication Errors
When authentication is required but not provided:
- Web pages: Redirect to `/login`
- API endpoints: Return 401 Unauthorized

---

## Service Dependencies

### External Dependencies
- **Google OAuth API**: For Google authentication
- **GitHub OAuth API**: For GitHub authentication  
- **MongoDB**: Session storage (via Login Management service)

### Internal Service Dependencies
- **Login Management Service** (Port 5001): OAuth processing, user management
- **File Parsing Service** (Port 5002): File upload validation and storage

---

## Configuration

### Environment Variables
```bash
FLASK_SECRET_KEY=your-secret-key
FRONTEND_PORT=5000
JWT_EXPIRY_HOURS=24
FLASK_DEBUG=False

# Service URLs (for service-to-service communication)
LOGIN_MANAGEMENT_URL=http://localhost:5001
FILE_PARSING_URL=http://localhost:5002
QA_GENERATION_URL=http://localhost:5003
ANSWER_ANALYSIS_URL=http://localhost:5004
RESOURCES_URL=http://localhost:5005
```

### Security Configuration
- **Session Security**: Uses Flask-Session with secure cookies in production
- **CSRF Protection**: Built-in Flask CSRF protection for forms
- **File Upload Security**: Delegates to File Parsing service for validation
- **Authentication**: JWT tokens with configurable expiry

---

## Development Notes

### Session Management
- Sessions are stored server-side using Flask sessions
- JWT tokens from Login Management service are stored in session
- Session timeout matches JWT token expiry (24 hours default)

### File Upload Handling  
- Frontend service acts as a proxy for file uploads
- No file processing occurs in frontend service
- Files are immediately forwarded to File Parsing service
- Frontend service returns responses from File Parsing service

### Service Communication
- Uses ServiceClient class for backend API calls
- Automatically includes service authentication tokens
- Forwards user JWT tokens to backend services
- Handles service communication errors gracefully

### Template Rendering
- Uses Jinja2 templates for HTML pages
- Templates include user authentication status
- Error/success messages displayed via Flask flash messages
- Responsive design for mobile and desktop users