from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode

import pytest

from dateutil.relativedelta import relativedelta

from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import User
from pontoon.base.models.project import Project
from pontoon.base.tests import EntityFactory
from pontoon.base.utils import convert_to_unix_time
from pontoon.contributors import utils
from pontoon.test.factories import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
)


@pytest.fixture
def months_a():
    return [
        convert_to_unix_time(datetime(2020, 1, 1)),
        convert_to_unix_time(datetime(2020, 2, 1)),
        convert_to_unix_time(datetime(2020, 3, 1)),
    ]


@pytest.fixture
def action_a(translation_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action.created_at = timezone.make_aware(datetime(2020, 1, 1))
    action.save()
    return action


@pytest.fixture
def action_b(translation_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action.created_at = timezone.make_aware(datetime(2020, 1, 1))
    action.save()
    return action


@pytest.fixture
def action_c(translation_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action.created_at = timezone.make_aware(datetime(2020, 2, 1))
    action.save()
    return action


@pytest.fixture
def action_user_a(translation_a, user_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action.created_at = timezone.now() - relativedelta(months=1)
    action.save()
    return action


@pytest.fixture
def action_user_b(translation_a, user_b):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_b,
        translation=translation_a,
    )
    action.created_at = timezone.now()
    action.save()
    return action


@pytest.fixture
def yesterdays_action_user_a(translation_a, user_a):
    current_date = timezone.now()
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    if current_date.day == 1:
        # First day of the month, so we instead set created_at to be earlier today
        action.created_at = timezone.now() - relativedelta(minutes=1)
    else:
        action.created_at = timezone.now() - relativedelta(days=1)

    action.save()
    return action


@pytest.mark.django_db
def test_generate_verification_token(member):
    with patch("jwt.encode") as mock_encode:
        utils.generate_verification_token(member.user)
        assert mock_encode.called

        args = mock_encode.call_args.args
        assert list(args[0].values())[0] == member.user.pk
        assert list(args[0].values())[1] == member.user.profile.contact_email


@pytest.mark.django_db
def test_check_verification_token(member, user_b):
    # Invalid token
    token = "INVALID-VERIFICATION-TOKEN"
    title, message = utils.check_verification_token(member.user, token)
    assert title == "Oops!"
    assert message == "Invalid verification token"
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is False

    # Valid token
    token = utils.generate_verification_token(member.user)
    title, message = utils.check_verification_token(member.user, token)
    assert title == "Success!"
    assert message == "Your email address has been verified"
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is True

    # Invalid user
    token = utils.generate_verification_token(user_b)
    title, message = utils.check_verification_token(member.user, token)
    assert title == "Oops!"
    assert message == "Invalid verification token"


def test_get_n_months_before():
    assert utils.get_n_months_before(datetime(2020, 5, 1), 5) == [
        convert_to_unix_time(datetime(2020, 1, 1)),
        convert_to_unix_time(datetime(2020, 2, 1)),
        convert_to_unix_time(datetime(2020, 3, 1)),
        convert_to_unix_time(datetime(2020, 4, 1)),
        convert_to_unix_time(datetime(2020, 5, 1)),
    ]


@pytest.mark.django_db
def test_get_monthly_action_counts_without_actions(months_a):
    actions_qs = ActionLog.objects.filter()
    assert utils.get_monthly_action_counts(months_a, actions_qs) == [0, 0, 0]


@pytest.mark.django_db
def test_get_monthly_action_counts_with_actions(months_a, action_a, action_b, action_c):
    actions_qs = ActionLog.objects.filter(
        pk__in=[action_a.pk, action_b.pk, action_c.pk]
    )
    assert utils.get_monthly_action_counts(months_a, actions_qs) == [2, 1, 0]


def test_get_shares_of_totals():
    list1 = [1, 0, 0, 2, 6]
    list2 = [1, 2, 0, 0, 2]
    assert utils.get_shares_of_totals(list1, list2) == [50, 0, 0, 100, 75]


def test_get_12_month_averages():
    assert utils.get_12_month_averages([1, 2, 3], [1, 2, 3]) == [
        50,
        50,
        50,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
    ]


@pytest.mark.django_db
def test_get_approvals_charts_data_without_actions(user_a):
    data = utils.get_approvals_charts_data(user_a)

    assert data["approval_rates"] == [0] * 12
    assert data["approval_rates_12_month_avg"] == [0] * 12
    assert data["self_approval_rates"] == [0] * 12
    assert data["self_approval_rates_12_month_avg"] == [0] * 12


@pytest.mark.django_db
def test_get_approvals_charts_data_with_actions(user_a, action_user_a, action_user_b):
    data = utils.get_approvals_charts_data(user_a)

    assert data["approval_rates"] == [0] * 11 + [100]
    assert data["approval_rates_12_month_avg"] == [0] * 11 + [100]
    assert data["self_approval_rates"] == [0] * 10 + [100, 0]
    assert data["self_approval_rates_12_month_avg"] == [0] * 10 + [100, 50]


@pytest.mark.django_db
def test_get_approvals_charts_data_self_approval_not_double_counted(
    user_a, user_b, translation_a
):
    """
    A translation submitted directly as approved logs both a
    `translation:created` (with date == approved_date) and an implicit
    `translation:approved` action. It must be counted as a single
    self-approval, not two.
    """
    now = timezone.now()
    translation_a.date = now
    translation_a.approved_date = now
    translation_a.save()

    # Self-approval on submission: created + implicit approved, both by user_a.
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        performed_by=user_a,
        translation=translation_a,
    )
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
        is_implicit_action=True,
    )
    # Peer approval of user_a's translation by user_b.
    ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_b,
        translation=translation_a,
    )

    data = utils.get_approvals_charts_data(user_a)

    # 1 self-approval vs 1 peer approval this month => 50%.
    # If the implicit approval were double-counted, this would be ~66.7%.
    assert data["self_approval_rates"][-1] == 50


