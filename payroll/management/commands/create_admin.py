"""
Django management command to create admin superuser
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create admin superuser for user approval management'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Admin username')
        parser.add_argument('--email', type=str, help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        username = options.get('username') or 'admin'
        email = options.get('email') or 'admin@example.com'
        password = options.get('password') or 'admin123'

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'Admin user "{username}" already exists')
            )
            return

        # Create superuser
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='System',
            last_name='Administrator'
        )

        # Ensure profile is created and approved
        if hasattr(admin_user, 'profile'):
            admin_user.profile.approval_status = 'approved'
            admin_user.profile.organization_name = 'System Administration'
            admin_user.profile.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created admin user "{username}"')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Email: {email}')
        )
        self.stdout.write(
            self.style.SUCCESS('This user can approve/reject new registrations')
        )
