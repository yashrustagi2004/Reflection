"""
Test script for JobCategoryDetector
Tests regex patterns for various job categories
"""

import sys
import os

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from job_category_detector import JobCategoryDetector


def test_category_detection():
    """Test job category detection with sample texts"""
    
    print("=" * 80)
    print("Testing Job Category Detection")
    print("=" * 80)
    
    # Test cases
    test_cases = [
        {
            'name': 'DevOps Resume',
            'text': '''
            Senior DevOps Engineer with 5 years of experience in CI/CD pipelines,
            Kubernetes, Docker, and infrastructure automation. Proficient in Jenkins,
            Terraform, and Ansible. Experience with AWS and Azure cloud platforms.
            '''
        },
        {
            'name': 'Social Media Marketing JD',
            'text': '''
            Looking for a Social Media Marketing Manager to lead our digital marketing
            campaigns. Experience with Instagram, Facebook, TikTok, and content marketing
            required. Must have strong skills in influencer marketing and community management.
            '''
        },
        {
            'name': 'VAPT Security Resume',
            'text': '''
            Cybersecurity professional specializing in Vulnerability Assessment and
            Penetration Testing (VAPT). Certified Ethical Hacker with experience in
            red team operations, security auditing, and offensive security testing.
            '''
        },
        {
            'name': 'Biotech Research JD',
            'text': '''
            Seeking a Biotechnology Research Scientist with expertise in molecular biology,
            genetic engineering, and bioinformatics. PhD in Life Sciences preferred.
            Experience in pharmaceutical drug development is a plus.
            '''
        },
        {
            'name': 'SOC Analyst Position',
            'text': '''
            Security Operations Center (SOC) Analyst position available. Must have experience
            with SIEM tools, incident response, threat detection and hunting, and cyber defense.
            Blue team experience required. Knowledge of security monitoring essential.
            '''
        },
        {
            'name': 'AI/ML Engineer Resume',
            'text': '''
            Machine Learning Engineer with expertise in Artificial Intelligence, Deep Learning,
            Natural Language Processing (NLP), and Computer Vision. Experience with neural networks,
            TensorFlow, PyTorch, and Large Language Models (LLMs). Strong background in Data Science.
            '''
        },
        {
            'name': 'Accounting Position',
            'text': '''
            Certified Public Accountant (CPA) with 8 years in financial accounting and auditing.
            Expert in tax preparation, bookkeeping, accounts payable/receivable, general ledger
            management, and financial reporting. Experience with forensic accounting investigations.
            '''
        },
        {
            'name': 'Multiple Categories',
            'text': '''
            Tech company seeks DevOps Engineer with AI/Machine Learning background to work on
            security operations and penetration testing. Must understand artificial intelligence
            infrastructure and have experience with SOC operations.
            '''
        },
        {
            'name': 'No Specific Category',
            'text': '''
            General software developer with experience in web development, mobile apps,
            and database management. Familiar with JavaScript, Python, and SQL.
            '''
        }
    ]
    
    print("\nRunning Detection Tests:\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'=' * 80}")
        
        # Detect categories
        results = JobCategoryDetector.detect_categories(test_case['text'])
        detected = JobCategoryDetector.get_detected_categories_list(results)
        
        print(f"\nText Sample: {test_case['text'][:100]}...")
        print(f"\nDetected Categories: {', '.join(detected) if detected else 'None'}")
        print(f"\nDetailed Results:")
        for category, is_detected in results.items():
            status = "✓ DETECTED" if is_detected else "✗ Not detected"
            print(f"  {category:25} {status}")
    
    print("\n" + "=" * 80)
    print("Testing Combined Detection (Resume + JD)")
    print("=" * 80)
    
    # Test combined detection
    sample_resume = '''
    DevOps Engineer with experience in container orchestration using Kubernetes and Docker.
    Background in Artificial Intelligence and Machine Learning projects.
    '''
    
    sample_jd = '''
    Looking for a Security Operations Center (SOC) Analyst with penetration testing experience.
    Knowledge of VAPT tools and vulnerability assessment is required.
    '''
    
    combined_results = JobCategoryDetector.detect_categories_from_both(sample_resume, sample_jd)
    formatted = JobCategoryDetector.format_results_for_response(combined_results)
    
    print(f"\nResume Categories: {', '.join(formatted['details']['resume_categories'])}")
    print(f"JD Categories: {', '.join(formatted['details']['jd_categories'])}")
    print(f"Combined Categories: {', '.join(formatted['detected_categories'])}")
    
    print("\n" + "=" * 80)
    print("Security Tests")
    print("=" * 80)
    
    # Test with malicious inputs
    security_tests = [
        {
            'name': 'Very Long Text (ReDoS Prevention)',
            'text': 'A' * 150000  # 150k characters
        },
        {
            'name': 'Null Bytes',
            'text': 'DevOps\x00Engineer with\x00experience'
        },
        {
            'name': 'Empty String',
            'text': ''
        },
        {
            'name': 'None Value',
            'text': None
        }
    ]
    
    print("\nRunning Security Tests:\n")
    
    for test in security_tests:
        try:
            print(f"Testing: {test['name']}")
            results = JobCategoryDetector.detect_categories(test['text'])
            print(f"  ✓ Handled safely")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("All Tests Completed!")
    print("=" * 80)


if __name__ == '__main__':
    test_category_detection()