@pytest.mark.django_db
def test_get_contributions_map_keys(user_a, user_b):
    map = utils.get_contributions_map(user_a, user_b)

    assert list(map.keys()) == [
        "user_translations",
        "user_reviews",
        "peer_reviews",
        "all_user_contributions",
        "all_contributions",
    ]


@pytest.mark.django_db
def test_get_contributions_map_without_actions(user_a, user_b):
    map = utils.get_contributions_map(user_a, user_b)

    for key, value in map.items():
        assert not value.exists()


@pytest.mark.django_db
def test_get_contributions_map_with_actions(user_a, action_user_a, user_b):
    map = utils.get_contributions_map(user_a, user_b)

    for key, value in map.items():
        if key == "user_translations":
            assert not value.exists()
        else:
            assert value.exists()


@pytest.mark.django_db
def test_get_contribution_graph_data_without_actions(user_a, user_b):
    assert utils.get_contribution_graph_data(user_a, user_b) == (
        {},
        "0 contributions in the last year",
    )


@pytest.mark.django_db
def test_get_contribution_graph_data_with_actions(user_a, action_user_a, user_b):
    # Truncate time
    date = action_user_a.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
    assert utils.get_contribution_graph_data(user_a, user_b) == (
        {
            convert_to_unix_time(date): 1,
        },
        "1 contribution in the last year",
    )


@pytest.mark.django_db
def test_get_contribution_graph_data_for_year(user_a, user_b, translation_a):
    # Action in 2025
    action_2025 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action_2025.created_at = timezone.make_aware(datetime(2025, 6, 15))
    action_2025.save()

    # Action in 2026, which must be excluded when filtering by 2025
    action_2026 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action_2026.created_at = timezone.make_aware(datetime(2026, 1, 1))
    action_2026.save()

    date = action_2025.created_at.replace(hour=0, minute=0, second=0, microsecond=0)
    assert utils.get_contribution_graph_data(user_a, user_b, year=2025) == (
        {
            convert_to_unix_time(date): 1,
        },
        "1 contribution in 2025",
    )


