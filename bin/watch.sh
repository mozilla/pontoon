#!/bin/bash

# Detect which compose command is installed
docker compose --help >/dev/null 2>&1 && DOCKER="docker compose"
docker-compose --help >/dev/null 2>&1 && DOCKER="docker-compose"

# Traps & exits on SIGINT, so calling from make as
#   bash -c 'set -m; bash ./bin/watch.sh'
# will not cause the parent process to exit.
# Source: https://stackoverflow.com/a/65935205
sigint_handler() { exit 0; }
trap sigint_handler INT

npx concurrently -n translate,server,pg -c cyan,magenta,green,red \
  'npm start -w translate' \
  "sh -c '${DOCKER} logs --tail=0 --follow --no-log-prefix server'" \
  "sh -c '${DOCKER} logs --tail=0 --follow --no-log-prefix postgresql'"
