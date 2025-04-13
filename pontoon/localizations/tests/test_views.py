from unittest.mock import patch

import pytest

from django.shortcuts import render
from django.urls import reverse

from pontoon.base.tests import (
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
