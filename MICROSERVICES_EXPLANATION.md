# Reflection Platform - Complete Microservices Explanation
## Study Guide for Presentation

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Flow](#application-flow)
3. [Microservices Explained (In Order)](#microservices-explained-in-order)
   - [1. Frontend Service](#1-frontend-service-port-5000)
   - [2. Login Management Service](#2-login-management-service-port-5001)
   - [3. File Parsing Service](#3-file-parsing-service-port-5002)
   - [4. Question-Answer Generation Service](#4-question-answer-generation-service-port-5003)
   - [5. Speech-to-Text Service](#5-speech-to-text-service-port-5004)
   - [6. Resources Service](#6-resources-service-port-5005)
4. [Shared Components](#shared-components)
5. [Key Technologies & Terms](#key-technologies--terms)
6. [Data Flow Diagrams](#data-flow-diagrams)

---

## 🏗️ Architecture Overview

### What is Reflection?
**Reflection** is an AI-powered interview preparation platform that helps job seekers practice for technical and behavioral interviews. The application uses a **microservices architecture** where different functionalities are separated into independent services.

### Microservices Architecture Benefits:
- **Scalability**: Each service can scale independently based on demand
- **Maintainability**: Changes to one service don't affect others
- **Technology Diversity**: Each service can use the best tools for its purpose
- **Fault Isolation**: If one service fails, others continue working

### High-Level Architecture:
```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│              FRONTEND SERVICE (Port 5000)               │
│  • Web Interface (HTML/Jinja2 Templates)                │
│  • Orchestrates all backend services                    │
│  • Session Management                                   │
└──────┬─────────────┬─────────────┬─────────────┬────────┘
       │             │             │             │
       ▼             ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  Login   │  │  File    │  │   QA     │  │  Speech  │
│  Mgt     │  │ Parsing  │  │ Gen      │  │  2 Text  │
│  :5001   │  │  :5002   │  │  :5003   │  │  :5004   │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └──────────┘
     │             │             │
     │             │             │
     ▼             ▼             ▼
┌─────────────────────────────────────────────┐
│        EXTERNAL SERVICES & DATABASES        │
│  • MongoDB (User data, Questions)           │
│  • Pinecone (Vector Embeddings)             │
│  • Google Gemini AI (Question Generation)   │
│  • Google OAuth (Authentication)            │
│  • GitHub OAuth (Authentication)            │
└─────────────────────────────────────────────┘
```

---

## 🔄 Application Flow

### Typical User Journey:

1. **Landing** → User visits the website (Frontend)
2. **Authentication** → User logs in via Google/GitHub (Login Management)
3. **Dashboard** → User sees their profile (Frontend + Login Management)
4. **Upload Documents** → User uploads resume and/or job description (File Parsing)
5. **Processing** → Files are parsed, PII removed, embeddings created (File Parsing + Pinecone)
6. **Question Generation** → AI generates personalized questions (QA Generation + Gemini)
7. **Practice** → User views questions and practices (Frontend + QA Generation)
8. **Answer Analysis** → User submits answers for feedback (QA Generation + Gemini)
9. **Resources** → User gets learning resources (Resources Service)
10. **Speech Input** → User can speak answers (Speech-to-Text)

---

## 🎯 Microservices Explained (In Order)

### 1. Frontend Service (Port 5000)

**Purpose**: The main entry point and user interface for the application.

**Technology Stack**:
- **Flask**: Python web framework for serving HTML pages
- **Jinja2**: Template engine for rendering HTML with dynamic content
- **Session Management**: Stores user authentication tokens

**Key Responsibilities**:
1. **Serves Web Pages**: Renders HTML templates (index, login, dashboard, practice, etc.)
2. **Orchestrates Services**: Acts as a coordinator between all backend microservices
3. **Session Management**: Maintains user sessions using Flask sessions (stores JWT tokens)
4. **Request Routing**: Routes user requests to appropriate backend services
5. **UI/UX**: Provides the visual interface users interact with

**Key Endpoints**:
- `/` - Landing page
- `/login` - Login page
- `/dashboard` - User dashboard (protected)
- `/practice` - Interview practice page (protected)
- `/resources` - Learning resources page (protected)
- `/api/upload/*` - File upload endpoints (proxies to File Parsing)

**Key Concepts**:
- **Session Cookies**: Stores JWT token after login for subsequent requests
- **Service Client**: Uses `ServiceClient` to communicate with other microservices
- **Authentication Decorator**: `@login_required` checks if user is authenticated

**How It Works**:
1. User visits a page (e.g., `/practice`)
2. Frontend checks if user is authenticated via `is_authenticated()`
3. If authenticated, it calls File Parsing service to get questions
4. It renders the `practice.html` template with the questions
5. When user submits an answer, Frontend forwards it to QA Generation service

---

### 2. Login Management Service (Port 5001)

**Purpose**: Handles all authentication and user management operations.

**Technology Stack**:
- **Flask**: Web framework
- **MongoDB**: Stores user data (profiles, upload history, categories)
- **OAuth 2.0**: Google and GitHub authentication
- **JWT (JSON Web Tokens)**: Secure token-based authentication

**Key Responsibilities**:
1. **OAuth Authentication**: Manages Google and GitHub OAuth flows
2. **User Management**: Creates, updates, and deletes user accounts
3. **Token Generation**: Issues JWT tokens after successful authentication
4. **Token Verification**: Validates JWT tokens for other services
5. **User Profile Storage**: Stores user data in MongoDB
6. **Upload Tracking**: Records file upload history per user
7. **Category Storage**: Stores detected job categories for users

**Key Endpoints**:
- `/api/auth/google/login` - Initiates Google OAuth
- `/api/auth/google/callback` - Handles Google OAuth callback
- `/api/auth/github/login` - Initiates GitHub OAuth
- `/api/auth/github/callback` - Handles GitHub OAuth callback
- `/api/users/profile` - Get/Update user profile
- `/api/users/verify` - Verify JWT token (for inter-service calls)
- `/api/users/uploads` - Record file uploads
- `/api/users/categories` - Store/Retrieve job categories

**Key Concepts**:
- **OAuth Flow**:
  1. User clicks "Login with Google"
  2. Service generates OAuth URL and redirects user to Google
  3. User authorizes the application on Google
  4. Google redirects back with an authorization code
  5. Service exchanges code for user info (email, name, avatar)
  6. Service creates/updates user in MongoDB
  7. Service generates JWT token and returns it

- **JWT Token**: Contains user ID, email, expiration time; signed with secret key
- **User Model**: MongoDB document structure:
  ```json
  {
    "_id": "user123",
    "email": "user@example.com",
    "name": "John Doe",
    "provider": "google",
    "avatar_url": "...",
    "uploads": [...],
    "categories": ["DevOps", "AI"]
  }
  ```

**How It Works**:
1. User initiates OAuth login via Frontend
2. Login Management generates OAuth URL and returns to Frontend
3. Frontend redirects user to OAuth provider
4. After authorization, OAuth provider redirects back with code
5. Login Management exchanges code for user info
6. Creates/updates user in MongoDB
7. Generates JWT token
8. Returns token to Frontend, which stores it in session

---

### 3. File Parsing Service (Port 5002)

**Purpose**: Handles secure file upload, validation, parsing, and embedding generation.

**Technology Stack**:
- **Flask**: Web framework
- **PyPDF2**: PDF parsing library
- **sentence-transformers**: Generates text embeddings
- **Pinecone**: Vector database for storing embeddings
- **python-magic**: File type validation (magic number checking)

**Key Responsibilities**:
1. **File Security**: Multi-layer validation (extension, MIME type, magic numbers)
2. **File Parsing**: Extracts text from PDF, DOC, DOCX files
3. **PII Removal**: Removes personally identifiable information from resumes
4. **Embedding Generation**: Creates vector embeddings using sentence transformers
5. **Vector Storage**: Stores embeddings in Pinecone with metadata
6. **Job Category Detection**: Detects job categories from resume/JD using regex patterns
7. **Question Trigger**: Automatically triggers question generation after file processing
8. **Content Storage**: Temporarily stores parsed content for question generation

**Key Endpoints**:
- `/api/files/upload/resume` - Upload and process resume
- `/api/files/upload/job-description` - Upload job description file
- `/api/files/text/job-description` - Save text-based job description
- `/api/upload/submit` - Combined upload (resume + JD)
- `/api/questions` - Get questions for user (proxies to QA service)
- `/api/files/requirements` - Get upload requirements

**Key Concepts**:

1. **File Security Validation**:
   - **Extension Check**: Validates file extension (.pdf, .doc, .docx)
   - **MIME Type**: Checks Content-Type header
   - **Magic Number**: Reads file header bytes to verify actual file type (prevents fake extensions)
   - **Size Limit**: Maximum 10MB
   - **Filename Sanitization**: Removes dangerous characters
   - **Path Traversal Prevention**: Blocks `../` attacks

2. **PII (Personally Identifiable Information) Removal**:
   - Extracts text from PDF/DOC files
   - Uses regex patterns to identify and remove:
     - Email addresses
     - Phone numbers
     - Addresses
     - Social Security Numbers (if present)
   - Keeps only professional content

3. **Vector Embeddings**:
   - **What**: Numerical representations of text in high-dimensional space (384 dimensions)
   - **How**: Uses `sentence-transformers/all-MiniLM-L6-v2` model
   - **Why**: Enables semantic search and similarity matching
   - **Storage**: Stored in Pinecone with metadata (user_id, document_type, timestamp)

4. **Pinecone Vector Database**:
   - **Purpose**: Stores document embeddings for semantic search
   - **Index**: Named `interview-prep-assistant`
   - **Dimension**: 384 (matches embedding model)
   - **Metric**: Cosine similarity
   - **Structure**: Each vector has:
     - ID: `{user_id}_{document_type}_{timestamp}`
     - Vector: 384-dimensional array
     - Metadata: user_id, document_type, text_preview, etc.

5. **Job Category Detection**:
   - Uses regex patterns to detect keywords in resume/JD
   - Categories: DevOps, AI, Cloud Computing, Security, etc.
   - Stores detected categories in user profile

**How It Works**:
1. User uploads resume file
2. File Parsing validates security (extension, MIME, magic number, size)
3. File is saved temporarily
4. Text is extracted using PyPDF2 or similar
5. PII is removed from resume text
6. Cleaned text is saved as `.txt` file
7. Embedding is generated using sentence-transformers
8. Embedding is stored in Pinecone with metadata
9. Upload record is saved to Login Management service
10. If JD also exists, triggers question generation
11. Job categories are detected and stored

---

### 4. Question-Answer Generation Service (Port 5003)

**Purpose**: Generates personalized interview questions and analyzes user answers using AI.

**Technology Stack**:
- **Flask**: Web framework
- **Google Gemini AI**: Large Language Model for question generation and answer analysis
- **LangChain**: Framework for building AI applications
- **MongoDB**: Stores user-specific questions
- **sentence-transformers**: Embedding model (for vector operations)

**Key Responsibilities**:
1. **Question Generation**: Uses Google Gemini to generate personalized interview questions
2. **Question Storage**: Saves questions to MongoDB associated with user ID
3. **Answer Analysis**: Analyzes user answers and provides feedback
4. **Question Retrieval**: Fetches user's questions from MongoDB

**Key Endpoints**:
- `/api/questions/generate` - Generate questions from resume/JD
- `/api/questions/user/<user_id>` - Get questions for a user
- `/api/answers/analyze` - Analyze user's answer and provide feedback

**Key Concepts**:

1. **Google Gemini AI**:
   - **Model**: `gemini-2.0-flash` (fast, efficient model)
   - **Provider**: Google Generative AI
   - **Purpose**: Natural language understanding and generation
   - **Usage**: 
     - Generates questions based on resume and job description
     - Analyzes answers and provides feedback with scores

2. **Question Generation Process**:
   ```
   Input: Resume text + Job description text
   ↓
   Sanitize inputs (remove malicious content, limit length)
   ↓
   Create prompt with structured format:
   - Instructions for Gemini
   - Resume data (marked as data, not instructions)
   - Job description data (marked as data, not instructions)
   ↓
   Send to Gemini API
   ↓
   Parse JSON response (14 questions: 5 behavioral, 9 technical)
   ↓
   Save to MongoDB with user association
   ↓
   Return questions to caller
   ```

3. **Question Structure**:
   ```json
   {
     "text": "Tell me about a time you worked with microservices architecture.",
     "category": "Technical",  // or "Behavioral"
     "difficulty": "Medium"     // Easy, Medium, Hard
   }
   ```

4. **MongoDB Storage** (UserQuestionsModel):
   ```json
   {
     "_id": "...",
     "user_id": "user123",
     "resume_embedding_id": "resume_emb_123",
     "jd_embedding_id": "jd_emb_456",
     "questions": [
       { "text": "...", "category": "...", "difficulty": "..." },
       ...
     ],
     "created_at": "2025-01-15T10:00:00Z",
     "updated_at": "2025-01-15T10:00:00Z"
   }
   ```

5. **Answer Analysis**:
   - Takes question and user's answer
   - Sends to Gemini with analysis prompt
   - Returns:
     - Score (0-100)
     - Strengths
     - Weaknesses
     - Suggestions for improvement

**How It Works**:
1. File Parsing service calls `/api/questions/generate` after processing files
2. QA Service receives resume text, JD text, and embedding IDs
3. Inputs are sanitized and limited in length
4. Prompt is created with clear delimiters (prevents prompt injection)
5. Request is sent to Google Gemini API
6. Response is parsed (expects JSON array of questions)
7. Questions are saved to MongoDB with user_id
8. Questions are returned to caller
9. When user views practice page, Frontend fetches questions via File Parsing service
10. When user submits answer, Frontend calls `/api/answers/analyze`
11. Gemini analyzes the answer and returns feedback

---

### 5. Speech-to-Text Service (Port 5004)

**Purpose**: Converts audio recordings to text for voice-based answer input.

**Technology Stack**:
- **Flask**: Web framework
- **Google Speech Recognition API**: Converts audio to text
- **pydub + FFmpeg**: Audio format conversion
- **speech_recognition**: Python library for speech-to-text

**Key Responsibilities**:
1. **Audio Upload**: Accepts audio files in various formats (webm, ogg, m4a, wav, mp3, flac)
2. **Format Conversion**: Converts any audio format to WAV/FLAC for processing
3. **Speech Recognition**: Uses Google Speech Recognition API to transcribe audio
4. **Text Return**: Returns transcribed text to caller

**Key Endpoints**:
- `/SpeechToText` - Upload audio file and get transcript

**Key Concepts**:

1. **Audio Processing**:
   - Accepts multiple formats: `.webm`, `.ogg`, `.m4a`, `.wav`, `.mp3`, `.flac`
   - Uses `pydub` library to convert to WAV format
   - Requires `FFmpeg` installed on server

2. **Google Speech Recognition**:
   - Free tier available (with limits)
   - Supports multiple languages
   - Good accuracy for clear speech
   - Requires internet connection

**How It Works**:
1. User records audio answer using browser's MediaRecorder API (creates .webm file)
2. Frontend sends audio file to Speech-to-Text service
3. Service saves file temporarily
4. Converts to WAV format using pydub/FFmpeg
5. Sends to Google Speech Recognition API
6. Receives transcribed text
7. Deletes temporary files
8. Returns transcript to Frontend
9. Frontend populates answer textarea with transcript

---

### 6. Resources Service (Port 5005)

**Purpose**: Provides learning resources (courses, certifications, projects) categorized by job roles.

**Technology Stack**:
- **Flask**: Web framework
- **MongoDB**: Stores resource data organized by categories

**Key Responsibilities**:
1. **Resource Storage**: Stores courses, certifications, and projects in MongoDB
2. **Category-based Retrieval**: Returns resources filtered by job category
3. **Multi-category Support**: Can fetch resources for multiple categories at once

**Key Endpoints**:
- `/resources` - Get resources for a category (with optional filters)
- `/categories` - List all available categories
- `/resources/by-categories` - Get resources for multiple categories

**Key Concepts**:

1. **Resource Structure** (in MongoDB):
   ```json
   {
     "_id": "DevOps",  // Category name is the document ID
     "courses": [
       {
         "title": "Docker Mastery",
         "url": "https://...",
         "description": "..."
       }
     ],
     "certifications": [...],
     "projects": [...]
   }
   ```

2. **Categories**: Match detected job categories from File Parsing service
   - Examples: DevOps, AI, Cloud Computing, Security, etc.

3. **Filtering**: Can request specific resource types:
   - `?courses=1` - Only courses
   - `?certifications=1` - Only certifications
   - `?projects=1` - Only projects
   - No params = All types

**How It Works**:
1. User uploads resume/JD
2. File Parsing detects job categories
3. Categories are stored in user profile
4. User visits Resources page
5. Frontend fetches user categories from Login Management
6. Frontend calls Resources service with categories
7. Resources service queries MongoDB for each category
8. Returns aggregated resources
9. Frontend displays resources organized by category

---

## 🔧 Shared Components

### 1. Authentication Middleware (`shared/auth_middleware.py`)

**Purpose**: Provides JWT token generation and validation for all services.

**Key Functions**:
- `generate_token(user_id, email)`: Creates JWT token
- `verify_token(token)`: Validates and decodes token
- `require_auth`: Decorator to protect endpoints
- `generate_service_token(service_name)`: Creates inter-service tokens

**How JWT Works**:
```
Token Structure (Base64 encoded):
Header: { "alg": "HS256", "typ": "JWT" }
Payload: { "user_id": "...", "email": "...", "exp": ..., "iat": ... }
Signature: HMACSHA256(header.payload, secret_key)
```

### 2. Service Client (`shared/service_client.py`)

**Purpose**: Provides secure HTTP client for inter-service communication.

**Key Features**:
- Automatic service token generation
- User token forwarding
- Error handling
- Timeout management

**How It Works**:
```python
service_client.post(
    'file-parsing',           # Target service
    '/api/files/upload/resume',  # Endpoint
    data={...},               # Request body
    user_token=token          # User's JWT token
)
```

Headers sent:
```
Authorization: Bearer <user_token>
X-Service-Token: <service_token>
X-Service-Name: frontend
Content-Type: application/json
```

### 3. Database Connection (`shared/database.py`)

**Purpose**: Centralized MongoDB connection management.

**Features**:
- Singleton pattern (one connection per application)
- Connection pooling
- Automatic reconnection
- Collection getters

---

## 📚 Key Technologies & Terms

### Authentication & Security

1. **OAuth 2.0**
   - Industry standard for authorization
   - Allows users to login with Google/GitHub without sharing passwords
   - Flow: Authorization Code Grant

2. **JWT (JSON Web Token)**
   - Compact, URL-safe token format
   - Contains user info and expiration
   - Signed with secret key (prevents tampering)
   - Stateless (no need to store on server)

3. **Session Management**
   - Flask sessions store data in cookies (encrypted)
   - Stores JWT token after login
   - Expires after 24 hours (configurable)

4. **File Security**
   - **Magic Numbers**: File signatures in file headers (e.g., PDF starts with `%PDF`)
   - **MIME Type**: Content-Type header (e.g., `application/pdf`)
   - **Path Traversal**: Attack technique using `../` to access files outside intended directory

### AI & Machine Learning

1. **Vector Embeddings**
   - Text converted to numerical vectors (arrays of numbers)
   - Similar texts have similar vectors
   - Used for semantic search and similarity matching
   - Model: `all-MiniLM-L6-v2` (384 dimensions)

2. **Vector Database (Pinecone)**
   - Specialized database for storing and querying vectors
   - Enables fast similarity search
   - Uses cosine similarity metric
   - Cloud-based, serverless

3. **LLM (Large Language Model)**
   - **Gemini 2.0 Flash**: Google's AI model
   - Generates human-like text
   - Used for question generation and answer analysis
   - Requires API key from Google

4. **Prompt Engineering**
   - Designing inputs to LLMs for desired outputs
   - Uses delimiters (---BEGIN---/---END---) to prevent injection
   - Structured prompts with clear instructions

### Databases

1. **MongoDB**
   - NoSQL document database
   - Stores JSON-like documents
   - Collections = Tables, Documents = Rows
   - Flexible schema (no fixed structure)

2. **Collections Used**:
   - `users`: User profiles, uploads, categories
   - `user_questions`: Generated questions per user
   - `resources`: Learning resources by category

### Architecture Patterns

1. **Microservices**
   - Each service is independent
   - Communicates via HTTP/REST APIs
   - Can be deployed separately
   - Own database/storage

2. **API Gateway Pattern**
   - Frontend acts as gateway/orchestrator
   - Single entry point for users
   - Routes to appropriate backend services

3. **Service-to-Service Authentication**
   - Services authenticate each other
   - Prevents unauthorized access between services
   - Uses service tokens

4. **Monorepo**
   - All services in one repository
   - Shared utilities in `shared/` folder
   - Easier code reuse

### Other Technologies

1. **Flask**
   - Lightweight Python web framework
   - Minimal and flexible
   - Good for microservices

2. **Jinja2**
   - Template engine for Flask
   - Renders HTML with dynamic content
   - Similar to Django templates

3. **REST API**
   - Representational State Transfer
   - HTTP methods: GET, POST, PUT, DELETE
   - Stateless communication

4. **CORS (Cross-Origin Resource Sharing)**
   - Allows browser to make requests to different domains
   - Configured in Flask services

---

## 🔀 Data Flow Diagrams

### Complete User Flow: Login → Upload → Practice

```
1. LOGIN FLOW
   User → Frontend → Login Management → Google OAuth
   Google OAuth → Login Management → MongoDB (create user)
   Login Management → Frontend (JWT token)
   Frontend → Session (store token)

2. UPLOAD FLOW
   User → Frontend → File Parsing (resume file)
   File Parsing → Security Validation → PyPDF2 (parse PDF)
   File Parsing → PII Removal → Cleaned Text
   File Parsing → sentence-transformers (generate embedding)
   File Parsing → Pinecone (store embedding)
   File Parsing → Login Management (record upload)
   File Parsing → Job Category Detection → Login Management (store categories)
   File Parsing → QA Generation (trigger question generation)
   QA Generation → Gemini AI → Generate Questions
   QA Generation → MongoDB (save questions)

3. PRACTICE FLOW
   User → Frontend → File Parsing → QA Generation (fetch questions)
   QA Generation → MongoDB (get user questions)
   QA Generation → Frontend (return questions)
   Frontend → Display questions to user
   User → Record audio → Frontend → Speech-to-Text
   Speech-to-Text → Google STT → Transcript
   Speech-to-Text → Frontend (transcript)
   User → Submit answer → Frontend → QA Generation
   QA Generation → Gemini AI (analyze answer)
   Gemini AI → QA Generation (feedback with score)
   QA Generation → Frontend (display feedback)

4. RESOURCES FLOW
   User → Frontend → Login Management (get user categories)
   Login Management → MongoDB (fetch user document)
   Login Management → Frontend (categories)
   Frontend → Resources Service (request resources for categories)
   Resources Service → MongoDB (fetch resources)
   Resources Service → Frontend (aggregated resources)
   Frontend → Display resources
```

---

## 📝 Summary for Presentation

### Key Points to Remember:

1. **Architecture**: 6 independent microservices communicating via REST APIs

2. **Authentication**: OAuth 2.0 (Google/GitHub) → JWT tokens → Session management

3. **File Processing**: Multi-layer security → PDF parsing → PII removal → Embeddings → Pinecone

4. **AI Integration**: Google Gemini generates questions and analyzes answers

5. **Data Storage**: 
   - MongoDB: User data, questions
   - Pinecone: Vector embeddings

6. **Service Communication**: ServiceClient with service tokens + user tokens

7. **User Isolation**: Each user's data is isolated by user_id in all services

---

## 🎓 Presentation Tips

1. **Start with the Big Picture**: Show the architecture diagram first

2. **Follow User Journey**: Explain services in the order users encounter them

3. **Emphasize Security**: Multi-layer file validation, JWT tokens, OAuth

4. **Highlight AI Features**: Gemini for questions and answer analysis

5. **Explain Why Microservices**: Scalability, maintainability, fault isolation

6. **Demo the Flow**: Show how data flows from upload → processing → questions → practice

7. **Mention Technologies**: Don't just list them, explain why they're used

---

**Good luck with your presentation!** 🚀


