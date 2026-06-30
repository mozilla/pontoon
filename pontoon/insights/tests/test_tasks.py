from datetime import timedelta
from unittest.mock import patch

import pytest

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Locale
from pontoon.insights.chs import (
    KEY_PROJECT_SLUGS,
    build_chs_snapshots,
    compute_chs,
    get_completion_by_locale,
    get_contributor_metrics_by_locale,
    get_key_projects_enabled_by_locale,
)
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
    GroupFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    UserFactory,
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


@pytest.mark.django_db
def test_projectlocale_insights_no_pretranslations_chrf_score_is_none(
    locale_a, project_locale_a, resource_a
):
    """When there are no pretranslation reviews, chrF++ score should be None,
    not 0."""
    now, t = now_times()
    TranslatedResourceFactory.create(resource=resource_a, locale=locale_a)
    activities = {
        project_locale_a.pk: Activity(
            locale=locale_a.pk,
            human_translations={1},
            new_suggestions={1},
            peer_approved={1},
        )
    }
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
    (pli,) = projectlocale_insights(now, activities, {}, pl_stats)
    assert pli.pretranslations_chrf_score is None


@pytest.mark.django_db
def test_count_activities_chrf_score_zero_included(
    user_a, gt_user, locale_a, project_locale_a, resource_a
):
    """A rejected pretranslation with a chrF++ score of 0.0 should be
    included."""
    now, t = now_times()
    tr = TranslationFactory.create(
        entity__resource=resource_a,
        locale=locale_a,
        user=gt_user,
        date=t[1],
        active=False,
        approved=False,
        rejected=True,
        rejected_user=user_a,
        rejected_date=t[2],
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        created_at=t[1],
        performed_by=gt_user,
        translation=tr,
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
        created_at=t[2],
        performed_by=user_a,
        translation=tr,
    )
    with patch("pontoon.insights.tasks.calculate_chrf_score", return_value=0.0):
        result = count_activities(now)
    activity = result[project_locale_a.pk]
    assert 0.0 in activity.pretranslations_chrf_scores


def test_compute_chs():
    # full metric chs activity
    assert compute_chs(
        {
            "active_managers": 1,
            "active_translators": 2,
            "active_contributors": 2,
            "all_contributors": 2,
            "new_signups": 2,
            "key_projects_enabled": len(KEY_PROJECT_SLUGS),
            "completion": 100.0,
        }
    ) == {
        "active_managers_score": 20.0,
        "active_translators_score": 15.0,
        "active_contributors_score": 6.0,
        "all_contributors_score": 4.0,
        "new_signups_score": 5.0,
        "key_projects_enabled_score": 4.0,
        "completion_score": 46.0,
        "chs": 100.0,
    }

    # half chs metric activity
    assert compute_chs(
        {
            "active_managers": 1,
            "active_translators": 1,
            "active_contributors": 1,
            "all_contributors": 1,
            "new_signups": 1,
            "key_projects_enabled": len(KEY_PROJECT_SLUGS),
            "completion": 50.0,
        }
    ) == {
        "active_managers_score": 20.0,
        "active_translators_score": 7.5,
        "active_contributors_score": 3.0,
        "all_contributors_score": 2.0,
        "new_signups_score": 2.5,
        "key_projects_enabled_score": 4,
        "completion_score": 23.0,
        "chs": 62,
    }

    # no chs metric activity
    assert compute_chs(
        {
            "active_managers": 0,
            "active_translators": 0,
            "active_contributors": 0,
            "all_contributors": 0,
            "new_signups": 0,
            "key_projects_enabled": 0,
            "completion": 0.0,
        }
    ) == {
        "active_managers_score": 0,
        "active_translators_score": 0,
        "active_contributors_score": 0,
        "all_contributors_score": 0,
        "new_signups_score": 0,
        "key_projects_enabled_score": 0.0,
        "completion_score": 0.0,
        "chs": 0.0,
    }


@pytest.mark.django_db
def test_get_completion_by_locale(locale_a, locale_b):
    key_project = ProjectFactory.create(slug="firefox", name="Firefox", repositories=[])
    key_resource_a = ResourceFactory.create(project=key_project, path="key_a.po")
    key_resource_b = ResourceFactory.create(project=key_project, path="key_b.po")
    key_resource_c = ResourceFactory.create(project=key_project, path="key_c.po")
    # A non-key project must not contribute to the completion score.
    other_resource = ResourceFactory.create(path="other.po")

    TranslatedResourceFactory.create(
        resource=key_resource_a,
        locale=locale_a,
        total_strings=6,
        approved_strings=5,
        strings_with_warnings=0,
    )
    TranslatedResourceFactory.create(
        resource=key_resource_b,
        locale=locale_a,
        total_strings=4,
        approved_strings=2,
        strings_with_warnings=1,
    )
    TranslatedResourceFactory.create(
        resource=key_resource_c,
        locale=locale_b,
        total_strings=0,
    )
    TranslatedResourceFactory.create(
        resource=other_resource,
        locale=locale_a,
        total_strings=100,
        approved_strings=100,
        strings_with_warnings=0,
    )

    locales = Locale.objects.filter(pk__in=[locale_a.pk, locale_b.pk])
    assert get_completion_by_locale(locales) == {
        locale_a.pk: 80.0,
        locale_b.pk: 0.0,
    }


