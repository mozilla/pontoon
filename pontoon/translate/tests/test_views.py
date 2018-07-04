import pytest

from django.urls import reverse

from waffle.testutils import override_switch


@pytest.mark.django_db
def test_translate_behind_switch(client):
    url = reverse('pontoon.translate')

    response = client.get(url)
    assert response.status_code == 404

    with override_switch('translate_next', active=True):
        response = client.get(url)
        assert response.status_code == 200


@pytest.mark.django_db
def test_translate_template(client):
    url = reverse('pontoon.translate')

    with override_switch('translate_next', active=True):
        response = client.get(url)
        assert response.status_code == 200
        print response.content
        assert 'Translate.Next' in response.content
