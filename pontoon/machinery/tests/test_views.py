import json
import urllib.parse

from unittest.mock import MagicMock, patch

import pytest
import requests
import requests_mock

from django.core.cache import cache
from django.urls import reverse

from pontoon.base.models import (
    Entity,
    Locale,
)
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    SectionFactory,
    TeamCommentFactory,
    TermFactory,
    TermTranslationFactory,
    TranslationFactory,
    TranslationMemoryFactory,
)


@pytest.mark.django_db
def test_view_microsoft_translator_not_logged_in(client, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")
    response = client.get(url, {"text": "text", "locale": ms_locale.ms_translator_code})

    assert response.status_code == 302


@pytest.mark.django_db
def test_view_microsoft_translator(member, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")

    with requests_mock.mock() as m:
        data = [{"translations": [{"text": "target"}]}]
        m.post("https://api.cognitive.microsofttranslator.com/translate", json=data)
        response = member.client.get(
            url,
            {"text": "text", "locale": ms_locale.ms_translator_code},
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
def test_view_microsoft_translator_bad_locale(member, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")
    response = member.client.get(url, {"text": "text", "locale": "bad"})

    assert response.status_code == 401


@pytest.mark.django_db
def test_view_microsoft_translator_missing_api_key(member, ms_locale, settings):
    settings.MICROSOFT_TRANSLATOR_API_KEY = ""
    cache.clear()
    url = reverse("pontoon.microsoft_translator")
    response = member.client.get(
        url, {"text": "text", "locale": ms_locale.ms_translator_code}
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_microsoft_translator_api_http_error(member, ms_locale, ms_api_key):
    cache.clear()
    url = reverse("pontoon.microsoft_translator")
    with requests_mock.mock() as m:
        m.post(
            "https://api.cognitive.microsofttranslator.com/translate",
            status_code=401,
        )
        response = member.client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code}
        )
    assert response.status_code == 401


@pytest.mark.django_db
def test_view_microsoft_translator_api_connection_error(member, ms_locale, ms_api_key):
    cache.clear()
    url = reverse("pontoon.microsoft_translator")
    with requests_mock.mock() as m:
        m.post(
            "https://api.cognitive.microsofttranslator.com/translate",
            exc=requests.exceptions.ConnectionError,
        )
        response = member.client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code}
        )
    assert response.status_code == 500


@pytest.mark.django_db
def test_view_microsoft_translator_api_error_in_response(member, ms_locale, ms_api_key):
    cache.clear()
    url = reverse("pontoon.microsoft_translator")
    with requests_mock.mock() as m:
        m.post(
            "https://api.cognitive.microsofttranslator.com/translate",
            json={"error": {"code": 400000, "message": "Bad request"}},
        )
        response = member.client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code}
        )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_google_translate_not_logged_in(
    client, google_translate_locale, google_translate_api_key
):
    url = reverse("pontoon.google_translate")
    response = client.get(
        url, {"text": "text", "locale": google_translate_locale.google_translate_code}
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_view_google_translate(
    member, google_translate_locale, google_translate_api_key
):
    url = reverse("pontoon.google_translate")

    with requests_mock.mock() as m:
        data = {"data": {"translations": [{"translatedText": "target"}]}}
        m.post("https://translation.googleapis.com/language/translate/v2", json=data)
        response = member.client.get(
            url,
            {"text": "text", "locale": google_translate_locale.code},
        )

    assert response.status_code == 200
    assert json.loads(response.content) == {
        "translation": "target",
    }

    req = m.request_history[0]

    assert urllib.parse.parse_qs(req.query) == {
        "q": ["text"],
        "source": ["en"],
        "target": ["google-translate"],
        "format": ["text"],
        "key": ["2fffff"],
    }


@pytest.mark.django_db
def test_view_google_translate_bad_locale(
    member,
    google_translate_locale,
    google_translate_api_key,
):
    url = reverse("pontoon.google_translate")
    response = member.client.get(url, {"text": "text", "locale": "bad"})

    assert response.status_code == 400


@pytest.mark.django_db
def test_view_google_translate_missing_api_key(
    member, google_translate_locale, settings
):
    settings.GOOGLE_TRANSLATE_API_KEY = ""
    cache.clear()
    url = reverse("pontoon.google_translate")
    response = member.client.get(
        url, {"text": "text", "locale": google_translate_locale.code}
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_google_translate_api_http_error(
    member, google_translate_locale, google_translate_api_key
):
    cache.clear()
    url = reverse("pontoon.google_translate")
    with requests_mock.mock() as m:
        m.post(
            "https://translation.googleapis.com/language/translate/v2",
            status_code=403,
        )
        response = member.client.get(
            url, {"text": "text", "locale": google_translate_locale.code}
        )
    assert response.status_code == 403


@pytest.mark.django_db
def test_view_google_translate_api_connection_error(
    member, google_translate_locale, google_translate_api_key
):
    cache.clear()
    url = reverse("pontoon.google_translate")
    with requests_mock.mock() as m:
        m.post(
            "https://translation.googleapis.com/language/translate/v2",
            exc=requests.exceptions.ConnectionError,
        )
        response = member.client.get(
            url, {"text": "text", "locale": google_translate_locale.code}
        )
    assert response.status_code == 500


@pytest.mark.django_db
def test_view_google_translate_api_unexpected_response(
    member, google_translate_locale, google_translate_api_key
):
    cache.clear()
    url = reverse("pontoon.google_translate")
    with requests_mock.mock() as m:
        m.post(
            "https://translation.googleapis.com/language/translate/v2",
            json={"unexpected": "response"},
        )
        response = member.client.get(
            url, {"text": "text", "locale": google_translate_locale.code}
        )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_microsoft_translator_cache(member, ms_locale, ms_api_key):
    url = reverse("pontoon.microsoft_translator")
    cache.clear()

    with requests_mock.mock() as m:
        data = [{"translations": [{"text": "target"}]}]
        m.post("https://api.cognitive.microsofttranslator.com/translate", json=data)

        response1 = member.client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code}
        )
        assert len(m.request_history) == 1

        # Second identical request should be served from cache
        response2 = member.client.get(
            url, {"text": "text", "locale": ms_locale.ms_translator_code}
        )
        assert len(m.request_history) == 1

    assert json.loads(response1.content) == json.loads(response2.content)


