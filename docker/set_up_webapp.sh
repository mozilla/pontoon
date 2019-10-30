#!/bin/sh

# Runs steps needed only once for the webapp.

cd /app

echo "Creating a new django superuser"
python manage.py createsuperuser

echo "Updating authentication provider settings"
python manage.py update_auth_providers

echo "Running migration of the pontoon-intro module"
python manage.py sync_projects --projects=pontoon-intro --no-commit
