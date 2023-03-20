#!/bin/bash

echo "out/logs is going into '/app/server_run.log'"

# user pontoon stuff --> get env vars
(echo ">>> running as user: " && whoami) >> /app/server_run.log
if [ ! -z "$SSH_KEY" ]; then
    echo ">>> loading ssh key and kown_hosts for default user pontoon..." >> /app/server_run.log
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
    echo "...done." >> /app/server_run.log
fi

echo ">>> Setting up the db for Django" >> /app/server_run.log
python manage.py migrate >> /app/server_run.log

echo ">>> Starting local server as user pontoon" >> /app/server_run.log
exec python manage.py runserver 0.0.0.0:8000
