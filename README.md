# Reflection - AI-Powered Interview Preparation Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Architecture](https://img.shields.io/badge/architecture-microservices-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**An intelligent interview preparation platform using microservices architecture**

[Quick Start](#-quick-start) • [Documentation](#-documentation) • [Features](#-features) • [Architecture](#-architecture)

</div>

---

## 🎯 Overview

Reflection is an AI-powered interview preparation platform that helps job seekers prepare for technical and behavioral interviews. The application analyzes resumes and job descriptions to generate personalized interview questions and provides real-time feedback on answers.

### ✨ Key Features

- 🔐 **Secure Authentication** - OAuth integration with Google and GitHub
- 📄 **Smart File Processing** - Multi-layer security validation for document uploads
- 🤖 **AI-Powered Questions** - Generate tailored interview questions using Google Gemini
- 💡 **Intelligent Feedback** - Real-time answer analysis and improvement suggestions
- 🎯 **Personalized Practice** - Context-aware questions based on your resume and target role
- 📊 **Progress Tracking** - Monitor your interview preparation journey

---

### Service Responsibilities

| Service | Purpose | Tech Stack |
|---------|---------|------------|
| **Frontend** | User interface & orchestration | Flask, Jinja2 |
| **Login Management** | Authentication & user data | Flask, MongoDB, OAuth |
| **File Parsing** | Secure upload & document parsing | Flask, PyPDF2, python-magic |
| **Q&A Generation** | Interview question generation | Flask, LangChain, Gemini |
| **Answer Analysis** | Answer evaluation & feedback | Flask, LangChain, Gemini |
| **Resources** | Vector storage & retrieval | Flask, Pinecone |

---

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Git

### Installation (5 minutes)

```bash
# 1. Clone the repository
git clone <repository-url>
cd Reflection

# 2. Configure environment
cp services/.env.example services/.env
# Edit services/.env with your API keys

# 3. Start MongoDB
docker run -d -p 27017:27017 --name reflection-mongodb mongo:7.0

# 4. Start all services
chmod +x start-services.sh
./start-services.sh

# 5. Open browser
open http://localhost:5000
```

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md).

---

## Security Features

### Multi-Layer File Validation

- ✅ File extension checking
- ✅ MIME type validation
- ✅ Magic number verification
- ✅ Size limits enforcement
- ✅ Path traversal prevention
- ✅ Filename sanitization

### Authentication & Authorization

- ✅ JWT-based authentication
- ✅ OAuth 2.0 integration
- ✅ Service-to-service authentication
- ✅ Token expiration handling
- ✅ Secure session management

### API Security

- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ Request size limits
- ✅ Error handling without information leakage
- ✅ Secure coding practices

---

## Technology Stack

### Backend
- **Framework:** Flask 3.0
- **Database:** MongoDB 7.0
- **Vector DB:** Pinecone
- **AI/ML:** Google Gemini, LangChain
- **Authentication:** OAuth 2.0, JWT

### Infrastructure
- **Containerization:** 
- **Orchestration:** 
- **Architecture:** Microservices (Monorepo)

### Security
- **File Validation:** python-magic
- **Password Hashing:** bcrypt
- **Token Management:** PyJWT

---

## Project Structure

```
Reflection/
├── services/                      # Microservices monorepo
│   ├── shared/                   # Shared utilities
│   │   ├── auth_middleware.py   # JWT authentication
│   │   ├── service_client.py    # Inter-service communication
│   │   └── database.py          # Database connection
│   │
│   ├── frontend/                # Web interface
│   ├── login-management/        # Authentication service
│   ├── file-parsing/            # File processing service
│   ├── question-answer-generation/  # AI question generation
│   ├── answer-analysis/         # Answer evaluation service
│   └── resources/               # Vector storage service
│
├── start-services.sh            # Startup script
├── stop-services.sh             # Shutdown script
```

---

## Configuration

### Environment Variables

Copy `services/.env.example` to `services/.env` and configure:

---

## 🧪 Testing

### Manual Testing

```bash
# Test service health
curl http://localhost:5000/health
curl http://localhost:5001/health
curl http://localhost:5002/health

# Test file upload
curl -X POST http://localhost:5002/api/files/upload/resume \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

### Automated Testing (TODO)

```bash
# Run tests
pytest services/login-management/tests
pytest services/file-parsing/tests
```

---

## Service Endpoints

| Service | Health Check | Port |
|---------|--------------|------|
| Frontend | http://localhost:5000/health | 5000 |
| Login Management | http://localhost:5001/health | 5001 |
| File Parsing | http://localhost:5002/health | 5002 |
| Q&A Generation | http://localhost:5003/health | 5003 |
| Answer Analysis | http://localhost:5004/health | 5004 |
| Resources | http://localhost:5005/health | 5005 |

---

## Development

### Running a Single Service

```bash
cd services/<service-name>
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Adding a New Service

1. Create service directory
2. Create `app.py` with Flask app
3. Add `requirements.txt`
4. Import shared utilities
5. Update `docker-compose.yml`
6. Document API endpoints

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Write docstrings for functions
- Keep functions small and focused

---

## 🌐 Deployment

### Production Deployment

1. Use managed MongoDB (MongoDB Atlas)
2. Set up reverse proxy (Nginx)
3. Enable HTTPS (Let's Encrypt)
4. Configure environment variables
6. Implement CI/CD pipeline

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Changelog

### Version 2.0.0 (October 2025)
- ✨ Migrated from monolithic to microservices architecture
- 🔒 Enhanced security with multi-layer file validation
- 🚀 Improved scalability with independent services
- 📚 Comprehensive documentation
- 🐳 Docker support

### Version 1.0.0 (Previous)
- Initial monolithic implementation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

- 📖 Docs: [Documentation](/docs/api/)

---
