# Question-Answer Generation Service API Documentation

## Overview

The Question-Answer Generation Service is the core intelligence engine of the AI Interview Platform. It generates customized interview questions based on uploaded resumes and job descriptions, creates realistic interview scenarios, and provides intelligent question sequencing for comprehensive interview preparation.

**Base URL**: `http://localhost:5003`  
**Port**: 5003  
**Technology**: Flask (Python) + AI/ML Libraries  
**Authentication**: JWT tokens (validated via Login Management Service)  
**AI Engine**: Natural Language Processing + Machine Learning Models

## Core Responsibilities

- **Question Generation**: Create relevant interview questions based on user content
- **Content Analysis**: Analyze resumes and job descriptions for question targeting
- **Interview Scenarios**: Generate realistic interview workflows and progressions
- **Difficulty Scaling**: Adjust question complexity based on experience level
- **Question Categories**: Technical, behavioral, situational, and company-specific questions
- **Personalization**: Tailor questions to specific skills and experience

---

## Question Generation Flow

### Generation Process Diagram
```
1. User requests questions → Frontend Service
2. Frontend → Q&A Generation: POST /api/generate/questions
3. Q&A Generation → File Parsing: GET file content and analysis
4. Q&A Generation: Analyze resume + job description match
5. Q&A Generation: Generate questions using AI models
6. Q&A Generation: Categorize and sequence questions
7. Q&A Generation: Return structured question sets
8. User receives personalized interview questions
```

### AI Processing Pipeline
```
1. Content Preprocessing: Clean and structure resume/JD text
2. Skill Extraction: Identify technical and soft skills
3. Experience Analysis: Determine seniority and expertise level  
4. Job Matching: Align resume experience with job requirements
5. Question Template Selection: Choose appropriate question types
6. Dynamic Generation: Create personalized questions using AI
7. Quality Validation: Ensure question relevance and clarity
8. Sequencing: Order questions for optimal interview flow
```

---

## API Endpoints

### Health Check

#### GET /health
**Description**: Service health check and AI model status  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "service": "question-answer-generation",
  "status": "healthy",
  "ai_models": {
    "question_generator": {
      "loaded": true,
      "version": "v2.1.0",
      "last_update": "2024-01-10T08:00:00Z"
    },
    "content_analyzer": {
      "loaded": true,
      "performance": "optimal"
    }
  },
  "generation_queue": {
    "pending_requests": 0,
    "average_processing_time": 3.2
  }
}
```
**Purpose**: Monitor service health and AI model availability

---

### Question Generation

#### POST /api/generate/questions
**Description**: Generate personalized interview questions based on uploaded content  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "resume_file": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
  "job_description_file": "jd_507f1f77bcf86cd799439011_1634567890456.pdf",
  "preferences": {
    "question_count": 15,
    "difficulty_level": "intermediate",
    "question_types": ["technical", "behavioral", "situational"],
    "focus_areas": ["backend_development", "system_design", "leadership"],
    "interview_duration": 60
  }
}
```

