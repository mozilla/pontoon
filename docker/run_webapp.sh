#!/bin/bash

# Prepares then runs the webapp.

echo "Install latest npm modules"
cd /app
npm install

echo "Setting up the db for Django"
python manage.py migrate

echo "Collect static assets"
python manage.py collectstatic --noinput

# Note: this should be a one-off, but if that project is already synced,
# it will simply not do anything and won't complain about it.
echo "Running migration of the pontoon-intro module"
python manage.py sync_projects --projects=pontoon-intro --no-commit

echo "Running webapp. Connect with browser using http://localhost:8000/ ."
python manage.py runserver 0.0.0.0:8000
