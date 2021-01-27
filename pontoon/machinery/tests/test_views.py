import json
import urllib.parse

import caighdean
import pytest
import requests_mock
from django.urls import reverse

from pontoon.base.models import (
    Entity,
    Locale,
)
from pontoon.test.factories import (
    EntityFactory,
    TranslationFactory,
    TranslationMemoryFactory,
)


@pytest.mark.django_db
def test_view_microsoft_translator(client, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")

    with requests_mock.mock() as m:
        data = [{"translations": [{"text": "target"}]}]
        m.post("https://api.cognitive.microsofttranslator.com/translate", json=data)
        response = client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code},
        )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "translation": "target",
    }

    req = m.request_history[0]

    assert req.headers["Ocp-Apim-Subscription-Key"] == ms_api_key
    assert json.loads(req.text) == [{"Text": "text"}]
    assert urllib.parse.parse_qs(req.query) == {
        "api-version": ["3.0"],
        "from": ["en"],
        "to": ["gb"],
        "texttype": ["html"],
    }


@pytest.mark.django_db
def test_view_microsoft_translator_bad_locale(client, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")
    response = client.get(url, {"text": "text", "locale": "bad"})

    assert response.status_code == 404


@pytest.mark.django_db
def test_view_google_translate(
    client, google_translate_locale, google_translate_api_key
):
    url = reverse("pontoon.google_translate")

    with requests_mock.mock() as m:
        data = {"data": {"translations": [{"translatedText": "target"}]}}
        m.post("https://translation.googleapis.com/language/translate/v2", json=data)
        response = client.get(
            url,
            {"text": "text", "locale": google_translate_locale.google_translate_code},
        )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "status": True,
        "translation": "target",
    }

    req = m.request_history[0]

    assert urllib.parse.parse_qs(req.query) == {
        "q": ["text"],
        "source": ["en"],
        "target": ["bg"],
        "format": ["text"],
        "key": ["2fffff"],
    }


@pytest.mark.django_db
def test_view_google_translate_bad_locale(
    client, google_translate_locale, google_translate_api_key,
):
    url = reverse("pontoon.google_translate")
    response = client.get(url, {"text": "text", "locale": "bad"})

    assert response.status_code == 404


@pytest.mark.django_db
def test_view_caighdean(client, entity_a):
    gd = Locale.objects.get(code="gd")
    url = reverse("pontoon.caighdean")

    response = client.get(url, dict(id=entity_a.id))
    assert json.loads(response.content) == {}

    translation = TranslationFactory.create(
        entity=entity_a,
        locale=gd,
        string="GD translation",
        plural_form=None,
        approved=True,
    )
    entity_a.translation_set.add(translation)

    translator = caighdean.Translator()

    with requests_mock.mock() as m:
        m.post(translator.service_url, text='[["source", "target"]]')
        response = client.get(url, dict(id=entity_a.id))

    assert json.loads(response.content) == {
        "translation": "target",
        "original": translation.string,
    }
    assert urllib.parse.parse_qs(m.request_history[0].text) == {
        u"teacs": [translation.string],
        u"foinse": [gd.code],
    }


@pytest.mark.django_db
def test_view_caighdean_bad(client, entity_a):
    gd = Locale.objects.get(code="gd")
    url = reverse("pontoon.caighdean")

    response = client.get(url)
    assert response.status_code == 400
    assert response.get("Content-Type") == "application/json"
    assert json.loads(response.content)["message"] == "Bad Request: 'id'"

    response = client.get(url, dict(id="DOESNOTEXIST"))
    assert response.status_code == 400
    assert response.get("Content-Type") == "application/json"
    assert json.loads(response.content)["message"] == (
        "Bad Request: invalid literal for int() " "with base 10: 'DOESNOTEXIST'"
    )

    maxid = Entity.objects.values_list("id", flat=True).order_by("-id").first()
    response = client.get(url, dict(id=maxid + 1))
    assert response.status_code == 404
    assert response.get("Content-Type") == "application/json"
    assert (
        json.loads(response.content)["message"]
        == "Not Found: Entity matching query does not exist."
    )

    translator = caighdean.Translator()
    translation = TranslationFactory.create(
        entity=entity_a, locale=gd, string="foo", plural_form=None, approved=True,
    )
    entity_a.translation_set.add(translation)

    with requests_mock.mock() as m:
        m.post(translator.service_url, status_code=403)
        response = client.get(url, dict(id=entity_a.id))

    assert response.status_code == 500
    assert response.get("Content-Type") == "application/json"
    assert (
        json.loads(response.content)["message"]
        == "Server Error: Unable to connect to translation service"
    )


@pytest.mark.django_db
def test_view_translation_memory_best_quality_entry(
    client, locale_a, resource_a,
):
    """
    Translation memory should return results entries aggregated by
    translation string.
    """
    entities = [
        EntityFactory(resource=resource_a, string="Entity %s" % i, order=i)
        for i in range(3)
    ]
    tm = TranslationMemoryFactory.create(
        entity=entities[0], source="aaa", target="ccc", locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1], source="aaa", target="ddd", locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[2], source="bbb", target="ccc", locale=locale_a,
    )
    response = client.get(
        "/translation-memory/",
        {"text": "aaa", "pk": tm.entity.pk, "locale": locale_a.code},
    )
    assert json.loads(response.content) == [
        {"count": 1, "source": u"aaa", "quality": u"100", "target": u"ddd"}
    ]


