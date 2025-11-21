"""
Test script for Forgot Password API Flow

This script tests the complete forgot password flow:
1. Request password reset with email
2. Receive reset token
3. Reset password using the token

Requirements:
- Django development server must be running
- At least one approved user in the database
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "testuser@example.com"  # Change this to a valid user email in your database
NEW_PASSWORD = "NewSecurePassword123!"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_response(response):
    """Pretty print the response"""
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))

def test_forgot_password_flow():
    """Test the complete forgot password flow"""

    print_section("Forgot Password API Flow Test")
    print(f"Testing with email: {TEST_EMAIL}")
    print(f"Base URL: {BASE_URL}")

    # Step 1: Request Password Reset
    print_section("Step 1: Request Password Reset")
    print(f"POST {BASE_URL}/auth/forgot-password/")

    reset_request_data = {
        "email": TEST_EMAIL
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/forgot-password/",
            json=reset_request_data
        )

        print_response(response)

        if response.status_code != 200:
            print("\nL Password reset request failed!")
            print("\nPossible reasons:")
            print("1. Email doesn't exist in database")
            print("2. User is not approved")
            print("3. User account is not active")
            print("\nPlease check the error message above and try again.")
            return False

        # Extract token from response
        data = response.json()
        reset_token = data.get('data', {}).get('token')
        username = data.get('data', {}).get('username')
        expires_at = data.get('data', {}).get('expires_at')

        print("\n Password reset token generated successfully!")
        print(f"Username: {username}")
        print(f"Token: {reset_token}")
        print(f"Expires at: {expires_at}")

    except requests.exceptions.ConnectionError:
        print("\nL Connection Error!")
        print("Make sure the Django development server is running:")
        print("  python manage.py runserver")
        return False
    except Exception as e:
        print(f"\nL Error: {str(e)}")
        return False

    # Step 2: Reset Password Using Token
    print_section("Step 2: Reset Password Using Token")
    print(f"POST {BASE_URL}/auth/reset-password/")

    reset_password_data = {
        "token": reset_token,
        "new_password": NEW_PASSWORD,
        "new_password2": NEW_PASSWORD
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password/",
            json=reset_password_data
        )

        print_response(response)

        if response.status_code != 200:
            print("\nL Password reset failed!")
            return False

        # Extract JWT token from response
        data = response.json()
        jwt_token = data.get('data', {}).get('token')

        print("\n Password reset successful!")
        print(f"New JWT Token: {jwt_token[:50]}...")
        print("\nYou can now login with:")
        print(f"  Email: {TEST_EMAIL}")
        print(f"  Password: {NEW_PASSWORD}")

    except Exception as e:
        print(f"\nL Error: {str(e)}")
        return False

    # Step 3: Verify Login with New Password
    print_section("Step 3: Verify Login with New Password")
    print(f"POST {BASE_URL}/auth/login/")

    login_data = {
        "username": username,  # Using username from step 1
        "password": NEW_PASSWORD
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data
        )

        print_response(response)

        if response.status_code != 200:
            print("\nL Login with new password failed!")
            return False

        print("\n Login successful with new password!")
        print("\n<‰ Forgot Password Flow Test PASSED!")

    except Exception as e:
        print(f"\nL Error: {str(e)}")
        return False

    # Test token reuse prevention
    print_section("Step 4: Test Token Reuse Prevention")
    print("Attempting to reuse the same token...")

    try:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password/",
            json=reset_password_data
        )

        print_response(response)

        if response.status_code == 400:
            error_message = response.json().get('message', '')
            if 'already been used' in error_message:
                print("\n Token reuse prevention working correctly!")
            else:
                print("\n   Token rejected but unexpected error message")
        else:
            print("\nL Token reuse prevention failed - token was accepted again!")
            return False

    except Exception as e:
        print(f"\nL Error: {str(e)}")
        return False

    return True


def test_invalid_scenarios():
    """Test invalid scenarios"""

    print_section("Testing Invalid Scenarios")

    # Test 1: Invalid Email
    print("\nTest 1: Request reset with invalid email")
    response = requests.post(
        f"{BASE_URL}/auth/forgot-password/",
        json={"email": "nonexistent@example.com"}
    )
    print(f"Status: {response.status_code}")
    print(f"Message: {response.json().get('errors', {}).get('email', [''])[0]}")

    if response.status_code == 400:
        print(" Invalid email properly rejected")

    # Test 2: Invalid Token
    print("\nTest 2: Reset password with invalid token")
    response = requests.post(
        f"{BASE_URL}/auth/reset-password/",
        json={
            "token": "invalid_token_12345",
            "new_password": "TestPassword123!",
            "new_password2": "TestPassword123!"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Message: {response.json().get('message', '')}")

    if response.status_code == 400:
        print(" Invalid token properly rejected")

    # Test 3: Password mismatch
    print("\nTest 3: Reset password with mismatched passwords")
    response = requests.post(
        f"{BASE_URL}/auth/reset-password/",
        json={
            "token": "some_valid_looking_token",
            "new_password": "Password123!",
            "new_password2": "DifferentPassword123!"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Message: {response.json().get('errors', {})}")

    if response.status_code == 400:
        print(" Password mismatch properly rejected")


if __name__ == "__main__":
    print("\n" + "= FORGOT PASSWORD API FLOW TEST".center(70, "="))
    print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Run main flow test
    success = test_forgot_password_flow()

    # Run invalid scenarios test
    if success:
        test_invalid_scenarios()

    print("\n" + "="*70)
    print("Test completed!")
    print("="*70 + "\n")
