#!/bin/bash

# Prepares then runs the webapp.

echo "Install latest npm modules"
cd /app
npm install

echo "Setting up the db for Django"
python manage.py migrate

echo "Running webapp. Connect with browser using http://localhost:8000/ ."
python manage.py runserver 0.0.0.0:8000
