#!/bin/bash
# Sync and migrate the database.
./manage.py syncdb --noinput
./manage.py migrate
