from django.contrib import admin
from .models import PayrollUpload, Employee, SalaryComponent, PayrollReport


@admin.register(PayrollUpload)
class PayrollUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'user', 'status', 'total_employees', 'upload_date']
    list_filter = ['status', 'upload_date']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['upload_date', 'processed_date']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'email', 'department', 'designation', 'upload']
    list_filter = ['department', 'designation']
    search_fields = ['employee_id', 'name', 'email']


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'gross_salary', 'total_deductions', 
        'net_salary', 'take_home_pay'
    ]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PayrollReport)
class PayrollReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'report_type', 'generated_date', 'file_size']
    list_filter = ['report_type', 'generated_date']
    readonly_fields = ['generated_date']