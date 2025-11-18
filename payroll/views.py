from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.utils import timezone

from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)
from .jwt_utils import generate_jwt_token


class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    POST: Register a new user
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT token
            token = generate_jwt_token(user)
            
            # Login the user
            login(request, user)
            
            return Response({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'user': UserSerializer(user).data,
                    'token': token
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Registration failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    API endpoint for user login
    POST: Login user with credentials
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate JWT token
            token = generate_jwt_token(user)
            
            # Login the user (creates session)
            login(request, user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'data': {
                    'user': UserSerializer(user).data,
                    'token': token
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Login failed',
            'errors': serializer.errors
        }, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    POST: Logout current user
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        logout(request)
        
        return Response({
            'success': True,
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    API endpoint for user profile
    GET: Get current user profile
    PUT: Update current user profile
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Profile updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Profile update failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    API endpoint for changing password
    POST: Change user password
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            # Generate new token after password change
            token = generate_jwt_token(user)
            
            return Response({
                'success': True,
                'message': 'Password changed successfully',
                'data': {
                    'token': token
                }
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'message': 'Password change failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CheckAuthView(APIView):
    """
    API endpoint to check if user is authenticated
    GET: Check authentication status
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'success': True,
            'authenticated': True,
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    

from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction
import os
from .models import PayrollUpload, Employee, SalaryComponent, PayrollReport
from .serializers import (
    PayrollUploadSerializer,
    PayrollUploadDetailSerializer,
    EmployeeSerializer,
    PayrollReportSerializer
)
from .utils import ExcelProcessor, ReportGenerator


class PayrollUploadView(APIView):
    """
    API endpoint for payroll file upload
    POST: Upload Excel file for processing
    GET: List all uploads for current user
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'message': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Validate file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({
                'success': False,
                'message': 'Invalid file format. Please upload an Excel file (.xlsx or .xls)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            return Response({
                'success': False,
                'message': 'File size exceeds 10MB limit'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create upload record
            with transaction.atomic():
                upload = PayrollUpload.objects.create(
                    user=request.user,
                    file=file,
                    filename=file.name,
                    status='pending'
                )
                
                # Process file
                processor = ExcelProcessor(upload.file.path, upload)
                
                # Validate file
                if not processor.validate_file():
                    upload.status = 'failed'
                    upload.error_message = '; '.join(processor.errors)
                    upload.save()
                    
                    return Response({
                        'success': False,
                        'message': 'File validation failed',
                        'errors': processor.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Update status to processing
                upload.status = 'processing'
                upload.save()
                
                # Parse and save data
                success, employees_count = processor.parse_and_save()
                
                if not success:
                    return Response({
                        'success': False,
                        'message': 'File processing failed',
                        'errors': processor.errors,
                        'warnings': processor.warnings
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Refresh upload instance
                upload.refresh_from_db()
                
                return Response({
                    'success': True,
                    'message': f'File processed successfully. {employees_count} employees loaded.',
                    'data': PayrollUploadSerializer(upload).data,
                    'warnings': processor.warnings if processor.warnings else None
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error processing file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get all uploads for current user"""
        uploads = PayrollUpload.objects.filter(user=request.user)
        serializer = PayrollUploadSerializer(uploads, many=True)
        
        return Response({
            'success': True,
            'count': uploads.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class PayrollUploadDetailView(APIView):
    """
    API endpoint for payroll upload details
    GET: Get details of a specific upload with all employees
    DELETE: Delete an upload
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, upload_id):
        try:
            upload = PayrollUpload.objects.get(id=upload_id, user=request.user)
            serializer = PayrollUploadDetailSerializer(upload)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except PayrollUpload.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, upload_id):
        try:
            upload = PayrollUpload.objects.get(id=upload_id, user=request.user)
            
            # Delete associated file
            if upload.file:
                if os.path.isfile(upload.file.path):
                    os.remove(upload.file.path)
            
            upload.delete()
            
            return Response({
                'success': True,
                'message': 'Upload deleted successfully'
            }, status=status.HTTP_200_OK)
            
        except PayrollUpload.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)


class EmployeeListView(APIView):
    """
    API endpoint to list employees for a specific upload
    GET: Get all employees with salary details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, upload_id):
        try:
            upload = PayrollUpload.objects.get(id=upload_id, user=request.user)
            employees = Employee.objects.filter(upload=upload).select_related('salary')
            
            serializer = EmployeeSerializer(employees, many=True)
            
            return Response({
                'success': True,
                'count': employees.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except PayrollUpload.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)


class EmployeeDetailView(APIView):
    """
    API endpoint for individual employee details
    GET: Get employee details with salary breakdown
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, employee_id):
        try:
            employee = Employee.objects.select_related('salary', 'upload').get(
                id=employee_id,
                upload__user=request.user
            )
            
            serializer = EmployeeSerializer(employee)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Employee.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)


class GenerateReportView(APIView):
    """
    API endpoint to generate payroll reports
    POST: Generate report for a specific upload
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, upload_id):
        try:
            upload = PayrollUpload.objects.get(id=upload_id, user=request.user)
            
            # Check if upload is completed
            if upload.status != 'completed':
                return Response({
                    'success': False,
                    'message': 'Cannot generate report. Upload is not completed yet.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get report type from request
            report_type = request.data.get('report_type', 'excel')
            
            if report_type not in ['excel', 'pdf']:
                return Response({
                    'success': False,
                    'message': 'Invalid report type. Choose "excel" or "pdf"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate report
            generator = ReportGenerator(upload)
            
            if report_type == 'excel':
                report = generator.generate_excel_report()
            else:
                report = generator.generate_pdf_report()
            
            serializer = PayrollReportSerializer(report)
            
            return Response({
                'success': True,
                'message': f'{report_type.upper()} report generated successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except PayrollUpload.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Upload not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReportListView(APIView):
    """
    API endpoint to list all generated reports
    GET: List all reports for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        reports = PayrollReport.objects.filter(
            upload__user=request.user
        ).select_related('upload').order_by('-generated_date')
        
        serializer = PayrollReportSerializer(reports, many=True)
        
        return Response({
            'success': True,
            'count': reports.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class ReportDetailView(APIView):
    """
    API endpoint for report details and download
    GET: Get report details
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, report_id):
        try:
            report = PayrollReport.objects.select_related('upload').get(
                id=report_id,
                upload__user=request.user
            )
            
            serializer = PayrollReportSerializer(report)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except PayrollReport.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Report not found'
            }, status=status.HTTP_404_NOT_FOUND)


class DashboardStatsView(APIView):
    """
    API endpoint for dashboard statistics
    GET: Get overall statistics for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get all uploads
        uploads = PayrollUpload.objects.filter(user=user)
        
        # Calculate statistics
        total_uploads = uploads.count()
        completed_uploads = uploads.filter(status='completed').count()
        failed_uploads = uploads.filter(status='failed').count()
        processing_uploads = uploads.filter(status='processing').count()
        
        # Get total employees processed
        total_employees = Employee.objects.filter(upload__user=user).count()
        
        # Get total reports generated
        total_reports = PayrollReport.objects.filter(upload__user=user).count()
        
        # Get recent uploads (last 5)
        recent_uploads = uploads.order_by('-upload_date')[:5]
        
        # Calculate total salary disbursement
        from django.db.models import Sum
        total_disbursement = SalaryComponent.objects.filter(
            employee__upload__user=user
        ).aggregate(
            total=Sum('net_salary')
        )['total'] or 0
        
        return Response({
            'success': True,
            'data': {
                'uploads': {
                    'total': total_uploads,
                    'completed': completed_uploads,
                    'failed': failed_uploads,
                    'processing': processing_uploads
                },
                'employees': {
                    'total': total_employees
                },
                'reports': {
                    'total': total_reports
                },
                'disbursement': {
                    'total': float(total_disbursement)
                },
                'recent_uploads': PayrollUploadSerializer(recent_uploads, many=True).data
            }
        }, status=status.HTTP_200_OK)


class ValidateUploadView(APIView):
    """
    API endpoint to validate uploaded file without processing
    POST: Validate Excel file structure
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        if 'file' not in request.FILES:
            return Response({
                'success': False,
                'message': 'No file provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Validate file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({
                'success': False,
                'message': 'Invalid file format. Please upload an Excel file (.xlsx or .xls)'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Save temporary file
            temp_upload = PayrollUpload.objects.create(
                user=request.user,
                file=file,
                filename=file.name,
                status='pending'
            )
            
            # Validate file
            processor = ExcelProcessor(temp_upload.file.path, temp_upload)
            is_valid = processor.validate_file()
            
            # Delete temporary upload
            if temp_upload.file:
                if os.path.isfile(temp_upload.file.path):
                    os.remove(temp_upload.file.path)
            temp_upload.delete()
            
            if is_valid:
                return Response({
                    'success': True,
                    'message': 'File validation successful',
                    'warnings': processor.warnings if processor.warnings else None
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'success': False,
                    'message': 'File validation failed',
                    'errors': processor.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error validating file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from rest_framework.decorators import api_view, permission_classes

@api_view(['GET'])
@permission_classes([AllowAny])
def api_documentation(request):
    """API Documentation endpoint"""
    
    docs = {
        'version': '1.0',
        'title': 'Payroll Processor API',
        'description': 'API for automated payroll processing system',
        'endpoints': {
            'authentication': {
                'register': {
                    'url': '/api/auth/register/',
                    'method': 'POST',
                    'description': 'Register new HR user',
                    'auth_required': False
                },
                'login': {
                    'url': '/api/auth/login/',
                    'method': 'POST',
                    'description': 'Login HR user',
                    'auth_required': False
                },
                'logout': {
                    'url': '/api/auth/logout/',
                    'method': 'POST',
                    'description': 'Logout current user',
                    'auth_required': True
                },
                'check': {
                    'url': '/api/auth/check/',
                    'method': 'GET',
                    'description': 'Check authentication status',
                    'auth_required': True
                }
            },
            'profile': {
                'get_profile': {
                    'url': '/api/user/profile/',
                    'method': 'GET',
                    'description': 'Get user profile',
                    'auth_required': True
                },
                'update_profile': {
                    'url': '/api/user/profile/',
                    'method': 'PUT',
                    'description': 'Update user profile',
                    'auth_required': True
                },
                'change_password': {
                    'url': '/api/user/change-password/',
                    'method': 'POST',
                    'description': 'Change user password',
                    'auth_required': True
                }
            },
            'dashboard': {
                'stats': {
                    'url': '/api/dashboard/stats/',
                    'method': 'GET',
                    'description': 'Get dashboard statistics',
                    'auth_required': True
                }
            },
            'uploads': {
                'list': {
                    'url': '/api/uploads/',
                    'method': 'GET',
                    'description': 'List all uploads',
                    'auth_required': True
                },
                'create': {
                    'url': '/api/uploads/',
                    'method': 'POST',
                    'description': 'Upload and process Excel file',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/uploads/{id}/',
                    'method': 'GET',
                    'description': 'Get upload details with employees',
                    'auth_required': True
                },
                'delete': {
                    'url': '/api/uploads/{id}/',
                    'method': 'DELETE',
                    'description': 'Delete an upload',
                    'auth_required': True
                },
                'validate': {
                    'url': '/api/uploads/validate/',
                    'method': 'POST',
                    'description': 'Validate Excel file without processing',
                    'auth_required': True
                }
            },
            'employees': {
                'list': {
                    'url': '/api/uploads/{upload_id}/employees/',
                    'method': 'GET',
                    'description': 'List employees for an upload',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/employees/{id}/',
                    'method': 'GET',
                    'description': 'Get employee details',
                    'auth_required': True
                }
            },
            'reports': {
                'generate': {
                    'url': '/api/uploads/{upload_id}/reports/generate/',
                    'method': 'POST',
                    'description': 'Generate report (Excel or PDF)',
                    'auth_required': True
                },
                'list': {
                    'url': '/api/reports/',
                    'method': 'GET',
                    'description': 'List all generated reports',
                    'auth_required': True
                },
                'detail': {
                    'url': '/api/reports/{id}/',
                    'method': 'GET',
                    'description': 'Get report details',
                    'auth_required': True
                }
            }
        }
    }
    
    return Response(docs, status=status.HTTP_200_OK)