@pytest.mark.django_db
def test_view_google_translate_cache(
    member, google_translate_locale, google_translate_api_key
):
    url = reverse("pontoon.google_translate")
    cache.clear()

    with requests_mock.mock() as m:
        data = {"data": {"translations": [{"translatedText": "target"}]}}
        m.post("https://translation.googleapis.com/language/translate/v2", json=data)

        response1 = member.client.get(
            url, {"text": "text", "locale": google_translate_locale.code}
        )
        assert len(m.request_history) == 1

        # Second identical request should be served from cache
        response2 = member.client.get(
            url, {"text": "text", "locale": google_translate_locale.code}
        )
        assert len(m.request_history) == 1

    assert json.loads(response1.content) == json.loads(response2.content)


@pytest.mark.django_db
def test_view_gpt_transform_cache(member, locale_a, openai_api_key):
    url = reverse("pontoon.gpt_transform")
    cache.clear()

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "  formal translation  "

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.return_value = mock_response

        params = {
            "english_text": "Hello",
            "translated_text": "Hola",
            "characteristic": "formal",
            "locale": locale_a.code,
        }

        response1 = member.client.post(url, params)
        assert MockOpenAI.return_value.chat.completions.create.call_count == 1

        # Second identical request should be served from cache
        response2 = member.client.post(url, params)
        assert MockOpenAI.return_value.chat.completions.create.call_count == 1

    assert json.loads(response1.content) == json.loads(response2.content)


