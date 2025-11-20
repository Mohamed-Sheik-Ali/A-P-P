# Quick fix for Digital Ocean deployment
# Run this command before your regular build process

# Clear migration state
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_config.settings')
django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute('DELETE FROM django_migrations WHERE app = \\'payroll\\';')
    c.execute('INSERT INTO django_migrations (app, name, applied) VALUES (\\'payroll\\', \\'0001_initial\\', NOW());')
print('Migration state fixed')
"
