#!/bin/bash
echo "out/logs is going into '/app/server_run.log'"

#user pontoon stuff --> get enc vars
(echo ">>> running as user: " && whoami) >> /app/server_run.log
if [ ! -z "$SSH_KEY" ]; then
    echo ">>> loading ssh key and kown_hosts for default user pontoon..." >> /app/server_run.log
    mkdir /home/pontoon/.ssh
    chmod 700 /home/pontoon/.ssh

    # To preserve newlines, the env var is base64 encoded. Flip it back.
    echo $SSH_KEY | base64 -d > /home/pontoon/.ssh/id_rsa
    chmod 400 /home/pontoon/.ssh/id_rsa 
    # do the same to known_hosts
    echo $KNOWN_HOSTS | base64 -d > /home/pontoon/.ssh/known_hosts
    chmod 400 /home/pontoon/.ssh/known_hosts 
    chown -R pontoon:pontoon /home/pontoon/.ssh/
    echo "...done." >> /app/server_run.log
fi

echo ">>> Setting up the db for Django" >> /app/server_run.log
python manage.py migrate >> /app/server_run.log

echo ">>> Starting frontend build process in the background" >> /app/server_run.log
cd frontend && npm start &

# syncing projects if env SYNC_INTERVAL is set, if it is set and you need to "work" on the bash, kill the process syncprojects.sh
echo ">>> starting continuos syncing projects" >> /app/server_run.log
/app/docker/syncprojects.sh &

echo ">>> Starting local server as user pontoon" >> /app/server_run.log
python manage.py runserver 0.0.0.0:8000