@pytest.mark.django_db
def test_view_gpt_transform_context(member, locale_a, openai_api_key):
    url = reverse("pontoon.gpt_transform")
    cache.clear()

    mock_response = MagicMock()
    mock_response.choices[0].message.content = "translated"

    # Create entity with full context: key, comment, group (section) comment,
    # resource comment
    section = SectionFactory(key=["nav"], comment="Navigation section")
    entity = EntityFactory(
        key=["open-browser"],
        string="Open browser",
        comment="Button label",
        resource=section.resource,
        section=section,
    )
    entity.resource.comment = "Main UI file"
    entity.resource.save(update_fields=["comment"])

    # Pinned comment
    TeamCommentFactory(
        entity=entity,
        locale=locale_a,
        content="<p>Use formal register</p>",
        pinned=True,
    )
    TeamCommentFactory(
        entity=entity, locale=locale_a, content="Keep it short", pinned=True
    )

    # Term matching the source string, with a translation for the target locale
    term = TermFactory(
        text="browser", part_of_speech="noun", definition="A web browser"
    )
    TermTranslationFactory(term=term, locale=locale_a, text="navigateur")

    with patch("pontoon.machinery.openai_service.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.chat.completions.create.return_value = mock_response

        member.client.post(
            url,
            {
                "english_text": "Open browser",
                "translated_text": "Ouvrir le navigateur",
                "characteristic": "formal",
                "locale": locale_a.code,
                "entity_pk": entity.pk,
            },
        )

    call_kwargs = MockOpenAI.return_value.chat.completions.create.call_args
    user_message = call_kwargs.kwargs["messages"][1]["content"]
    assert "STRING ID:\nopen-browser" in user_message
    assert "STRING COMMENT:\nButton label" in user_message
    assert "GROUP COMMENT:\nNavigation section" in user_message
    assert "RESOURCE COMMENT:\nMain UI file" in user_message
    assert "PINNED COMMENTS:" in user_message
    assert "Use formal register" in user_message
    assert "Keep it short" in user_message
    assert "TERMINOLOGY:" in user_message
    assert '"browser" (noun) → "navigateur"' in user_message


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
        approved=True,
    )
    entity_a.translation_set.add(translation)

    with requests_mock.mock() as m:
        m.post("https://cadhan.com/api/intergaelic/3.0", text='[["source", "target"]]')
        response = client.get(url, dict(id=entity_a.id))

    assert json.loads(response.content) == {
        "translation": "target",
        "original": translation.string,
    }
    assert urllib.parse.parse_qs(m.request_history[0].text) == {
        "teacs": [translation.string],
        "foinse": [gd.code],
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
        "Bad Request: invalid literal for int() with base 10: 'DOESNOTEXIST'"
    )

    maxid = Entity.objects.values_list("id", flat=True).order_by("-id").first()
    response = client.get(url, dict(id=maxid + 1))
    assert response.status_code == 400
    assert response.get("Content-Type") == "application/json"
    assert (
        json.loads(response.content)["message"]
        == "Bad Request: Entity matching query does not exist."
    )

    translation = TranslationFactory.create(
        entity=entity_a,
        locale=gd,
        string="foo",
        approved=True,
    )
    entity_a.translation_set.add(translation)

    with requests_mock.mock() as m:
        m.post("https://cadhan.com/api/intergaelic/3.0", status_code=500)
        response = client.get(url, dict(id=entity_a.id))

    assert response.status_code == 500
    assert response.get("Content-Type") == "application/json"
    assert (
        json.loads(response.content)["message"]
        == "500 Server Error: None for url: https://cadhan.com/api/intergaelic/3.0"
    )


@pytest.mark.django_db
def test_view_translation_memory_best_quality_entry(
    client,
    locale_a,
    resource_a,
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
        entity=entities[0],
        source="aaa",
        target="ccc",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1],
        source="aaa",
        target="ddd",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[2],
        source="bbb",
        target="ccc",
        locale=locale_a,
    )
    response = client.get(
        "/translation-memory/",
        {"text": "aaa", "pk": tm.entity.pk, "locale": locale_a.code},
    )
    assert json.loads(response.content) == [
        {"count": 1, "source": "aaa", "quality": "100", "target": "ddd"}
    ]


