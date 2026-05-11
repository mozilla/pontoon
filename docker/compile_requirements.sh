#!/bin/bash

# This compiles all requirements files with uv pip compile.
# You should always use this script, because dev.txt and test.txt depend on default.txt.

export CUSTOM_COMPILE_COMMAND="./docker/compile_requirements.sh"

# Run compile command from the requirements directory
cd "$(dirname "$0")/../requirements"

requirement_files=(default dev lint test)

for name in "${requirement_files[@]}"; do
  # --no-emit-package matches pip-tools' default "unsafe packages" set, so the
  # lockfile stays stable when Dependabot (which uses pip-tools) recompiles it.
  uv pip compile --generate-hashes --no-strip-extras \
    --no-emit-package setuptools \
    $@ "$name.in" -o "$name.txt"
done
