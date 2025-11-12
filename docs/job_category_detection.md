# Job Category Detection Feature

## Overview
This feature performs automated detection of job categories from resume and job description content using regex-based pattern matching. The detection runs in parallel after successful file parsing and sends results to the frontend for display.

## Detected Categories
The system can detect the following job categories:

1. **DevOps** - DevOps Engineer, SRE, CI/CD, Infrastructure Automation
2. **Social Media Marketing** - SMM, Digital Marketing, Content Marketing, Community Manager
3. **VAPT** - Vulnerability Assessment, Penetration Testing, Ethical Hacking, Security Testing
4. **Biotech** - Biotechnology, Bioinformatics, Pharmaceutical, Life Sciences
5. **SOC** - Security Operations Center, Security Analyst, Incident Response, Threat Hunting
6. **AI** - Artificial Intelligence, Machine Learning, Deep Learning, NLP, Computer Vision
7. **Accounting** - Accountant, CPA, Bookkeeping, Auditing, Tax Preparation

## Implementation Details

### Backend Components

#### 1. Job Category Detector Service
**File:** `services/file-parsing/services/job_category_detector.py`

**Key Features:**
- Regex-based pattern matching with comprehensive synonyms and variations
- Case-insensitive detection by default
- ReDoS attack prevention through text sanitization
- Handles edge cases (empty strings, None values, null bytes)
- Maximum text length enforcement (100,000 characters)

**Main Methods:**
```python
# Detect categories from a single text
JobCategoryDetector.detect_categories(text: str) -> Dict[str, bool]

# Detect categories from both resume and JD
JobCategoryDetector.detect_categories_from_both(resume_text: str, jd_text: str) -> Dict

# Format results for API response
JobCategoryDetector.format_results_for_response(detection_results: Dict) -> Dict
```

**Security Measures:**
- Text length limitation to prevent excessive processing
- Null byte removal to prevent injection attacks
- Regex error handling to prevent crashes
- Input sanitization for all text processing

#### 2. Integration in File Parsing Service
**File:** `services/file-parsing/app.py`

**Changes:**
- Import `JobCategoryDetector` service
- Category detection integrated in `/api/upload/submit` endpoint
- Runs after successful resume and JD parsing
- Non-blocking: errors in category detection don't fail the upload
- Results included in API response under `job_categories` key

**API Response Structure:**
```json
{
  "success": true,
  "message": "Files uploaded successfully...",
  "files": {...},
  "embeddings": {...},
  "job_categories": {
    "detected_categories": ["DevOps", "AI"],
    "details": {
      "resume_categories": ["DevOps", "AI"],
      "jd_categories": ["DevOps"],
      "all_categories": {
        "resume": {
          "DevOps": true,
          "Social Media Marketing": false,
          "VAPT": false,
          "Biotech": false,
          "SOC": false,
          "AI": true,
          "Accounting": false
        },
        "job_description": {...},
        "combined": {...}
      }
    }
  },
  "user_id": "user123",
  "redirect_url": "/practice"
}
```

### Frontend Components

#### 3. Display Integration
**File:** `services/frontend/templates/home.html`

**Changes:**
- Enhanced success message display with HTML formatting
- Category badges with styled tags
- Extended display time (3 seconds instead of 2) to allow users to see categories
- Responsive layout for category display

**Visual Display:**
- Success message with checkmark icon
- Category section with light blue background
- Individual category tags with blue background and rounded corners
- Flexible wrapping for multiple categories

## Testing

### Test File
**File:** `services/file-parsing/test_job_category_detector.py`

**Test Coverage:**
1. Individual category detection (9 test cases)
2. Multiple category detection
3. Combined detection (resume + JD)
4. Security tests:
   - Very long text (ReDoS prevention)
   - Null bytes
   - Empty strings
   - None values

### Running Tests
```bash
cd services/file-parsing
python3 test_job_category_detector.py
```

**All tests pass successfully!**

## Pattern Examples

### DevOps Patterns
- `devops`, `dev ops`, `site reliability engineer`, `SRE`
- `ci/cd`, `continuous integration`, `continuous deployment`
- `kubernetes`, `docker`, `jenkins`, `terraform`, `ansible`

### VAPT Patterns
- `vapt`, `vulnerability assessment`, `penetration testing`, `pen test`
- `ethical hacker`, `security testing`, `security audit`
- `offensive security`, `red team`

### AI Patterns
- `artificial intelligence`, `AI`, `machine learning`, `ML`
- `deep learning`, `neural networks`, `NLP`
- `computer vision`, `data science`, `LLM`

### Similar patterns exist for all other categories...

## Security Best Practices

### 1. Input Validation
- Maximum text length enforcement (100,000 characters)
- Null byte removal to prevent injection
- Safe handling of None and empty values

### 2. ReDoS Prevention
- Text length limits before regex processing
- Error handling for regex operations
- Timeout-safe regex patterns

### 3. Authentication
- All API endpoints use existing authentication middleware
- User token validation maintained
- No new authentication vulnerabilities introduced

### 4. Error Handling
- Graceful degradation: category detection failures don't affect file upload
- All errors logged for monitoring
- User-friendly error messages

### 5. Data Privacy
- No sensitive data stored in category detection
- Categories derived from already-parsed content
- No additional PII exposure

## Usage Flow

1. User uploads resume and job description files
2. Files are validated and parsed
3. **Category detection runs in parallel:**
   - Resume text analyzed for job categories
   - JD text analyzed for job categories
   - Combined results calculated
4. Results formatted for API response
5. Frontend displays success message with detected categories
6. Page refreshes to show updated dashboard

## Benefits

1. **User Insight** - Users see what job categories their resume/JD align with
2. **Quick Feedback** - Immediate category identification
3. **Multiple Categories** - Detects all applicable categories
4. **Non-Intrusive** - Doesn't affect existing workflow
5. **Secure** - Follows all security best practices
6. **Maintainable** - Easy to add new categories or patterns

## Future Enhancements

Potential improvements:
1. Add more job categories
2. Machine learning-based category detection
3. Confidence scores for each category
4. Category-based question customization
5. Historical category tracking per user
6. Category-based analytics and insights

## Maintenance

### Adding New Categories
1. Add pattern list to `CATEGORY_PATTERNS` in `job_category_detector.py`
2. Include variations, synonyms, and common misspellings
3. Test with sample texts
4. Update documentation

### Modifying Patterns
- Use word boundaries (`\b`) to prevent false positives
- Test for case sensitivity requirements
- Consider plural forms and variations
- Avoid overly complex regex patterns (ReDoS risk)
