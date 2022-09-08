from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode

import pytest
from dateutil.relativedelta import relativedelta
from django.test.client import RequestFactory
from django.utils import timezone
from pontoon.actionlog.models import ActionLog
from pontoon.base.models import User
from pontoon.base.utils import convert_to_unix_time
from pontoon.contributors import utils


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
    action.created_at = datetime(2020, 1, 1)
    action.save()
    return action


@pytest.fixture
def action_b(translation_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action.created_at = datetime(2020, 1, 1)
    action.save()
    return action


@pytest.fixture
def action_c(translation_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action.created_at = datetime(2020, 2, 1)
    action.save()
    return action


@pytest.fixture
def action_user_a(translation_a, user_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action.created_at = datetime.now() - relativedelta(months=1)
    action.save()
    return action


@pytest.fixture
def action_user_b(translation_a, user_b):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_b,
        translation=translation_a,
    )
    action.created_at = datetime.now()
    action.save()
    return action


@pytest.fixture
def yesterdays_action_user_a(translation_a, user_a):
    action = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action.created_at = datetime.now() - relativedelta(days=1)
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
def test_send_verification_email(member):
    with patch("pontoon.contributors.utils.EmailMessage") as mock_email_message:
        rf = RequestFactory()
        request = rf.get("/settings/")
        request.user = member.user

        token = "EMAIL-VERIFICATION-TOKEN"
        utils.send_verification_email(request, token)
        assert mock_email_message.called

        kwargs = mock_email_message.call_args.kwargs
        assert token in kwargs["body"]
        assert kwargs["to"] == [None]


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


def test_get_sublist_averages():
    assert utils.get_sublist_averages([1, 2, 3, 4, 5], 3) == [2, 3, 4]


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
    assert data["approval_rates_12_month_avg"] == [0] * 11 + [8.333333333333334]
    assert data["self_approval_rates"] == [0] * 10 + [100, 0]
    assert (
        data["self_approval_rates_12_month_avg"] == [0] * 10 + [8.333333333333334] * 2
    )


@pytest.mark.django_db
def test_get_contributions_map_keys(user_a):
    map = utils.get_contributions_map(user_a)

    assert list(map.keys()) == [
        "user_translations",
        "user_reviews",
        "peer_reviews",
        "all_user_contributions",
        "all_contributions",
    ]


@pytest.mark.django_db
def test_get_contributions_map_without_actions(user_a):
    map = utils.get_contributions_map(user_a)

    for key, value in map.items():
        assert not value.exists()


@pytest.mark.django_db
def test_get_contributions_map_with_actions(user_a, action_user_a):
    map = utils.get_contributions_map(user_a)

    for key, value in map.items():
        if key == "user_translations":
            assert not value.exists()
        else:
            assert value.exists()


@pytest.mark.django_db
def test_get_contribution_graph_data_without_actions(user_a):
    assert utils.get_contribution_graph_data(user_a) == (
        {},
        "0 contributions in the last year",
    )


@pytest.mark.django_db
def test_get_contribution_graph_data_with_actions(user_a, action_user_a, action_user_b):
    # Truncate time
    date = action_user_a.created_at.replace(hour=0, minute=0, second=0, microsecond=0)

    assert utils.get_contribution_graph_data(user_a) == (
        {
            convert_to_unix_time(date): 1,
        },
        "1 contribution in the last year",
    )


@pytest.mark.django_db
def test_get_contribution_timeline_data_without_actions(user_a):
    assert utils.get_contribution_timeline_data(user_a) == (
        {},
        "Contribution activity in the last month",
    )


@pytest.mark.django_db
def test_get_contribution_timeline_data_with_actions(
    user_a, yesterdays_action_user_a, action_user_b
):
    end = timezone.now()
    start = end - relativedelta(months=1)

    params = {
        "reviewer": user_a.email,
        "review_time": f"{start.strftime('%Y%m%d%H%M')}-{end.strftime('%Y%m%d%H%M')}",
    }

    assert utils.get_contribution_timeline_data(user_a) == (
        {
            "Reviewed 1 suggestion in 1 project": {
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
                "type": "user-reviews",
            }
        },
        "Contribution activity in the last month",
    )
