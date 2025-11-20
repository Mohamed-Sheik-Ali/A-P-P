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
    
    # Create multiple test users with different profiles
    test_users = [
        {
            "username": "john_doe",
            "email": "john.doe@techcorp.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
            "organization_name": "Tech Corp Solutions"
        },
        {
            "username": "sarah_smith",
            "email": "sarah.smith@designstudio.com",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Sarah",
            "last_name": "Smith",
            "organization_name": "Creative Design Studio"
        },
        {
            "username": "mike_wilson",
            "email": "m.wilson@consulting.org",
            "password": "testpass123",
            "password2": "testpass123",
            "first_name": "Michael",
            "last_name": "Wilson",
            "organization_name": "Business Consulting Group"
        }
    ]
    
    for user_data in test_users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
            
            if response.status_code == 201:
                print(f"✅ User {user_data['username']} registered successfully!")
                
            else:
                print(f"⚠️ User {user_data['username']} registration failed: {response.status_code}")
                if "already exists" in response.text.lower():
                    print(f"   (User {user_data['username']} already exists)")
                
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to the server. Make sure Django is running on port 8000.")
            return
        except Exception as e:
            print(f"❌ Error registering {user_data['username']}: {e}")
    
    print(f"\n📋 Now you can:")
    print("1. Go to http://127.0.0.1:8000/admin/")
    print("2. Login with admin credentials")
    print("3. Check the User Approval Management section")
    print("4. Or go directly to: http://127.0.0.1:8000/api/admin-panel/pending-users/")
    print("\n🎯 Test the approval workflow with multiple users!")

if __name__ == "__main__":
    print("🧪 Creating multiple test users for approval workflow testing...")
    register_test_user()
