# Resources Service API Documentation

## Overview

The Resources Service manages document storage, retrieval, and organization for the AI Interview Platform. It provides secure access to user-uploaded files, maintains document metadata, handles file versioning, and offers advanced document search capabilities. This service acts as the central repository for all interview preparation materials.

**Base URL**: `http://localhost:5005`  
**Port**: 5005  
**Technology**: Flask (Python) + Document Management  
**Authentication**: JWT tokens (validated via Login Management Service)  
**Storage**: Secure file system with organized directory structure

## Core Responsibilities

- **Document Repository**: Secure storage and organization of user documents
- **File Metadata Management**: Track document information, versions, and access patterns
- **Search & Discovery**: Advanced document search and content matching
- **Access Control**: User-based permissions and document ownership validation
- **Version Management**: Handle document updates and maintain version history
- **Integration Support**: Provide document access for other services

---

## Document Management Flow

### Document Access Flow
```
1. User/Service requests document → Frontend Service
2. Frontend → Resources: GET /api/documents/{document_id}
3. Resources: Validate user permissions and document ownership
4. Resources: Retrieve document metadata and content location
5. Resources: Stream document content or provide access URL
6. Resources: Log access and update usage statistics
7. User receives document content or access information
```

### Document Organization Structure
```
/documents/
├── users/{user_id}/
│   ├── resumes/
│   │   ├── current/
│   │   │   └── resume_latest.pdf
│   │   └── versions/
│   │       ├── resume_v1_timestamp.pdf
│   │       └── resume_v2_timestamp.pdf
│   ├── job_descriptions/
│   │   ├── active/
│   │   │   └── current_jd.pdf
│   │   └── archive/
│   │       └── old_jds/
│   └── interview_materials/
│       ├── questions/
│       └── analyses/
└── shared/
    ├── templates/
    └── resources/
```

---

## API Endpoints

### Health Check

#### GET /health
**Description**: Service health check and storage system status  
**Authentication**: None  
**Response**:
```json
{
  "success": true,
  "service": "resources",
  "status": "healthy",
  "storage_system": {
    "available": true,
    "free_space_gb": 125.7,
    "total_documents": 1542,
    "active_users": 89
  },
  "search_index": {
    "status": "online",
    "indexed_documents": 1538,
    "last_index_update": "2024-01-15T09:30:00Z"
  },
  "performance_metrics": {
    "average_response_time": 0.8,
    "documents_served_today": 245
  }
}
```
**Purpose**: Monitor service health and storage capacity

---

### Document Retrieval

#### GET /api/documents/{document_id}
**Description**: Retrieve specific document by ID with metadata  
**Authentication**: Required (JWT token + document ownership validation)  
**Parameters**:
- `document_id`: Unique document identifier
- `include_content`: Whether to include document content (`true`/`false`) - optional
- `version`: Specific version to retrieve (default: latest) - optional

**Response (Success)**:
```json
{
  "success": true,
  "document": {
    "id": "doc_507f1f77bcf86cd799439015",
    "user_id": "507f1f77bcf86cd799439011",
    "type": "resume",
    "filename": "john_doe_resume_v3.pdf",
    "original_name": "John_Doe_Resume_Updated.pdf",
    "title": "John Doe - Senior Software Engineer Resume",
    "description": "Updated resume with latest project experience",
    "file_size": 1048576,
    "mime_type": "application/pdf",
    "created_at": "2024-01-10T14:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "last_accessed": "2024-01-15T16:45:00Z",
    "access_count": 12,
    "version": 3,
    "status": "active",
    "tags": ["resume", "software_engineer", "python", "backend"],
    "metadata": {
      "content_extracted": true,
      "content_length": 2456,
      "language": "en",
      "page_count": 2,
      "key_skills": ["Python", "Django", "PostgreSQL", "AWS"],
      "experience_years": 6,
      "education_level": "Bachelor's Degree"
    },
    "file_path": "/documents/users/507f1f77bcf86cd799439011/resumes/current/john_doe_resume_v3.pdf",
    "download_url": "/api/documents/doc_507f1f77bcf86cd799439015/download",
    "preview_available": true
  },
  "content": {
    "text_preview": "John Doe\nSenior Software Engineer\nemail@example.com | (555) 123-4567\n\nPROFESSIONAL SUMMARY\nExperienced software engineer with 6+ years...",
    "structured_content": {
      "sections": ["personal_info", "summary", "experience", "education", "skills"],
      "contact_info": {
        "name": "John Doe",
        "email": "email@example.com",
        "phone": "(555) 123-4567"
      },
      "skills": {
        "technical": ["Python", "Django", "PostgreSQL", "Docker", "AWS"],
        "soft": ["Leadership", "Team Management", "Problem Solving"]
      }
    }
  }
}
```

