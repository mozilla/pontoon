#!/usr/bin/env python
import os
import sys

# Add a temporary path so that we can import the funfactory
tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        'vendor', 'src', 'funfactory')
sys.path.append(tmp_path)

from funfactory import manage

# Let the path magic happen in setup_environ() !
sys.path.remove(tmp_path)


manage.setup_environ(__file__)

if __name__ == "__main__":
    manage.main()
