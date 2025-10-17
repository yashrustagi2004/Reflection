# Login Management Service API Documentation

## Overview

The Login Management Service handles all user authentication, OAuth flows, user profile management, and JWT token generation. It serves as the central authentication authority for the AI Interview Platform and manages user data persistence in MongoDB.

**Base URL**: `http://localhost:5001`  
**Port**: 5001  
**Technology**: Flask (Python) + MongoDB  
**Authentication**: JWT tokens + OAuth2 (Google, GitHub)  

## Core Responsibilities

- **OAuth Authentication**: Google and GitHub OAuth2 flows
- **JWT Token Management**: Generation, validation, and refresh
- **User Profile Management**: User data storage and retrieval
- **Upload Record Tracking**: File upload history and metadata
- **Account Management**: Account creation, updates, and deletion
- **Service Authentication**: Inter-service authentication validation

---

## Authentication Flow

### OAuth2 Flow Diagram
```
1. User clicks login → Frontend Service
2. Frontend → Login Management: GET /api/auth/{provider}/login
3. Login Management → OAuth Provider: Redirect with auth URL
4. User authorizes → OAuth Provider
5. OAuth Provider → Frontend: Callback with code
6. Frontend → Login Management: GET /api/auth/{provider}/callback?code=...
7. Login Management → OAuth Provider: Exchange code for token
8. Login Management → OAuth Provider: Get user info
9. Login Management → Database: Store/update user
10. Login Management → Frontend: Return JWT token
11. Frontend stores JWT in session
```

### JWT Token Structure
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "email": "user@example.com", 
  "name": "John Doe",
  "provider": "google",
  "iat": 1634567890,
  "exp": 1634654290
}
```

---

## API Endpoints

### Health Check

#### GET /health
**Description**: Service health check and status  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "service": "login-management",
  "status": "healthy",
  "database_connected": true,
  "oauth_providers": {
    "google": true,
    "github": true
  }
}
```
**Purpose**: Monitor service health and OAuth provider configuration

---

### OAuth Configuration  

#### GET /api/auth/status
**Description**: Check OAuth provider configuration status  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "google_configured": true,
  "github_configured": true,
  "environment": "development"
}
```
**Purpose**: Verify OAuth providers are properly configured with client credentials

---

### Google OAuth Flow

#### GET /api/auth/google/login
**Description**: Initiate Google OAuth2 authorization flow  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...&redirect_uri=...&scope=openid+email+profile&response_type=code&state=random_state_token&access_type=offline&prompt=consent"
}
```

**OAuth Parameters**:
- `client_id`: Google OAuth2 client ID
- `redirect_uri`: `http://localhost:5000/api/auth/google/callback`
- `scope`: `openid email profile` 
- `state`: CSRF protection token
- `prompt`: `consent` (forces authorization screen)

**Purpose**: Generate Google OAuth URL with proper parameters

#### GET /api/auth/google/callback
**Description**: Handle Google OAuth2 callback and complete authentication  
**Authentication**: None  
**Parameters**:
- `code`: Authorization code from Google (required)
- `state`: CSRF protection token (required)

**Response (Success)**:
```json
{
  "success": true,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe", 
    "email": "john.doe@example.com",
    "provider": "google",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "Invalid authorization code",
  "error_code": "OAUTH_INVALID_CODE"
}
```

**Flow**:
1. Validates state parameter for CSRF protection
2. Exchanges authorization code for access token with Google
3. Fetches user profile information from Google APIs
4. Creates or updates user record in database  
5. Generates JWT token for session management
6. Returns user data and JWT token

**Purpose**: Complete Google OAuth flow and establish user session

---

### GitHub OAuth Flow

#### GET /api/auth/github/login  
**Description**: Initiate GitHub OAuth2 authorization flow  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "auth_url": "https://github.com/login/oauth/authorize?client_id=...&redirect_uri=...&scope=user:email&state=random_state_token"
}
```

**OAuth Parameters**:
- `client_id`: GitHub OAuth2 client ID
- `redirect_uri`: `http://localhost:5000/api/auth/github/callback`
- `scope`: `user:email`
- `state`: CSRF protection token

**Purpose**: Generate GitHub OAuth URL with proper parameters

#### GET /api/auth/github/callback
**Description**: Handle GitHub OAuth2 callback and complete authentication  
**Authentication**: None  
**Parameters**:
- `code`: Authorization code from GitHub (required)
- `state`: CSRF protection token (required)

**Response (Success)**:
```json
{
  "success": true,
  "user": {
    "id": "507f1f77bcf86cd799439011", 
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "provider": "github",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4",
    "github_username": "janesmith",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z"
  },
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Flow**:
1. Validates state parameter for CSRF protection
2. Exchanges authorization code for access token with GitHub
3. Fetches user profile information from GitHub APIs  
4. Creates or updates user record in database
5. Generates JWT token for session management
6. Returns user data and JWT token

**Purpose**: Complete GitHub OAuth flow and establish user session

---

### Session Management

#### POST /api/auth/logout
**Description**: Logout user and invalidate session  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```
**Purpose**: End user session (note: JWT tokens are stateless, so this mainly clears frontend session)

---

### User Profile Management

#### GET /api/users/profile
**Description**: Get current user's profile information  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com", 
    "provider": "google",
    "avatar_url": "https://lh3.googleusercontent.com/...",
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z",
    "preferences": {
      "notification_email": true,
      "interview_difficulty": "medium"
    },
    "statistics": {
      "total_uploads": 5,
      "resumes_uploaded": 2,
      "job_descriptions_uploaded": 3,
      "last_activity": "2024-01-15T10:30:00Z"
    }
  }
}
```
**Purpose**: Retrieve complete user profile with preferences and statistics

#### PUT /api/users/profile
**Description**: Update user profile information  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "name": "Updated Name",
  "preferences": {
    "notification_email": false,
    "interview_difficulty": "advanced",
    "preferred_question_types": ["technical", "behavioral"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "Updated Name",
    "email": "john.doe@example.com",
    "preferences": {
      "notification_email": false,
      "interview_difficulty": "advanced", 
      "preferred_question_types": ["technical", "behavioral"]
    },
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```
**Purpose**: Allow users to modify their profile information and preferences

---

### Token Validation (Internal Service Use)

#### POST /api/users/verify
**Description**: Verify JWT token validity and return user information (for inter-service calls)  
**Authentication**: Service token required  
**Request Body**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (Valid Token)**:
```json
{
  "success": true,
  "valid": true,
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "provider": "google"
  },
  "token_info": {
    "issued_at": "2024-01-15T10:30:00Z",
    "expires_at": "2024-01-16T10:30:00Z",
    "remaining_hours": 18.5
  }
}
```

**Response (Invalid Token)**:
```json
{
  "success": false,
  "valid": false,
  "error": "Token expired",
  "error_code": "TOKEN_EXPIRED"
}
```
**Purpose**: Allow other services to validate user tokens and get user context

---

### Account Management

#### DELETE /api/users/delete
**Description**: Permanently delete user account and all associated data  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "message": "Account deleted successfully",
  "deleted_data": {
    "user_profile": true,
    "upload_records": 5,
    "session_data": true
  }
}
```

**Flow**:
1. Validates user authentication
2. Removes user profile from database
3. Removes all upload records and file references
4. Cleans up any associated session data
5. Returns confirmation of deletion

**Purpose**: Allow users to permanently delete their accounts and all data

---

### Upload Record Management

#### POST /api/users/uploads
**Description**: Add file upload record to user's profile (called by File Parsing Service)  
**Authentication**: Required (JWT token + Service token)  
**Request Body**:
```json
{
  "file_type": "resume",
  "filename": "resume_user123_1634567890.pdf",
  "original_name": "my_resume.pdf",
  "file_path": "/uploads/resumes/resume_user123_1634567890.pdf",
  "file_size": 1048576,
  "mime_type": "application/pdf"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Upload record added successfully",
  "upload_id": "507f1f77bcf86cd799439012"
}
```
**Purpose**: Track user file uploads for history and statistics

#### GET /api/users/uploads
**Description**: Get user's upload history and file records  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "uploads": {
    "resumes": [
      {
        "id": "507f1f77bcf86cd799439012",
        "filename": "resume_user123_1634567890.pdf",
        "original_name": "my_resume.pdf",
        "uploaded_at": "2024-01-15T10:30:00Z",
        "file_size": 1048576,
        "mime_type": "application/pdf",
        "status": "processed"
      }
    ],
    "job_descriptions": [
      {
        "id": "507f1f77bcf86cd799439013", 
        "filename": "jd_user123_1634567890.pdf",
        "original_name": "software_engineer_jd.pdf",
        "uploaded_at": "2024-01-15T11:00:00Z", 
        "file_size": 2097152,
        "mime_type": "application/pdf",
        "status": "processed"
      }
    ],
    "statistics": {
      "total_uploads": 2,
      "total_size": 3145728,
      "last_upload": "2024-01-15T11:00:00Z"
    }
  }
}
```
**Purpose**: Provide users with their complete upload history

