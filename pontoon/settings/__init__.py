import sys

from .base import *


# Import local settings if they exist (usually only in development).
try:
    from .local import *
except ImportError, exc:
    pass


# Import test settings
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TEST:
    try:
        from .test import *
    except ImportError:
        pass
