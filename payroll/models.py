from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile with organization information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization_name = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"{self.user.username} - {self.organization_name or 'No Organization'}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save user profile when user is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class PayrollUpload(models.Model):
    """Model to track uploaded payroll files"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payroll_uploads')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_employees = models.IntegerField(default=0)
    upload_date = models.DateTimeField(default=timezone.now)
    processed_date = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-upload_date']
        db_table = 'payroll_uploads'
    
    @property
    def employees_count(self):
        """Count of unique employees in this upload"""
        return self.salary_components.values('employee').distinct().count()
    
    def __str__(self):
        return f"{self.filename} - {self.status}"


class Employee(models.Model):
    """Model to store unique employee information"""
    
    employee_id = models.CharField(max_length=50, unique=True)  # Unique across all uploads
    name = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
    
    def __str__(self):
        return f"{self.employee_id} - {self.name}"


class SalaryComponent(models.Model):
    """Model to store salary components for each employee per upload/period"""
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_records')
    upload = models.ForeignKey(PayrollUpload, on_delete=models.CASCADE, related_name='salary_components', null=True, blank=True)
    salary_month = models.DateField(null=True, blank=True)  # For which month this salary is for
    
    # Earnings
    basic_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    variable_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Calculated values
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Deductions
    provident_fund = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Final amounts
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    take_home_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'salary_components'
        unique_together = ['employee', 'upload', 'salary_month']  # Prevent duplicate salary for same employee in same upload/month
    
    def calculate_salary(self):
        """Calculate all salary components"""
        from decimal import Decimal
        
        # Calculate gross salary
        self.gross_salary = (
            self.basic_pay + 
            self.hra + 
            self.variable_pay + 
            self.special_allowance + 
            self.other_allowances
        )
        
        # Calculate deductions (simplified model)
        # PF: 12% of basic pay
        self.provident_fund = self.basic_pay * Decimal('0.12')
        
        # Professional Tax: Fixed amount (example: 200 for salaries above 15000)
        if self.gross_salary > 15000:
            self.professional_tax = Decimal('200.00')
        else:
            self.professional_tax = Decimal('0.00')
        
        # Income Tax: Simplified progressive tax (monthly calculation)
        annual_gross = self.gross_salary * 12
        if annual_gross <= 250000:
            self.income_tax = Decimal('0.00')
        elif annual_gross <= 500000:
            annual_tax = (annual_gross - Decimal('250000')) * Decimal('0.05')
            self.income_tax = annual_tax / 12
        elif annual_gross <= 1000000:
            annual_tax = Decimal('12500') + (annual_gross - Decimal('500000')) * Decimal('0.20')
            self.income_tax = annual_tax / 12
        else:
            annual_tax = Decimal('112500') + (annual_gross - Decimal('1000000')) * Decimal('0.30')
            self.income_tax = annual_tax / 12
        
        # Total deductions
        self.total_deductions = (
            self.provident_fund + 
            self.professional_tax + 
            self.income_tax + 
            self.other_deductions
        )
        
        # Net salary and take-home pay
        self.net_salary = self.gross_salary - self.total_deductions
        self.take_home_pay = self.net_salary
        
        self.save()
    
    def __str__(self):
        return f"Salary for {self.employee.name} - {self.salary_month}"


class PayrollReport(models.Model):
    """Model to track generated reports"""
    
    REPORT_TYPE_CHOICES = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    upload = models.ForeignKey(PayrollUpload, on_delete=models.CASCADE, related_name='reports')
    report_type = models.CharField(max_length=10, choices=REPORT_TYPE_CHOICES)
    file = models.FileField(upload_to='reports/%Y/%m/%d/')
    generated_date = models.DateTimeField(default=timezone.now)
    file_size = models.IntegerField(default=0)  # in bytes
    
    class Meta:
        db_table = 'payroll_reports'
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.report_type} report for {self.upload.filename}"