---

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "email": "string (unique)",
  "name": "string", 
  "provider": "google|github",
  "provider_id": "string",
  "avatar_url": "string",
  "github_username": "string (for GitHub users)",
  "preferences": {
    "notification_email": "boolean",
    "interview_difficulty": "string",
    "preferred_question_types": ["string"]
  },
  "created_at": "datetime",
  "last_login": "datetime", 
  "updated_at": "datetime"
}
```

### Upload Records Collection  
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId (ref: users)",
  "file_type": "resume|job_description|job_description_text",
  "filename": "string",
  "original_name": "string", 
  "file_path": "string",
  "file_size": "number",
  "mime_type": "string",
  "uploaded_at": "datetime",
  "status": "uploaded|processed|error"
}
```

---

## Error Handling

### Authentication Errors
```json
{
  "success": false,
  "error": "Invalid or expired token",
  "error_code": "TOKEN_INVALID",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### OAuth Errors
```json
{
  "success": false,
  "error": "OAuth provider returned error",
  "error_code": "OAUTH_PROVIDER_ERROR", 
  "provider": "google",
  "provider_error": "access_denied",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Database Errors
```json
{
  "success": false,
  "error": "Database operation failed",
  "error_code": "DATABASE_ERROR",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Security Features

### JWT Token Security
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Expiry**: Configurable (default 24 hours)
- **Secret**: Environment variable, rotatable
- **Claims**: User ID, email, name, provider, issued/expiry times

### OAuth Security
- **State Parameter**: CSRF protection for OAuth flows
- **Secure Redirect**: Validates redirect URIs match configured values
- **Token Exchange**: Server-side exchange prevents code interception
- **Scope Limitation**: Minimal scopes (profile, email)

### Database Security
- **Connection**: Encrypted connections to MongoDB
- **Validation**: Input validation and sanitization
- **Indexing**: Email uniqueness enforced at database level
- **Backup**: Regular automated backups

### API Security
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: All inputs validated and sanitized
- **Service Authentication**: Inter-service calls require service tokens
- **Error Handling**: No sensitive information in error responses

---

## Configuration

### Environment Variables
```bash
# Database Configuration
MONGODB_URI=mongodb://localhost:27017/
DATABASE_NAME=Reflection

# JWT Configuration  
JWT_SECRET=your-jwt-secret-key
JWT_EXPIRY_HOURS=24

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret  
GOOGLE_REDIRECT_URI=http://localhost:5000/api/auth/google/callback

# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:5000/api/auth/github/callback

# Service Configuration
LOGIN_MANAGEMENT_PORT=5001
FLASK_DEBUG=False
```

### OAuth Provider Setup

#### Google OAuth Setup
1. Create project in Google Cloud Console
2. Enable Google+ API
3. Create OAuth 2.0 Client ID
4. Add authorized redirect URI: `http://localhost:5000/api/auth/google/callback`

#### GitHub OAuth Setup  
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Create new OAuth App
3. Set Authorization callback URL: `http://localhost:5000/api/auth/github/callback`

---

## Monitoring & Logging

### Health Check Monitoring
- Service availability status
- Database connection status  
- OAuth provider configuration status
- Response time metrics

### Security Logging
- Failed authentication attempts
- Token validation failures
- OAuth errors and anomalies
- Account creation and deletion events

### Performance Metrics
- Response times for authentication flows
- Database query performance
- Token generation/validation times
- Error rates by endpoint