#!/bin/bash

# Installs packages and other things in an Ubuntu Docker image.

# Failures should cause setup to fail
set -v -e -x

# Update the operating system and install OS-level dependencies
apt-get update

# Install packages for building python packages, postgres, lxml, sasl, and cffi
apt-get install -y git build-essential libxml2-dev libxslt1-dev libmemcached-dev \
    postgresql-server-dev-9.4 postgresql-client-9.4 sudo
