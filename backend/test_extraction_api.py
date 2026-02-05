"""
Quick Test Script for Skill Extraction API
Tests all 4 endpoints with sample data
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/skills/extract"

def test_project_extraction():
    """Test project description skill extraction"""
    print("\n" + "="*60)
    print("TEST 1: Project Extraction")
    print("="*60)
    
    payload = {
        "project_description": "Built a web dashboard using React and Python Flask with PostgreSQL database. Implemented REST APIs and deployed on AWS."
    }
    
    print(f"\nInput: {payload['project_description']}")
    print("\nSending request...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/project", json=payload, timeout=30)
    duration = time.time() - start
    
    print(f"Response time: {duration:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {data['skills_found']} skills:")
        for skill in data['skills']:
            print(f"   - {skill['skill_name']} (confidence: {skill['confidence']:.2f}, type: {skill['match_type']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_certification_mapping():
    """Test certification to skills mapping"""
    print("\n" + "="*60)
    print("TEST 2: Certification Mapping")
    print("="*60)
    
    payload = {
        "certification_title": "AWS Certified Solutions Architect",
        "provider": "Amazon"
    }
    
    print(f"\nCertification: {payload['certification_title']}")
    print(f"Provider: {payload['provider']}")
    print("\nSending request...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/certification", json=payload, timeout=10)
    duration = time.time() - start
    
    print(f"Response time: {duration:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {data['skills_found']} skills:")
        for skill in data['skills']:
            print(f"   - {skill['skill_name']} (confidence: {skill['confidence']:.2f})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_course_mapping():
    """Test course to skills mapping"""
    print("\n" + "="*60)
    print("TEST 3: Course Mapping")
    print("="*60)
    
    payload = {
        "course_code": "CS101",
        "course_name": "Introduction to Machine Learning"
    }
    
    print(f"\nCourse: {payload['course_code']} - {payload['course_name']}")
    print("\nSending request...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/course", json=payload, timeout=10)
    duration = time.time() - start
    
    print(f"Response time: {duration:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {data['skills_found']} skills:")
        for skill in data['skills']:
            print(f"   - {skill['skill_name']} (confidence: {skill['confidence']:.2f})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

def test_resume_extraction():
    """Test resume skill extraction"""
    print("\n" + "="*60)
    print("TEST 4: Resume Extraction")
    print("="*60)
    
    payload = {
        "resume_text": """
        Software Developer with 2 years of experience.
        
        Skills: Python, Java, React, SQL, Git
        
        Experience:
        - Developed REST APIs using Flask and FastAPI
        - Built responsive web applications with React and TypeScript
        - Managed PostgreSQL databases
        - Deployed applications on AWS EC2 and Docker containers
        """
    }
    
    print(f"\nInput: Resume text ({len(payload['resume_text'])} chars)")
    print("\nSending request...")
    
    start = time.time()
    response = requests.post(f"{BASE_URL}/resume", json=payload, timeout=30)
    duration = time.time() - start
    
    print(f"Response time: {duration:.2f}s")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ Found {data['skills_found']} skills:")
        for skill in data['skills']:
            print(f"   - {skill['skill_name']} (confidence: {skill['confidence']:.2f}, type: {skill['match_type']})")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("\n" + "🔬 SKILL EXTRACTION API TESTS ".center(60, "="))
    
    try:
        # Test 1: Project (might take longer on first run due to model loading)
        print("\n⚠️  First test may take 30-60s for model initialization...")
        test_project_extraction()
        
        # Test 2: Certification (should be fast)
        test_certification_mapping()
        
        # Test 3: Course (should be fast)
        test_course_mapping()
        
        # Test 4: Resume (uses same models as project, should be fast now)
        test_resume_extraction()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the backend server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
