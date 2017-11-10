
import json
import urlparse

import pytest

import requests_mock

import caighdean

from django.core.urlresolvers import reverse

from pontoon.base.models import Entity, Locale, Translation


@pytest.mark.django_db
def test_view_mt_caighdean(client, entity0):
    gd = Locale.objects.get(code='gd')
    url = reverse('pontoon.machine_translation_caighdean')

    response = client.get(url, dict(id=entity0.id))
    assert json.loads(response.content) == {}

    translation = Translation.objects.create(
        entity=entity0, locale=gd, string='GD translation')
    entity0.translation_set.add(translation)

    translator = caighdean.Translator()

    with requests_mock.mock() as m:
        m.post(translator.service_url, text='[["source", "target"]]')
        response = client.get(url, dict(id=entity0.id))
    assert (
        json.loads(response.content)
        == {"translation": "target",
            "original": translation.string})
    assert (
        urlparse.parse_qs(m.request_history[0].text)
        == {u'teacs': [translation.string],
            u'foinse': [gd.code]})


@pytest.mark.django_db
def test_view_mt_caighdean_bad(client, entity0):
    gd = Locale.objects.get(code='gd')
    url = reverse('pontoon.machine_translation_caighdean')

    response = client.get(url)
    assert response.status_code == 400
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == 'Bad Request: "\'id\'"')

    response = client.get(url, dict(id="DOESNOTEXIST"))
    assert response.status_code == 400
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == ("Bad Request: invalid literal for int() "
            "with base 10: 'DOESNOTEXIST'"))

    maxid = Entity.objects.values_list(
        "id", flat=True).order_by("-id").first()
    response = client.get(url, dict(id=maxid + 1))
    assert response.status_code == 404
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == "No Entity matches the given query.")

    translator = caighdean.Translator()
    translation = Translation.objects.create(
        entity=entity0, locale=gd, string='foo')
    entity0.translation_set.add(translation)

    with requests_mock.mock() as m:
        m.post(translator.service_url, status_code=403)
        response = client.get(url, dict(id=entity0.id))

    assert response.status_code == 500
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == 'Unable to connect to translation service')
