from unittest.mock import patch

import pytest

from pontoon.base.models import Entity


@pytest.mark.django_db
def test_view_entity_filters(member, resource_a, locale_a):
    """
    Tests if right filter calls right method in the Entity manager.
    """
    filters = (
        "missing",
        "fuzzy",
        "unreviewed",
        "translated",
        "unchanged",
        "rejected",
    )
    for filter_ in filters:
        filter_name = filter_.replace("-", "_")
        params = {
            "project": resource_a.project.slug,
            "locale": locale_a.code,
            "paths[]": [resource_a.path],
            "limit": 1,
        }
        if filter_ in ("unchanged", "has-suggestions", "rejected"):
            params["extra"] = filter_
        else:
            params["status"] = filter_
        patched_entity = patch(f"pontoon.base.models.Entity.objects.{filter_name}")
        with patched_entity as m:
            m.return_value = getattr(Entity.objects, filter_name)(locale_a)
            member.client.post(
                "/get-entities/",
                params,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )
            assert m.called is True
