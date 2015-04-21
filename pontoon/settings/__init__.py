from .base import *

# Import local settings if they exist (usually only in development).
try:
    from .local import *
except ImportError, exc:
    pass
