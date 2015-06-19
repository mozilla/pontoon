#!/usr/bin/env python
import os
import sys
import warnings

import dotenv


if __name__ == '__main__':
    # Filter out missing .env warning, it's fine if we don't have one.
    warnings.filterwarnings('ignore', module='dotenv')

    # Read .env file and inject it's values into the environment
    dotenv.read_dotenv()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pontoon.settings')

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
