
from pkgutil import iter_modules

import pytest

from . import env
from . import fixtures


def _load_fixtures(*modules):
    for mod in modules:
        path = mod.__path__
        prefix = '%s.' % mod.__name__
        for loader_, name, is_pkg in iter_modules(path, prefix):
            if not is_pkg:
                yield name


@pytest.fixture(scope='session')
def tests_use_db(request):
    """Check if any of the tests in this run require db setup"""
    return any(
        item for item
        in request.node.items
        if item.get_marker('django_db'))


@pytest.fixture(autouse=True, scope='session')
def setup_db_if_needed(request, tests_use_db):
    """Sets up the site DB only if tests requested to use the DB (autouse)."""
    if tests_use_db and not request.config.getvalue('reuse_db'):
        return request.getfixturevalue('post_db_setup')


@pytest.fixture(scope='session')
def post_db_setup(django_db_setup, django_db_blocker, tests_use_db, request):
    """Sets up the site DB for the test session."""
    if tests_use_db:
        with django_db_blocker.unblock():
            env.Environment().setup()


pytest_plugins = list(_load_fixtures(fixtures))
