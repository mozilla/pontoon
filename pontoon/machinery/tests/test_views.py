
import json
import urlparse

import caighdean
import factory
import pytest
import requests_mock

from django.core.urlresolvers import reverse

from pontoon.base.models import (
    Entity,
    Group,
    Locale,
    Project,
    Resource,
    Translation,
    TranslationMemoryEntry,
)


class EntityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Entity


@pytest.fixture
def locale():
    translators_group = Group.objects.create(
        name='locale translators',
    )
    managers_group = Group.objects.create(
        name='locale managers',
    )
    return Locale.objects.create(
        code="kg",
        name="Klingon",
        translators_group=translators_group,
        managers_group=managers_group,
    )


@pytest.fixture
def resource(locale):
    project = Project.objects.create(
        slug="project", name="Project"
    )
    return Resource.objects.create(
        project=project, path="resource.po", format="po"
    )


@pytest.fixture
def entity(resource):
    return Entity.objects.create(
        resource=resource, string="entity"
    )


@pytest.mark.django_db
def test_view_mt_caighdean(client, entity):
    gd = Locale.objects.get(code='gd')
    url = reverse('pontoon.machine_translation_caighdean')

    response = client.get(url, dict(id=entity.id))
    assert json.loads(response.content) == {}

    translation = Translation.objects.create(
        entity=entity, locale=gd, string='GD translation'
    )
    entity.translation_set.add(translation)

    translator = caighdean.Translator()

    with requests_mock.mock() as m:
        m.post(translator.service_url, text='[["source", "target"]]')
        response = client.get(url, dict(id=entity.id))

    assert (
        json.loads(response.content)
        == {
            "translation": "target",
            "original": translation.string,
        }
    )
    assert (
        urlparse.parse_qs(m.request_history[0].text)
        == {
            u'teacs': [translation.string],
            u'foinse': [gd.code],
        }
    )


@pytest.mark.django_db
def test_view_mt_caighdean_bad(client, entity):
    gd = Locale.objects.get(code='gd')
    url = reverse('pontoon.machine_translation_caighdean')

    response = client.get(url)
    assert response.status_code == 400
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == 'Bad Request: "\'id\'"'
    )

    response = client.get(url, dict(id="DOESNOTEXIST"))
    assert response.status_code == 400
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == ("Bad Request: invalid literal for int() "
            "with base 10: 'DOESNOTEXIST'")
    )

    maxid = (
        Entity.objects
        .values_list("id", flat=True)
        .order_by("-id")
        .first()
    )
    response = client.get(url, dict(id=maxid + 1))
    assert response.status_code == 404
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == "No Entity matches the given query."
    )

    translator = caighdean.Translator()
    translation = Translation.objects.create(
        entity=entity, locale=gd, string='foo'
    )
    entity.translation_set.add(translation)

    with requests_mock.mock() as m:
        m.post(translator.service_url, status_code=403)
        response = client.get(url, dict(id=entity.id))

    assert response.status_code == 500
    assert response.get("Content-Type") == 'application/json'
    assert (
        json.loads(response.content)["message"]
        == 'Unable to connect to translation service'
    )


@pytest.mark.django_db
def test_view_tm_best_quality_entry(
    client,
    locale,
    resource,
):
    """
    Translation memory should return results entries aggregated by
    translation string.
    """
    entities = [
        EntityFactory(resource=resource, string='Entity %s' % i, order=i)
        for i in range(3)
    ]
    tm = TranslationMemoryEntry.objects.create(
        entity=entities[0],
        source="aaa",
        target="ccc",
        locale=locale,
    )
    TranslationMemoryEntry.objects.create(
        entity=entities[1],
        source="aaa",
        target="ddd",
        locale=locale,
    )
    TranslationMemoryEntry.objects.create(
        entity=entities[2],
        source="bbb",
        target="ccc",
        locale=locale,
    )
    response = client.get(
        '/translation-memory/',
        {
            'text': 'aaa',
            'pk': tm.entity.pk,
            'locale': locale.code,
        }
    )
    assert (
        json.loads(response.content)
        == [{
            "count": 1,
            "source": "aaa",
            "quality": 100.0,
            "target": "ddd",
         }]
    )


@pytest.mark.django_db
def test_view_tm_translation_counts(
    client,
    locale,
    resource,
):
    """
    Translation memory should aggregate identical translations strings
    from the different entities and count up their occurrences.
    """
    entities = [
        EntityFactory(resource=resource, string=x, order=i)
        for i, x in enumerate(["abaa", "abaa", "aaab", "aaab"])
    ]
    tm = TranslationMemoryEntry.objects.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale,
    )
    TranslationMemoryEntry.objects.create(
        entity=entities[1],
        source=entities[1].string,
        target="ccc",
        locale=locale,
    )
    TranslationMemoryEntry.objects.create(
        entity=entities[2],
        source=entities[2].string,
        target="ccc",
        locale=locale,
    )
    TranslationMemoryEntry.objects.create(
        entity=entities[3],
        source=entities[3].string,
        target="ccc",
        locale=locale,
    )
    response = client.get(
        '/translation-memory/',
        {
            'text': 'aaaa',
            'pk': tm.entity.pk,
            'locale': locale.code,
        }
    )
    result = json.loads(response.content)
    assert result[0].pop('source') in ('abaa', 'aaab', 'aaab')
    assert (
        result
        == [{
            u'count': 3,
            u'quality': 75.0,
            u'target': u'ccc'
        }]
    )


@pytest.mark.django_db
def test_view_tm_exclude_entity(client, entity, locale, resource):
    """
    Exclude entity from results to avoid false positive results.
    """
    tm = TranslationMemoryEntry.objects.create(
        entity=entity,
        source=entity.string,
        target="ccc",
        locale=locale,
    )
    response = client.get(
        '/translation-memory/',
        {
            'text': entity.string,
            'pk': entity.pk,
            'locale': tm.locale.code,
        }
    )
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_view_tm_minimal_quality(client, locale, resource):
    """
    View shouldn't return any entries if 70% of quality at minimum.
    """
    entities = [
        EntityFactory(resource=resource, string='Entity %s' % i, order=i)
        for i in range(5)
    ]
    for i, entity in enumerate(entities):
        TranslationMemoryEntry.objects.create(
            entity=entity,
            source="source %s" % entity.string,
            target="target %s" % entity.string,
            locale=locale,
        )
    response = client.get(
        '/translation-memory/',
        {
            'text': 'no match',
            'pk': entities[0].pk,
            'locale': locale.code,
        }
    )
    assert response.status_code == 200
    assert json.loads(response.content) == []
