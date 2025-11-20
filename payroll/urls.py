from django.urls import path
from .views import (
    # Authentication views
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    ChangePasswordView,
    CheckAuthView,
    
    # Payroll views
    PayrollUploadView,
    PayrollUploadDetailView,
    EmployeeListView,
    EmployeeDetailView,
    EmployeeExportView,
    GenerateReportView,
    ReportListView,
    ReportDetailView,
    DashboardStatsView,
    ValidateUploadView,
    api_documentation,
    
    # Admin views
    AdminUserApprovalView,
    AdminApproveUserView,
    AdminRejectUserView,
    AdminUserStatsView,
)
from .admin_views import PendingUsersView, quick_approve_user, quick_reject_user

app_name = 'payroll'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/', UserLogoutView.as_view(), name='logout'),
    path('auth/check/', CheckAuthView.as_view(), name='check-auth'),
    
    # User profile endpoints
    path('user/profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Dashboard
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    
    # Payroll upload endpoints
    path('uploads/', PayrollUploadView.as_view(), name='payroll-upload-list'),
    path('uploads/<int:upload_id>/', PayrollUploadDetailView.as_view(), name='payroll-upload-detail'),
    path('uploads/validate/', ValidateUploadView.as_view(), name='validate-upload'),
    
    # Employee endpoints
    path('uploads/<int:upload_id>/employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:employee_id>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:employee_id>/export/', EmployeeExportView.as_view(), name='employee-export'),
    
    # Report endpoints
    path('uploads/<int:upload_id>/reports/generate/', GenerateReportView.as_view(), name='generate-report'),
    path('reports/', ReportListView.as_view(), name='report-list'),
    path('reports/<int:report_id>/', ReportDetailView.as_view(), name='report-detail'),
    
    # Admin endpoints for user approval
    path('admin/users/', AdminUserApprovalView.as_view(), name='admin-user-list'),
    path('admin/users/<int:user_id>/approve/', AdminApproveUserView.as_view(), name='admin-approve-user'),
    path('admin/users/<int:user_id>/reject/', AdminRejectUserView.as_view(), name='admin-reject-user'),
    path('admin/users/stats/', AdminUserStatsView.as_view(), name='admin-user-stats'),
    
    # Custom admin panel views
    path('admin-panel/pending-users/', PendingUsersView.as_view(), name='admin-pending-users'),
    path('admin-panel/approve-user/<int:user_id>/', quick_approve_user, name='admin-quick-approve-user'),
    path('admin-panel/reject-user/<int:user_id>/', quick_reject_user, name='admin-quick-reject-user'),

    path('', api_documentation, name='api-docs'),
]