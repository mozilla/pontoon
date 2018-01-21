
import pytest

from pontoon.base.models import Locale, Project


@pytest.fixture
def db_doctest(db):
    # clear all Locales and Projects to make doctest clearer
    Locale.objects.all().delete()
    Project.objects.all().delete()
