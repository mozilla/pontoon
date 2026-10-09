#!/bin/bash

# This compiles all requirements files with uv pip compile.
# You should always use this script, because 2-dev.txt depends on 1-prod.txt.
#
# The numeric prefixes of the requirements files are needed for Dependabot,
# which compiles them in alphabetical order and ignores `-c` constraints when
# ordering, so 1-prod.txt must sort before 2-dev.txt.

export UV_CUSTOM_COMPILE_COMMAND="./docker/compile_requirements.sh"

# Run compile command from the requirements directory
cd "$(dirname "$0")/../requirements"

requirement_files=(1-prod 2-dev)

for name in "${requirement_files[@]}"; do
  # --no-emit-package matches pip-tools' default "unsafe packages" set, so the
  # lockfile stays stable when Dependabot (which uses pip-tools) recompiles it.
  uv pip compile --generate-hashes --no-strip-extras \
    --no-emit-package distribute \
    --no-emit-package pip \
    --no-emit-package setuptools \
    $@ "$name.in" -o "$name.txt"
done
