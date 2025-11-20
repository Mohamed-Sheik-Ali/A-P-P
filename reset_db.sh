#!/bin/bash

# Database reset script for Digital Ocean
# This completely resets the database and applies fresh migrations

echo "=== Resetting Database ==="

# Drop all tables (this will delete all data!)
echo "Dropping all payroll tables..."
python manage.py dbshell << EOF
DROP TABLE IF EXISTS salary_components CASCADE;
DROP TABLE IF EXISTS payroll_reports CASCADE;
DROP TABLE IF EXISTS payroll_uploads CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
DELETE FROM django_migrations WHERE app = 'payroll';
EOF

# Apply fresh migrations
echo "Applying fresh migrations..."
python manage.py migrate

echo "Database reset complete!"
