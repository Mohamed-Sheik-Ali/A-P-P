#!/usr/bin/env python
"""
Test script to verify the organization name feature works correctly
"""

import requests
import json

# Test configuration
BASE_URL = 'http://127.0.0.1:8000/api'

def test_organization_feature():
    print("Testing Organization Name Feature")
    print("=" * 50)
    
    # Test 1: Register a new user with organization name
    print("\n1. Testing User Registration with Organization Name")
    registration_data = {
        'username': f'testorg_{hash("test") % 1000}',
        'email': 'testorg@example.com',
        'password': 'testpassword123',
        'organization_name': 'Acme Corporation'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/register/', json=registration_data)
        print(f"Registration Response: {response.status_code}")
        print(f"Response Data: {response.json()}")
        
        if response.status_code == 201:
            print("✅ Registration with organization name successful!")
            token = response.json().get('data', {}).get('token')
            
            if token:
                # Test 2: Check dashboard stats includes organization
                print("\n2. Testing Dashboard Stats with Organization Info")
                headers = {'Authorization': f'Bearer {token}'}
                
                dashboard_response = requests.get(f'{BASE_URL}/dashboard/stats/', headers=headers)
                print(f"Dashboard Response: {dashboard_response.status_code}")
                
                if dashboard_response.status_code == 200:
                    dashboard_data = dashboard_response.json()
                    print(f"Dashboard Data: {json.dumps(dashboard_data, indent=2)}")
                    
                    user_info = dashboard_data.get('data', {}).get('user', {})
                    org_name = user_info.get('organization_name')
                    
                    if org_name:
                        print(f"✅ Organization name found in dashboard: {org_name}")
                    else:
                        print("❌ Organization name not found in dashboard")
                else:
                    print(f"❌ Dashboard stats failed: {dashboard_response.text}")
            else:
                print("❌ No token received in registration response")
        else:
            print(f"❌ Registration failed: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_organization_feature()
