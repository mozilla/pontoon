#!/bin/bash

# Script that sets up the docker environment to run the tests in and runs the
# tests.

# Pass --shell to run a shell in the test container.

# Failures should cause setup to fail.
set -e

DC="$(which docker-compose)"

# Use the same image we use for building docker images because it'll be cached
# already.
BASEIMAGENAME="local/pontoon:base"

# Start services in background (this is idempotent).
echo "Starting services in the background..."
${DC} up -d postgresql

# If we're running a shell, then we start up a test container with . mounted
# to /app.
if [ "$1" == "--shell" ]; then
    echo "Running shell..."

    docker run \
           --rm \
           --volume "$(pwd)":/app \
           --workdir /app \
           --network pontoon_default \
           --link "${DC} ps -q postgresql" \
           --env-file ./docker/dev/config/webapp.env \
           -e LOCAL_USER_ID=$UID \
           --tty \
           --interactive \
           local/pontoon:dev /bin/bash "${@:2}"

else
    docker run \
           --rm \
           --volume "$(pwd)":/app \
           --workdir /app \
           --network pontoon_default \
           --link "${DC} ps -q postgresql" \
           --env-file ./docker/dev/config/webapp.env \
           -e LOCAL_USER_ID=$UID \
           local/pontoon:dev \
           /app/docker/run_tests.sh

    echo "Done!"
fi
