#!/bin/bash

# This compiles all requirements files with uv pip compile.
# You should always use this script, because dev.txt and test.txt depend on default.txt.

export CUSTOM_COMPILE_COMMAND="./docker/compile_requirements.sh"

uv pip compile --generate-hashes --resolver=backtracking $@ requirements/default.in
uv pip compile --generate-hashes --resolver=backtracking $@ requirements/dev.in
uv pip compile --generate-hashes --resolver=backtracking $@ requirements/lint.in
uv pip compile --generate-hashes --resolver=backtracking $@ requirements/test.in
