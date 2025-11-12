# REFLECTION API - Complete cURL Commands

**Generated:** 12 November 2025  
**Last Updated:** 12 November 2025 - Added authentication to all critical endpoints

## Base URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5000 |
| Login Management | http://localhost:5001 |
| File Parsing | http://localhost:5002 |
| Question-Answer Gen | http://localhost:5003 |
| Speech-to-Text | http://localhost:5004 |
| Resources | http://localhost:5005 |

> **NOTE:** Replace `<JWT_TOKEN>` with your actual JWT token from login response  
> Replace `<USER_ID>` with actual user ID

## 🔐 Security Updates

**All critical endpoints now require authentication:**
- ✅ All file upload and parsing endpoints (File Parsing Service)
- ✅ All question generation and answer analysis endpoints (Question-Answer Generation Service)
- ✅ All resource access endpoints (Resources Service)
- ✅ All speech-to-text endpoints (Speech-to-Text Service)
- ✅ All user management endpoints except OAuth and `/api/users/verify`

**Endpoints that remain public:**
- `/health` endpoints (for service monitoring)
- OAuth login/callback routes (required for authentication)
- `/api/users/verify` (used during authentication flow, validates tokens internally)
- Frontend landing pages (index, about, contact, etc.)

---

## 1. LOGIN-MANAGEMENT SERVICE (Port 5001)

### 1.1 Health Check (Public)

```bash
curl -X GET http://localhost:5001/health
```

### 1.2 Check OAuth Configuration Status (Public)

```bash
curl -X GET http://localhost:5001/api/auth/status
```

### 1.3 Initiate Google OAuth Login (Public)

```bash
curl -X GET http://localhost:5001/api/auth/google/login
```

### 1.4 Google OAuth Callback (Public)

```bash
curl -X GET "http://localhost:5001/api/auth/google/callback?code=<OAUTH_CODE>&state=<STATE>"
```

### 1.5 Initiate GitHub OAuth Login (Public)

```bash
curl -X GET http://localhost:5001/api/auth/github/login
```

### 1.6 GitHub OAuth Callback (Public)

```bash
curl -X GET "http://localhost:5001/api/auth/github/callback?code=<OAUTH_CODE>&state=<STATE>"
```

### 1.7 Logout User (Authenticated)

```bash
curl -X POST http://localhost:5001/api/auth/logout \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json"
```

### 1.8 Get User Profile (Authenticated)

```bash
curl -X GET http://localhost:5001/api/users/profile \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 1.9 Update User Profile (Authenticated)

```bash
curl -X PUT http://localhost:5001/api/users/profile \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

### 1.10 Verify User Token (Public - Inter-service)

> **Note:** This endpoint is used during authentication flow and must remain publicly accessible. It validates the token internally.

```bash
curl -X POST http://localhost:5001/api/users/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "<TOKEN_TO_VERIFY>"
  }'
```

### 1.11 Delete User Account (Authenticated)

```bash
curl -X DELETE http://localhost:5001/api/users/delete \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 1.12 Add Upload Record (Authenticated)

```bash
curl -X POST http://localhost:5001/api/users/uploads \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "file_type": "resume",
    "filename": "resume_cleaned.txt",
    "original_name": "resume.pdf",
    "file_path": "/path/to/file",
    "file_size": 12345,
    "mime_type": "text/plain",
    "pinecone_id": "embedding_id_123"
  }'
```

### 1.13 Get User Upload History (Authenticated)

```bash
curl -X GET http://localhost:5001/api/users/uploads \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 1.14 Store Job Categories (Authenticated)

```bash
curl -X POST http://localhost:5001/api/users/categories \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "detected_categories": ["DevOps", "AI", "Cloud Computing"]
  }'
```

### 1.15 Get Job Categories (Authenticated)

```bash
curl -X GET http://localhost:5001/api/users/categories \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 2. FILE-PARSING SERVICE (Port 5002)

### 2.1 Health Check (Public)

```bash
curl -X GET http://localhost:5002/health
```

### 2.2 Debug Request Headers (Debug Only - Remove in Production)

```bash
curl -X GET http://localhost:5002/debug/request-headers \
  -H "Authorization: Bearer <JWT_TOKEN>"

curl -X POST http://localhost:5002/debug/request-headers \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### 2.3 Upload Resume File (Authenticated)