**Response (Not Found)**:
```json
{
  "success": false,
  "error": "Document not found or access denied",
  "error_code": "DOCUMENT_NOT_FOUND",
  "details": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "possible_reasons": [
      "Document does not exist",
      "User does not have access permissions",
      "Document has been deleted"
    ]
  }
}
```

**Security**: Document ownership validated - users can only access their own documents

**Purpose**: Provide secure access to user documents with comprehensive metadata

---

### Document Listing

#### GET /api/documents
**Description**: List user's documents with filtering and pagination  
**Authentication**: Required (JWT token)  
**Parameters**:
- `type`: Filter by document type (`resume`, `job_description`, `interview_material`) - optional
- `status`: Filter by status (`active`, `archived`, `deleted`) - optional  
- `tags`: Filter by tags (comma-separated) - optional
- `search`: Search in document titles and content - optional
- `sort`: Sort order (`created_desc`, `created_asc`, `updated_desc`, `name_asc`) - optional
- `limit`: Number of documents per page (default: 20, max: 100) - optional
- `offset`: Number of documents to skip (default: 0) - optional

**Response**:
```json
{
  "success": true,
  "documents": [
    {
      "id": "doc_507f1f77bcf86cd799439015",
      "type": "resume",
      "filename": "john_doe_resume_v3.pdf",
      "title": "John Doe - Senior Software Engineer Resume",
      "file_size": 1048576,
      "mime_type": "application/pdf",
      "created_at": "2024-01-10T14:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "version": 3,
      "status": "active",
      "tags": ["resume", "software_engineer", "python"],
      "access_count": 12,
      "preview_url": "/api/documents/doc_507f1f77bcf86cd799439015/preview"
    },
    {
      "id": "doc_507f1f77bcf86cd799439016",
      "type": "job_description", 
      "filename": "senior_python_dev_jd.pdf",
      "title": "Senior Python Developer - TechCorp",
      "file_size": 524288,
      "mime_type": "application/pdf",
      "created_at": "2024-01-12T09:15:00Z",
      "updated_at": "2024-01-12T09:15:00Z",
      "version": 1,
      "status": "active",
      "tags": ["job_description", "python", "senior", "techcorp"],
      "access_count": 8,
      "preview_url": "/api/documents/doc_507f1f77bcf86cd799439016/preview"
    }
  ],
  "pagination": {
    "total_documents": 15,
    "total_pages": 1,
    "current_page": 1,
    "per_page": 20,
    "has_next": false,
    "has_previous": false
  },
  "statistics": {
    "resumes": 3,
    "job_descriptions": 8,
    "interview_materials": 4,
    "total_size_mb": 45.2
  }
}
```
**Purpose**: Provide paginated listing of user documents with search and filtering

---

### Document Download

#### GET /api/documents/{document_id}/download
**Description**: Download document file with proper content headers  
**Authentication**: Required (JWT token + document ownership validation)  
**Parameters**:
- `document_id`: Unique document identifier
- `version`: Specific version to download (default: latest) - optional

**Response**: Binary file content with appropriate headers
```
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="john_doe_resume_v3.pdf"
Content-Length: 1048576
Cache-Control: private, max-age=3600

[Binary PDF content]
```

**Security Features**:
- **Access Logging**: All downloads logged with timestamp and user
- **Rate Limiting**: Prevent excessive downloads
- **Virus Scanning**: Files scanned before serving
- **Content Validation**: Ensure file integrity

**Purpose**: Secure file download with proper headers and security measures

---

### Document Preview

#### GET /api/documents/{document_id}/preview
**Description**: Get document preview/thumbnail for quick viewing  
**Authentication**: Required (JWT token + document ownership validation)  
**Parameters**:
- `document_id`: Unique document identifier
- `format`: Preview format (`text`, `html`, `image`) - optional
- `page`: Page number for multi-page documents (default: 1) - optional

