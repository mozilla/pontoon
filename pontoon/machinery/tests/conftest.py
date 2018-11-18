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


@pytest.fixture
def google_translate_api_key(settings):
    """Set the settings.GOOGLE_TRANSLATE_API_KEY for this test"""
    key = '2fffff'
    settings.GOOGLE_TRANSLATE_API_KEY = key
    return key


@pytest.fixture
def google_translate_locale(locale_a):
    """Set the Google Cloud Translation API locale code for locale_a"""
    locale_a.google_translate_code = 'bg'
    locale_a.save()
    return locale_a