```bash
curl -X POST http://localhost:5002/api/files/upload/resume \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "resume=@/path/to/resume.pdf"
```

### 2.4 Upload Job Description File (Authenticated)

```bash
curl -X POST http://localhost:5002/api/files/upload/job-description \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "job_description=@/path/to/job_description.pdf"
```

### 2.5 Save Text Job Description (Authenticated)

```bash
curl -X POST http://localhost:5002/api/files/text/job-description \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "We are looking for a Senior Software Engineer with 5+ years experience in Python, React, and cloud technologies..."
  }'
```

### 2.6 Combined Upload - Resume + JD Files (Authenticated)

```bash
curl -X POST http://localhost:5002/api/upload/submit \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=@/path/to/job_description.pdf"
```

### 2.7 Get Upload Requirements (Authenticated)

```bash
curl -X GET http://localhost:5002/api/files/requirements \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 2.8 Get Parsed Content (Authenticated)

```bash
curl -X GET http://localhost:5002/api/files/parsed-content \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 2.9 Clear Parsed Content (Authenticated)

```bash
curl -X POST http://localhost:5002/api/files/clear-content \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 2.10 Get Content Status (Authenticated)

```bash
curl -X GET http://localhost:5002/api/files/content-status \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 2.11 Get User Questions (Authenticated)

```bash
curl -X GET http://localhost:5002/api/questions \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 3. QUESTION-ANSWER-GENERATION SERVICE (Port 5003)

### 3.1 Health Check (Public)

```bash
curl -X GET http://localhost:5003/health
```

### 3.2 Generate Interview Questions (Authenticated)

```bash
curl -X POST http://localhost:5003/api/questions/generate \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<USER_ID>",
    "resume_text": "Software Engineer with 5 years experience in Python...",
    "jd_text": "Looking for Senior Developer with Python expertise...",
    "resume_embedding_id": "resume_emb_123",
    "jd_embedding_id": "jd_emb_456"
  }'
```

### 3.3 Get User Questions (Authenticated)

```bash
curl -X GET http://localhost:5003/api/questions/user/<USER_ID> \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 3.4 Analyze User Answer (Authenticated)

```bash
curl -X POST http://localhost:5003/api/answers/analyze \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is your experience with microservices?",
    "user_answer": "I have worked with microservices architecture for 3 years...",
    "category": "System Design",
    "difficulty": "Medium"
  }'
```

---

## 4. SPEECH-TO-TEXT SERVICE (Port 5004)

### 4.1 Health Check (Public)

```bash
curl -X GET http://localhost:5004/health
```

### 4.2 Convert Speech to Text (Authenticated)

```bash
curl -X POST http://localhost:5004/SpeechToText \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -F "file=@/path/to/audio.webm"
```

> Supports multiple audio formats: `.webm`, `.ogg`, `.m4a`, `.wav`, `.mp3`, `.flac`

---

## 5. RESOURCES SERVICE (Port 5005)

### 5.1 Health Check (Public)

```bash
curl -X GET http://localhost:5005/health
```

### 5.2 Get Resources by Category (Authenticated)

Get all resources for a category:

```bash
curl -X GET http://localhost:5005/resources \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Resource-ID: DevOps"
```

Get only courses:

```bash
curl -X GET "http://localhost:5005/resources?courses=1" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Resource-ID: DevOps"
```

Get courses and certifications:

```bash
curl -X GET "http://localhost:5005/resources?courses=1&certifications=1" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Resource-ID: AI"
```

Get all types (courses, certifications, projects):

```bash
curl -X GET "http://localhost:5005/resources?courses=1&certifications=1&projects=1" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Resource-ID: Cloud Computing"
```

### 5.3 List All Categories (Authenticated)

```bash
curl -X GET http://localhost:5005/categories \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 5.4 Get Resources by Multiple Categories (Authenticated)

```bash
curl -X POST http://localhost:5005/resources/by-categories \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["DevOps", "AI", "Cloud Computing"]
  }'
