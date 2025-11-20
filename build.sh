#!/bin/bash

# Build script for deployment

echo "Starting build process..."

# Install dependencies
pip install -r requirements.txt

# Fix migration state if needed
echo "Fixing migration state..."
python manage.py fix_migration_state || echo "Migration state already correct"

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Create admin user if it doesn't exist
echo "Creating admin user..."
python manage.py create_admin --username admin --email admin@payroll.com --password admin123 || echo "Admin user already exists"

echo "Build process completed successfully!"