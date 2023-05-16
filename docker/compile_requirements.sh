#!/bin/bash

# This compiles all requirements files with pip-compile.
# You should always use this script, because dev.txt and test.txt depend on default.txt.

export CUSTOM_COMPILE_COMMAND="./docker/compile_requirements.sh"

pip-compile --generate-hashes --resolver=backtracking $@ requirements/default.in
pip-compile --generate-hashes --resolver=backtracking $@ requirements/dev.in
pip-compile --generate-hashes --resolver=backtracking $@ requirements/lint.in
pip-compile --generate-hashes --resolver=backtracking $@ requirements/test.in
