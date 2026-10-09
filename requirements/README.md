# Python requirements

Declare direct dependencies in `*.in` files. The compile script uses
`uv pip compile` to generate `*.txt` files with pinned versions and hashes.

| File        | Contents                                             | Compiled to  |
| ----------- | ---------------------------------------------------- | ------------ |
| `0-base.in` | Dependencies used in both production and development | —            |
| `1-prod.in` | Production-only dependencies (includes `0-base.in`)  | `1-prod.txt` |
| `2-dev.in`  | Development-only dependencies (includes `0-base.in`) | `2-dev.txt`  |

`2-dev.in` uses `1-prod.txt` as a constraint to keep shared dependencies at
the same versions in both environments.

## Updating requirements

After editing any `*.in` file, recompile all requirements:

- `make requirements` if using the development Docker environment
- `./docker/compile_requirements.sh` if using `uv` directly

Both commands compile production requirements before development requirements.
Use them instead of compiling individual files.

To upgrade all dependencies, run `make requirements opts=--upgrade` or
`./docker/compile_requirements.sh --upgrade`.

## Why the numeric prefixes?

Dependabot compiles files alphabetically, ignoring constraints when choosing
the order. The prefixes ensure it compiles `1-prod.txt` before `2-dev.txt`,
so development requirements use the updated production versions.
