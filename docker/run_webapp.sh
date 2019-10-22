#!/bin/bash

# Prepares then runs the webapp.

echo ">>> Setting up the db for Django"
python manage.py migrate

echo ">>> Starting frontend build process in the background"
cd frontend && yarn start &

echo ">>> Starting local server"
python manage.py runserver 0.0.0.0:8000
