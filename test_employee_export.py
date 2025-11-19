#!/usr/bin/env python3
"""
Test script for Individual Employee Export functionality
This script tests the new employee export feature (Excel and PDF)
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
timestamp = str(int(time.time()))
TEST_USER = {
    "username": "exporttest_" + timestamp,
    "email": f"exporttest_{timestamp}@example.com",
    "password": "testpass123",
    "password2": "testpass123",
    "first_name": "Export",
    "last_name": "Tester"
}

class EmployeeExportTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.upload_id = None
        self.employee_id = None
        
    def log(self, message):
        """Log messages with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def register_and_login(self):
        """Register and login user"""
        self.log("Setting up test user...")
        
        # Register
        url = f"{self.base_url}/auth/register/"
        response = requests.post(url, json=TEST_USER)
        
        if response.status_code != 201:
            self.log("❌ Registration failed - using existing user for login")
        
        # Login
        url = f"{self.base_url}/auth/login/"
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data and 'token' in data['data']:
                self.token = data['data']['token']
                self.headers["Authorization"] = f"Bearer {self.token}"
                self.log("✅ User authenticated successfully!")
                return True
        
        self.log("❌ Authentication failed!")
        return False
    
    def upload_sample_file(self):
        """Upload sample Excel file"""
        self.log("Uploading sample Excel file...")
        
        sample_file = "sample_payroll_template.xlsx"
        url = f"{self.base_url}/uploads/"
        
        upload_headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            with open(sample_file, 'rb') as file:
                files = {'file': (sample_file, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(url, headers=upload_headers, files=files)
            
            if response.status_code == 201:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self.upload_id = data['data'].get('id')
                    self.log(f"✅ File uploaded successfully! Upload ID: {self.upload_id}")
                    return True
            
            self.log("❌ File upload failed!")
            return False
            
        except Exception as e:
            self.log(f"❌ Error uploading file: {e}")
            return False
    
    def get_employee_list(self):
        """Get list of employees and pick one for testing"""
        if not self.upload_id:
            self.log("❌ No upload ID available!")
            return False
        
        self.log("Getting employee list...")
        
        url = f"{self.base_url}/uploads/{self.upload_id}/employees/"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and 'data' in data and data['data']:
                employees = data['data']
                self.employee_id = employees[0]['id']  # Pick first employee
                employee_name = employees[0]['name']
                self.log(f"✅ Found {len(employees)} employees. Testing with: {employee_name} (ID: {self.employee_id})")
                return True
        
        self.log("❌ Failed to get employee list!")
        return False
    
    def test_excel_export(self):
        """Test Excel export for individual employee"""
        if not self.employee_id:
            self.log("❌ No employee ID available!")
            return False
        
        self.log("Testing Excel export...")
        
        url = f"{self.base_url}/employees/{self.employee_id}/export/"
        export_data = {"report_type": "excel"}
        
        response = requests.post(url, headers=self.headers, json=export_data)
        
        if response.status_code == 200:
            # Check if it's a file download
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            if 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type:
                file_size = len(response.content)
                filename = content_disposition.split('filename="')[1].split('"')[0] if 'filename=' in content_disposition else 'employee_export.xlsx'
                
                # Save file for verification
                with open(f"test_{filename}", 'wb') as f:
                    f.write(response.content)
                
                self.log(f"✅ Excel export successful! File: {filename}, Size: {file_size} bytes")
                return True
            else:
                self.log(f"❌ Excel export failed! Content-Type: {content_type}")
                return False
        else:
            self.log(f"❌ Excel export failed! Status: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                self.log(f"Error details: {error_data}")
            return False
    
    def test_pdf_export(self):
        """Test PDF export for individual employee"""
        if not self.employee_id:
            self.log("❌ No employee ID available!")
            return False
        
        self.log("Testing PDF export...")
        
        url = f"{self.base_url}/employees/{self.employee_id}/export/"
        export_data = {"report_type": "pdf"}
        
        response = requests.post(url, headers=self.headers, json=export_data)
        
        if response.status_code == 200:
            # Check if it's a file download
            content_type = response.headers.get('content-type', '')
            content_disposition = response.headers.get('content-disposition', '')
            
            if 'application/pdf' in content_type:
                file_size = len(response.content)
                filename = content_disposition.split('filename="')[1].split('"')[0] if 'filename=' in content_disposition else 'employee_export.pdf'
                
                # Save file for verification
                with open(f"test_{filename}", 'wb') as f:
                    f.write(response.content)
                
                self.log(f"✅ PDF export successful! File: {filename}, Size: {file_size} bytes")
                return True
            else:
                self.log(f"❌ PDF export failed! Content-Type: {content_type}")
                return False
        else:
            self.log(f"❌ PDF export failed! Status: {response.status_code}")
            if response.headers.get('content-type') == 'application/json':
                error_data = response.json()
                self.log(f"Error details: {error_data}")
            return False
    
    def test_invalid_employee_id(self):
        """Test export with invalid employee ID"""
        self.log("Testing with invalid employee ID...")
        
        url = f"{self.base_url}/employees/99999/export/"
        export_data = {"report_type": "excel"}
        
        response = requests.post(url, headers=self.headers, json=export_data)
        
        if response.status_code == 404:
            self.log("✅ Invalid employee ID handled correctly (404 response)")
            return True
        else:
            self.log(f"❌ Invalid employee ID test failed! Status: {response.status_code}")
            return False
    
    def test_invalid_report_type(self):
        """Test export with invalid report type"""
        if not self.employee_id:
            self.log("❌ No employee ID available!")
            return False
        
        self.log("Testing with invalid report type...")
        
        url = f"{self.base_url}/employees/{self.employee_id}/export/"
        export_data = {"report_type": "word"}  # Invalid type
        
        response = requests.post(url, headers=self.headers, json=export_data)
        
        if response.status_code == 400:
            self.log("✅ Invalid report type handled correctly (400 response)")
            return True
        else:
            self.log(f"❌ Invalid report type test failed! Status: {response.status_code}")
            return False
    
    def run_complete_test(self):
        """Run complete test suite for employee export"""
        print("🚀 Starting Employee Export Testing...")
        print("=" * 60)
        
        test_results = []
        
        # Test all functions
        test_functions = [
            ("User Authentication", self.register_and_login),
            ("File Upload", self.upload_sample_file),
            ("Get Employee List", self.get_employee_list),
            ("Excel Export", self.test_excel_export),
            ("PDF Export", self.test_pdf_export),
            ("Invalid Employee ID", self.test_invalid_employee_id),
            ("Invalid Report Type", self.test_invalid_report_type),
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
        print("📊 EMPLOYEE EXPORT TEST RESULTS")
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
            print("🎉 ALL TESTS PASSED! Employee export is working correctly.")
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
    tester = EmployeeExportTester()
    tester.run_complete_test()
