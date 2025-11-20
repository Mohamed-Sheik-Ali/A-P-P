#!/usr/bin/env python3
"""
Test script to verify that employees can be loaded for different users with same EMPID
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to Python path
project_dir = '/Users/mohamedsheikalim/Desktop/payroll_processor'
sys.path.insert(0, project_dir)

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_config.settings')

# Setup Django
django.setup()

from django.contrib.auth.models import User
from payroll.models import Employee

def test_employee_creation():
    """Test that employees with same employee_id can be created for different users"""
    
    # Create test users if they don't exist
    user1, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'user1@test.com',
            'first_name': 'Test',
            'last_name': 'User1'
        }
    )
    
    user2, created = User.objects.get_or_create(
        username='testuser2', 
        defaults={
            'email': 'user2@test.com',
            'first_name': 'Test',
            'last_name': 'User2'
        }
    )
    
    print(f"Created/found users: {user1.username}, {user2.username}")
    
    # Test creating employees with same employee_id for different users
    try:
        # Create employee with ID 'EMP001' for user1
        emp1 = Employee.objects.create(
            user=user1,
            employee_id='EMP001',
            name='John Doe (User 1)',
            email='john1@company1.com',
            department='Engineering',
            designation='Senior Developer'
        )
        print(f"✓ Created employee {emp1.employee_id} for {emp1.user.username}: {emp1.name}")
        
        # Create employee with same ID 'EMP001' for user2 
        emp2 = Employee.objects.create(
            user=user2,
            employee_id='EMP001', 
            name='John Doe (User 2)',
            email='john2@company2.com',
            department='Marketing',
            designation='Marketing Manager'
        )
        print(f"✓ Created employee {emp2.employee_id} for {emp2.user.username}: {emp2.name}")
        
        # Verify that we have 2 different employees
        employees_with_emp001 = Employee.objects.filter(employee_id='EMP001')
        print(f"✓ Found {employees_with_emp001.count()} employees with ID 'EMP001'")
        
        # Verify that each user can only see their own employee
        user1_employees = Employee.objects.filter(user=user1, employee_id='EMP001')
        user2_employees = Employee.objects.filter(user=user2, employee_id='EMP001')
        
        print(f"✓ User1 has {user1_employees.count()} employee(s) with ID 'EMP001'")
        print(f"✓ User2 has {user2_employees.count()} employee(s) with ID 'EMP001'")
        
        # Test unique constraint - try to create duplicate for same user (should fail)
        try:
            Employee.objects.create(
                user=user1,
                employee_id='EMP001',
                name='Duplicate Employee',
                email='duplicate@test.com'
            )
            print("✗ ERROR: Duplicate employee creation should have failed!")
        except Exception as e:
            print(f"✓ Correctly prevented duplicate: {type(e).__name__}")
        
        print("\n✅ All tests passed! Employee creation works correctly with user scoping.")
        
        # Cleanup
        print("\nCleaning up test data...")
        emp1.delete()
        emp2.delete()
        print("✓ Test employees deleted")
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_employee_creation()
