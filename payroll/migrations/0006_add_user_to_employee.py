# Generated migration for adding user field to Employee model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payroll', '0005_userprofile'),
    ]

    operations = [
        # Step 1: Add user field as nullable first
        migrations.AddField(
            model_name='employee',
            name='user',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='employees', to=settings.AUTH_USER_MODEL),
        ),
        
        # Step 2: Remove the old unique constraint on employee_id
        migrations.AlterField(
            model_name='employee',
            name='employee_id',
            field=models.CharField(max_length=50),
        ),
        
        # Step 3: Data migration will be handled in the next step
        
        # Step 4: Make user field non-nullable and add unique constraint
        migrations.AlterField(
            model_name='employee',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to=settings.AUTH_USER_MODEL),
        ),
        
        # Step 5: Add unique constraint on (user, employee_id)
        migrations.AlterUniqueTogether(
            name='employee',
            unique_together={('user', 'employee_id')},
        ),
    ]
