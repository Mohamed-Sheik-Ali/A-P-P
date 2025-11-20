from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from .models import PayrollUpload, Employee, SalaryComponent, PayrollReport, UserProfile

# Customize admin site
admin.site.site_header = "Payroll System Administration"
admin.site.site_title = "Payroll Admin"
admin.site.index_title = "Welcome to Payroll Administration"


# Custom User Admin with UserProfile integration
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    fk_name = 'user'  # Specify which foreign key to use
    can_delete = False
    verbose_name_plural = 'User Profile'
    fields = ('organization_name', 'approval_status', 'approved_by', 'approval_date', 'rejection_reason')
    readonly_fields = ('approved_by', 'approval_date')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_approval_status', 'get_organization')
    list_filter = BaseUserAdmin.list_filter + ('profile__approval_status',)
    
    def get_approval_status(self, obj):
        try:
            status = obj.profile.approval_status
            color = {
                'pending': 'orange',
                'approved': 'green', 
                'rejected': 'red'
            }.get(status, 'gray')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color, 
                obj.profile.get_approval_status_display()
            )
        except UserProfile.DoesNotExist:
            return format_html('<span style="color: gray;">No Profile</span>')
    get_approval_status.short_description = 'Approval Status'
    
    def get_organization(self, obj):
        try:
            return obj.profile.organization_name or 'Not specified'
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_organization.short_description = 'Organization'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization_name', 'colored_approval_status', 'approved_by', 'approval_date', 'created_at')
    list_filter = ('approval_status', 'created_at', 'approval_date')
    search_fields = ('user__username', 'user__email', 'organization_name')
    readonly_fields = ('created_at', 'updated_at', 'approval_date')
    actions = ['approve_users', 'reject_users']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'organization_name')
        }),
        ('Approval Status', {
            'fields': ('approval_status', 'approved_by', 'approval_date', 'rejection_reason')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def colored_approval_status(self, obj):
        color = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red'
        }.get(obj.approval_status, 'gray')
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_approval_status_display()
        )
    colored_approval_status.short_description = 'Status'
    
    def approve_users(self, request, queryset):
        """Bulk approve selected users"""
        count = 0
        for profile in queryset.filter(approval_status='pending'):
            profile.approve(request.user)
            profile.save()
            count += 1
        
        self.message_user(
            request,
            f'{count} user(s) were successfully approved.',
            messages.SUCCESS
        )
    approve_users.short_description = "Approve selected users"
    
    def reject_users(self, request, queryset):
        """Bulk reject selected users"""
        count = 0
        for profile in queryset.filter(approval_status='pending'):
            profile.reject(request.user, "Rejected by admin")
            profile.save()
            count += 1
            
        self.message_user(
            request,
            f'{count} user(s) were successfully rejected.',
            messages.WARNING
        )
    reject_users.short_description = "Reject selected users"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'approved_by')


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(PayrollUpload)
class PayrollUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'filename', 'user', 'status', 'employees_count', 'upload_date']
    list_filter = ['status', 'upload_date', 'user']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['upload_date', 'processed_date']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all uploads for superusers, but scope for regular users
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'name', 'email', 'department', 'designation', 'user', 'created_at']
    list_filter = ['department', 'designation', 'created_at', 'user']
    search_fields = ['employee_id', 'name', 'email', 'user__username']
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Show all employees for superusers, but scope for regular users
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'salary_month', 'upload', 'gross_salary', 'total_deductions', 
        'net_salary', 'take_home_pay'
    ]
    list_filter = ['salary_month', 'upload', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PayrollReport)
class PayrollReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'report_type', 'generated_date', 'file_size']
    list_filter = ['report_type', 'generated_date']
    readonly_fields = ['generated_date']