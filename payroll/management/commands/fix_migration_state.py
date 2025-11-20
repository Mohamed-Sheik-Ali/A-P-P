"""
Management command to fix migration state conflicts
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Fix migration state by clearing old migration records'

    def handle(self, *args, **options):
        self.stdout.write('Fixing migration state...')
        
        with connection.cursor() as cursor:
            # Remove all payroll migration records
            cursor.execute(
                "DELETE FROM django_migrations WHERE app = 'payroll';"
            )
            
            # Mark the new initial migration as applied
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES ('payroll', '0001_initial', NOW());"
            )
        
        self.stdout.write(
            self.style.SUCCESS('Migration state fixed successfully!')
        )
