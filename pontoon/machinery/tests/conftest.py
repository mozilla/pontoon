import pytest


@pytest.fixture
def ms_api_key(settings):
    """Set the settings.MICROSOFT_TRANSLATOR_API_KEY for this test"""
    key = '1fffff'
    settings.MICROSOFT_TRANSLATOR_API_KEY = key
    return key


@pytest.fixture
def ms_locale(locale_a):
    """Set the Microsoft API locale code for locale_a"""
    locale_a.ms_translator_code = 'gb'
    locale_a.save()
    return locale_a
