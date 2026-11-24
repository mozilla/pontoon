from unittest.mock import patch

import pytest

from django.shortcuts import render
from django.urls import reverse

from pontoon.base.models import Project
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


@pytest.mark.django_db
@patch("pontoon.localizations.views.render", wraps=render)
def test_ajax_resources(mock_render, client, project_a, locale_a):
    """Ensure that the latest_activity field is added to parts."""
    ProjectLocaleFactory.create(locale=locale_a, project=project_a)

    resource1 = ResourceFactory.create(project=project_a, path="has/stats1.po")
    resource2 = ResourceFactory.create(project=project_a, path="has/stats2.po")

    entity = EntityFactory.create(resource=resource1)
    EntityFactory.create(resource=resource2)
    translation = TranslationFactory.create(entity=entity, locale=locale_a)

    tr = TranslatedResourceFactory.create(
        resource=resource2, locale=locale_a, latest_translation=translation
    )
    tr.total_strings = 1
    tr.save()

    client.get(
        reverse(
            "pontoon.localizations.ajax.resources",
            args=[locale_a.code, project_a.slug],
        ),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    ctx = mock_render.call_args[0][2]

    assert len(ctx["resources"]) == 2

    res = ctx["resources"][1]
    assert res.title == "has/stats2.po"
    assert res.deadline is None
    assert res.priority is None
    assert res.latest_activity == translation.latest_activity
    assert res.chart == {
        "total": 1,
        "pretranslated": 0,
        "approved": 0,
        "unreviewed": 0,
        "errors": 0,
        "warnings": 0,
    }


@pytest.mark.django_db
def test_localization_view_private_stats(
    client_superuser, project_a, locale_a, project_locale_a, resource_a
):
    """Private project locale stats are visible to superusers."""
    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()
    TranslatedResourceFactory.create(
        resource=resource_a,
        locale=locale_a,
        total_strings=1,
        approved_strings=1,
    )

    with patch("pontoon.localizations.views.render", wraps=render) as mock_render:
        response = client_superuser.get(
            reverse(
                "pontoon.localizations.localization",
                args=[locale_a.code, project_a.slug],
            )
        )

    assert response.status_code == 200
    stats = mock_render.call_args[0][2]["project_locale_stats"]
    assert stats["total"] > 0
    assert stats["approved"] > 0


@pytest.mark.django_db
def test_localization_view_private_stats_anonymous(
    client, project_a, locale_a, project_locale_a, resource_a
):
    """Private project locale stats are hidden from anonymous users."""
    # The page is accessible while public; the 404 below is caused by visibility.
    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            args=[locale_a.code, project_a.slug],
        )
    )
    assert response.status_code == 200

    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()

    response = client.get(
        reverse(
            "pontoon.localizations.localization",
            args=[locale_a.code, project_a.slug],
        )
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_localization_view_private_stats_non_superuser(
    member, project_a, locale_a, project_locale_a, resource_a
):
    """Private project locale stats are hidden from non-superusers."""
    # The page is accessible while public; the 404 below is caused by visibility.
    response = member.client.get(
        reverse(
            "pontoon.localizations.localization",
            args=[locale_a.code, project_a.slug],
        )
    )
    assert response.status_code == 200

    project_a.visibility = Project.Visibility.PRIVATE
    project_a.save()

    response = member.client.get(
        reverse(
            "pontoon.localizations.localization",
            args=[locale_a.code, project_a.slug],
        )
    )
    assert response.status_code == 404
