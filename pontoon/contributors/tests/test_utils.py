import pytest

from dateutil.relativedelta import relativedelta
from datetime import datetime
from django.test.client import RequestFactory
from unittest.mock import patch

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import User
from pontoon.base.utils import convert_to_unix_time
from pontoon.contributors import utils


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
def test_get_monthly_action_counts(translation_a):
    months = [
        convert_to_unix_time(datetime(2020, 1, 1)),
        convert_to_unix_time(datetime(2020, 2, 1)),
        convert_to_unix_time(datetime(2020, 3, 1)),
    ]

    # No actions
    actions_qs = ActionLog.objects.filter()
    assert utils.get_monthly_action_counts(months, actions_qs) == [0, 0, 0]

    # Some actions
    action1 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action1.created_at = datetime(2020, 1, 1)
    action1.save()

    action2 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action2.created_at = datetime(2020, 1, 1)
    action2.save()

    action3 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation_a,
    )
    action3.created_at = datetime(2020, 2, 1)
    action3.save()

    actions_qs = ActionLog.objects.filter(pk__in=[action1.pk, action2.pk, action3.pk])
    assert utils.get_monthly_action_counts(months, actions_qs) == [2, 1, 0]


def test_get_shares_of_totals():
    list1 = [1, 0, 0, 2, 6]
    list2 = [1, 2, 0, 0, 2]
    assert utils.get_shares_of_totals(list1, list2) == [50, 0, 0, 100, 75]


def test_get_sublist_averages():
    assert utils.get_sublist_averages([1, 2, 3, 4, 5], 3) == [2, 3, 4]


@pytest.mark.django_db
def test_get_approval_rates(user_a, user_b, translation_a):
    # User without any contributions
    data = utils.get_approval_rates(user_a)

    assert data["approval_rates"] == [0] * 12
    assert data["approval_rates_12_month_avg"] == [0] * 12
    assert data["self_approval_rates"] == [0] * 12
    assert data["self_approval_rates_12_month_avg"] == [0] * 12

    # User with some contributions
    action1 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_b,
        translation=translation_a,
    )
    action1.created_at = datetime.now()
    action1.save()

    action2 = ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=user_a,
        translation=translation_a,
    )
    action2.created_at = datetime.now() - relativedelta(months=1)
    action2.save()

    data = utils.get_approval_rates(user_a)

    assert data["approval_rates"] == [0] * 11 + [100]
    assert data["approval_rates_12_month_avg"] == [0] * 11 + [8.333333333333334]
    assert data["self_approval_rates"] == [0] * 10 + [100, 0]
    assert (
        data["self_approval_rates_12_month_avg"] == [0] * 10 + [8.333333333333334] * 2
    )
