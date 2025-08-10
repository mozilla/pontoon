import sys

from .base import *  # noqa


# Import local settings if they exist (usually only in development).
try:
    from .local import *  # noqa
except ImportError:
    pass


# Import test settings
TEST = "pytest" in sys.modules
if TEST:
    try:
        from .test import *  # noqa
    except ImportError:
        pass


# Import settings that are helpful during the process of development.
if DEV and not TEST:  # noqa
    try:
        from .dev import *  # noqa
    except ImportError:
        pass
