import pytest

from django.db import connection
from django.db.utils import ProgrammingError


@pytest.fixture(scope="session")
def tests_use_db(request):
    """Check if any of the tests in this run require db setup"""
    return any(item.get_closest_marker("django_db") for item in request.node.items)


@pytest.fixture(autouse=True, scope="session")
def setup_db_if_needed(request, tests_use_db):
    """Sets up the site DB only if tests requested to use the DB (autouse)."""
    if tests_use_db:
        return request.getfixturevalue("post_db_setup")


@pytest.fixture(scope="session")
def post_db_setup(django_db_setup, django_db_blocker, tests_use_db, request):
    """Sets up the site DB for the test session."""
    if tests_use_db:
        with django_db_blocker.unblock():
            setup_database()


def setup_database():
    """Required for collation lookup tests

    At the moment this is only set up for Turkish.

    cf: Bug 1440940

    """
    cursor = connection.cursor()
    try:
        cursor.execute("CREATE COLLATION tr_tr (LOCALE = 'tr_TR.utf8');")
    except ProgrammingError:
        # This happens when the database has already been set up before,
        # if --reuse-db is used for example. In such cases, we simply do
        # nothing.
        pass
