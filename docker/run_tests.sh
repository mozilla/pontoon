#!/bin/bash

# Run all linting, testing and coverage steps for Pontoon.

# Failures should cause setup to fail.
set -e

# Make sure we use correct binaries.
PYTHON="$(which python)"
PYLAMA="$(which pylama)"
NPM="$(which npm)"
PYTEST="$(which pytest)"
CODECOV="$(which codecov)"


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Linting Python code"
$PYLAMA pontoon

echo "Linting JavaScript code"
./node_modules/.bin/eslint .

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Collecting static files and bundles"
$WEBPACK_BINARY
$PYTHON manage.py collectstatic -v0 --noinput

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running JavaScript tests"
$NPM test

echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running Python tests"
$PYTEST --cov-append --cov-report=term --cov=.
