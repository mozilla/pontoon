
from pkgutil import iter_modules

from . import fixtures


def _load_fixtures(*modules):
    for mod in modules:
        path = mod.__path__
        prefix = '%s.' % mod.__name__
        for loader_, name, is_pkg in iter_modules(path, prefix):
            if not is_pkg:
                yield name


pytest_plugins = list(_load_fixtures(fixtures))
