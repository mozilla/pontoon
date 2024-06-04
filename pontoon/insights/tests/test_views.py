import json
import pytest

from dataclasses import dataclass
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.shortcuts import render
from django.urls import reverse
from http import HTTPStatus
from pontoon.actionlog.models import ActionLog
from pontoon.insights import views
from pontoon.test.factories import (
    ResourceFactory,
    TranslationFactory,
)
from unittest.mock import patch


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
def test_default_empty(
    client, clear_cache, sync_user, tm_user, locale_a, project_a, user_a
):
    url = reverse("pontoon.insights")
    with patch.object(views, "render", wraps=render) as mock_render:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    response_context = mock_render.call_args[0][2]
    start_date = response_context["start_date"]
    end_date = response_context["end_date"]
    assert start_date < end_date <= datetime.now(timezone.utc)
    team_pretranslation_quality = response_context["team_pretranslation_quality"]
    assert json.loads(team_pretranslation_quality["dataset"]) == [
        {
            "name": "All",
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
    assert json.loads(project_pretranslation_quality["dataset"]) == [
        {
            "name": "All",
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
    client, clear_cache, sync_user, tm_user, locale_a, project_a, user_a
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
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    response_context = mock_render.call_args[0][2]
    start_date = response_context["start_date"]
    end_date = response_context["end_date"]
    assert start_date < end_date <= datetime.now(timezone.utc)
    team_pretranslation_quality = response_context["team_pretranslation_quality"]
    assert json.loads(team_pretranslation_quality["dataset"]) == [
        {
            "name": "All",
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
    ]
    project_pretranslation_quality = response_context["project_pretranslation_quality"]
    assert json.loads(project_pretranslation_quality["dataset"]) == [
        {
            "name": "All",
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
    ]
