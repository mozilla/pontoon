#!/usr/bin/env python
import os
import sys

import dotenv


if __name__ == "__main__":
    # Read dotenv file and inject it's values into the environment
    root_path = os.path.dirname(__file__)
    if (
        "DOTENV_PATH" in os.environ
        or os.path.isfile(os.path.join(root_path, ".env"))
        or os.path.isfile(os.path.join(root_path, ".env", ".env"))
    ):
        dotenv.read_dotenv(os.environ.get("DOTENV_PATH"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
