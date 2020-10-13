import pytest


@pytest.fixture
def ms_api_key(settings):
    """Set the settings.MICROSOFT_TRANSLATOR_API_KEY for this test"""
    key = "1fffff"
    settings.MICROSOFT_TRANSLATOR_API_KEY = key
    return key


@pytest.fixture
def google_translate_api_key(settings):
    """Set the settings.GOOGLE_TRANSLATE_API_KEY for this test"""
    key = "2fffff"
    settings.GOOGLE_TRANSLATE_API_KEY = key
    return key
