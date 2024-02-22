from unittest.mock import patch

import pytest

from django.urls import reverse
from django.shortcuts import render

from pontoon.base.tests import (
    EntityFactory,
    ResourceFactory,
    TranslationFactory,
    TranslatedResourceFactory,
    ProjectLocaleFactory,
)


@pytest.mark.django_db
@patch("pontoon.localizations.views.render", wraps=render)
def test_ajax_resources(mock_render, client, project_a, locale_a):
    """Ensure that the latest_activity field is added to parts."""
    ProjectLocaleFactory.create(locale=locale_a, project=project_a)

    resource = ResourceFactory.create(project=project_a, path="has/stats.po")
    resource2 = ResourceFactory.create(project=project_a, path="has/stats2.po")

    entity = EntityFactory.create(resource=resource)
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

    assert ctx["resources"][0].title == "has/stats2.po"
    assert ctx["resources"][0].deadline is None
    assert ctx["resources"][0].priority is None
    assert ctx["resources"][0].latest_activity == translation.latest_activity
    assert ctx["resources"][0].chart == {
        "pretranslated_strings": 0,
        "total_strings": 1,
        "approved_strings": 0,
        "unreviewed_strings": 0,
        "strings_with_errors": 0,
        "strings_with_warnings": 0,
        "approved_share": 0.0,
        "unreviewed_share": 0.0,
        "pretranslated_share": 0.0,
        "warnings_share": 0.0,
        "errors_share": 0.0,
        "completion_percent": 0,
    }
