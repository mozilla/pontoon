#!/bin/bash

# Run all linting, testing and coverage steps for Pontoon.

# Failures should cause setup to fail.
set -e

# Make sure we use correct binaries.
PYTHON="$(which python)"
BLACK="$(which black)"
FLAKE8="$(which flake8)"
NPM="$(which npm)"
PYTEST="$(which pytest)"


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Formatting Python code"
$BLACK pontoon/ --check


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Linting Python code"
$FLAKE8 pontoon/


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Formatting Javascript code"
npm run check-prettier


echo ""
echo "Linting JavaScript code"
npm run eslint


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Collecting static files and bundles"
$WEBPACK_BINARY
$PYTHON manage.py collectstatic -v0 --noinput


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running JavaScript tests"
$NPM test
pushd frontend
yarn test --watchAll=false
popd


echo ""
echo "--------------------------------------------------------------------------------------------"
echo "Running Python tests"
$PYTEST --cov-append --cov-report=term --cov=.
