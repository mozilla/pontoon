
import pytest

from pontoon.base.models import Locale


@pytest.fixture
def locale0():
    """Locale 0"""
    return Locale.objects.get(code="locale0")


@pytest.fixture
def locale1():
    """Locale 1"""
    return Locale.objects.get(code="locale1")


@pytest.fixture
def localeX():
    """Locale X - empty locale"""
    return Locale.objects.get(code="localeX")
