# Data migration to populate user field for existing employees

from django.db import migrations
from django.db import transaction


def populate_employee_users(apps, schema_editor):
    """
    Populate the user field for existing employees by looking at their salary components
    and finding which user uploaded them.
    """
    Employee = apps.get_model('payroll', 'Employee')
    SalaryComponent = apps.get_model('payroll', 'SalaryComponent')
    PayrollUpload = apps.get_model('payroll', 'PayrollUpload')
    
    with transaction.atomic():
        for employee in Employee.objects.filter(user__isnull=True):
            # Find the first salary component for this employee
            salary = SalaryComponent.objects.filter(employee=employee).first()
            
            if salary and salary.upload:
                # Set the employee's user to the upload's user
                employee.user = salary.upload.user
                employee.save()
                print(f"Assigned employee {employee.employee_id} to user {salary.upload.user.username}")
            else:
                # If no salary component or upload found, we need to handle this case
                # For now, we'll assign to the first user or delete the employee
                from django.contrib.auth.models import User
                first_user = User.objects.first()
                if first_user:
                    employee.user = first_user
                    employee.save()
                    print(f"Assigned orphaned employee {employee.employee_id} to first user {first_user.username}")
                else:
                    # If no users exist, delete the employee
                    print(f"Deleting orphaned employee {employee.employee_id} (no users found)")
                    employee.delete()


def reverse_populate_employee_users(apps, schema_editor):
    """
    Reverse the migration by setting user field to null.
    """
    Employee = apps.get_model('payroll', 'Employee')
    Employee.objects.all().update(user=None)


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0006_add_user_to_employee'),
    ]

    operations = [
        migrations.RunPython(
            populate_employee_users,
            reverse_populate_employee_users,
        ),
    ]
