#!/bin/sh

# Runs steps needed only once for the server

cd /app

echo "Creating a new django superuser"
python manage.py createsuperuser