```

---

## 6. FRONTEND SERVICE (Port 5000)

### 6.1 Public Pages (No Authentication Required)

Landing Page:

```bash
curl -X GET http://localhost:5000/
```

About Page:

```bash
curl -X GET http://localhost:5000/about
```

Testimonials Page:

```bash
curl -X GET http://localhost:5000/testimonials
```

Privacy Policy:

```bash
curl -X GET http://localhost:5000/privacy
```

Contact Page:

```bash
curl -X GET http://localhost:5000/contact
```

Health Check:

```bash
curl -X GET http://localhost:5000/health
```

### 6.2 Authentication Flow (Public)

Login Page:

```bash
curl -X GET http://localhost:5000/login
```

Initiate Google Login:

```bash
curl -X GET http://localhost:5000/api/auth/google/login
```

Initiate GitHub Login:

```bash
curl -X GET http://localhost:5000/api/auth/github/login
```

Google Callback:

```bash
curl -X GET "http://localhost:5000/api/auth/google/callback?code=<CODE>&state=<STATE>"
```

GitHub Callback:

```bash
curl -X GET "http://localhost:5000/api/auth/github/callback?code=<CODE>&state=<STATE>"
```

Logout:

```bash
curl -X GET http://localhost:5000/logout
```

### 6.3 Debug Endpoints (Remove in Production)

Debug Session Info:

```bash
curl -X GET http://localhost:5000/debug/session \
  --cookie "session=<SESSION_COOKIE>"
```

Debug Service Token:

```bash
curl -X GET http://localhost:5000/debug/service-token \
  --cookie "session=<SESSION_COOKIE>"
```

### 6.4 Protected Pages (Authenticated via Session Cookie)

Dashboard/Home:

```bash
curl -X GET http://localhost:5000/dashboard \
  --cookie "session=<SESSION_COOKIE>"
```

Practice Page:

```bash
curl -X GET http://localhost:5000/practice \
  --cookie "session=<SESSION_COOKIE>"
```

Question Detail:

```bash
curl -X GET "http://localhost:5000/question/1?filter=most-asked" \
  --cookie "session=<SESSION_COOKIE>"
```

Profile Page:

```bash
curl -X GET http://localhost:5000/profile \
  --cookie "session=<SESSION_COOKIE>"
```

Resources Page:

```bash
curl -X GET http://localhost:5000/resources \
  --cookie "session=<SESSION_COOKIE>"
```

Delete Account Page:

```bash
curl -X GET http://localhost:5000/delete-account \
  --cookie "session=<SESSION_COOKIE>"
```

### 6.5 Protected API Endpoints (Authenticated via Session Cookie)

Analyze Answer:

```bash
curl -X POST http://localhost:5000/api/practice/analyze-answer \
  --cookie "session=<SESSION_COOKIE>" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain microservices architecture",
    "user_answer": "Microservices is an architectural style...",
    "category": "System Design",
    "difficulty": "Medium"
  }'
```

Get User Categories:

```bash
curl -X GET http://localhost:5000/api/resources/user-categories \
  --cookie "session=<SESSION_COOKIE>"
```

Get Categorized Resources:

```bash
curl -X POST http://localhost:5000/api/resources/categorized \
  --cookie "session=<SESSION_COOKIE>" \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["DevOps", "AI"]
  }'
```

Speech to Text Proxy:

```bash
curl -X POST http://localhost:5000/api/speech-to-text \
  --cookie "session=<SESSION_COOKIE>" \
  -F "file=@/path/to/audio.webm"
```

Validate Resume:

```bash
curl -X POST http://localhost:5000/api/upload/resume \
  --cookie "session=<SESSION_COOKIE>" \
  -F "resume_file=@/path/to/resume.pdf"
```

Validate Job Description:

```bash
curl -X POST http://localhost:5000/api/upload/job-description \
  --cookie "session=<SESSION_COOKIE>" \
  -F "jd_file=@/path/to/jd.pdf"
```

Upload Text Job Description:

```bash
curl -X POST http://localhost:5000/api/upload/text/job-description \
  --cookie "session=<SESSION_COOKIE>" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "We are looking for a Senior Developer..."
  }'
```

Submit Mixed (Resume File + JD Text):

```bash
curl -X POST http://localhost:5000/api/upload/submit_mixed \
  --cookie "session=<SESSION_COOKIE>" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description_text=We are looking for a Senior Developer..."
```

Submit Combined (Both Files):

```bash
curl -X POST http://localhost:5000/api/upload/submit \
  --cookie "session=<SESSION_COOKIE>" \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=@/path/to/jd.pdf"
```

Process Resume Only:

```bash
curl -X POST http://localhost:5000/process_resume \
  --cookie "session=<SESSION_COOKIE>" \
  -F "resume=@/path/to/resume.pdf"
