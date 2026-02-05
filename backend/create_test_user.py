#!/usr/bin/env python3
"""
Create Test User Script
Creates a demo student user for testing the frontend
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def create_test_user():
    """Create a test student account"""
    
    # Test user credentials
    user_data = {
        "username": "student1",
        "email": "student1@example.com",
        "password": "password123",
        "role": "student",
        "full_name": "Test Student",
        "department": "Computer Science"
    }
    
    print("Creating test student account...")
    print(f"Username: {user_data['username']}")
    print(f"Password: {user_data['password']}")
    print("-" * 50)
    
    try:
        # Register user
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ User created successfully!")
            print(json.dumps(response.json(), indent=2))
            print("\n" + "=" * 50)
            print("LOGIN CREDENTIALS:")
            print(f"Username: {user_data['username']}")
            print(f"Password: {user_data['password']}")
            print("=" * 50)
        elif response.status_code == 400:
            print("⚠️  User might already exist")
            print(response.json())
            print("\n" + "=" * 50)
            print("TRY THESE CREDENTIALS:")
            print(f"Username: {user_data['username']}")
            print(f"Password: {user_data['password']}")
            print("=" * 50)
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_test_user()
