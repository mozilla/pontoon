#!/bin/bash

#user pontoon stuff --> get enc vars
(echo ">>> running as user: " && whoami)
if [ ! -z "$SSH_KEY" ]; then
    echo ">>> loading ssh key and kown_hosts for default user pontoon..."
    mkdir ~/.ssh
    chmod 700 ~/.ssh

    # To preserve newlines, the env var is base64 encoded. Flip it back.
    echo $SSH_KEY | base64 -d > ~/.ssh/id_rsa
    echo $KNOWN_HOSTS | base64 -d > ~/.ssh/known_hosts
    echo $SSH_CONFIG | base64 -d > ~/.ssh/config

    chmod 400 ~/.ssh/id_rsa ~/.ssh/known_hosts 
    chown -R $(whoami):$(whoami) ~/.ssh/
    echo "...done."
fi

# Prepares then runs the server

env > .env

echo ">>> Setting up the db for Django"
python manage.py migrate

echo ">>> Starting gunicorn"
gunicorn pontoon.wsgi:application -t 120 --log-file - --log-level info -b 0.0.0.0:8000 --workers=${GUNICORN_WORKERS:-5} --threads=${GUNICORN_THREADS:-2} &
echo ">>> Starting celery worker"
celery worker --app=pontoon.base.celeryapp --loglevel=info --without-gossip --without-mingle --without-heartbeat --concurrency=${CELERY_CONCURRENCY:-10}
