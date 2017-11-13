
import pytest

from pontoon.base.models import Locale


@pytest.fixture
def locale0():
    return Locale.objects.create(code="locale0", name="Locale 0")


@pytest.fixture
def locale1():
    return Locale.objects.create(code="locale1", name="Locale 1")
