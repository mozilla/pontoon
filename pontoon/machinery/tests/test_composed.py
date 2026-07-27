import json

from textwrap import dedent
from unittest.mock import patch

import pytest

from django.urls import reverse

from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ResourceFactory,
    TranslationMemoryFactory,
)


@pytest.fixture
def fluent_resource(project_a):
    return ResourceFactory(project=project_a, path="resource.ftl", format="fluent")


@pytest.mark.django_db
def test_composed_bad_request(client, locale_a):
    """Missing or invalid params should return 400."""
    url = reverse("pontoon.machinery_composed")

    response = client.get(url)
    assert response.status_code == 400

    response = client.get(url, {"entity": "not-a-number", "locale": locale_a.code})
    assert response.status_code == 400

    response = client.get(url, {"entity": "999999999", "locale": locale_a.code})
    assert response.status_code == 400


@pytest.mark.django_db
def test_composed_single_leaf_is_still_returned(
    client, fluent_resource, entity_a, locale_a
):
    """A single-leaf message composes; whether to show it is the caller's call.

    The composed result here just repeats the per-leaf TM match, so the
    Machinery panel doesn't ask for it (see `hasMultipleFields`), but the
    endpoint doesn't second-guess a caller that does.
    """
    fluent_string = dedent(
        """\
        networking-with-logs =
            .label = Networking with Logs
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Networking with Logs",
        target="TM_label",
        locale=locale_a,
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {
        "value": [],
        "properties": {"label": ["TM_label"]},
        "sources": ["translation-memory"],
        "quality": 100,
    }


@pytest.mark.django_db
def test_composed_multiple_attributes_no_value(
    client, fluent_resource, entity_a, locale_a
):
    """A Fluent message with several attributes but no value is multi-leaf.

    The empty value counts as zero, but the two attributes are two real leaves,
    so composition still applies: the composed suggestion fills both fields at
    once, which no single per-leaf match can do.
    """
    fluent_string = dedent(
        """\
        networking-with-logs =
            .label = Networking with Logs
            .tooltip = Record network requests
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Networking with Logs",
        target="TM_label",
        locale=locale_a,
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Record network requests",
        target="TM_tooltip",
        locale=locale_a,
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    # Attribute-only message: empty value, both attributes filled from TM.
    assert json.loads(response.content) == {
        "value": [],
        "properties": {"label": ["TM_label"], "tooltip": ["TM_tooltip"]},
        "sources": ["translation-memory"],
        "quality": 100,
    }


@pytest.mark.django_db
def test_composed_unknown_service(client, fluent_resource, locale_a):
    fluent_entity = EntityFactory(resource=fluent_resource, string="hello = Hello\n")
    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "bogus",
        },
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_composed_mt_service_requires_auth(
    client, fluent_resource, google_translate_locale
):
    """MT services require authentication; TM-only is anonymous-friendly."""
    fluent_entity = EntityFactory(resource=fluent_resource, string="hello = Hello\n")
    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": google_translate_locale.code,
            "service": "google-translate",
        },
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_composed_tm_only_full_hit(client, fluent_resource, entity_a, locale_a):
    """When every leaf has a TM hit, TM-only returns a composed Fluent string."""
    fluent_string = dedent(
        """
        button = Click Me
            .title = Tooltip text
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a, source="Click Me", target="TM_value", locale=locale_a
    )
    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Tooltip text",
        target="TM_tooltip",
        locale=locale_a,
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    # Every leaf is a 100% TM match, so the composed result is a full TM match.
    assert json.loads(response.content) == {
        "value": ["TM_value"],
        "properties": {"title": ["TM_tooltip"]},
        "sources": ["translation-memory"],
        "quality": 100,
    }


@pytest.mark.django_db
def test_composed_expands_source_plural_for_target_locale(
    client, fluent_resource, entity_a
):
    """A source with a single plural variant composes to multiple target patterns.

    en-US declares only `*[other]`, but a locale with several CLDR plural
    categories (here one/two/few/other) needs a pattern per category. The walk
    expands the selector to the locale's categories, so the entity counts as
    multi-pattern even though the source has a single variant, and a composed
    suggestion is returned.
    """
    locale = LocaleFactory(code="sl-test", name="Plural", cldr_plurals="1,2,3,5")

    fluent_string = dedent(
        """\
        popup =
            { $count ->
               *[other] Many popups.
            }
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a, source="Many popups.", target="TM_popups", locale=locale
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    body = json.loads(response.content)
    # The single `*[other]` source expands to all four of the target locale's
    # plural categories, each filled from the same TM match.
    assert body == {
        "value": {
            "decl": {"count": {"$": "count", "fn": "number"}},
            "sel": ["count"],
            "alt": [
                {"keys": ["one"], "pat": ["TM_popups"]},
                {"keys": ["two"], "pat": ["TM_popups"]},
                {"keys": ["few"], "pat": ["TM_popups"]},
                {"keys": [{"*": "other"}], "pat": ["TM_popups"]},
            ],
        },
        "properties": {},
        "sources": ["translation-memory"],
        "quality": 100,
    }


@pytest.mark.django_db
def test_composed_tm_only_partial_returns_empty(
    client, fluent_resource, entity_a, locale_a
):
    """TM-only mode emits no result when any leaf misses TM."""
    fluent_string = dedent(
        """
        button = Click Me
            .title = Tooltip text
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    # Only one of the two leaves has a TM match.
    TranslationMemoryFactory.create(
        entity=entity_a, source="Click Me", target="TM_value", locale=locale_a
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


@pytest.mark.django_db
def test_composed_tm_excludes_current_entity(client, fluent_resource, locale_a):
    """TM matches belonging to the composed entity itself are excluded.

    Once the entity is translated its leaves become TM entries; like regular TM
    matches, those must not be suggested back, so a TM-only composition that
    relies solely on them produces no result.
    """
    fluent_string = dedent(
        """
        button = Click Me
            .title = Tooltip text
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    # Both leaves only match TM entries that belong to this same entity.
    TranslationMemoryFactory.create(
        entity=fluent_entity, source="Click Me", target="TM_value", locale=locale_a
    )
    TranslationMemoryFactory.create(
        entity=fluent_entity,
        source="Tooltip text",
        target="TM_tooltip",
        locale=locale_a,
    )

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_composed_hybrid_tm_and_mt(
    gt_mock,
    member,
    fluent_resource,
    entity_a,
    google_translate_locale,
    google_translate_api_key,
):
    """TM hit for one leaf, MT fallback for the other — `sources` reflects the mix."""
    gt_mock.return_value = "MT_tooltip"

    fluent_string = dedent(
        """
        button = Click Me
            .title = Tooltip text
        """
    )
    fluent_entity = EntityFactory(resource=fluent_resource, string=fluent_string)

    TranslationMemoryFactory.create(
        entity=entity_a,
        source="Click Me",
        target="TM_value",
        locale=google_translate_locale,
    )

    url = reverse("pontoon.machinery_composed")
    response = member.client.get(
        url,
        {
            "entity": str(fluent_entity.pk),
            "locale": google_translate_locale.code,
            "service": "google-translate",
        },
    )
    assert response.status_code == 200
    # No `quality`: MT results carry no score, so there's nothing to aggregate.
    assert json.loads(response.content) == {
        "value": ["TM_value"],
        "properties": {"title": ["MT_tooltip"]},
        "sources": ["translation-memory", "google-translate"],
    }
