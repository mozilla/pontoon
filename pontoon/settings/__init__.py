import sys

from .base import * # noqa


# Import local settings if they exist (usually only in development).
try:
    from .local import * # noqa
except ImportError, exc:
    pass


# Import test settings
TEST = len(sys.argv) > 1 and sys.argv[1] == 'test'
if TEST:
    try:
        from .test import * # noqa
    except ImportError:
        pass
