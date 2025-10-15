from datetime import timedelta

import pytest

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.insights.tasks import (
    Activity,
    count_activities,
    count_created_entities,
    count_projectlocale_stats,
    locale_insights,
    projectlocale_insights,
)
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


def now_times():
    now = (
        timezone.now()
        .replace(hour=0)
        .replace(minute=0)
        .replace(second=0)
        .replace(microsecond=0)
    )
    t = [now - relativedelta(days=1) + relativedelta(hours=i) for i in range(24)]
    return now, t


@pytest.mark.django_db
def test_count_activities(user_a, user_b, locale_a, project_locale_a, resource_a):
    now, t = now_times()
    tr = TranslationFactory.create(
        entity__resource=resource_a,
        locale=locale_a,
        user=user_a,
        date=t[1],
        active=True,
        approved=True,
        approved_user=user_b,
        approved_date=t[2],
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        created_at=t[1],
        performed_by=user_a,
        translation=tr,
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        created_at=t[2],
        performed_by=user_b,
        translation=tr,
    )
    assert count_activities(now) == {
        project_locale_a.pk: Activity(
            locale=locale_a.pk,
            human_translations={tr.pk},
            new_suggestions={tr.pk},
            peer_approved={tr.pk},
            times_to_review_suggestions=[t[2] - t[1]],
        )
    }


@pytest.mark.django_db
def test_count_created_entities(locale_a, project_locale_a, resource_a):
    now, t = now_times()
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    EntityFactory.create(resource=resource_a, date_created=t[1])
    EntityFactory.create(resource=resource_a, date_created=t[2])
    EntityFactory.create(resource=resource_a, date_created=t[2])
    EntityFactory.create(
        resource=resource_a, date_created=t[2], obsolete=True, date_obsoleted=t[3]
    )
    assert count_created_entities(now) == {project_locale_a.pk: (locale_a.pk, 3)}


@pytest.mark.django_db
def test_count_projectlocale_stats(locale_a, project_locale_a, resource_a):
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    assert [
        ps
        for ps in count_projectlocale_stats()
        if ps["projectlocale"] == project_locale_a.pk
    ] == [
        {
            "approved": 0,
            "errors": 0,
            "locale": locale_a.pk,
            "pretranslated": 0,
            "projectlocale": project_locale_a.pk,
            "total": 0,
            "unreviewed": 0,
            "warnings": 0,
        }
    ]


@pytest.mark.django_db
def test_projectlocale_insights(locale_a, project_locale_a, resource_a):
    now, t = now_times()
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    activities = {
        project_locale_a.pk: Activity(
            locale=locale_a.pk,
            human_translations={1, 2},
            new_suggestions={1, 2},
            peer_approved={1},
        )
    }
    new_entities = {project_locale_a.pk: (locale_a.pk, 3)}
    pl_stats = [
        {
            "approved": 9,
            "errors": 0,
            "locale": locale_a.pk,
            "pretranslated": 0,
            "projectlocale": project_locale_a.pk,
            "total": 10,
            "unreviewed": 0,
            "warnings": 0,
        }
    ]
    (pli,) = projectlocale_insights(now, activities, new_entities, pl_stats)
    assert pli.created_at == now
    assert pli.total_strings == 10
    assert pli.completion == 90
    assert pli.human_translations == 2
    assert pli.new_source_strings == 3


@pytest.mark.django_db
def test_locale_insights(
    locale_a, project_a, project_b, resource_a, resource_b, entity_a
):
    now, t = now_times()
    pla = ProjectLocaleFactory(project=project_a, locale=locale_a)
    plb = ProjectLocaleFactory(project=project_b, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource_b, locale=locale_a)
    activities = {
        pla.pk: Activity(
            locale=locale_a.pk,
            human_translations={1, 2},
            new_suggestions={1, 2},
            peer_approved={1},
            times_to_review_suggestions=[t[2] - t[1]],
        ),
        plb.pk: Activity(
            locale=locale_a.pk,
            human_translations={3, 4},
            new_suggestions={3, 4},
            peer_approved={3},
            times_to_review_suggestions=[t[3] - t[1]],
        ),
    }
    new_entities = {
        pla.pk: (locale_a.pk, 3),
        plb.pk: (locale_a.pk, 2),
    }
    pl_stats = [
        {
            "approved": 9,
            "errors": 0,
            "locale": locale_a.pk,
            "pretranslated": 0,
            "projectlocale": pla.pk,
            "total": 10,
            "unreviewed": 0,
            "warnings": 0,
        },
        {
            "approved": 3,
            "errors": 0,
            "locale": locale_a.pk,
            "pretranslated": 0,
            "projectlocale": plb.pk,
            "total": 6,
            "unreviewed": 0,
            "warnings": 0,
        },
    ]
    (li,) = locale_insights(now, activities, new_entities, pl_stats)
    assert li.created_at == now
    assert li.total_strings == 16
    assert li.completion == 75
    assert li.human_translations == 4
    assert li.new_source_strings == 5
    assert li.time_to_review_suggestions == (t[2] - t[1] + t[3] - t[1]) / 2
    assert li.unreviewed_suggestions_lifespan == timedelta()

    TranslationFactory.create(entity=entity_a, locale=locale_a, date=t[0])
    (li,) = locale_insights(now, activities, new_entities, pl_stats)
    assert li.unreviewed_suggestions_lifespan >= timedelta(days=1)
    assert li.unreviewed_suggestions_lifespan <= timedelta(days=2)