@pytest.mark.django_db
def test_get_key_projects_enabled_by_locale(locale_a, locale_b):
    enabled_a = ProjectFactory.create(slug="firefox", name="Firefox", repositories=[])
    enabled_b = ProjectFactory.create(
        slug="firefox-for-ios", name="Firefox for iOS", repositories=[]
    )
    disabled = ProjectFactory.create(
        slug="firefox-for-android",
        name="Firefox for Android",
        repositories=[],
        disabled=True,
    )
    non_key = ProjectFactory.create(
        slug="not-a-key-project", name="Other", repositories=[]
    )

    ProjectLocaleFactory.create(project=enabled_a, locale=locale_a)
    ProjectLocaleFactory.create(project=enabled_b, locale=locale_a)

    ProjectLocaleFactory.create(project=disabled, locale=locale_a)
    ProjectLocaleFactory.create(project=non_key, locale=locale_a)

    ProjectLocaleFactory.create(project=non_key, locale=locale_b)

    locales = Locale.objects.filter(pk__in=[locale_a.pk, locale_b.pk])
    assert get_key_projects_enabled_by_locale(locales, KEY_PROJECT_SLUGS) == {
        locale_a.pk: 2,
    }


@pytest.mark.django_db
def test_get_contributor_metrics_by_locale(locale_a, locale_b, resource_a):
    now = timezone.now()
    in_12_month_window = now - relativedelta(days=1)
    out_12_month_window = now - relativedelta(months=13, days=1)

    managers_group = GroupFactory.create(name="managers")
    translators_group = GroupFactory.create(name="translators")
    locale_a.managers_group = managers_group
    locale_a.translators_group = translators_group
    locale_a.save()

    manager = UserFactory.create(username="manager")
    translator = UserFactory.create(username="translator")
    contributor_a = UserFactory.create(username="contributor_a")
    contributor_b = UserFactory.create(username="contributor_b")
    managers_group.user_set.add(manager)
    translators_group.user_set.add(translator)

    # Managers and translators need one authored translation to appear in the
    # results, and cross their thresholds through review actions
    manager_translation = TranslationFactory.create(
        entity__resource=resource_a,
        locale=locale_a,
        user=manager,
        date=in_12_month_window,
    )
    translator_translation = TranslationFactory.create(
        entity__resource=resource_a,
        locale=locale_a,
        user=translator,
        date=in_12_month_window,
    )
    ActionLog.objects.bulk_create(
        [
            ActionLog(
                action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
                created_at=in_12_month_window,
                performed_by=manager,
                translation=manager_translation,
            )
            for _ in range(501)
        ]
        + [
            ActionLog(
                action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
                created_at=in_12_month_window,
                performed_by=translator,
                translation=translator_translation,
            )
            for _ in range(401)
        ]
    )

    # An active contributor crosses the active, all-contributor, and new-signup
    # thresholds at once
    for entity in EntityFactory.create_batch(size=201, resource=resource_a):
        TranslationFactory.create(
            entity=entity,
            locale=locale_a,
            user=contributor_a,
            date=in_12_month_window,
            approved=True,
        )

    # A contributor below every threshold is counted nowhere
    TranslationFactory.create(
        entity__resource=resource_a,
        locale=locale_a,
        user=contributor_b,
        date=in_12_month_window,
        approved=True,
    )

    # contributions made outside 12 month window - current month
    # are not counted
    for entity in EntityFactory.create_batch(size=201, resource=resource_a):
        TranslationFactory.create(
            entity=entity,
            locale=locale_b,
            user=contributor_b,
            date=out_12_month_window,
            approved=True,
        )

    locales = Locale.objects.filter(pk__in=[locale_a.pk, locale_b.pk])
    assert get_contributor_metrics_by_locale(locales, now) == {
        locale_a.pk: {
            "active_managers": 1,
            "active_translators": 1,
            "active_contributors": 1,
            "all_contributors": 1,
            "new_signups": 1,
        },
        locale_b.pk: {
            "active_managers": 0,
            "active_translators": 0,
            "active_contributors": 0,
            "all_contributors": 0,
            "new_signups": 0,
        },
    }


@pytest.mark.django_db
def test_build_chs_snapshots(locale_a):
    key_project = ProjectFactory.create(slug="firefox", name="Firefox", repositories=[])
    resource = ResourceFactory.create(project=key_project, path="firefox.po")
    ProjectLocaleFactory.create(project=key_project, locale=locale_a)
    TranslatedResourceFactory.create(
        resource=resource,
        locale=locale_a,
        total_strings=10,
        approved_strings=8,
        strings_with_warnings=0,
    )

    locales = Locale.objects.filter(pk__in=[locale_a.pk])
    snapshots = build_chs_snapshots(locales)

    # Only visible locales get snapshots
    assert {snapshot.locale_id for snapshot in snapshots} == {locale_a.pk}
    assert len(snapshots) == 1

    snapshot = snapshots[0]
    assert snapshot.completion == 80.0
    assert snapshot.key_projects_enabled == 1
    assert snapshot.active_managers == 0
    assert snapshot.active_contributors == 0
    assert snapshot.completion_score == 36.8
    assert snapshot.key_projects_enabled_score == 0.57
    assert snapshot.chs == 37.37