@pytest.mark.django_db
def test_get_contribution_years(user_a):
    user_a.date_joined = timezone.make_aware(datetime(2021, 3, 1))
    user_a.save()
    current_year = timezone.now().year
    assert utils.get_contribution_years(user_a) == list(range(current_year, 2020, -1))


@pytest.mark.django_db
def test_get_contribution_timeline_data_without_actions(user_a, user_b):
    assert utils.get_contribution_timeline_data(user_a, user_b) == ({})


@pytest.mark.django_db
def test_get_contribution_timeline_data_with_actions(
    user_a, user_b, yesterdays_action_user_a, action_user_b
):
    end = timezone.now()
    start = end - relativedelta(day=1)
    start = start.replace(hour=0, minute=0, second=0, microsecond=0)

    date = end.strftime("%B %Y")

    params = {
        "reviewer": user_a.email,
        "review_time": f"{start.strftime('%Y%m%d%H%M')}-{end.strftime('%Y%m%d%H%M')}",
    }

    assert utils.get_contribution_timeline_data(user_a, user_b) == (
        {
            date: {
                "user_reviews": {
                    "data": {
                        ("project_a", "kg"): {
                            "project": {
                                "name": "Project A",
                                "slug": "project_a",
                            },
                            "locale": {
                                "name": "Klingon",
                                "code": "kg",
                            },
                            "actions": ["1 approved"],
                            "count": 1,
                            "url": f"/kg/project_a/all-resources/?{urlencode(params)}",
                        },
                    },
                    "title": "Reviewed 1 suggestion in 1 project",
                    "type": "user-reviews",
                }
            }
        }
    )


@pytest.mark.django_db
def test_get_contribution_timeline_data_for_year(user_a, user_b, translation_a):
    # Reviews in two different months of 2025
    for review_date in [datetime(2025, 6, 15), datetime(2025, 12, 10)]:
        action = ActionLog.objects.create(
            action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
            performed_by=user_a,
            translation=translation_a,
        )
        action.created_at = timezone.make_aware(review_date)
        action.save()

    # Review in 2026, which must be excluded when filtering by 2025
    action_2026 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action_2026.created_at = timezone.make_aware(datetime(2026, 6, 15))
    action_2026.save()

    # The full year shows all months of the selected year, most recent first
    full_year = utils.get_contribution_timeline_data(
        user_a, user_b, full_year=True, contribution_type="user_reviews", year=2025
    )
    assert list(full_year.keys()) == ["December 2025", "June 2025"]

    # Collapsed view shows only the most recent month within the year
    collapsed = utils.get_contribution_timeline_data(
        user_a, user_b, contribution_type="user_reviews", year=2025
    )
    assert list(collapsed.keys()) == ["December 2025"]
    assert (
        collapsed["December 2025"]["user_reviews"]["title"]
        == "Reviewed 1 suggestion in 1 project"
    )


@pytest.mark.django_db
def test_get_contributions_map_hides_private_project_actions(user_a, user_b, admin):
    """Regular user cannot see actions on private projects."""
    locale_a = LocaleFactory(
        code="thl",
        name="Klingon",
    )
    project_a = ProjectFactory(
        slug="project_a", name="Project A", visibility=Project.Visibility.PRIVATE
    )

    resource_a = ResourceFactory.create(
        project=project_a, path=f"resource_{project_a.slug}.po", format="gettext"
    )

    entity_a = EntityFactory.create(string="Test String", resource=resource_a)

    translation_a = TranslationFactory(
        entity=entity_a,
        locale=locale_a,
        user=user_a,
        string="Translation for entity_a",
    )

    action_a = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        performed_by=user_a,
        translation=translation_a,
    )
    action_a.created_at = timezone.make_aware(datetime(2020, 1, 1))
    action_a.save()

    map = utils.get_contributions_map(user_a, user_b)
    assert not map["user_translations"].exists()

    map = utils.get_contributions_map(user_a, admin)
    assert map["user_translations"].exists()
