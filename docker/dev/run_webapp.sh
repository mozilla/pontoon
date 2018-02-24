#!/bin/bash

# Prepares then runs the webapp.

echo "Install latest npm modules"
cd /app
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use node
npm install .

echo "Prepare revision file"
mkdir -p static
git rev-parse HEAD > static/revision.txt

echo "Setting up the db for Django"
python manage.py migrate

echo "Webpacking resources"
./node_modules/.bin/webpack

echo "Collecting some static"
python manage.py collectstatic -v0 --no-input

echo "Checking build status"
buildlock="./.docker-build"
if [ ! -e "$buildlock" ]; then
  echo "Initializing the database"
  echo "Creating a new django superuser"
  python manage.py createsuperuser

  echo "Updating Firefox Account provider settings"
  python manage.py updatefxaprovider

  echo "Running migration of the pontoon-intro module"
  python manage.py sync_projects --projects=pontoon-intro --no-commit

  touch $buildlock
fi

echo "Running webapp. Connect with browser using http://localhost:8000/ ."
python manage.py runserver 0.0.0.0:8000
