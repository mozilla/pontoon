#!/bin/bash

# Prepares then runs the server
if [ ! -z "$SSH_KEY" ]; then
    echo ">>> loading ssh key and kown_hosts for default user pontoon..."
    mkdir /home/pontoon/.ssh
    chmod 700 /home/pontoon/.ssh

    # To preserve newlines, the env var is base64 encoded. Flip it back.
    echo -n "$SSH_KEY" > /home/pontoon/.ssh/id_ed25519
    chmod 400 /home/pontoon/.ssh/id_ed25519
    # do the same to known_hosts
    echo -n "$KNOWN_HOSTS" > /home/pontoon/.ssh/known_hosts
    chmod 400 /home/pontoon/.ssh/known_hosts
    # do the same to .gitconfig
    echo -n "$GIT_CONFIG" > /home/pontoon/.gitconfig
    chmod 400 /home/pontoon/.gitconfig

    chown -R pontoon:pontoon /home/pontoon/.ssh/
    echo "...done"
fi

echo ">>> Setting up the db for Django"
python manage.py migrate

echo ">>> Starting local server..."
exec python manage.py runserver 0.0.0.0:8000
