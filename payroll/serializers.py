from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import PayrollUpload, Employee, SalaryComponent, PayrollReport, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )
    organization_name = serializers.CharField(
        max_length=200,
        required=False,
        allow_blank=True,
        help_text='Your company/organization name'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2', 'organization_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        """Create new user with organization profile"""
        organization_name = validated_data.pop('organization_name', '')
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        
        # Update the user profile with organization name
        if hasattr(user, 'profile'):
            user.profile.organization_name = organization_name
            user.profile.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate user credentials"""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "username" and "password".',
                code='authorization'
            )


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    organization_name = serializers.CharField(source='profile.organization_name', read_only=True)
    approval_status = serializers.CharField(source='profile.approval_status', read_only=True)
    approval_status_display = serializers.CharField(source='profile.get_approval_status_display', read_only=True)
    is_approved = serializers.BooleanField(source='profile.is_approved', read_only=True)
    approved_by = serializers.CharField(source='profile.approved_by.username', read_only=True)
    approval_date = serializers.DateTimeField(source='profile.approval_date', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login', 
            'organization_name', 'approval_status', 'approval_status_display', 'is_approved',
            'approved_by', 'approval_date'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='Confirm New Password'
    )
    
    def validate(self, attrs):
        """Validate passwords"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class SalaryComponentSerializer(serializers.ModelSerializer):
    """Serializer for salary components"""
    
    class Meta:
        model = SalaryComponent
        fields = [
            'basic_pay', 'hra', 'variable_pay', 'special_allowance', 
            'other_allowances', 'gross_salary', 'provident_fund', 
            'professional_tax', 'income_tax', 'other_deductions',
            'total_deductions', 'net_salary', 'take_home_pay'
        ]


class EmployeeSerializer(serializers.ModelSerializer):
    """Serializer for employee with salary details"""
    
    salary = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'name', 'email', 
            'department', 'designation', 'salary'
        ]
    
    def get_salary(self, obj):
        """Get salary component for this employee and upload"""
        # Get the upload_id from context if available
        upload_id = self.context.get('upload_id')
        if upload_id:
            try:
                salary_component = SalaryComponent.objects.get(employee=obj, upload_id=upload_id)
                return SalaryComponentSerializer(salary_component).data
            except SalaryComponent.DoesNotExist:
                return None
        
        # If no upload context, get the latest salary record
        latest_salary = obj.salary_records.first()
        if latest_salary:
            return SalaryComponentSerializer(latest_salary).data
        return None


class PayrollUploadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    employees_count = serializers.IntegerField(read_only=True)
    total_amount_processed = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollUpload
        fields = [
            'id', 'user', 'file', 'filename', 'status', 
            'total_employees', 'employees_count', 'total_amount_processed',
            'upload_date', 'processed_date', 'error_message'
        ]
    
    def get_total_amount_processed(self, obj):
        """Calculate total net salary for all employees in this upload"""
        from django.db.models import Sum
        from decimal import Decimal
        
        total = obj.salary_components.aggregate(
            total=Sum('net_salary')
        )['total']
        
        return float(total) if total else 0.0

class PayrollUploadDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for payroll upload with employees"""
    
    user = UserSerializer(read_only=True)
    employees = serializers.SerializerMethodField()
    
    class Meta:
        model = PayrollUpload
        fields = [
            'id', 'user', 'file', 'filename', 'status', 
            'total_employees', 'upload_date', 'processed_date', 
            'error_message', 'employees'
        ]
    
    def get_employees(self, obj):
        """Get all employees for this upload with their salary data"""
        # Get all employees who have salary components in this upload
        employee_ids = obj.salary_components.values_list('employee_id', flat=True).distinct()
        employees = Employee.objects.filter(id__in=employee_ids)
        
        # Pass upload_id in context for salary lookup
        context = self.context.copy()
        context['upload_id'] = obj.id
        
        return EmployeeSerializer(employees, many=True, context=context).data


class PayrollReportSerializer(serializers.ModelSerializer):
    """Serializer for payroll reports"""

    upload = PayrollUploadSerializer(read_only=True)
    file_size_kb = serializers.SerializerMethodField()

    class Meta:
        model = PayrollReport
        fields = [
            'id', 'upload', 'report_type', 'file',
            'generated_date', 'file_size', 'file_size_kb'
        ]

    def get_file_size_kb(self, obj):
        """Convert file size to KB"""
        return round(obj.file_size / 1024, 2)


class ForgotPasswordRequestSerializer(serializers.Serializer):
    """Serializer for forgot password request"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate that email exists"""
        try:
            user = User.objects.get(email=value)

            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError(
                    "Your account is not active. Please contact support."
                )

            # Check if user has profile and is approved (skip for superusers)
            if not user.is_superuser:
                if not hasattr(user, 'profile'):
                    raise serializers.ValidationError(
                        "Account profile not found. Please contact support."
                    )

                if not user.profile.is_approved:
                    status_messages = {
                        'pending': 'Your account is pending admin approval. Please wait for approval before resetting password.',
                        'rejected': 'Your account has been rejected. Please contact support.'
                    }
                    message = status_messages.get(
                        user.profile.approval_status,
                        'Your account is not approved. Please contact support.'
                    )
                    raise serializers.ValidationError(message)

            return value

        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No account found with this email address."
            )


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset with token"""

    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        label='Confirm New Password'
    )

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs