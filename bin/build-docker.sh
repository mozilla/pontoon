#!/bin/bash
# Build an instance of the site using docker-compose.
set -e
docker-compose build
docker-compose run web ./bin/wait-for-db.sh ./bin/run-migrations.sh
docker-compose run web ./bin/wait-for-db.sh ./manage.py update_projects
