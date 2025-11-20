# Custom migration to safely add user field to Employee model
# This handles the case where the column might already exist in production

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


def add_user_field_if_not_exists(apps, schema_editor):
    """
    Safely add user field only if it doesn't exist
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if user_id column exists in employees table
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'user_id'
            AND table_schema = 'public';
        """)
        
        result = cursor.fetchone()
        
        if not result:
            # Column doesn't exist, safe to add it
            cursor.execute("""
                ALTER TABLE employees 
                ADD COLUMN user_id INTEGER;
            """)
            # Add foreign key constraint separately
            cursor.execute("""
                ALTER TABLE employees 
                ADD CONSTRAINT employees_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;
            """)
            print("Added user_id column to employees table")
        else:
            print("user_id column already exists in employees table")


def remove_user_field_if_exists(apps, schema_editor):
    """
    Safely remove user field if it exists
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # Check if user_id column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'employees' AND column_name = 'user_id'
            AND table_schema = 'public';
        """)
        
        result = cursor.fetchone()
        
        if result:
            # First drop the foreign key constraint if it exists
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints tc
                WHERE tc.table_name = 'employees' 
                AND tc.constraint_type = 'FOREIGN KEY'
                AND tc.constraint_name LIKE '%user_id%';
            """)
            fk_constraint = cursor.fetchone()
            if fk_constraint:
                cursor.execute(f"ALTER TABLE employees DROP CONSTRAINT {fk_constraint[0]};")
            
            cursor.execute("ALTER TABLE employees DROP COLUMN user_id;")
            print("Removed user_id column from employees table")


def populate_user_field_safe(apps, schema_editor):
    """
    Safely populate user field for existing employees
    """
    from django.db import connection
    
    # First check if there are any employees without user_id
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM employees WHERE user_id IS NULL;")
        null_user_count = cursor.fetchone()[0]
        
        if null_user_count > 0:
            print(f"Found {null_user_count} employees without user_id")
            
            # Get the first available user
            cursor.execute("SELECT id FROM auth_user ORDER BY id LIMIT 1;")
            first_user = cursor.fetchone()
            
            if first_user:
                first_user_id = first_user[0]
                
                # Try to populate based on salary components first
                cursor.execute("""
                    UPDATE employees 
                    SET user_id = (
                        SELECT DISTINCT pu.user_id 
                        FROM salary_components sc 
                        JOIN payroll_uploads pu ON sc.upload_id = pu.id 
                        WHERE sc.employee_id = employees.id 
                        LIMIT 1
                    )
                    WHERE user_id IS NULL 
                    AND EXISTS (
                        SELECT 1 FROM salary_components sc 
                        WHERE sc.employee_id = employees.id
                    );
                """)
                
                # For any remaining employees, assign to first user
                cursor.execute(
                    "UPDATE employees SET user_id = %s WHERE user_id IS NULL;",
                    [first_user_id]
                )
                print("Populated user_id for existing employees")
            else:
                print("No users found - cannot populate user_id")
        else:
            print("All employees already have user_id")


def make_user_field_required_safe(apps, schema_editor):
    """
    Safely make user field required and add constraints
    """
    from django.db import connection
    
    with connection.cursor() as cursor:
        # First make the field NOT NULL
        cursor.execute("ALTER TABLE employees ALTER COLUMN user_id SET NOT NULL;")
        
        # Check if unique constraint already exists
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints tc
            WHERE tc.table_name = 'employees' 
            AND tc.constraint_type = 'UNIQUE'
            AND tc.constraint_name LIKE '%user_id%employee_id%';
        """)
        
        if not cursor.fetchone():
            # Add unique constraint on (user_id, employee_id)
            cursor.execute("""
                ALTER TABLE employees 
                ADD CONSTRAINT payroll_employee_user_id_employee_id_unique 
                UNIQUE (user_id, employee_id);
            """)
            print("Added unique constraint on (user_id, employee_id)")
        else:
            print("Unique constraint already exists")


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payroll', '0009_merge_20251120_1103'),
    ]

    operations = [
        migrations.RunPython(
            add_user_field_if_not_exists,
            remove_user_field_if_exists,
        ),
        migrations.RunPython(
            populate_user_field_safe,
            migrations.RunPython.noop,
        ),
        migrations.RunPython(
            make_user_field_required_safe,
            migrations.RunPython.noop,
        ),
    ]