**Response (Text Preview)**:
```json
{
  "success": true,
  "preview": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "format": "text",
    "content": "John Doe\nSenior Software Engineer\nemail@example.com | (555) 123-4567\n\nPROFESSIONAL SUMMARY\nExperienced software engineer with 6+ years of development experience in Python, Django, and cloud technologies. Proven track record of leading development teams and delivering scalable web applications...",
    "content_length": 2456,
    "truncated": true,
    "full_content_available": true,
    "page_info": {
      "current_page": 1,
      "total_pages": 2
    }
  }
}
```

**Response (HTML Preview)**:
```json
{
  "success": true,
  "preview": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "format": "html",
    "content": "<div class=\"document-preview\"><h1>John Doe</h1><h2>Senior Software Engineer</h2><p>email@example.com | (555) 123-4567</p><h3>PROFESSIONAL SUMMARY</h3><p>Experienced software engineer with 6+ years...</p></div>",
    "css_styles": ".document-preview { font-family: Arial; } h1 { color: #333; }",
    "page_info": {
      "current_page": 1,
      "total_pages": 2
    }
  }
}
```
**Purpose**: Provide quick document previews without full download

---

### Document Search

#### GET /api/search
**Description**: Advanced document search with content and metadata filtering  
**Authentication**: Required (JWT token)  
**Parameters**:
- `query`: Search query string - required
- `type`: Document type filter - optional
- `tags`: Tag filter - optional
- `date_from`: Start date for search (YYYY-MM-DD) - optional
- `date_to`: End date for search (YYYY-MM-DD) - optional
- `content_search`: Include content in search (`true`/`false`, default: `true`) - optional
- `limit`: Results per page (default: 10, max: 50) - optional

**Response**:
```json
{
  "success": true,
  "search_results": {
    "query": "python django experience",
    "total_matches": 7,
    "search_time": 0.15,
    "results": [
      {
        "document": {
          "id": "doc_507f1f77bcf86cd799439015",
          "type": "resume",
          "title": "John Doe - Senior Software Engineer Resume",
          "filename": "john_doe_resume_v3.pdf",
          "created_at": "2024-01-10T14:30:00Z"
        },
        "relevance_score": 0.92,
        "match_highlights": [
          "5+ years of <mark>Python</mark> development experience",
          "Expert in <mark>Django</mark> framework and REST API development",
          "Led <mark>Django</mark> migration project for high-traffic application"
        ],
        "match_sections": ["experience", "skills", "projects"],
        "content_preview": "Senior Software Engineer with extensive Python and Django experience..."
      },
      {
        "document": {
          "id": "doc_507f1f77bcf86cd799439017",
          "type": "job_description",
          "title": "Python Developer - StartupXYZ",
          "filename": "python_dev_startup_jd.pdf",
          "created_at": "2024-01-08T11:20:00Z"
        },
        "relevance_score": 0.85,
        "match_highlights": [
          "Looking for <mark>Python</mark> developer with <mark>Django</mark> expertise",
          "3+ years <mark>experience</mark> with Python web frameworks"
        ],
        "match_sections": ["requirements", "qualifications"],
        "content_preview": "We are seeking a talented Python developer with Django experience..."
      }
    ],
    "facets": {
      "document_types": {
        "resume": 3,
        "job_description": 4
      },
      "tags": {
        "python": 6,
        "django": 5,
        "backend": 4,
        "senior": 3
      },
      "date_ranges": {
        "last_week": 2,
        "last_month": 5,
        "older": 2
      }
    }
  }
}
```
**Purpose**: Provide powerful search capabilities across user documents

---

### Document Versions

#### GET /api/documents/{document_id}/versions
**Description**: Get version history for a document  
**Authentication**: Required (JWT token + document ownership validation)  
**Parameters**:
- `document_id`: Unique document identifier