**Response (Success)**:
```json
{
  "success": true,
  "message": "Interview questions generated successfully",
  "generation_metadata": {
    "processing_time": 4.2,
    "content_match_score": 0.87,
    "generated_at": "2024-01-15T10:30:00Z",
    "model_version": "v2.1.0"
  },
  "content_analysis": {
    "resume_analysis": {
      "experience_level": "Senior (6+ years)",
      "primary_skills": ["Python", "Django", "PostgreSQL", "AWS"],
      "domain_expertise": ["Web Development", "Backend Systems", "Team Leadership"],
      "skill_match_percentage": 85
    },
    "job_requirements": {
      "required_skills": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
      "preferred_experience": "5+ years",
      "seniority_level": "Senior",
      "team_size": "3-5 developers"
    },
    "compatibility_score": 87
  },
  "question_sets": {
    "technical_questions": {
      "category": "Technical Skills",
      "count": 8,
      "estimated_time": 35,
      "questions": [
        {
          "id": "tech_001",
          "question": "Describe your experience with Django ORM. How would you optimize a query that's causing performance issues in a high-traffic application?",
          "type": "technical_deep_dive",
          "difficulty": "intermediate",
          "focus_area": "backend_development",
          "expected_duration": 5,
          "follow_up_questions": [
            "What tools would you use to identify the performance bottleneck?",
            "How would you implement database indexing for this scenario?"
          ],
          "evaluation_criteria": [
            "Understanding of ORM concepts",
            "Knowledge of query optimization",
            "Practical problem-solving approach"
          ]
        },
        {
          "id": "tech_002", 
          "question": "You're designing a REST API for a microservices architecture. Walk me through how you would handle authentication, rate limiting, and error handling across services.",
          "type": "system_design",
          "difficulty": "advanced",
          "focus_area": "system_architecture",
          "expected_duration": 8,
          "follow_up_questions": [
            "How would you implement JWT token validation across services?",
            "What strategies would you use for handling service failures?"
          ],
          "evaluation_criteria": [
            "System design thinking",
            "Security considerations", 
            "Scalability awareness"
          ]
        }
      ]
    },
    "behavioral_questions": {
      "category": "Behavioral & Leadership",
      "count": 4,
      "estimated_time": 15,
      "questions": [
        {
          "id": "behav_001",
          "question": "Tell me about a time when you had to lead a team through a challenging technical project. What was your approach, and what was the outcome?",
          "type": "behavioral_leadership",
          "difficulty": "intermediate",
          "focus_area": "leadership",
          "expected_duration": 4,
          "follow_up_questions": [
            "How did you handle team members who disagreed with your technical decisions?",
            "What would you do differently if you could repeat that project?"
          ],
          "evaluation_criteria": [
            "Leadership style",
            "Conflict resolution",
            "Team management skills",
            "Learning from experience"
          ]
        }
      ]
    },
    "situational_questions": {
      "category": "Problem Solving & Scenarios",
      "count": 3,
      "estimated_time": 10,
      "questions": [
        {
          "id": "sit_001",
          "question": "Your production application is experiencing 500% increased traffic, and the database is becoming a bottleneck. You have 2 hours to implement a solution. Walk me through your approach.",
          "type": "crisis_management",
          "difficulty": "advanced", 
          "focus_area": "problem_solving",
          "expected_duration": 3,
          "scenario_context": {
            "urgency": "high",
            "resources": "limited",
            "impact": "customer-facing"
          },
          "evaluation_criteria": [
            "Crisis management skills",
            "Prioritization under pressure",
            "Technical decision making",
            "Communication during incidents"
          ]
        }
      ]
    }
  },
  "interview_structure": {
    "recommended_sequence": [
      {
        "phase": "warm_up",
        "duration": 5,
        "questions": ["behav_001"],
        "purpose": "Build rapport and assess communication"
      },
      {
        "phase": "technical_core",
        "duration": 35,
        "questions": ["tech_001", "tech_002"],
        "purpose": "Evaluate core technical competency"
      },
      {
        "phase": "problem_solving", 
        "duration": 15,
        "questions": ["sit_001", "tech_003"],
        "purpose": "Assess analytical and crisis management skills"
      },
      {
        "phase": "closing",
        "duration": 5,
        "questions": ["behav_002"],
        "purpose": "Understand motivation and culture fit"
      }
    ],
    "total_estimated_time": 60,
    "flexibility_notes": [
      "Adjust technical depth based on candidate responses",
      "Skip advanced questions if basic concepts aren't solid",
      "Extend problem-solving phase if candidate shows strong analytical skills"
    ]
  }
}
```

**Processing Logic**:
1. Retrieve and analyze uploaded resume and job description content
2. Extract skills, experience level, and domain expertise
3. Calculate compatibility score between resume and job requirements
4. Select appropriate question templates based on analysis
5. Generate personalized questions using AI models
6. Categorize questions by type and difficulty
7. Create optimal interview sequence and timing
8. Return structured question sets with evaluation criteria

**Purpose**: Provide comprehensive, personalized interview preparation materials

---

### Quick Question Generation

