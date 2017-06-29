#!/bin/sh

# Runs steps needed only once for the webapp.

cd /app

echo "Creating a new django superuser"
python manage.py createsuperuser

echo "Updating Firefox Account provider settings"
python manage.py updatefxaprovider