**Response**:
```json
{
  "success": true,
  "document_versions": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "current_version": 3,
    "total_versions": 3,
    "versions": [
      {
        "version": 3,
        "filename": "john_doe_resume_v3.pdf",
        "created_at": "2024-01-15T10:30:00Z",
        "file_size": 1048576,
        "status": "current",
        "changes": "Updated work experience with latest project",
        "created_by": "user",
        "download_url": "/api/documents/doc_507f1f77bcf86cd799439015/download?version=3"
      },
      {
        "version": 2,
        "filename": "john_doe_resume_v2.pdf", 
        "created_at": "2024-01-12T15:45:00Z",
        "file_size": 987654,
        "status": "archived",
        "changes": "Added new skills section and certifications",
        "created_by": "user",
        "download_url": "/api/documents/doc_507f1f77bcf86cd799439015/download?version=2"
      },
      {
        "version": 1,
        "filename": "john_doe_resume_v1.pdf",
        "created_at": "2024-01-10T14:30:00Z", 
        "file_size": 876543,
        "status": "archived",
        "changes": "Initial upload",
        "created_by": "user",
        "download_url": "/api/documents/doc_507f1f77bcf86cd799439015/download?version=1"
      }
    ],
    "version_comparison_available": true
  }
}
```
**Purpose**: Track document version history and changes

---

### Document Metadata Management

#### PUT /api/documents/{document_id}/metadata
**Description**: Update document metadata (title, description, tags)  
**Authentication**: Required (JWT token + document ownership validation)  
**Request Body**:
```json
{
  "title": "John Doe - Senior Full Stack Engineer Resume",
  "description": "Updated resume highlighting full-stack development experience",
  "tags": ["resume", "full_stack", "python", "react", "senior"],
  "custom_metadata": {
    "target_roles": ["Senior Developer", "Tech Lead"],
    "industries": ["fintech", "healthcare"],
    "salary_range": "120k-150k"
  }
}
```

**Response**:
```json
{
  "success": true,
  "message": "Document metadata updated successfully",
  "updated_document": {
    "id": "doc_507f1f77bcf86cd799439015",
    "title": "John Doe - Senior Full Stack Engineer Resume",
    "description": "Updated resume highlighting full-stack development experience",
    "tags": ["resume", "full_stack", "python", "react", "senior"],
    "custom_metadata": {
      "target_roles": ["Senior Developer", "Tech Lead"],
      "industries": ["fintech", "healthcare"],
      "salary_range": "120k-150k"
    },
    "updated_at": "2024-01-15T17:30:00Z"
  }
}
```
**Purpose**: Allow users to organize and categorize their documents

#### GET /api/documents/{document_id}/analytics
**Description**: Get document usage analytics and insights  
**Authentication**: Required (JWT token + document ownership validation)  
**Response**:
```json
{
  "success": true,
  "analytics": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "usage_statistics": {
      "total_views": 45,
      "total_downloads": 12,
      "unique_access_days": 8,
      "last_accessed": "2024-01-15T16:45:00Z",
      "access_pattern": [
        {"date": "2024-01-15", "views": 8, "downloads": 2},
        {"date": "2024-01-14", "views": 12, "downloads": 3},
        {"date": "2024-01-13", "views": 6, "downloads": 1}
      ]
    },
    "integration_usage": {
      "question_generation_requests": 23,
      "answer_analysis_references": 15,
      "last_used_for_questions": "2024-01-15T14:30:00Z"
    },
    "performance_metrics": {
      "average_load_time": 0.8,
      "search_appearances": 34,
      "search_click_rate": 0.67
    },
    "recommendations": [
      "Document is frequently accessed - consider featuring in dashboard",
      "High usage for question generation - update regularly for best results",
      "Consider adding more detailed tags for improved searchability"
    ]
  }
}
```
**Purpose**: Provide insights on document usage and performance

---

### Document Organization

#### POST /api/collections
**Description**: Create document collections for better organization  
**Authentication**: Required (JWT token)  
**Request Body**:
```json
{
  "name": "Software Engineer Job Applications",
  "description": "Documents for software engineering positions",
  "type": "job_search",
  "document_ids": [
    "doc_507f1f77bcf86cd799439015",
    "doc_507f1f77bcf86cd799439016"
  ],
  "tags": ["job_search", "software_engineer", "2024"],
  "privacy": "private"
}
```

**Response**:
```json
{
  "success": true,
  "collection": {
    "id": "col_507f1f77bcf86cd799439018",
    "name": "Software Engineer Job Applications",
    "description": "Documents for software engineering positions",
    "type": "job_search",
    "created_at": "2024-01-15T18:00:00Z",
    "updated_at": "2024-01-15T18:00:00Z",
    "document_count": 2,
    "documents": [
      {
        "id": "doc_507f1f77bcf86cd799439015",
        "title": "John Doe Resume",
        "type": "resume"
      },
      {
        "id": "doc_507f1f77bcf86cd799439016", 
        "title": "Senior Python Developer JD",
        "type": "job_description"
      }
    ],
    "tags": ["job_search", "software_engineer", "2024"],
    "privacy": "private",
    "share_url": null
  }
}
```