#### POST /api/generate/quick
**Description**: Generate a smaller set of questions for rapid interview prep  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "content_type": "resume_only",
  "resume_file": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
  "quick_preferences": {
    "question_count": 5,
    "time_limit": 15,
    "focus": "technical_basics"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Quick questions generated successfully",
  "generation_time": 1.8,
  "questions": [
    {
      "id": "quick_001",
      "question": "Explain the difference between Django's select_related() and prefetch_related() methods.",
      "type": "technical_concept",
      "difficulty": "basic",
      "expected_duration": 3,
      "key_points": [
        "Understanding of Django ORM",
        "Database query optimization",
        "Performance considerations"
      ]
    },
    {
      "id": "quick_002",
      "question": "How do you handle database migrations in a production Django application?",
      "type": "practical_knowledge",
      "difficulty": "intermediate", 
      "expected_duration": 3,
      "key_points": [
        "Migration strategies",
        "Production deployment",
        "Risk mitigation"
      ]
    }
  ],
  "total_time": 15,
  "preparation_tips": [
    "Focus on Django ORM concepts and best practices",
    "Review database optimization techniques",
    "Prepare examples from your actual project experience"
  ]
}
```
**Purpose**: Quick interview preparation with focused question sets

---

### Content-Based Question Generation

#### POST /api/generate/by_content
**Description**: Generate questions based on specific content areas or skills  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "target_skills": ["Python", "Django", "PostgreSQL", "Docker"],
  "experience_level": "senior",
  "question_types": ["technical", "practical"],
  "scenario": "backend_engineer_interview",
  "company_context": {
    "industry": "fintech",
    "team_size": "15-20 engineers", 
    "tech_stack": ["Python", "Django", "PostgreSQL", "Redis", "AWS"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "targeted_questions": [
    {
      "id": "target_001",
      "question": "In a fintech application handling financial transactions, how would you ensure data consistency and ACID compliance when using Django with PostgreSQL?",
      "type": "domain_specific_technical",
      "difficulty": "advanced",
      "context": "fintech_backend",
      "skills_assessed": ["Django", "PostgreSQL", "Data Integrity", "Financial Systems"],
      "follow_up_questions": [
        "How would you implement database transactions for multi-step financial operations?",
        "What monitoring would you put in place for transaction failures?"
      ]
    }
  ],
  "industry_context": {
    "regulatory_considerations": "Financial data handling and compliance",
    "performance_requirements": "High availability and low latency",
    "security_focus": "Data encryption and audit trails"
  }
}
```
**Purpose**: Generate highly targeted questions for specific roles and industries

---

### Interview Templates

#### GET /api/templates
**Description**: Get available interview templates and question categories  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "templates": {
    "technical_interview": {
      "name": "Technical Interview",
      "duration": "45-60 minutes",
      "categories": ["coding", "system_design", "algorithms", "debugging"],
      "difficulty_levels": ["junior", "mid", "senior", "staff"],
      "description": "Comprehensive technical assessment covering programming skills and system design"
    },
    "behavioral_interview": {
      "name": "Behavioral Interview", 
      "duration": "30-45 minutes",
      "categories": ["leadership", "teamwork", "problem_solving", "communication"],
      "focus_areas": ["past_experience", "situational_judgment", "cultural_fit"],
      "description": "Evaluate soft skills, leadership potential, and cultural alignment"
    },
    "full_stack_interview": {
      "name": "Full Stack Developer Interview",
      "duration": "60-90 minutes",
      "categories": ["frontend", "backend", "database", "deployment", "testing"],
      "technology_focus": ["React", "Node.js", "Python", "AWS", "Docker"],
      "description": "Comprehensive evaluation for full-stack development roles"
    }
  },
  "question_types": {
    "technical": {
      "coding_problems": "Write and debug code in real-time",
      "system_design": "Design scalable systems and architectures",
      "concept_explanation": "Explain technical concepts and best practices",
      "debugging": "Identify and fix issues in existing code"
    },
    "behavioral": {
      "experience_based": "Questions about past projects and decisions",
      "situational": "Hypothetical scenarios and problem-solving",
      "leadership": "Team management and mentoring experiences",
      "learning": "Adaptability and continuous learning examples"
    }
  }
}
```
**Purpose**: Provide available interview formats and question categories

#### POST /api/templates/apply
**Description**: Apply a specific interview template to generate questions  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "template": "technical_interview",
  "user_profile": {
    "resume_file": "resume_507f1f77bcf86cd799439011_1634567890123.pdf",
    "experience_level": "senior",
    "target_role": "backend_engineer"
  },
  "customization": {
    "focus_categories": ["system_design", "coding", "debugging"],
    "exclude_topics": ["frontend", "mobile"],
    "time_constraint": 45
  }
}
```

**Response**:
```json
{
  "success": true,
  "applied_template": "technical_interview",
  "customized_questions": [
    {
      "category": "system_design",
      "questions": [...],
      "estimated_time": 20
    },
    {
      "category": "coding",
      "questions": [...], 
      "estimated_time": 15
    },
    {
      "category": "debugging",
      "questions": [...],
      "estimated_time": 10
    }
  ],
  "total_time": 45,
  "interview_notes": "Adjusted for senior backend engineer with focus on system architecture and debugging skills"
}
```
**Purpose**: Apply structured interview templates with personalization

