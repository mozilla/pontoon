#!/bin/bash

# Traps & exits on SIGINT, so calling from make as
#   bash -c 'set -m; bash ./bin/watch.sh'
# will not cause the parent process to exit.
# Source: https://stackoverflow.com/a/65935205
sigint_handler() { exit 0; }
trap sigint_handler INT

npx concurrently -n frontend,tagadmin,server,pg -c cyan,magenta,green,red \
  'npm run watch -w frontend' \
  'npm run watch -w tag-admin' \
  'docker-compose logs --tail=0 --follow --no-log-prefix server' \
  'docker-compose logs --tail=0 --follow --no-log-prefix postgresql' \
