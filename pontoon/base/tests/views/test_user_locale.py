import pytest

from pontoon.base.views import _get_user_preferred_locale


@pytest.fixture
def user_arabic(user_a):
    user_a.profile.custom_homepage = 'ar'
    user_a.save()
    return user_a


@pytest.mark.django_db
def test_user_preferred_locale_from_user_prefs(rf, user_arabic):
    # This user has 'ar' set as their favorite locale. That should take
    # precedence over other ways of choosing a locale.
    rf.user = user_arabic
    rf.META = {
        'HTTP_ACCEPT_LANGUAGE': 'fr',
    }
    locale = _get_user_preferred_locale(rf)

    assert locale == 'ar'


@pytest.mark.django_db
def test_user_preferred_locale_from_headers(rf, user_a):
    # This user has no preferred locale set, so we'll choose the locale based
    # on the metadata of the request.
    rf.user = user_a
    rf.META = {
        'HTTP_ACCEPT_LANGUAGE': 'fr',
    }
    locale = _get_user_preferred_locale(rf)

    assert locale == 'fr'


@pytest.mark.django_db
def test_user_preferred_locale_default(rf, user_a):
    # This user has no preferred locale set, and the request has no metadata.
    rf.user = user_a
    rf.META = {}
    locale = _get_user_preferred_locale(rf)

    assert locale == 'en-US'