@pytest.mark.django_db
def test_view_translation_memory_translation_counts(
    client,
    locale_a,
    resource_a,
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
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="ccc",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[2],
        source=entities[2].string,
        target="ccc",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entities[3],
        source=entities[3].string,
        target="ccc",
        locale=locale_a,
    )
    response = client.get(
        "/translation-memory/",
        {"text": "aaaa", "pk": tm.entity.pk, "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result[0].pop("source") in ("abaa", "aaab", "aaab")
    assert result == [{"count": 3, "quality": "75", "target": "ccc"}]


@pytest.mark.django_db
def test_view_tm_exclude_entity(client, entity_a, locale_a, resource_a):
    """
    Exclude entity from results to avoid false positive results.
    """
    tm = TranslationMemoryFactory.create(
        entity=entity_a,
        source=entity_a.string,
        target="ccc",
        locale=locale_a,
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
        EntityFactory(
            resource=resource_a,
            string=x,
            order=i,
        )
        for i, x in enumerate(["abaa", "aBaf", "aaAb", "aAab"])
    ]
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
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
        "/concordance-search/",
        {"text": "cdd", "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result == {
        "results": [
            {
                "source": "aBaf",
                "target": "cCDd",
                "projects": [
                    {
                        "name": "Project A",
                        "slug": "project_a",
                    }
                ],
                "entities": [entities[1].id],
            }
        ],
        "has_next": False,
    }

    response = client.get(
        "/concordance-search/",
        {"text": "abaa", "locale": locale_a.code},
    )
    result = json.loads(response.content)
    assert result == {
        "results": [
            {
                "source": "abaa",
                "target": "ccc",
                "projects": [
                    {
                        "name": "Project A",
                        "slug": "project_a",
                    }
                ],
                "entities": [entities[0].id],
            }
        ],
        "has_next": False,
    }


@pytest.mark.django_db
def test_view_concordance_search_multiple_names(
    client, project_a, project_b, locale_a, locale_b, resource_a
):
    """Check Concordance search doesn't produce duplicated search results."""
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x,
            order=i,
        )
        for i, x in enumerate(["abaa", "abaf"])
    ]
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
    ProjectLocaleFactory.create(project=project_b, locale=locale_a)
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
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {
                "source": "abaa",
                "target": "ccc",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    },
                    {
                        "name": project_b.name,
                        "slug": project_b.slug,
                    },
                ],
                "entities": [entities[0].id],
            },
            {
                "source": "abaf",
                "target": "ccc",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[1].id],
            },
        ],
        "has_next": False,
    }


@pytest.mark.django_db
def test_view_concordance_search_remove_duplicates(
    client, project_a, locale_a, resource_a
):
    """Check Concordance search doesn't produce duplicated search results."""
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x,
            order=i,
        )
        for i, x in enumerate(["abaa", "abaf"])
    ]
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
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
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {
                "source": "abaa",
                "target": "ccc",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[0].id],
            },
            {
                "source": "abaf",
                "target": "ccc",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[1].id],
            },
            {
                "source": "abaf",
                "target": "cccbbb",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[1].id],
            },
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
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code, **parameters},
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_view_concordance_search_pagination(client, project_a, locale_a, resource_a):
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i)
        for i, x in enumerate(["abaa", "abaf"])
    ]
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)

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
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code, "limit": 1},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {
                "source": "abaa",
                "target": "ccc",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[0].id],
            },
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
            {
                "source": "abaf",
                "target": "cccbbb",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[1].id],
            },
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


@pytest.mark.django_db
def test_view_concordance_search_null_project_exclusion(
    client, project_a, locale_a, resource_a
):
    entities = [
        EntityFactory(
            resource=resource_a,
            string=x,
            order=i,
        )
        for i, x in enumerate(["abaa", "abaf"])
    ]

    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
    TranslationMemoryFactory.create(
        entity=entities[0],
        source=entities[0].string,
        target="ccc",
        locale=locale_a,
        project=None,
    )

    TranslationMemoryFactory.create(
        entity=entities[1],
        source=entities[1].string,
        target="cccbbb",
        locale=locale_a,
        project=project_a,
    )

    response = client.get(
        "/concordance-search/",
        {"text": "ccc", "locale": locale_a.code},
    )
    results = json.loads(response.content)
    assert results == {
        "results": [
            {
                "source": "abaf",
                "target": "cccbbb",
                "projects": [
                    {
                        "name": project_a.name,
                        "slug": project_a.slug,
                    }
                ],
                "entities": [entities[1].id],
            },
        ],
        "has_next": False,
    }
