import pytest

from django.urls import reverse

from waffle.testutils import override_switch

from pontoon.translate.views import get_preferred_locale


@pytest.fixture
def user_arabic(user_a):
    user_a.profile.custom_homepage = 'ar'
    user_a.save()
    return user_a


@pytest.mark.django_db
def test_translate_behind_switch(client):
    url = reverse('pontoon.translate.next')

    response = client.get(url)
    assert response.status_code == 404

    with override_switch('translate_next', active=True):
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_translate_template(client):
    url = reverse('pontoon.translate.next')

    with override_switch('translate_next', active=True):
        response = client.get(url)
        assert response.status_code == 200
        assert 'Translate.Next' in response.content


@pytest.mark.django_db
def test_get_preferred_locale_from_user_prefs(rf, user_arabic):
    # This user has 'ar' set as their favorite locale. That should take
    # precedence over other ways of choosing a locale.
    rf.user = user_arabic
    rf.META = {
        'HTTP_ACCEPT_LANGUAGE': 'fr',
    }
    locale = get_preferred_locale(rf)

    assert locale == 'ar'


@pytest.mark.django_db
def test_get_preferred_locale_from_headers(rf, user_a):
    # This user has no preferred locale set, so we'll choose the locale based
    # on the metadata of the request.
    rf.user = user_a
    rf.META = {
        'HTTP_ACCEPT_LANGUAGE': 'fr',
    }
    locale = get_preferred_locale(rf)

    assert locale == 'fr'


@pytest.mark.django_db
def test_get_preferred_locale_default(rf, user_a):
    # This user has no preferred locale set, and the request has no metadata.
    rf.user = user_a
    rf.META = {}
    locale = get_preferred_locale(rf)

    assert locale == 'en-US'
