from dataclasses import dataclass
from datetime import date, datetime, timezone
from http import HTTPStatus
from unittest.mock import patch

import pytest

from dateutil.relativedelta import relativedelta

from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse

from pontoon.actionlog.models import ActionLog
from pontoon.base.utils import convert_to_unix_time
from pontoon.insights import views
from pontoon.insights.models import LocaleHealthSnapshot
from pontoon.insights.utils import (
    get_global_locale_health_insights,
    get_locale_health_data,
)
from pontoon.test.factories import (
    LocaleFactory,
    ResourceFactory,
    TranslationFactory,
)


@pytest.fixture
def clear_cache():
    cache.clear()


def perform_action(action_type, translation, user, timestamp):
    action = ActionLog.objects.create(
        action_type=action_type,
        performed_by=user,
        translation=translation,
    )
    action.created_at = timestamp
    action.save()
    return action


@dataclass
class MonthlyQualityEntry:
    months_ago: int
    approved: int
    rejected: int


@pytest.mark.django_db
def test_default_empty(client_superuser, clear_cache, locale_a, project_a, user_a):
    url = reverse("pontoon.insights")
    with patch.object(views, "render", wraps=render) as mock_render:
        response = client_superuser.get(url)
    assert response.status_code == HTTPStatus.OK

    response_context = mock_render.call_args[0][2]
    start_date = response_context["start_date"]
    end_date = response_context["end_date"]
    assert start_date < end_date <= datetime.now(timezone.utc)
    team_pretranslation_quality = response_context["team_pretranslation_quality"]
    assert team_pretranslation_quality["dataset"] == [
        {
            "name": "Average (all locales)",
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        }
    ]
    project_pretranslation_quality = response_context["project_pretranslation_quality"]
    assert project_pretranslation_quality["dataset"] == [
        {
            "name": "Average (all locales)",
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        }
    ]


@pytest.mark.django_db
def test_default_with_data(
    client_superuser, clear_cache, tm_user, locale_a, project_a, user_a
):
    entries = [
        MonthlyQualityEntry(months_ago=0, approved=1, rejected=0),
        MonthlyQualityEntry(months_ago=1, approved=0, rejected=1),
        MonthlyQualityEntry(months_ago=2, approved=1, rejected=1),
        MonthlyQualityEntry(months_ago=3, approved=3, rejected=0),
        MonthlyQualityEntry(months_ago=4, approved=0, rejected=3),
        MonthlyQualityEntry(months_ago=5, approved=3, rejected=1),
    ]
    resource = ResourceFactory.create(project=project_a, path="has/stats.po")

    now = datetime.now(timezone.utc)
    for entry in entries:
        timestamp = now - relativedelta(now, months=entry.months_ago)
        for approval_index in range(entry.approved):
            translation = TranslationFactory.create(
                entity__resource=resource, locale=locale_a, user=tm_user
            )
            perform_action(
                ActionLog.ActionType.TRANSLATION_APPROVED,
                translation,
                user_a,
                timestamp,
            )
        for rejected_index in range(entry.rejected):
            translation = TranslationFactory.create(
                entity__resource=resource, locale=locale_a, user=tm_user
            )
            perform_action(
                ActionLog.ActionType.TRANSLATION_REJECTED,
                translation,
                user_a,
                timestamp,
            )

    url = reverse("pontoon.insights")
    with patch.object(views, "render", wraps=render) as mock_render:
        response = client_superuser.get(url)
    assert response.status_code == HTTPStatus.OK

    response_context = mock_render.call_args[0][2]
    start_date = response_context["start_date"]
    end_date = response_context["end_date"]
    assert start_date < end_date <= datetime.now(timezone.utc)
    team_pretranslation_quality = response_context["team_pretranslation_quality"]
    assert team_pretranslation_quality["dataset"] == [
        {
            "name": f"{locale_a.name} · {locale_a.code}",
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                75.0,
                0.0,
                100.0,
                50.0,
                0.0,
                100.0,
            ],
        },
        {
            "name": "Average (all locales)",
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                75.0,
                0.0,
                100.0,
                50.0,
                0.0,
                100.0,
            ],
        },
    ]
    project_pretranslation_quality = response_context["project_pretranslation_quality"]
    assert project_pretranslation_quality["dataset"] == [
        {
            "name": project_a.name,
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                75.0,
                0.0,
                100.0,
                50.0,
                0.0,
                100.0,
            ],
        },
        {
            "name": "Average (all locales)",
            "approval_rate": [
                None,
                None,
                None,
                None,
                None,
                None,
                75.0,
                0.0,
                100.0,
                50.0,
                0.0,
                100.0,
            ],
        },
    ]


@pytest.mark.django_db
def test_get_locale_health_data_date_alignment():
    """Dates are the snapshot months shifted back one (noon-anchored), and each
    locale's scores align by index with None padding for missing months."""
    locale_a = LocaleFactory.create()
    locale_b = LocaleFactory.create()

    # locale_a missing 2024-04-01 snapshot
    LocaleHealthSnapshot.objects.create(
        locale=locale_a, created_at=date(2024, 2, 1), chs=10
    )
    LocaleHealthSnapshot.objects.create(
        locale=locale_a, created_at=date(2024, 3, 1), chs=20
    )
    LocaleHealthSnapshot.objects.create(
        locale=locale_a, created_at=date(2024, 5, 1), chs=30
    )
    # locale_b missing 2024-03-01 snapshot
    LocaleHealthSnapshot.objects.create(
        locale=locale_b, created_at=date(2024, 3, 1), chs=40
    )
    LocaleHealthSnapshot.objects.create(
        locale=locale_b, created_at=date(2024, 5, 1), chs=50
    )

    dates, data = get_locale_health_data([locale_a, locale_b])

    # Distinct snapshot months (Feb, Mar, May) shifted back one month
    assert dates == [
        convert_to_unix_time(date(2024, 1, 1), anchor_noon=True),
        convert_to_unix_time(date(2024, 2, 1), anchor_noon=True),
        convert_to_unix_time(date(2024, 4, 1), anchor_noon=True),
    ]

    assert data[locale_a.code]["chs"][:3] == [10.0, 20.0, 30.0]
    assert data[locale_b.code]["chs"][:3] == [None, 40.0, 50.0]


@pytest.mark.django_db
def test_get_global_locale_health_insights_shape():
    locale_a = LocaleFactory.create()
    locale_b = LocaleFactory.create()
    LocaleHealthSnapshot.objects.create(
        locale=locale_a, created_at=date(2024, 3, 1), chs=10
    )
    LocaleHealthSnapshot.objects.create(
        locale=locale_b, created_at=date(2024, 3, 1), chs=20
    )

    insights = get_global_locale_health_insights([locale_a, locale_b])

    assert insights["dates"] == [
        convert_to_unix_time(date(2024, 2, 1), anchor_noon=True)
    ]
    assert len(insights["dataset"]) == 3
    assert insights["dataset"] == [
        {
            "name": f"{locale_a.name} · {locale_a.code}",
            "chs": [
                10.0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        },
        {
            "name": f"{locale_b.name} · {locale_b.code}",
            "chs": [
                20.0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        },
        {
            "name": "Average (all locales)",
            "chs": [
                15.0,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ],
        },
    ]
