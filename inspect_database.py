#!/usr/bin/env python3
"""
Database Inspector for Payroll Processor
This script helps you inspect the data stored in the database
"""

import os
import django
import sys

# Add the project directory to Python path
sys.path.append('/Users/mohamedsheikalim/Desktop/payroll_processor')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_config.settings')
django.setup()

from django.contrib.auth.models import User
from payroll.models import PayrollUpload, Employee, SalaryComponent, PayrollReport
from datetime import datetime


class DatabaseInspector:
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "=" * 60)
        print(f" {title}")
        print("=" * 60)
    
    def print_subheader(self, title):
        """Print a formatted subheader"""
        print(f"\n--- {title} ---")
    
    def inspect_users(self):
        """Inspect users table"""
        self.print_header("USERS")
        
        users = User.objects.all().order_by('-date_joined')
        print(f"Total Users: {users.count()}")
        
        if users.exists():
            print("\nUsers List:")
            for user in users:
                print(f"  ID: {user.id} | Username: {user.username} | Email: {user.email}")
                print(f"      Name: {user.first_name} {user.last_name}")
                print(f"      Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
                print(f"      Active: {user.is_active}")
                print()
    
    def inspect_uploads(self):
        """Inspect payroll uploads"""
        self.print_header("PAYROLL UPLOADS")
        
        uploads = PayrollUpload.objects.all().order_by('-upload_date')
        print(f"Total Uploads: {uploads.count()}")
        
        if uploads.exists():
            print("\nUploads List:")
            for upload in uploads:
                print(f"  ID: {upload.id}")
                print(f"  User: {upload.user.username}")
                print(f"  Filename: {upload.filename}")
                print(f"  Status: {upload.status}")
                print(f"  Total Employees: {upload.total_employees}")
                print(f"  Upload Date: {upload.upload_date.strftime('%Y-%m-%d %H:%M')}")
                if upload.processed_date:
                    print(f"  Processed Date: {upload.processed_date.strftime('%Y-%m-%d %H:%M')}")
                if upload.error_message:
                    print(f"  Error: {upload.error_message}")
                print(f"  File Path: {upload.file.name if upload.file else 'N/A'}")
                print()
    
    def inspect_employees(self, upload_id=None):
        """Inspect employees table"""
        self.print_header("EMPLOYEES")
        
        if upload_id:
            employees = Employee.objects.filter(upload_id=upload_id).order_by('employee_id')
            print(f"Employees for Upload ID {upload_id}: {employees.count()}")
        else:
            employees = Employee.objects.all().order_by('upload_id', 'employee_id')
            print(f"Total Employees: {employees.count()}")
        
        if employees.exists():
            print("\nEmployees List:")
            for emp in employees:
                print(f"  ID: {emp.id} | Upload ID: {emp.upload_id}")
                print(f"  Employee ID: {emp.employee_id}")
                print(f"  Name: {emp.name}")
                print(f"  Email: {emp.email or 'N/A'}")
                print(f"  Department: {emp.department or 'N/A'}")
                print(f"  Designation: {emp.designation or 'N/A'}")
                print()
    
    def inspect_salary_components(self, upload_id=None):
        """Inspect salary components"""
        self.print_header("SALARY COMPONENTS")
        
        if upload_id:
            salary_components = SalaryComponent.objects.filter(
                employee__upload_id=upload_id
            ).order_by('employee__employee_id')
            print(f"Salary Components for Upload ID {upload_id}: {salary_components.count()}")
        else:
            salary_components = SalaryComponent.objects.all().order_by('employee__upload_id', 'employee__employee_id')
            print(f"Total Salary Components: {salary_components.count()}")
        
        if salary_components.exists():
            print("\nSalary Components:")
            for salary in salary_components:
                emp = salary.employee
                print(f"  Employee: {emp.name} ({emp.employee_id})")
                print(f"  Upload ID: {emp.upload_id}")
                
                print("\n  EARNINGS:")
                print(f"    Basic Pay: ₹{salary.basic_pay:,.2f}")
                print(f"    HRA: ₹{salary.hra:,.2f}")
                print(f"    Variable Pay: ₹{salary.variable_pay:,.2f}")
                print(f"    Special Allowance: ₹{salary.special_allowance:,.2f}")
                print(f"    Other Allowances: ₹{salary.other_allowances:,.2f}")
                print(f"    GROSS SALARY: ₹{salary.gross_salary:,.2f}")
                
                print("\n  DEDUCTIONS:")
                print(f"    Provident Fund: ₹{salary.provident_fund:,.2f}")
                print(f"    Professional Tax: ₹{salary.professional_tax:,.2f}")
                print(f"    Income Tax: ₹{salary.income_tax:,.2f}")
                print(f"    Other Deductions: ₹{salary.other_deductions:,.2f}")
                print(f"    TOTAL DEDUCTIONS: ₹{salary.total_deductions:,.2f}")
                
                print("\n  FINAL AMOUNTS:")
                print(f"    NET SALARY: ₹{salary.net_salary:,.2f}")
                print(f"    Take Home Pay: ₹{salary.take_home_pay:,.2f}")
                
                print(f"  Created: {salary.created_at.strftime('%Y-%m-%d %H:%M')}")
                print("-" * 40)
    
    def inspect_reports(self):
        """Inspect generated reports"""
        self.print_header("PAYROLL REPORTS")
        
        reports = PayrollReport.objects.all().order_by('-generated_date')
        print(f"Total Reports: {reports.count()}")
        
        if reports.exists():
            print("\nReports List:")
            for report in reports:
                print(f"  ID: {report.id}")
                print(f"  Upload: {report.upload.filename} (ID: {report.upload.id})")
                print(f"  Type: {report.report_type}")
                print(f"  File: {report.file.name if report.file else 'N/A'}")
                print(f"  Size: {report.file_size:,} bytes")
                print(f"  Generated: {report.generated_date.strftime('%Y-%m-%d %H:%M')}")
                print()
    
    def get_summary_statistics(self):
        """Get summary statistics"""
        self.print_header("SUMMARY STATISTICS")
        
        users_count = User.objects.count()
        uploads_count = PayrollUpload.objects.count()
        employees_count = Employee.objects.count()
        salary_components_count = SalaryComponent.objects.count()
        reports_count = PayrollReport.objects.count()
        
        # Status breakdown
        upload_statuses = {}
        for upload in PayrollUpload.objects.all():
            upload_statuses[upload.status] = upload_statuses.get(upload.status, 0) + 1
        
        print(f"Users: {users_count}")
        print(f"Uploads: {uploads_count}")
        print(f"Employees: {employees_count}")
        print(f"Salary Components: {salary_components_count}")
        print(f"Reports: {reports_count}")
        
        if upload_statuses:
            print("\nUpload Status Breakdown:")
            for status, count in upload_statuses.items():
                print(f"  {status.title()}: {count}")
        
        # Latest upload info
        latest_upload = PayrollUpload.objects.order_by('-upload_date').first()
        if latest_upload:
            print(f"\nLatest Upload:")
            print(f"  ID: {latest_upload.id}")
            print(f"  File: {latest_upload.filename}")
            print(f"  Status: {latest_upload.status}")
            print(f"  Date: {latest_upload.upload_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"  Employees: {latest_upload.total_employees}")
    
    def inspect_specific_upload(self, upload_id):
        """Inspect a specific upload in detail"""
        self.print_header(f"DETAILED INSPECTION - UPLOAD ID: {upload_id}")
        
        try:
            upload = PayrollUpload.objects.get(id=upload_id)
            
            print("UPLOAD DETAILS:")
            print(f"  ID: {upload.id}")
            print(f"  User: {upload.user.username}")
            print(f"  Filename: {upload.filename}")
            print(f"  Status: {upload.status}")
            print(f"  Total Employees: {upload.total_employees}")
            print(f"  Upload Date: {upload.upload_date.strftime('%Y-%m-%d %H:%M')}")
            if upload.processed_date:
                print(f"  Processed Date: {upload.processed_date.strftime('%Y-%m-%d %H:%M')}")
            if upload.error_message:
                print(f"  Error: {upload.error_message}")
            
            # Show employees for this upload
            self.inspect_employees(upload_id)
            
            # Show salary components for this upload
            self.inspect_salary_components(upload_id)
            
        except PayrollUpload.DoesNotExist:
            print(f"❌ Upload with ID {upload_id} not found!")
    
    def run_complete_inspection(self):
        """Run complete database inspection"""
        print("🔍 PAYROLL DATABASE INSPECTION")
        print("=" * 60)
        print(f"Inspection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.get_summary_statistics()
        self.inspect_users()
        self.inspect_uploads()
        self.inspect_employees()
        self.inspect_salary_components()
        self.inspect_reports()
        
        print("\n✅ Database inspection complete!")
    
    def run_latest_upload_inspection(self):
        """Inspect only the latest upload"""
        latest_upload = PayrollUpload.objects.order_by('-upload_date').first()
        if latest_upload:
            self.inspect_specific_upload(latest_upload.id)
        else:
            print("❌ No uploads found in database!")


def main():
    inspector = DatabaseInspector()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "summary":
            inspector.get_summary_statistics()
        elif command == "users":
            inspector.inspect_users()
        elif command == "uploads":
            inspector.inspect_uploads()
        elif command == "employees":
            inspector.inspect_employees()
        elif command == "salary":
            inspector.inspect_salary_components()
        elif command == "reports":
            inspector.inspect_reports()
        elif command == "latest":
            inspector.run_latest_upload_inspection()
        elif command.startswith("upload="):
            upload_id = int(command.split("=")[1])
            inspector.inspect_specific_upload(upload_id)
        else:
            print("Available commands:")
            print("  summary  - Show summary statistics")
            print("  users    - Show users")
            print("  uploads  - Show uploads")
            print("  employees - Show employees")
            print("  salary   - Show salary components")
            print("  reports  - Show reports")
            print("  latest   - Show latest upload details")
            print("  upload=ID - Show specific upload details")
            print("  (no command) - Complete inspection")
    else:
        inspector.run_complete_inspection()


if __name__ == "__main__":
    main()