#### GET /api/collections
**Description**: List user's document collections  
**Authentication**: Required (JWT token)  
**Response**:
```json
{
  "success": true,
  "collections": [
    {
      "id": "col_507f1f77bcf86cd799439018",
      "name": "Software Engineer Job Applications",
      "description": "Documents for software engineering positions",
      "type": "job_search",
      "document_count": 2,
      "created_at": "2024-01-15T18:00:00Z",
      "updated_at": "2024-01-15T18:00:00Z"
    }
  ],
  "total_collections": 1
}
```
**Purpose**: Organize related documents into collections

---

### Cross-Service Integration

#### GET /api/documents/for_service/{service_name}
**Description**: Get documents formatted for specific service integration (Internal API)  
**Authentication**: Required (Service token)  
**Parameters**:
- `service_name`: Name of requesting service (`question-generation`, `answer-analysis`)
- `user_id`: User ID for document access
- `document_types`: Comma-separated list of document types needed

**Response**:
```json
{
  "success": true,
  "service_documents": {
    "user_id": "507f1f77bcf86cd799439011",
    "requested_for": "question-generation",
    "documents": [
      {
        "id": "doc_507f1f77bcf86cd799439015",
        "type": "resume",
        "content_path": "/documents/users/507f1f77bcf86cd799439011/resumes/current/john_doe_resume_v3.pdf",
        "extracted_content": {
          "text": "Full extracted text content...",
          "structured_data": {
            "skills": ["Python", "Django", "PostgreSQL"],
            "experience_years": 6,
            "education": "Bachelor's Degree"
          }
        },
        "metadata": {
          "content_length": 2456,
          "language": "en",
          "last_updated": "2024-01-15T10:30:00Z"
        }
      }
    ],
    "usage_tracking": {
      "access_logged": true,
      "service_request_id": "req_507f1f77bcf86cd799439019"
    }
  }
}
```
**Purpose**: Provide formatted document access for other services

---

## Storage Management

### File System Organization
```
/documents/
├── users/
│   └── {user_id}/
│       ├── resumes/
│       │   ├── current/           # Active resume
│       │   └── versions/          # Historical versions
│       ├── job_descriptions/
│       │   ├── active/            # Current job searches  
│       │   └── archive/           # Past opportunities
│       ├── interview_materials/
│       │   ├── questions/         # Generated questions
│       │   ├── analyses/          # Answer analyses
│       │   └── reports/           # Interview reports
│       └── collections/           # User-organized collections
├── shared/
│   ├── templates/                 # Document templates
│   └── public_resources/          # Public materials
└── system/
    ├── backups/                   # Document backups
    ├── thumbnails/                # Generated previews
    └── search_index/              # Search indexing files
```

### Security & Access Control
- **User Isolation**: Each user's documents in separate directory
- **Permission Validation**: Every access validates user ownership  
- **Audit Logging**: All document access logged with timestamps
- **Encryption**: Sensitive documents encrypted at rest
- **Backup**: Regular automated backups with version retention

### Performance Optimization
- **Caching**: Frequently accessed documents cached in memory
- **Lazy Loading**: Document content loaded on-demand
- **Thumbnail Generation**: Pre-generated previews for quick access
- **Search Indexing**: Full-text search index maintained asynchronously
- **CDN Integration**: Optional CDN for static document delivery

---

## Error Handling

### Access Errors
```json
{
  "success": false,
  "error": "Access denied to document",
  "error_code": "ACCESS_DENIED",
  "details": {
    "document_id": "doc_507f1f77bcf86cd799439015",
    "user_id": "507f1f77bcf86cd799439011",
    "reason": "User does not own this document",
    "action": "Contact administrator if you believe this is an error"
  }
}
```

### Storage Errors
```json
{
  "success": false,
  "error": "Document storage unavailable",
  "error_code": "STORAGE_ERROR",
  "details": {
    "storage_status": "degraded",
    "available_space": "5.2GB",
    "recommended_action": "Try again in a few minutes or contact support"
  }
}
```

### Search Errors
```json
{
  "success": false,
  "error": "Search service temporarily unavailable", 
  "error_code": "SEARCH_SERVICE_ERROR",
  "details": {
    "search_index_status": "rebuilding",
    "estimated_recovery": "10 minutes",
    "fallback_available": true
  }
}
```

