#!/bin/bash

# Script that sets up the docker environment to run the tests in and runs the
# tests.

# Pass --shell to run a shell in the test container.

# Failures should cause setup to fail.
set -v -e -x

DC="$(which docker-compose)"

# Use the same image we use for building docker images because it'll be cached
# already.
BASEIMAGENAME="local/pontoon_base"

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
           --env-file ./docker/config/webapp.env \
           -e LOCAL_USER_ID=$UID \
           --tty \
           --interactive \
           local/pontoon /bin/bash "${@:2}"

else
    # Create a data container to hold the repo directory contents and copy the
    # contents into it.
    if [ "$(docker container ls --all | grep pontoon-tests)" != "" ]; then
        echo "Removing previously existing container"
        docker rm pontoon-tests
    fi

    echo "Creating pontoon-tests container..."
    docker create \
           --volume "$(pwd)":/app \
           -e LOCAL_USER_ID=$UID \
           --name pontoon-tests \
           ${BASEIMAGENAME} /bin/true

    # Run cmd in that environment and then remove the container.
    echo "Running tests..."
    docker run \
           --rm \
           --volumes-from pontoon-tests \
           --workdir /app \
           --network pontoon_default \
           --link "${DC} ps -q postgresql" \
           --env-file ./docker/config/webapp.env \
           -e LOCAL_USER_ID=$UID \
           local/pontoon \
           python manage.py test $@

    docker run \
           --rm \
           --volumes-from pontoon-tests \
           --workdir /app \
           --network pontoon_default \
           --link "${DC} ps -q postgresql" \
           --env-file ./docker/config/webapp.env \
           -e LOCAL_USER_ID=$UID \
           local/pontoon \
           py.test

    echo "Done!"
fi
