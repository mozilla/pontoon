from __future__ import absolute_import

import pytest

from django.urls import reverse

from pontoon.translate.views import get_preferred_locale


@pytest.fixture
def user_arabic(user_a):
    user_a.profile.custom_homepage = 'ar'
    user_a.save()
    return user_a


@pytest.mark.django_db
def test_translate_template(client, project_locale_a, resource_a):
    url = reverse(
        'pontoon.translate',
        kwargs={
            'locale': project_locale_a.locale.code,
            'project': project_locale_a.project.slug,
            'resource': 'all-resources',
        },
    )

    response = client.get(url)
    assert b'Pontoon' in response.content


@pytest.mark.django_db
def test_translate_validate_parameters(client, project_locale_a, resource_a):
    url_invalid = reverse(
        'pontoon.translate',
        kwargs={
            'locale': 'locale',
            'project': 'project',
            'resource': 'resource',
        }
    )

    url_valid = reverse(
        'pontoon.translate',
        kwargs={
            'locale': project_locale_a.locale.code,
            'project': project_locale_a.project.slug,
            'resource': 'resource',
        }
    )

    response = client.get(url_invalid)
    assert response.status_code == 404

    response = client.get(url_valid)
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_preferred_locale_from_user_prefs(rf, user_arabic):
    # This user has 'ar' set as their favorite locale.
    rf.user = user_arabic
    locale = get_preferred_locale(rf)

    assert locale == 'ar'


@pytest.mark.django_db
def test_get_preferred_locale_default(rf, user_a):
    # This user has no preferred locale set.
    rf.user = user_a
    locale = get_preferred_locale(rf)

    assert locale is None
