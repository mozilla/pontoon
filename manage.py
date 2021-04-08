#!/usr/bin/env python
import os
import sys

import dotenv


ROOT = os.path.dirname(__file__)


def path(*args):
    return os.path.join(ROOT, *args)


if __name__ == "__main__":
    # Read dotenv file and inject it's values into the environment
    if "DOTENV_PATH" in os.environ:
        dotenv.read_dotenv(os.environ.get("DOTENV_PATH"))
    elif os.path.isfile(path(".env")):
        dotenv.read_dotenv(path(".env"))
    elif os.path.isfile(path(".env", ".env")):
        dotenv.read_dotenv(path(".env", ".env"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
