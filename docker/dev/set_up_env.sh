#!/bin/bash

# Installs packages and other things in an Ubuntu Docker image.

# Failures should cause setup to fail
set -v -e -x

echo 'getting nvm/node/npm'
curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.8/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" # This loads nvm
nvm install node
