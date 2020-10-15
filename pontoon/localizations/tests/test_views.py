import pytest

from mock import patch

from django.urls import reverse
from django.shortcuts import render

from pontoon.base.models import Locale
from pontoon.base.tests import (
    ResourceFactory,
    TranslationFactory,
    TranslatedResourceFactory,
)


@pytest.mark.django_db
@patch("pontoon.localizations.views.render", wraps=render)
@patch.object(Locale, "parts_stats")
def test_latest_activity(mock_parts_stats, mock_render, client, project_a, locale_a):
    """Ensure that the latest_activity field is added to parts."""
    resource = ResourceFactory.create(project=project_a, path="has/stats.po")
    resource2 = ResourceFactory.create(project=project_a, path="has/stats2.po")

    translation = TranslationFactory.create(entity__resource=resource, locale=locale_a)
    TranslatedResourceFactory.create(
        resource=resource2, locale=locale_a, latest_translation=translation
    )

    mock_parts_stats.return_value = [
        {
            "title": "has/stats.po",
            "resource__path": "has/stats.po",
            "resource__total_strings": 1,
            "approved_strings": 0,
            "unreviewed_strings": 1,
            "fuzzy_strings": 0,
            "strings_with_warnings": 0,
            "strings_with_errors": 0,
            "resource__deadline": None,
            "resource__priority": None,
        },
        {
            "title": "no/stats.po",
            "resource__path": "no/stats.po",
            "resource__total_strings": 1,
            "approved_strings": 0,
            "unreviewed_strings": 0,
            "fuzzy_strings": 0,
            "strings_with_warnings": 0,
            "strings_with_errors": 0,
            "resource__deadline": None,
            "resource__priority": None,
        },
    ]

    client.get(
        reverse(
            "pontoon.localizations.ajax.resources",
            args=[locale_a.code, project_a.slug],
        ),
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    ctx = mock_render.call_args[0][2]

    assert ctx["resources"] == [
        {
            "latest_activity": translation.latest_activity,
            "title": "has/stats.po",
            "resource__path": "has/stats.po",
            "resource__deadline": None,
            "resource__priority": None,
            "resource__total_strings": 1,
            "approved_strings": 0,
            "unreviewed_strings": 1,
            "fuzzy_strings": 0,
            "strings_with_errors": 0,
            "strings_with_warnings": 0,
            "chart": {
                "fuzzy_strings": 0,
                "total_strings": 1,
                "approved_strings": 0,
                "unreviewed_strings": 1,
                "strings_with_errors": 0,
                "strings_with_warnings": 0,
                "approved_share": 0.0,
                "unreviewed_share": 100.0,
                "fuzzy_share": 0.0,
                "warnings_share": 0.0,
                "errors_share": 0.0,
                "completion_percent": 0,
            },
        },
        {
            "latest_activity": None,
            "title": "no/stats.po",
            "resource__path": "no/stats.po",
            "resource__deadline": None,
            "resource__priority": None,
            "resource__total_strings": 1,
            "approved_strings": 0,
            "unreviewed_strings": 0,
            "fuzzy_strings": 0,
            "strings_with_errors": 0,
            "strings_with_warnings": 0,
            "chart": {
                "fuzzy_strings": 0,
                "total_strings": 1,
                "approved_strings": 0,
                "unreviewed_strings": 0,
                "strings_with_errors": 0,
                "strings_with_warnings": 0,
                "approved_share": 0.0,
                "unreviewed_share": 0.0,
                "fuzzy_share": 0.0,
                "warnings_share": 0.0,
                "errors_share": 0.0,
                "completion_percent": 0,
            },
        },
    ]