---

## Performance & Monitoring

### Performance Metrics
- **Response Times**: <1 second for document metadata, <3 seconds for content
- **Throughput**: 500+ concurrent document requests supported
- **Storage Efficiency**: 95% storage utilization with compression
- **Search Performance**: <200ms average search response time

### Monitoring & Analytics
- **Usage Patterns**: Track document access patterns and popular content
- **Performance Monitoring**: Response times, error rates, storage usage
- **User Behavior**: Document organization, search patterns, collection usage
- **Service Health**: Storage health, search index status, backup integrity

### Scalability Features
- **Horizontal Scaling**: Support for distributed storage systems
- **Load Balancing**: Multiple service instances for high availability
- **Caching Strategy**: Multi-tier caching for optimal performance
- **Archive Management**: Automated archiving of old documents

---

## Configuration

### Environment Variables
```bash
# Storage Configuration
DOCUMENTS_ROOT=/documents
MAX_DOCUMENT_SIZE_MB=50
STORAGE_QUOTA_PER_USER_GB=5
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=90

# Search Configuration
SEARCH_INDEX_PATH=/search_index
SEARCH_ENABLED=true
FULL_TEXT_SEARCH=true
SEARCH_INDEX_REBUILD_HOUR=2

# Security Configuration
ENCRYPTION_ENABLED=true
ENCRYPTION_KEY_PATH=/keys/document_encryption.key
AUDIT_LOGGING=true
AUDIT_LOG_PATH=/logs/document_access.log

# Performance Configuration
CACHE_ENABLED=true
CACHE_SIZE_MB=512
THUMBNAIL_GENERATION=true
THUMBNAIL_CACHE_SIZE_MB=256

# Service Integration
FILE_PARSING_URL=http://localhost:5002
LOGIN_MANAGEMENT_URL=http://localhost:5001
SERVICE_AUTH_TOKEN=your-service-token
```

### Document Processing Configuration
```yaml
document_processing:
  preview_generation:
    enabled: true
    formats: ["text", "html", "image"]
    max_preview_length: 1000
    
  search_indexing:
    enabled: true
    include_content: true
    update_frequency: "real-time"
    
  version_management:
    max_versions_per_document: 10
    auto_archive_after_days: 365
    
storage_policies:
  compression:
    enabled: true
    algorithms: ["gzip", "lz4"]
    
  retention:
    active_documents: "unlimited"
    archived_documents: "2 years" 
    deleted_documents: "30 days"
```

---

## Development Notes

### Testing Document Operations
```bash
# Test document listing
curl -X GET http://localhost:5005/api/documents \
  -H "Authorization: Bearer your-jwt-token"

# Test document search
curl -X GET "http://localhost:5005/api/search?query=python+django" \
  -H "Authorization: Bearer your-jwt-token"

# Test document download
curl -X GET http://localhost:5005/api/documents/doc_123/download \
  -H "Authorization: Bearer your-jwt-token" \
  --output downloaded_document.pdf
```

### Storage System Setup
```bash
# Create directory structure
mkdir -p /documents/{users,shared,system}
mkdir -p /documents/system/{backups,thumbnails,search_index}

# Set proper permissions
chmod 755 /documents
chmod 700 /documents/users  # Restrict user directory access
chmod 644 /documents/shared

# Install document processing libraries
pip install PyPDF2 python-docx pillow
pip install whoosh elasticsearch  # For search functionality
pip install cryptography  # For document encryption
```

### Search Index Management
```python
# Example search index setup
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME

schema = Schema(
    document_id=ID(stored=True),
    title=TEXT(stored=True),
    content=TEXT,
    tags=TEXT,
    created_date=DATETIME(stored=True)
)

ix = index.create_in("/search_index", schema)
```

### Document Security Implementation
```python
# Example encryption/decryption for sensitive documents
from cryptography.fernet import Fernet

def encrypt_document(file_content, key):
    """Encrypt document content before storage"""
    f = Fernet(key)
    encrypted_content = f.encrypt(file_content)
    return encrypted_content

def decrypt_document(encrypted_content, key):
    """Decrypt document content for access"""
    f = Fernet(key)
    decrypted_content = f.decrypt(encrypted_content)
    return decrypted_content
```