---

### Question Analytics

#### GET /api/analytics/questions/{question_id}
**Description**: Get analytics and performance data for specific questions  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "question_analytics": {
    "question_id": "tech_001",
    "question_text": "Describe your experience with Django ORM...",
    "usage_stats": {
      "times_generated": 147,
      "average_difficulty_rating": 3.2,
      "success_rate": 0.68
    },
    "performance_insights": {
      "common_strong_responses": [
        "Detailed ORM optimization examples",
        "Practical query performance experience",
        "Understanding of database relationships"
      ],
      "common_weak_areas": [
        "Limited knowledge of query analysis tools",
        "Superficial understanding of indexing",
        "Lack of production performance examples"
      ]
    },
    "improvement_suggestions": [
      "Add follow-up about specific optimization tools",
      "Include database profiling questions",
      "Ask for concrete performance metrics"
    ]
  }
}
```
**Purpose**: Provide insights on question effectiveness and candidate performance patterns

---

## AI Models & Processing

### Question Generation Models

#### Content Analysis Engine
```python
class ContentAnalyzer:
    """
    Analyze resume and job description content for question generation
    - Skill extraction and categorization
    - Experience level assessment  
    - Domain expertise identification
    - Job-resume compatibility scoring
    """
    
    def analyze_content(self, resume_text, job_description_text):
        return {
            'skills': extracted_skills,
            'experience_level': calculated_level,
            'compatibility_score': match_percentage
        }
```

#### Question Generator
```python
class QuestionGenerator:
    """
    Generate personalized interview questions using AI models
    - Template-based generation with dynamic content
    - Difficulty scaling based on experience
    - Context-aware question creation
    - Multi-category question balancing
    """
    
    def generate_questions(self, analysis_data, preferences):
        return structured_question_sets
```

### Natural Language Processing

#### Skill Extraction
- **Technical Skills**: Programming languages, frameworks, tools
- **Domain Skills**: Industry-specific knowledge and experience
- **Soft Skills**: Leadership, communication, problem-solving
- **Certifications**: Professional certifications and qualifications

#### Experience Level Detection
```python
EXPERIENCE_LEVELS = {
    'junior': '0-2 years',
    'mid': '2-5 years', 
    'senior': '5-8 years',
    'staff': '8+ years',
    'principal': '10+ years'
}
```

#### Content Matching Algorithm
```python
def calculate_compatibility(resume_skills, job_requirements):
    """
    Calculate how well a resume matches job requirements
    - Required skills coverage
    - Experience level alignment
    - Domain expertise match
    - Additional qualifications
    """
    return compatibility_score
```

---

## Question Categories & Types

### Technical Questions

#### Coding & Programming
- **Algorithm Problems**: Data structures, algorithms, complexity analysis
- **Code Review**: Debug existing code, identify improvements
- **Best Practices**: Design patterns, code organization, testing
- **Language Specific**: Framework-specific knowledge and usage

#### System Design
- **Architecture**: Design scalable systems and microservices
- **Database Design**: Schema design, optimization, scaling
- **Performance**: Load balancing, caching, optimization strategies
- **Security**: Authentication, authorization, data protection

### Behavioral Questions

#### Experience-Based
- **Project Leadership**: Leading teams and technical initiatives
- **Problem Solving**: Overcoming technical and interpersonal challenges
- **Learning & Growth**: Adapting to new technologies and requirements
- **Collaboration**: Working with cross-functional teams

#### Situational Judgment
- **Crisis Management**: Handling production issues and emergencies
- **Technical Decisions**: Making architecture and technology choices
- **Team Dynamics**: Managing conflicts and building consensus
- **Time Management**: Prioritizing tasks and meeting deadlines

### Industry-Specific Questions

#### Domain Expertise
- **Fintech**: Regulatory compliance, security, transaction processing
- **Healthcare**: HIPAA compliance, data privacy, reliability
- **E-commerce**: Scalability, payment processing, user experience
- **Gaming**: Real-time systems, performance optimization, user engagement

---

## Error Handling

### Generation Errors
```json
{
  "success": false,
  "error": "Insufficient content for question generation",
  "error_code": "CONTENT_INSUFFICIENT",
  "details": {
    "required_content_length": 500,
    "received_content_length": 123,
    "suggestions": [
      "Upload a more detailed resume",
      "Provide a complete job description",
      "Use the quick generation mode for limited content"
    ]
  }
}
```

### AI Model Errors
```json
{
  "success": false,
  "error": "AI model temporarily unavailable",
  "error_code": "MODEL_UNAVAILABLE",
  "details": {
    "model_status": "loading",
    "estimated_wait_time": "2-3 minutes",
    "fallback_available": true
  }
}
```

### Content Analysis Errors
```json
{
  "success": false,
  "error": "Content analysis failed",
  "error_code": "ANALYSIS_ERROR",
  "details": {
    "analysis_stage": "skill_extraction",
    "content_type": "resume",
    "technical_details": "Unable to parse PDF content structure"
  }
}
```

---

## Performance & Optimization

### Generation Speed
- **Quick Questions**: 1-3 seconds average processing time
- **Full Question Set**: 3-8 seconds average processing time  
- **Complex Analysis**: 5-15 seconds for comprehensive generation
- **Caching**: Frequently used templates and patterns cached

### Model Performance
- **Accuracy**: 85%+ relevance rating for generated questions
- **Diversity**: Minimal question overlap across generations
- **Personalization**: 90%+ of questions tailored to specific content
- **Quality**: Human review and validation of question templates

### Scalability Features
- **Queue Management**: Handle multiple concurrent generation requests
- **Resource Scaling**: Auto-scale AI model instances based on load
- **Fallback Systems**: Backup question generation methods
- **Performance Monitoring**: Track generation times and success rates

---

## Configuration

### Environment Variables
```bash
# AI Model Configuration
AI_MODEL_PATH=/models/question_generator
MODEL_VERSION=v2.1.0
MODEL_CACHE_SIZE=1GB
GENERATION_TIMEOUT=30

