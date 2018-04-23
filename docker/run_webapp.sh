#!/bin/bash

# Prepares then runs the webapp.

echo ">>> Prepare revision file"
git rev-parse HEAD > static/revision.txt

echo ">>> Setting up the db for Django"
python manage.py migrate

echo ">>> Starting local server"
python manage.py runserver 0.0.0.0:8000