@pytest.mark.django_db
def test_view_translation_memory_translation_counts(
    client, locale_a, resource_a,
):
    """
    Translation memory should aggregate identical translations strings
    from the different entities and count up their occurrences.
    """
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i)
        for i, x in enumerate(["abaa", "abaa", "aaab", "aaab"])
    ]
    tm = TranslationMemoryFactory.create(
        entity=entities[0], source=entities[0].string, target="ccc", locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1], source=entities[1].string, target="ccc", locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[2], source=entities[2].string, target="ccc", locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[3], source=entities[3].string, target="ccc", locale=locale_a,
    )
    response = client.get(
        "/translation-memory/",
        {"text": "aaaa", "pk": tm.entity.pk, "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result[0].pop("source") in ("abaa", "aaab", "aaab")
    assert result == [{u"count": 3, u"quality": u"75", u"target": u"ccc"}]


@pytest.mark.django_db
def test_view_tm_exclude_entity(client, entity_a, locale_a, resource_a):
    """
    Exclude entity from results to avoid false positive results.
    """
    tm = TranslationMemoryFactory.create(
        entity=entity_a, source=entity_a.string, target="ccc", locale=locale_a,
    )
    response = client.get(
        "/translation-memory/",
        {"text": entity_a.string, "pk": entity_a.pk, "locale": tm.locale.code},
    )
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_view_tm_minimal_quality(client, locale_a, resource_a):
    """
    View shouldn't return any entries if 70% of quality at minimum.
    """
    entities = [
        EntityFactory(resource=resource_a, string="Entity %s" % i, order=i)
        for i in range(5)
    ]
    for i, entity in enumerate(entities):
        TranslationMemoryFactory.create(
            entity=entity,
            source="source %s" % entity.string,
            target="target %s" % entity.string,
            locale=locale_a,
        )
    response = client.get(
        "/translation-memory/",
        {"text": "no match", "pk": entities[0].pk, "locale": locale_a.code},
    )
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_view_concordance_search(client, project_a, locale_a, resource_a):
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i,)
        for i, x in enumerate(["abaa", "aBaf", "aaAb", "aAab"])
    ]
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cCDd",
        locale=locale_a,
        project=project_a,
    )

    response = client.get(
        "/concordance-search/", {"text": "cdd", "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result == {
        "results": [
            {u"source": u"aBaf", u"target": u"cCDd", u"project_names": [project_a.name]}
        ],
        "has_next": False,
    }

    response = client.get(
        "/concordance-search/", {"text": "abaa", "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result == {
        "results": [
            {u"source": u"abaa", u"target": u"ccc", u"project_names": [project_a.name]}
        ],
        "has_next": False,
    }


@pytest.mark.django_db
def test_view_concordance_search_multiple_project_names(
    client, project_a, project_b, locale_a, locale_b, resource_a
):
    """Check Concordance search doesn't produce duplicated search results."""
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i,)
        for i, x in enumerate(["abaa", "abaf"])
    ]
    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_b,
    )
    response = client.get(
        "/concordance-search/", {"text": "ccc", "locale": locale_a.code},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {
                "source": "abaa",
                "target": "ccc",
                "project_names": [project_a.name, project_b.name],
            },
            {"source": "abaf", "target": "ccc", "project_names": [project_a.name]},
        ],
        "has_next": False,
    }


@pytest.mark.django_db
def test_view_concordance_search_remove_duplicates(
    client, project_a, locale_a, resource_a
):
    """Check Concordance search doesn't produce duplicated search results."""
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i,)
        for i, x in enumerate(["abaa", "abaf"])
    ]
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )

    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cccbbb",
        locale=locale_a,
        project=project_a,
    )

    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cccbbb",
        locale=locale_a,
        project=project_a,
    )

    response = client.get(
        "/concordance-search/", {"text": "ccc", "locale": locale_a.code},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {"source": "abaa", "target": "ccc", "project_names": [project_a.name]},
            {"source": "abaf", "target": "ccc", "project_names": [project_a.name]},
            {"source": "abaf", "target": "cccbbb", "project_names": [project_a.name]},
        ],
        "has_next": False,
    }


@pytest.mark.django_db
@pytest.mark.parametrize(
    "parameters",
    (
        {"limit": "a", "page": 1},
        {"limit": "a", "page": "a"},
        {"limit": 1, "page": "a"},
    ),
)
def test_view_concordance_search_invalid_pagination_parameters(
    parameters, client, locale_a
):
    response = client.get(
        "/concordance-search/", {"text": "ccc", "locale": locale_a.code, **parameters},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_concordance_search_pagination(client, project_a, locale_a, resource_a):
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i)
        for i, x in enumerate(["abaa", "abaf"])
    ]
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=project_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cccbbb",
        locale=locale_a,
        project=project_a,
    )

    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cccbbb",
        locale=locale_a,
        project=project_a,
    )

    response = client.get(
        "/concordance-search/", {"text": "ccc", "locale": locale_a.code, "limit": 1},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {"source": "abaa", "target": "ccc", "project_names": [project_a.name]},
        ],
        "has_next": True,
    }

    response = client.get(
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code, "limit": 1, "page": 2},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {"source": "abaf", "target": "cccbbb", "project_names": [project_a.name]},
        ],
        "has_next": False,
    }

    # Check a query that should return no results
    response = client.get(
        "/concordance-search/",
        {"text": "TEST", "locale": locale_a.code, "limit": 1, "page": 2},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [],
        "has_next": False,
    }
