#!/bin/bash

# Prepares then runs the webapp.

echo "Install latest npm modules"
cd /app
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use node
npm install .

echo "Prepare revision file"
git rev-parse HEAD > static/revision.txt

echo "Setting up the db for Django"
python manage.py migrate

echo "Running webapp. Connect with browser using http://localhost:8000/ ."
python manage.py runserver 0.0.0.0:8000
