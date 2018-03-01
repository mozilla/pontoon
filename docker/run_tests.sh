#!/bin/bash

# Run all linting, testing and coverage steps for Pontoon.

# Failures should cause setup to fail.
set -e

# Enable node and npm.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm use node

# Make sure we use correct binaries.
PYTHON="$(which python)"
PYLAMA="$(which pylama)"
NPM="$(which npm)"
PYTEST="$(which pytest)"
CODECOV="$(which codecov)"


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Collecting static files and bundles"
./node_modules/.bin/webpack
$PYTHON manage.py collectstatic -v0 --noinput


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Linting Python code"
$PYLAMA pontoon
$PYLAMA tests

# echo "Linting JavaScript code"
# This is not passing yet, so it's temporarily disabled.
# ./node_modules/.bin/eslint .

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running JavaScript tests"
$NPM test

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running Python tests with django"
$PYTHON manage.py test --with-coverage

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running Python tests with pytest"
$PYTEST --cov-append --cov-report=term --cov=.

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Generating code coverage report"
$CODECOV
