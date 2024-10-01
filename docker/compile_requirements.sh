#!/bin/bash

# This compiles all requirements files with uv pip compile.
# You should always use this script, because dev.txt and test.txt depend on default.txt.

export CUSTOM_COMPILE_COMMAND="./docker/compile_requirements.sh"

uv pip compile --generate-hashes $@ requirements/default.in -o requirements/default.txt
uv pip compile --generate-hashes $@ requirements/dev.in -o requirements/dev.txt
uv pip compile --generate-hashes $@ requirements/lint.in -o requirements/lint.txt
uv pip compile --generate-hashes $@ requirements/test.in -o requirements/test.txt
