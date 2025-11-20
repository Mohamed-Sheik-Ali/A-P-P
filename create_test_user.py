#!/usr/bin/env python3
"""
Test script to create a test user for approval testing
"""
import requests
import json

# API endpoint
BASE_URL = "http://127.0.0.1:8000/api"

def register_test_user():
    """Register a test user to test the approval workflow"""
    
    user_data = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "testpass123",
        "password2": "testpass123",  # Confirm password
        "first_name": "Test",
        "last_name": "User",
        "organization_name": "Test Organization Ltd"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        
        if response.status_code == 201:
            print("✅ Test user registered successfully!")
            print(f"Response: {response.json()}")
            print("\n📋 Now you can:")
            print("1. Go to http://127.0.0.1:8000/admin/")
            print("2. Login with admin credentials")
            print("3. Check the User Approval Management section")
            print("4. Or go directly to: http://127.0.0.1:8000/api/admin-panel/pending-users/")
            
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure Django is running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🧪 Creating test user for approval workflow testing...")
    register_test_user()
