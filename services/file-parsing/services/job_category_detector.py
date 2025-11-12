"""
Job Category Detection Service
Performs regex-based detection of job categories from resume and job description text
"""

import re
from typing import Dict, List, Set


class JobCategoryDetector:
    """Service for detecting job categories using regex patterns"""
    
    # Define category patterns with various synonyms and formats
    CATEGORY_PATTERNS = {
        'DevOps': [
            r'\bdev\s*ops\b',
            r'\bdevops\b',
            r'\bsite\s+reliability\s+engineer(?:ing)?\b',
            r'\bsre\b',
            r'\bci\s*/\s*cd\b',
            r'\bcontinuous\s+integration\b',
            r'\bcontinuous\s+deployment\b',
            r'\binfrastructure\s+automation\b',
            r'\bcontainer(?:ization)?\b',
            r'\bkubernetes\b',
            r'\bdocker\b',
            r'\bjenkins\b',
            r'\bterraform\b',
            r'\bansible\b'
        ],
        'Social Media Marketing': [
            r'\bsocial\s+media\s+market(?:ing|er)?\b',
            r'\bsmm\b',
            r'\bdigital\s+market(?:ing|er)?\b',
            r'\bcontent\s+market(?:ing|er)?\b',
            r'\bsocial\s+media\s+manag(?:er|ement)\b',
            r'\bcommunity\s+manag(?:er|ement)\b',
            r'\binfluencer\s+market(?:ing|er)?\b',
            r'\bsocial\s+media\s+strateg(?:y|ist)\b',
            r'\bbrand\s+manag(?:er|ement)\b',
            r'\bonline\s+market(?:ing|er)?\b'
        ],
        'VAPT': [
            r'\bvapt\b',
            r'\bvulnerability\s+assessment\b',
            r'\bpenetration\s+test(?:ing|er)?\b',
            r'\bpen\s*test(?:ing|er)?\b',
            r'\bethical\s+hack(?:ing|er)?\b',
            r'\bsecurity\s+test(?:ing|er)?\b',
            r'\bvulnerability\s+scan(?:ning)?\b',
            r'\bsecurity\s+audit(?:ing|or)?\b',
            r'\boffensive\s+security\b',
            r'\bred\s+team(?:ing)?\b',
            r'\bcyber\s+security\s+test(?:ing|er)?\b'
        ],
        'Biotech': [
            r'\bbiotech(?:nology)?\b',
            r'\bbiological\s+engineer(?:ing)?\b',
            r'\bbioinformatics\b',
            r'\bpharmaceutical\b',
            r'\bclinical\s+research\b',
            r'\bgenetic(?:s)?\s+engineer(?:ing)?\b',
            r'\bmolecular\s+biolog(?:y|ist)\b',
            r'\bbio\s*medical\b',
            r'\bdrug\s+development\b',
            r'\blife\s+sciences\b',
            r'\bbiotechnology\s+research\b'
        ],
        'SOC': [
            r'\bsoc\b',
            r'\bsecurity\s+operations\s+center\b',
            r'\bsecurity\s+operations\b',
            r'\bcyber\s+security\s+operat(?:ions|or)\b',
            r'\bsecurity\s+analyst\b',
            r'\bincident\s+respons(?:e|er)\b',
            r'\bthreat\s+(?:detection|hunting|intelligence)\b',
            r'\bsiem\b',
            r'\bsecurity\s+monitoring\b',
            r'\bcyber\s+defense\b',
            r'\bblue\s+team\b'
        ],
        'AI': [
            r'\bartificial\s+intelligence\b',
            r'\b(?:^|\s)ai(?:\s|$)\b',
            r'\bmachine\s+learning\b',
            r'\b(?:^|\s)ml(?:\s|$)\b',
            r'\bdeep\s+learning\b',
            r'\bneural\s+network(?:s)?\b',
            r'\bnatural\s+language\s+process(?:ing)?\b',
            r'\bnlp\b',
            r'\bcomputer\s+vision\b',
            r'\bdata\s+scien(?:ce|tist)\b',
            r'\bml\s+engineer(?:ing)?\b',
            r'\bai\s+engineer(?:ing)?\b',
            r'\blarge\s+language\s+model(?:s)?\b',
            r'\bllm(?:s)?\b'
        ],
        'Accounting': [
            r'\baccoun(?:t|ting|tant)(?:s)?\b',
            r'\bfinancial\s+account(?:ing|ant)\b',
            r'\bcertified\s+public\s+accountant\b',
            r'\bcpa\b',
            r'\bbook\s*keep(?:ing|er)\b',
            r'\bauditor?\b',
            r'\btax\s+(?:accountant|preparation|specialist)\b',
            r'\bfinancial\s+report(?:ing)?\b',
            r'\bgeneral\s+ledger\b',
            r'\baccounts\s+(?:payable|receivable)\b',
            r'\bforensic\s+accounting\b',
            r'\bmanagement\s+accounting\b'
        ]
    }
    
    @classmethod
    def detect_categories(cls, text: str, case_sensitive: bool = False) -> Dict[str, bool]:
        """
        Detect job categories from text using regex patterns
        
        Args:
            text: Text to analyze (resume or job description)
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            Dictionary with category names as keys and boolean detection results as values
        """
        if not text or not isinstance(text, str):
            return {category: False for category in cls.CATEGORY_PATTERNS.keys()}
        
        # Sanitize input to prevent ReDoS attacks
        text = cls._sanitize_text(text)
        
        results = {}
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            detected = False
            
            # Check if any pattern matches
            for pattern in patterns:
                try:
                    # Use timeout-safe regex search
                    if re.search(pattern, text, flags=flags):
                        detected = True
                        break
                except re.error as e:
                    # Log regex errors but continue processing
                    print(f"[JOB CATEGORY] Regex error for pattern '{pattern}': {e}")
                    continue
            
            results[category] = detected
        
        return results
    
    @classmethod
    def detect_categories_from_both(cls, resume_text: str, jd_text: str) -> Dict[str, Dict[str, bool]]:
        """
        Detect categories from both resume and job description
        
        Args:
            resume_text: Resume text content
            jd_text: Job description text content
            
        Returns:
            Dictionary with 'resume', 'job_description', and 'combined' keys,
            each containing category detection results
        """
        resume_categories = cls.detect_categories(resume_text)
        jd_categories = cls.detect_categories(jd_text)
        
        # Combined results: category detected in either resume or JD
        combined_categories = {
            category: resume_categories[category] or jd_categories[category]
            for category in resume_categories.keys()
        }
        
        return {
            'resume': resume_categories,
            'job_description': jd_categories,
            'combined': combined_categories
        }
    
    @classmethod
    def get_detected_categories_list(cls, detection_results: Dict[str, bool]) -> List[str]:
        """
        Get list of detected categories from detection results
        
        Args:
            detection_results: Dictionary with category detection results
            
        Returns:
            List of detected category names
        """
        return [category for category, detected in detection_results.items() if detected]
    
    @classmethod
    def _sanitize_text(cls, text: str, max_length: int = 100000) -> str:
        """
        Sanitize text to prevent ReDoS and other regex-based attacks
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed text length
            
        Returns:
            Sanitized text
        """
        # Limit text length to prevent excessive processing
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove null bytes and other problematic characters
        text = text.replace('\x00', '')
        
        return text
    
    @classmethod
    def format_results_for_response(cls, detection_results: Dict[str, Dict[str, bool]]) -> Dict:
        """
        Format detection results for API response
        
        Args:
            detection_results: Raw detection results from detect_categories_from_both
            
        Returns:
            Formatted results with detected categories lists and details
        """
        combined_list = cls.get_detected_categories_list(detection_results['combined'])
        resume_list = cls.get_detected_categories_list(detection_results['resume'])
        jd_list = cls.get_detected_categories_list(detection_results['job_description'])
        
        return {
            'detected_categories': combined_list,
            'details': {
                'resume_categories': resume_list,
                'jd_categories': jd_list,
                'all_categories': {
                    'resume': detection_results['resume'],
                    'job_description': detection_results['job_description'],
                    'combined': detection_results['combined']
                }
            }
        }
