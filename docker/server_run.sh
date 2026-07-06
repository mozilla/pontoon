#!/bin/bash

# Prepares then runs the server.
#
# This script fails fast (non-zero exit) rather than hanging or starting a
# broken server when the database never becomes reachable or a migration fails.
set -euo pipefail

# Git authentication is HTTPS-only: provide a read-only token via a
# .gitconfig url.<base>.insteadOf rewrite in the GIT_CONFIG env var, e.g.
#   [url "https://x-access-token:<TOKEN>@github.com/"]
#       insteadOf = https://github.com/
if [ -n "${GIT_CONFIG:-}" ]; then
    echo ">>> writing .gitconfig for default user pontoon..."
    echo -n "$GIT_CONFIG" > /home/pontoon/.gitconfig
    chmod 400 /home/pontoon/.gitconfig
    chown pontoon:pontoon /home/pontoon/.gitconfig
    echo "...done"
fi

# Wait for the database to accept connections, but give up after a bounded
# number of attempts so an unreachable DB surfaces as a failed container
# instead of hanging forever. Tune with DB_WAIT_ATTEMPTS / DB_WAIT_INTERVAL.
db_host=$(python -c "import os,urllib.parse as p; u=p.urlparse(os.environ.get('DATABASE_URL','')); print(u.hostname or 'localhost')")
db_port=$(python -c "import os,urllib.parse as p; u=p.urlparse(os.environ.get('DATABASE_URL','')); print(u.port or 5432)")
max_attempts="${DB_WAIT_ATTEMPTS:-30}"
interval="${DB_WAIT_INTERVAL:-2}"

echo ">>> Waiting for database ${db_host}:${db_port} (up to ${max_attempts} attempts)..."
attempt=1
until pg_isready -h "$db_host" -p "$db_port" -q; do
    if [ "$attempt" -ge "$max_attempts" ]; then
        echo "!!! Database ${db_host}:${db_port} not reachable after ${attempt} attempts; aborting." >&2
        exit 1
    fi
    echo "    database unavailable, retry ${attempt}/${max_attempts}..."
    attempt=$((attempt + 1))
    sleep "$interval"
done
echo "...database is ready"

echo ">>> Applying database migrations"
# --noinput guards against any prompt blocking startup; an explicit check turns
# a migration failure (e.g. a conflict / multiple leaf nodes) into a clean,
# non-zero exit instead of a server started against a half-migrated database.
if ! python manage.py migrate --noinput; then
    echo "!!! Database migration failed; refusing to start the server." >&2
    exit 1
fi

echo ">>> Starting local server..."
exec python manage.py runserver 0.0.0.0:8000
