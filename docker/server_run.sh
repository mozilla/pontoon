#!/bin/bash

# Prepares then runs the server.
# Git authentication is HTTPS-only: provide a read-only token via a
# .gitconfig url.<base>.insteadOf rewrite in the GIT_CONFIG env var, e.g.
#   [url "https://x-access-token:<TOKEN>@github.com/"]
#       insteadOf = https://github.com/
if [ ! -z "$GIT_CONFIG" ]; then
    echo ">>> writing .gitconfig for default user pontoon..."
    echo -n "$GIT_CONFIG" > /home/pontoon/.gitconfig
    chmod 400 /home/pontoon/.gitconfig
    chown pontoon:pontoon /home/pontoon/.gitconfig
    echo "...done"
fi

echo ">>> Setting up the db for Django"
python manage.py migrate

echo ">>> Starting local server..."
exec python manage.py runserver 0.0.0.0:8000