```

Process Job Description:

```bash
curl -X POST http://localhost:5000/process_job_description \
  --cookie "session=<SESSION_COOKIE>" \
  -F "jd=@/path/to/jd.pdf"
```

Submit Job Description Text (Simple):

```bash
curl -X POST http://localhost:5000/submit_job_description \
  --cookie "session=<SESSION_COOKIE>" \
  -F "job_description=We are looking for..."
```

Update Profile:

```bash
curl -X POST http://localhost:5000/profile \
  --cookie "session=<SESSION_COOKIE>" \
  -F "name=Updated Name" \
  -F "avatar_url=https://example.com/avatar.jpg"
```

Delete Account:

```bash
curl -X POST http://localhost:5000/delete-account \
  --cookie "session=<SESSION_COOKIE>" \
  -F "confirmation=delete my account"
```

---

## Common Usage Examples

### Example 1: Complete User Flow - Login to Question Generation

**Step 1:** Get Google OAuth URL

```bash
OAUTH_RESPONSE=$(curl -s http://localhost:5001/api/auth/google/login)
echo $OAUTH_RESPONSE
```

Visit the `auth_url` in browser to complete OAuth

**Step 2:** After OAuth callback, you'll receive JWT token

```bash
JWT_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Step 3:** Upload Resume

```bash
curl -X POST http://localhost:5002/api/files/upload/resume \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "resume=@resume.pdf"
```

**Step 4:** Upload Job Description Text

```bash
curl -X POST http://localhost:5002/api/files/text/job-description \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Looking for Python Developer with 5+ years experience..."
  }'
```

**Step 5:** Get Generated Questions

```bash
curl -X GET http://localhost:5002/api/questions \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Example 2: Direct Backend Testing (Resume + JD Upload)

Combined upload with both files:

```bash
curl -X POST http://localhost:5002/api/upload/submit \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "resume=@resume.pdf" \
  -F "job_description=@job_description.pdf"
```

### Example 3: Answer Analysis Flow

Get user's questions:

```bash
QUESTIONS=$(curl -s http://localhost:5003/api/questions/user/<USER_ID> \
  -H "Authorization: Bearer $JWT_TOKEN")
```

Analyze an answer:

```bash
curl -X POST http://localhost:5003/api/answers/analyze \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is REST API?",
    "user_answer": "REST API is an architectural style for designing networked applications...",
    "category": "Web Development",
    "difficulty": "Medium"
  }'
```

### Example 4: Resources Flow

Get user's detected categories:

```bash
curl -X GET http://localhost:5001/api/users/categories \
  -H "Authorization: Bearer $JWT_TOKEN"
```

Get resources for those categories:

```bash
curl -X POST http://localhost:5005/resources/by-categories \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "categories": ["DevOps", "Cloud Computing"]
  }'
```

### Example 5: Frontend Session-based Flow

Login via browser, get session cookie, then:

Upload resume via frontend:

```bash
curl -X POST http://localhost:5000/process_resume \
  --cookie "session=<YOUR_SESSION_COOKIE>" \
  -F "resume=@resume.pdf"
```

View practice page:

```bash
curl -X GET http://localhost:5000/practice \
  --cookie "session=<YOUR_SESSION_COOKIE>"
```

---

## Notes and Tips

### 1. Authentication

- **Backend services** (ports 5001-5005): Use JWT Bearer token
- **Frontend service** (port 5000): Use session cookie from browser

### 2. Getting JWT Token

- Complete OAuth flow via browser
- Token is returned in the callback response
- Store token for subsequent API calls

### 3. File Uploads

- Use `-F` flag for multipart/form-data
- **Supported formats:** PDF, DOC, DOCX
- **Max size:** 10MB

### 4. Session Cookie

- Login via browser to get session cookie
- Extract from browser dev tools (Application > Cookies)
- Use with `--cookie` flag

### 5. Testing

- Use health endpoints to check service status
- Debug endpoints should only be used in development
- Always include proper authentication headers

### 6. Error Handling

| Code | Meaning |
|------|---------|
| 401 | Unauthorized (missing/invalid token) |
| 400 | Bad Request (missing/invalid data) |
| 404 | Not Found |
| 500 | Internal Server Error |

### 7. Response Format

- All responses are in JSON format
- **Success responses:** `{"success": true, ...}`
- **Error responses:** `{"success": false, "error": "..."}`

---

**End of API Documentation**
