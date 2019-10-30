#!/bin/bash

# Installs packages and other things in an Ubuntu Docker image.

# Failures should cause setup to fail
set -v -e -x

# Install nodejs and npm from Nodesource's 10.x branch, as well as yarn
curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add -
echo 'deb https://deb.nodesource.com/node_10.x jessie main' > /etc/apt/sources.list.d/nodesource.list
echo 'deb-src https://deb.nodesource.com/node_10.x jessie main' >> /etc/apt/sources.list.d/nodesource.list

curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add -
echo 'deb https://dl.yarnpkg.com/debian/ stable main' > /etc/apt/sources.list.d/yarn.list

# Update the operating system and install OS-level dependencies
apt-get update

# Install packages for building python packages, postgres, lxml, sasl, and cffi
apt-get install -y --no-install-recommends \
    apt-transport-https \
    build-essential \
    ca-certificates \
    curl \
    git \
    libmemcached-dev \
    libxml2-dev \
    libxslt1-dev \
    nodejs \
    postgresql-client-9.6 \
    postgresql-server-dev-9.6 \
    yarn

apt-get autoremove -y
