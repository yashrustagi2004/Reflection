# Reflection - AI-Powered Interview Preparation Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.1.0-blue)
![Architecture](https://img.shields.io/badge/architecture-microservices-green)
![Kubernetes](https://img.shields.io/badge/platform-kubernetes-326CE5)

</div>

---

## Overview

Reflection is an AI-powered interview preparation platform that helps job seekers prepare for technical and behavioral interviews. The application analyzes resumes and job descriptions to generate personalized interview questions and provides real-time feedback on answers.

Built with a **cloud-native microservices architecture** running on Kubernetes, the platform ensures scalability, reliability, and seamless deployment through automated CI/CD pipelines.

### Key Features

**Application Features:**
- **Secure Authentication** - OAuth integration with Google and GitHub, JWT-based session management
- **Smart File Processing** - Multi-layer security validation for document uploads (MIME type, magic numbers, size limits)
- **AI-Powered Questions** - Generate tailored interview questions using Google Gemini AI
- **Intelligent Feedback** - Real-time answer analysis and improvement suggestions
- **Personalized Practice** - Context-aware questions based on resume and target job role
- **Progress Tracking** - Monitor interview preparation journey with persistent user data
- **Vector Embeddings** - Semantic storage using Pinecone for intelligent document retrieval
- **User-Specific Data** - Questions persist and are isolated per user in MongoDB

**Infrastructure Features:**
- **Kubernetes Orchestration** - Full containerized deployment with proper resource management
- **Service Mesh** - Microservices communication via Kubernetes ClusterIP Services
- **Persistent Storage** - MongoDB StatefulSets with PersistentVolumeClaims for data durability
- **Configuration Management** - Centralized ConfigMaps and Secrets for environment variables
- **Health Monitoring** - Liveness, readiness, and startup probes for all services
- **Auto-Scaling** - Horizontal Pod Autoscaler (HPA) based on CPU/memory utilization
- **Rolling Updates** - Zero-downtime deployments with configurable rollout strategies
- **CI/CD Pipeline** - Automated builds and deployments via Jenkins with git-based triggers

---

## Architecture

### Microservices Overview

The platform consists of six independent microservices orchestrated by Kubernetes:

| Service | Purpose | Port | Tech Stack |
|---------|---------|------|------------|
| **Frontend** | User interface & request orchestration | 5000 | Flask, Jinja2 Templates |
| **Login Management** | Authentication & user data management | 5001 | Flask, MongoDB, OAuth 2.0 |
| **File Parsing** | Secure file upload, parsing & vector embeddings | 5002 | Flask, PyPDF2, Pinecone, sentence-transformers |
| **QA Generation** | AI question generation & answer analysis | 5003 | Flask, LangChain, Google Gemini, MongoDB |
| **Resources** | Learning resource storage & retrieval | 5005 | Flask, MongoDB |
| **SpeechToText** | Voice-to-text transcription | 5006 | Flask, Speech Recognition APIs |

---

## Security Features

### Multi-Layer File Validation

- **File Extension Checking** - Whitelist-based validation
- **MIME Type Validation** - Content-type verification
- **Magic Number Verification** - Binary signature analysis using python-magic
- **Size Limits Enforcement** - Configurable file size restrictions
- **Path Traversal Prevention** - Filename sanitization and validation
- **Virus Scanning Ready** - Integration points for antivirus scanning

### Authentication & Authorization

- **JWT-Based Authentication** - Stateless token-based auth
- **OAuth 2.0 Integration** - Google and GitHub login
- **Service-to-Service Authentication** - Internal API security
- **Token Expiration Handling** - Automatic refresh mechanisms
- **Secure Session Management** - HttpOnly cookies, CSRF protection

### API Security

- **Input Validation** - Request payload sanitization
- **CORS Configuration** - Cross-origin resource sharing policies
- **Request Size Limits** - Protection against large payloads
- **Rate Limiting Ready** - Throttling mechanism integration points
- **Error Handling** - No sensitive information leakage
- **Security Headers** - X-Frame-Options, X-Content-Type-Options

### Infrastructure Security

- **Kubernetes Secrets** - Encrypted credential storage
- **Non-Root Containers** - All services run as non-root users
- **Security Contexts** - Dropped capabilities, read-only filesystems
- **Network Policies Ready** - Service mesh preparation
- **Resource Limits** - CPU/memory constraints to prevent DoS
- **Image Security** - Base image vulnerability scanning ready

---

## Configuration

### Environment Variables

Each service uses environment variables injected from Kubernetes ConfigMaps and Secrets:

**Secrets (mongodb-credentials):**
```yaml
MONGO_INITDB_ROOT_USERNAME: <base64-encoded>
MONGO_INITDB_ROOT_PASSWORD: <base64-encoded>
```

**Secrets (reflection-secrets):**
```yaml
GOOGLE_CLIENT_ID: <base64-encoded>
GOOGLE_CLIENT_SECRET: <base64-encoded>
GITHUB_CLIENT_ID: <base64-encoded>
GITHUB_CLIENT_SECRET: <base64-encoded>
GOOGLE_API_KEY: <base64-encoded>
PINECONE_API_KEY: <base64-encoded>
JWT_SECRET_KEY: <base64-encoded>
FLASK_SECRET_KEY: <base64-encoded>
```
---

## CI/CD Pipeline

### Jenkins Pipeline Features

**Automated Change Detection:**
- Git diff-based service detection (only rebuild changed services)
- ConfigMap change detection with automatic service restarts
- Database name change detection with data migration

**Build & Deploy Stages:**
1. **Checkout** - Fetch latest code from GitHub
2. **Detect Changes** - Identify modified services
3. **Apply Configuration** - Update ConfigMaps, handle database changes
4. **Build Services** - Docker image build with commit SHA tagging
5. **Deploy Services** - Kubernetes deployment with rolling updates
6. **Post-Deploy** - Restart port-forwards, health checks

**Credential Management:**
- `kubeconfig-file` - Kubernetes cluster access
- `db-credentials` - MongoDB admin credentials for data population

**Pipeline Trigger:**
- Automatic builds on git push to `refactorCodeBase` branch
- Manual trigger via Jenkins UI

### Jenkinsfile Structure

```groovy
pipeline {
  agent any
  environment {
    KUBECONFIG_CRED = 'kubeconfig-file'
    DB_CREDENTIALS = 'db-credentials'
    NAMESPACE = 'reflection'
    IMAGE_TAG = "${env.GIT_COMMIT}"
  }
  stages {
    // Checkout, detect changes, build, deploy
  }
}
```
---

## Local Installation and Setup

### Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.8+** (Python 3.12 or 3.13 recommended for QA Generation service)
- **MongoDB** (running locally on port 27017)
- **Git** (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yashrustagi2004/Reflection.git
cd Reflection/services
```

### Step 2: Start MongoDB

Ensure MongoDB is running on your system:

```bash
# Check if MongoDB is running
sudo systemctl status mongod

# If not running, start it
sudo systemctl start mongod
```

### Step 3: Configure Environment Variables

Create a `.env` file from the example template and add your API keys:

```bash
cd services
cp .env.example .env
```

Edit the `.env` file and add your credentials:

### Step 4: Install Dependencies and Run Services

You need to run **6 microservices** in separate terminal windows. Each service requires its own virtual environment.

#### Terminal 1: Frontend Service (Port 5000)

```bash
cd services/frontend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

#### Terminal 2: Login Management Service (Port 5001)

```bash
cd services/login-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

#### Terminal 3: File Parsing Service (Port 5002)

```bash
cd services/file-parsing
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

#### Terminal 4: Question-Answer Generation Service (Port 5003)

**Important:** Use Python 3.12 or 3.13 for this service due to LangChain dependencies.

```bash
cd services/question-answer-generation
python3.12 -m venv venv  # or python3.13
source venv/bin/activate
pip install -r requirements.txt
python3.12 app.py
```

#### Terminal 5: Speech-to-Text Service (Port 5004)

```bash
cd services/SpeechToText
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

#### Terminal 6: Resources Service (Port 5005)

```bash
cd services/resources
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Step 5: Access the Application

Once all services are running, open your browser and navigate to:

```
http://localhost:5000
```

### Verify Services are Running

Check that all services are healthy:

```bash
# Frontend
curl http://localhost:5000/health

# Login Management
curl http://localhost:5001/health

# File Parsing
curl http://localhost:5002/health

# QA Generation
curl http://localhost:5003/health

# Resources
curl http://localhost:5005/health
```

---