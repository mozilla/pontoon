import pytest

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from pontoon.insights.utils import get_monthly_health_report
from pontoon.settings.base import MONTHLY_HEALTH_REPORT_CHS_THRESHOLD
from pontoon.test.factories import (
    LocaleFactory,
    LocaleHealthSnapshotFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
)


def anchors():
    current = timezone.now().date()
    previous = current.replace(day=1) - relativedelta(days=1)
    return current, previous


@pytest.mark.django_db
def test_get_monthly_health_report_reports_locales_above_threshold():
    current_anchor, previous_anchor = anchors()

    locale_a = LocaleFactory.create(code="kg", name="Klingon")
    locale_b = LocaleFactory.create(code="gs", name="Geonosian")
    locale_c = LocaleFactory.create(code="vu", name="Vulcan")

    project = ProjectFactory.create(slug="project", name="Project", repositories=[])
    resource = ResourceFactory.create(project=project, path="resource.po")
    for locale in (locale_a, locale_b, locale_c):
        ProjectLocaleFactory.create(project=project, locale=locale)
        TranslatedResourceFactory.create(resource=resource, locale=locale)

    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=previous_anchor, chs=50
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=current_anchor, chs=50.5
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_b, created_at=previous_anchor, chs=50
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_b, created_at=current_anchor, chs=60
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_c, created_at=previous_anchor, chs=40
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_c, created_at=current_anchor, chs=35
    )

    report = get_monthly_health_report()

    assert report["locale_rows"] == [
        {
            "locale": locale_b,
            "previous_chs": 50,
            "current_chs": 60,
            "delta": 10,
            "percentage": 20,
        },
        {
            "locale": locale_c,
            "previous_chs": 40,
            "current_chs": 35,
            "delta": -5,
            "percentage": -12.5,
        },
    ]


@pytest.mark.django_db
def test_get_monthly_health_report_excludes_locales_without_key_projects_and_hidden_projects():
    current_anchor, previous_anchor = anchors()

    locale_a = LocaleFactory.create(code="kg", name="Klingon")
    project = ProjectFactory.create(slug="project", name="Project", repositories=[])
    resource = ResourceFactory.create(project=project, path="resource.po")
    ProjectLocaleFactory.create(project=project, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=previous_anchor, chs=50, key_projects_enabled=0
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=current_anchor, chs=60, key_projects_enabled=0
    )

    assert get_monthly_health_report()["locale_rows"] == []


@pytest.mark.django_db
def test_get_monthly_health_report_excludes_locales_without_previous_snapshot():
    current_anchor, _ = anchors()

    locale_a = LocaleFactory.create(code="kg", name="Klingon")
    project = ProjectFactory.create(slug="project", name="Project", repositories=[])
    resource = ResourceFactory.create(project=project, path="resource.po")
    ProjectLocaleFactory.create(project=project, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=current_anchor, chs=60
    )

    assert get_monthly_health_report()["locale_rows"] == []


@pytest.mark.django_db
def test_get_monthly_health_report_reports_locales_without_previous_chs_as_full_gain():
    current_anchor, previous_anchor = anchors()

    locale_a = LocaleFactory.create(code="kg", name="Klingon")
    project = ProjectFactory.create(slug="project", name="Project", repositories=[])
    resource = ResourceFactory.create(project=project, path="resource.po")
    ProjectLocaleFactory.create(project=project, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=previous_anchor, chs=0
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=current_anchor, chs=60
    )

    (locale_row,) = get_monthly_health_report()["locale_rows"]
    assert locale_row["delta"] == 60
    assert locale_row["percentage"] == 100


@pytest.mark.django_db
def test_get_monthly_health_report_uses_latest_snapshot_of_the_month():
    current_anchor, previous_anchor = anchors()

    locale_a = LocaleFactory.create(code="kg", name="Klingon")
    project = ProjectFactory.create(slug="project", name="Project", repositories=[])
    resource = ResourceFactory.create(project=project, path="resource.po")
    ProjectLocaleFactory.create(project=project, locale=locale_a)
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=previous_anchor.replace(day=1), chs=10
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=previous_anchor, chs=50
    )
    LocaleHealthSnapshotFactory.create(
        locale=locale_a, created_at=current_anchor, chs=60
    )

    (locale_row,) = get_monthly_health_report()["locale_rows"]
    assert locale_row["previous_chs"] == 50
    assert locale_row["delta"] == 10


@pytest.mark.django_db
def test_get_monthly_health_report_reports_the_previous_month():
    reported_month = timezone.now().date().replace(day=1) - relativedelta(months=1)
    report = get_monthly_health_report()

    assert report["month"] == reported_month.strftime("%B")
    assert report["year"] == reported_month.year
    assert report["threshold"] == MONTHLY_HEALTH_REPORT_CHS_THRESHOLD
