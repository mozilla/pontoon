#!/bin/bash

# Add local user
# Either use the LOCAL_USER_ID if passed in at runtime or
# fallback

USER_ID=${LOCAL_USER_ID:-10001}

echo "Starting with UID : $USER_ID"
usermod -o -u $USER_ID app
export HOME=/home/app
exec /usr/local/bin/gosu app "$@"
