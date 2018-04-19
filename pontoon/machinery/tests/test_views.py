
import json
import urlparse

import pytest

import requests_mock

import caighdean

from django.core.urlresolvers import reverse

from pontoon.base.models import (
    Entity, Locale, Translation, TranslationMemoryEntry)


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


@pytest.mark.django_db
def test_view_tm_best_quality_entry(client, entity_factory,
                                    locale0, resource0):
    """
    Translation memory should return results entries aggregated by
    translation string.
    """
    entities = entity_factory(resource=resource0, batch=3)
    tm = TranslationMemoryEntry.objects.create(
        entity=entities[0],
        source="aaa",
        target="ccc",
        locale=locale0)
    TranslationMemoryEntry.objects.create(
        entity=entities[1],
        source="aaa",
        target="ddd",
        locale=locale0)
    TranslationMemoryEntry.objects.create(
        entity=entities[2],
        source="bbb",
        target="ccc",
        locale=locale0)
    response = client.get(
        '/translation-memory/',
        {'text': 'aaa',
         'pk': tm.entity.pk,
         'locale': locale0.code})
    assert (
        json.loads(response.content)
        == [{"count": 1,
             "source": "aaa",
             "quality": 100.0,
             "target": "ddd"}])


@pytest.mark.django_db
def test_view_tm_translation_counts(client, entity_factory,
                                    locale0, resource0):
    """
    Translation memory should aggregate identical translations strings
    from the different entities and count up their occurrences.
    """
    entities = entity_factory(
        resource=resource0,
        batch_kwargs=[
            dict(string="abaa"),
            dict(string="abaa"),
            dict(string="aaab"),
            dict(string="aaab")])
    tm = TranslationMemoryEntry.objects.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale0)
    TranslationMemoryEntry.objects.create(
        entity=entities[1],
        source=entities[1].string,
        target="ccc",
        locale=locale0)
    TranslationMemoryEntry.objects.create(
        entity=entities[2],
        source=entities[2].string,
        target="ccc",
        locale=locale0)
    TranslationMemoryEntry.objects.create(
        entity=entities[3],
        source=entities[3].string,
        target="ccc",
        locale=locale0)
    response = client.get(
        '/translation-memory/',
        {'text': 'aaaa',
         'pk': tm.entity.pk,
         'locale': locale0.code})
    result = json.loads(response.content)
    assert result[0].pop('source') in ('abaa', 'aaab', 'aaab')
    assert (
        result
        == [{u'count': 3,
             u'quality': 75.0,
             u'target': u'ccc'}])


@pytest.mark.django_db
def test_view_tm_exclude_entity(client, entity0, locale0, resource0):
    """
    Exclude entity from results to avoid false positive results.
    """
    tm = TranslationMemoryEntry.objects.create(
        entity=entity0,
        source=entity0.string,
        target="ccc",
        locale=locale0)
    response = client.get(
        '/translation-memory/',
        {'text': entity0.string,
         'pk': entity0.pk,
         'locale': tm.locale.code})
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_view_tm_minimal_quality(client, entity_factory, locale0, resource0):
    """
    View shouldn't return any entries if 70% of quality at minimum.
    """
    entities = entity_factory(
        resource=resource0,
        batch=5)
    for i, entity in enumerate(entities):
        TranslationMemoryEntry.objects.create(
            entity=entity,
            source="source %s" % entity.string,
            target="target %s" % entity.string,
            locale=locale0)
    response = client.get(
        '/translation-memory/',
        {'text': 'no match',
         'pk': entities[0].pk,
         'locale': locale0.code})
    assert response.status_code == 200
    assert json.loads(response.content) == []
