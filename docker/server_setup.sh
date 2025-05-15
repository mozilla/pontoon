#!/bin/sh

# Runs steps needed only once for the server

cd /app

echo "Creating a new django superuser"
python manage.py createsuperuser

echo "Updating authentication provider settings"
python manage.py update_auth_providers