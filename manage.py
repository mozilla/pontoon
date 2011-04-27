#!/usr/bin/env python
import os
import sys

tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps')
sys.path.append(tmp_path)

from playdohlib import manage

# Let the path magic happen in setup_environ() !
sys.path.remove(tmp_path)


manage.setup_environ(__file__)

if __name__ == "__main__":
    manage.main()
