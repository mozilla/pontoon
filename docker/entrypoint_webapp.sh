#!/bin/bash

# Make sure links to the node modules are created.
ln -s /webapp-frontend-deps/node_modules /app/node_modules
ln -s /webapp-frontend-deps/frontend/node_modules /app/frontend/node_modules
ln -s /webapp-frontend-deps/assets /app/assets

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-10001}

echo "Starting with UID : $USER_ID"
usermod -o -u $USER_ID app
chown -R app:app /app
export HOME=/home/app
exec /usr/local/bin/gosu app "$@"
