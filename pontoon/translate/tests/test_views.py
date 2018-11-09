import pytest

from django.urls import reverse

from waffle.testutils import override_switch


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
