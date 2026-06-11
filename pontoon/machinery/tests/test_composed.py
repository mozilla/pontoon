import json

from textwrap import dedent
from unittest.mock import patch

import pytest

from django.urls import reverse

from pontoon.test.factories import (
    EntityFactory,
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
def test_composed_unsupported_format(client, entity_a, locale_a):
    """Non-composable formats (e.g. gettext-without-MF2-context: still allowed) skip cleanly.

    `entity_a` uses the `resource_a` gettext fixture, which IS in COMPOSED_FORMATS,
    so we should NOT get an empty response for it. Use a DTD fixture instead — DTD
    is not in the composable set, so we expect an empty `{}`.
    """
    dtd_resource = ResourceFactory(
        project=entity_a.resource.project, path="r.dtd", format="dtd"
    )
    dtd_entity = EntityFactory(resource=dtd_resource, string="Hello")

    url = reverse("pontoon.machinery_composed")
    response = client.get(
        url,
        {
            "entity": str(dtd_entity.pk),
            "locale": locale_a.code,
            "service": "translation-memory",
        },
    )
    assert response.status_code == 200
    assert json.loads(response.content) == {}


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
    body = json.loads(response.content)
    assert body["original"] == fluent_string
    assert "TM_value" in body["translation"]
    assert "TM_tooltip" in body["translation"]
    assert body["sources"] == ["translation-memory"]
    # Every leaf is a 100% TM match, so the composed result is a full TM match.
    assert body["quality"] == 100


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


@patch("pontoon.machinery.views.get_google_translate_data")
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
    body = json.loads(response.content)
    assert "TM_value" in body["translation"]
    assert "MT_tooltip" in body["translation"]
    assert set(body["sources"]) == {"translation-memory", "google-translate"}
    # MT-assisted results have no meaningful aggregate quality score.
    assert "quality" not in body
