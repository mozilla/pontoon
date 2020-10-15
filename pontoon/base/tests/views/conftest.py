import pytest


@pytest.fixture
def settings_debug(settings):
    """Make the settings.DEBUG for this test"""
    settings.DEBUG = True
