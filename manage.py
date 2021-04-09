#!/usr/bin/env python
import os
import sys

import dotenv


if __name__ == "__main__":
    # Read dotenv file and inject it's values into the environment
    dotenv.load_dotenv(dotenv_path=os.environ.get("DOTENV_PATH"))

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pontoon.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
