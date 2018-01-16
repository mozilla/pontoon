#!/bin/sh

# Runs steps needed only once for the webapp.

cd /app

echo "Creating a new django superuser"
python manage.py createsuperuser

echo "Updating Firefox Account provider settings"
python manage.py updatefxaprovider

echo "Running migration of the pontoon-intro module"
python manage.py sync_projects --projects=pontoon-intro --no-commit

echo 'getting nvm/node/npm'
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" # This loads nvm
nvm install node
