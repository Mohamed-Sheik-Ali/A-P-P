#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Payroll Processor
This script tests the complete workflow of the payroll API
"""

import requests
import json
import os
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
timestamp = str(int(time.time()))
TEST_USER = {
    "username": "testuser_" + timestamp,
    "email": f"test_{timestamp}@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Test",
    "last_name": "User"
}

class PayrollAPITester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.upload_id = None
        
    def log(self, message):
        """Log messages with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def log_response(self, response, action):
        """Log response details"""
        print(f"\n{'='*50}")
        print(f"Action: {action}")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        try:
            response_data = response.json()
            print(f"Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
        print(f"{'='*50}\n")
        
    def register_user(self):
        """Register a new test user"""
        self.log("Step 1: Registering new user...")
        
        url = f"{self.base_url}/auth/register/"
        response = requests.post(url, json=TEST_USER)
        self.log_response(response, "User Registration")
        
        if response.status_code == 201:
            self.log("✅ User registered successfully!")
            return True
        else:
            self.log("❌ User registration failed!")
            return False
    
    def login_user(self):
        """Login with test user"""
        self.log("Step 2: Logging in user...")
        
        url = f"{self.base_url}/auth/login/"
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(url, json=login_data)
        self.log_response(response, "User Login")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data and 'token' in data['data']:
                self.token = data['data']['token']
                self.headers["Authorization"] = f"Bearer {self.token}"
                self.log("✅ Login successful! Token obtained.")
                return True
        
        self.log("❌ Login failed!")
        return False
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        self.log("Step 3: Getting dashboard statistics...")
        
        url = f"{self.base_url}/dashboard/stats/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "Dashboard Stats")
        
        if response.status_code == 200:
            self.log("✅ Dashboard stats retrieved!")
            return True
        else:
            self.log("❌ Failed to get dashboard stats!")
            return False
    
    def get_user_profile(self):
        """Get user profile"""
        self.log("Step 4: Getting user profile...")
        
        url = f"{self.base_url}/user/profile/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "User Profile")
        
        if response.status_code == 200:
            self.log("✅ User profile retrieved!")
            return True
        else:
            self.log("❌ Failed to get user profile!")
            return False
    
    def upload_excel_file(self):
        """Upload Excel file for processing"""
        self.log("Step 5: Uploading Excel file...")
        
        # Check if sample file exists
        sample_file = "sample_payroll_template.xlsx"
        if not os.path.exists(sample_file):
            self.log(f"❌ Sample file '{sample_file}' not found!")
            return False
        
        url = f"{self.base_url}/uploads/"
        
        # Remove Content-Type for file upload
        upload_headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(sample_file, 'rb') as file:
            files = {'file': (sample_file, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, headers=upload_headers, files=files)
        
        self.log_response(response, "File Upload")
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success') and 'data' in data:
                self.upload_id = data['data'].get('id')
                self.log(f"✅ File uploaded successfully! Upload ID: {self.upload_id}")
                return True
        else:
            self.log("❌ File upload failed!")
            return False
    
    def get_upload_details(self):
        """Get details of the uploaded file"""
        if not self.upload_id:
            self.log("❌ No upload ID available!")
            return False
        
        self.log("Step 6: Getting upload details...")
        
        url = f"{self.base_url}/uploads/{self.upload_id}/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "Upload Details")
        
        if response.status_code == 200:
            self.log("✅ Upload details retrieved!")
            return True
        else:
            self.log("❌ Failed to get upload details!")
            return False
    
    def get_employees_list(self):
        """Get list of employees from the upload"""
        if not self.upload_id:
            self.log("❌ No upload ID available!")
            return False
        
        self.log("Step 7: Getting employees list...")
        
        url = f"{self.base_url}/uploads/{self.upload_id}/employees/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "Employees List")
        
        if response.status_code == 200:
            data = response.json()
            employees = data.get('results', [])
            self.log(f"✅ Found {len(employees)} employees!")
            
            # Show details of first few employees
            for i, emp in enumerate(employees[:3]):
                self.log(f"Employee {i+1}: {emp.get('name')} (ID: {emp.get('employee_id')})")
                if 'salary' in emp:
                    salary = emp['salary']
                    self.log(f"  - Basic Pay: ₹{salary.get('basic_pay', 0)}")
                    self.log(f"  - Gross Salary: ₹{salary.get('gross_salary', 0)}")
                    self.log(f"  - Net Salary: ₹{salary.get('net_salary', 0)}")
            
            return True
        else:
            self.log("❌ Failed to get employees list!")
            return False
    
    def get_all_uploads(self):
        """Get list of all uploads"""
        self.log("Step 8: Getting all uploads...")
        
        url = f"{self.base_url}/uploads/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "All Uploads")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data:
                uploads = data['data']
                self.log(f"✅ Found {len(uploads)} uploads!")
                return True
            else:
                self.log("❌ Failed to get uploads list!")
                return False
        else:
            self.log("❌ Failed to get uploads list!")
            return False
    
    def generate_report(self):
        """Generate Excel report"""
        if not self.upload_id:
            self.log("❌ No upload ID available!")
            return False
        
        self.log("Step 9: Generating Excel report...")
        
        url = f"{self.base_url}/uploads/{self.upload_id}/reports/generate/"
        report_data = {"report_type": "excel"}
        
        response = requests.post(url, headers=self.headers, json=report_data)
        self.log_response(response, "Generate Report")
        
        if response.status_code == 201:
            self.log("✅ Report generated successfully!")
            return True
        else:
            self.log("❌ Failed to generate report!")
            return False
    
    def get_reports(self):
        """Get list of generated reports"""
        self.log("Step 10: Getting reports list...")
        
        url = f"{self.base_url}/reports/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "Reports List")
        
        if response.status_code == 200:
            self.log("✅ Reports list retrieved!")
            return True
        else:
            self.log("❌ Failed to get reports list!")
            return False
    
    def validate_file_without_processing(self):
        """Validate file without processing"""
        self.log("Step 11: Testing file validation...")
        
        sample_file = "sample_payroll_template.xlsx"
        if not os.path.exists(sample_file):
            self.log(f"❌ Sample file '{sample_file}' not found!")
            return False
        
        url = f"{self.base_url}/uploads/validate/"
        upload_headers = {"Authorization": f"Bearer {self.token}"}
        
        with open(sample_file, 'rb') as file:
            files = {'file': (sample_file, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            response = requests.post(url, headers=upload_headers, files=files)
        
        self.log_response(response, "File Validation")
        
        if response.status_code == 200:
            self.log("✅ File validation successful!")
            return True
        else:
            self.log("❌ File validation failed!")
            return False
    
    def check_authentication(self):
        """Check authentication status"""
        self.log("Step 12: Checking authentication status...")
        
        url = f"{self.base_url}/auth/check/"
        response = requests.get(url, headers=self.headers)
        self.log_response(response, "Auth Check")
        
        if response.status_code == 200:
            self.log("✅ Authentication check successful!")
            return True
        else:
            self.log("❌ Authentication check failed!")
            return False
    
    def run_complete_test(self):
        """Run the complete API test suite"""
        print("🚀 Starting Payroll API Testing...")
        print("=" * 60)
        
        test_results = []
        
        # Test all endpoints
        test_functions = [
            ("User Registration", self.register_user),
            ("User Login", self.login_user),
            ("Dashboard Stats", self.get_dashboard_stats),
            ("User Profile", self.get_user_profile),
            ("File Upload", self.upload_excel_file),
            ("Upload Details", self.get_upload_details),
            ("Employees List", self.get_employees_list),
            ("All Uploads", self.get_all_uploads),
            ("Generate Report", self.generate_report),
            ("Reports List", self.get_reports),
            ("File Validation", self.validate_file_without_processing),
            ("Auth Check", self.check_authentication),
        ]
        
        for test_name, test_func in test_functions:
            try:
                result = test_func()
                test_results.append((test_name, result))
                time.sleep(1)  # Small delay between tests
            except Exception as e:
                self.log(f"❌ Error in {test_name}: {str(e)}")
                test_results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name:<25} {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "-" * 60)
        print(f"Total Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
        print("-" * 60)
        
        if passed == len(test_results):
            print("🎉 ALL TESTS PASSED! The API is working correctly.")
        else:
            print("⚠️  Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(BASE_URL.replace('/api', ''))
        print("✅ Server is running!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Django server is not running!")
        print("Please start the server with: python manage.py runserver")
        exit(1)
    
    # Run tests
    tester = PayrollAPITester()
    tester.run_complete_test()