# Content Analysis
NLP_MODEL_PATH=/models/content_analyzer
SKILL_DATABASE_PATH=/data/skills.json
EXPERIENCE_RULES_PATH=/config/experience_rules.yaml

# Question Templates
TEMPLATE_DIRECTORY=/templates
CUSTOM_TEMPLATES_ENABLED=true
TEMPLATE_CACHE_TTL=3600

# Performance Settings
MAX_CONCURRENT_GENERATIONS=10
GENERATION_QUEUE_SIZE=100
CACHE_ENABLED=true
CACHE_TTL_SECONDS=1800

# Service Integration
FILE_PARSING_URL=http://localhost:5002
LOGIN_MANAGEMENT_URL=http://localhost:5001
SERVICE_AUTH_TOKEN=your-service-token
```

### AI Model Configuration
```yaml
question_generator:
  model_type: "transformer"
  max_tokens: 2048
  temperature: 0.7
  top_p: 0.9
  
content_analyzer:
  skill_extraction:
    confidence_threshold: 0.75
    max_skills_per_category: 10
  
  experience_detection:
    keyword_weights:
      "senior": 2.0
      "lead": 1.8
      "architect": 2.2
      "junior": 0.5
```

---

## Development Notes

### Testing Question Generation
```bash
# Test basic question generation
curl -X POST http://localhost:5003/api/generate/questions \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_file": "test_resume.pdf",
    "job_description_file": "test_jd.pdf",
    "preferences": {
      "question_count": 5,
      "difficulty_level": "intermediate"
    }
  }'

# Test quick generation
curl -X POST http://localhost:5003/api/generate/quick \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "resume_only",
    "resume_file": "test_resume.pdf",
    "quick_preferences": {
      "question_count": 3,
      "time_limit": 10
    }
  }'
```

### AI Model Setup
```bash
# Install required ML libraries
pip install transformers torch nltk spacy
pip install scikit-learn pandas numpy

# Download NLP models
python -m spacy download en_core_web_sm
python -m nltk.downloader punkt stopwords

# Set up model directories
mkdir -p /models/{question_generator,content_analyzer}
mkdir -p /templates/{technical,behavioral,situational}
```

### Question Template Development
```python
# Example question template structure
QUESTION_TEMPLATE = {
    "id": "tech_django_orm_{difficulty}",
    "template": "Based on your {experience_level} experience with {skill}, {question_prompt}",
    "variables": {
        "skill": ["Django", "Django ORM"],
        "experience_level": ["junior", "senior"],
        "question_prompt": [
            "explain how you would optimize database queries",
            "describe how you handle complex relationships"
        ]
    },
    "difficulty_scaling": {
        "junior": "basic concepts and syntax",
        "senior": "performance optimization and best practices"
    }
}
```