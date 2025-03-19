from unittest.mock import patch

import pytest

from dateutil.relativedelta import relativedelta

from django.test.client import RequestFactory
from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import Group, Locale, User
from pontoon.messaging.emails import (
    _get_monthly_locale_contributors,
    send_verification_email,
)


@pytest.mark.django_db
def test_send_verification_email(member):
    with patch("pontoon.messaging.emails.EmailMultiAlternatives") as mock_email_message:
        rf = RequestFactory()
        request = rf.get("/settings/")
        request.user = member.user

        link = "EMAIL-VERIFICATION-LINK"
        send_verification_email(request.user, link)
        assert mock_email_message.called

        kwargs = mock_email_message.call_args.kwargs
        assert link in kwargs["body"]
        assert kwargs["to"] == [request.user.email]

@pytest.mark.django_db
def test_get_monthly_locale_contributors():
    locale = Locale.objects.create(code="test-locale")
    managers_group = Group.objects.create(name="managers")
    translators_group = Group.objects.create(name="translators")

    locale.managers_group = managers_group
    locale.translators_group = translators_group
    locale.save()

    manager_user = User.objects.create(username="manager", email="manager@example.com")
    translator_user = User.objects.create(username="translator", email="translator@example.com")
    regular_user = User.objects.create(username="regular", email="regular@example.com")

    managers_group.user_set.add(manager_user)
    translators_group.user_set.add(translator_user)

    # Set action date to previous month for monthly reporting
    current_date = timezone.now()
    action_date = current_date - relativedelta(months=1)

    ActionLog.objects.create(
        performed_by=manager_user,
        created_at=action_date,
        action_type="translation:created",
        translation__locale=locale
    )
    ActionLog.objects.create(
        performed_by=translator_user,
        created_at=action_date,
        action_type="translation:created",
        translation__locale=locale
    )
    ActionLog.objects.create(
        performed_by=regular_user,
        created_at=action_date,
        action_type="translation:created",
        translation__locale=locale
    )

    results = _get_monthly_locale_contributors([locale], months_ago=1)
    locale_result = results[locale.pk]

    assert manager_user in locale_result["active_managers"]
    assert translator_user not in locale_result["active_managers"]
    assert regular_user not in locale_result["active_managers"]

    assert translator_user in locale_result["active_translators"]
    assert manager_user not in locale_result["active_translators"]
    assert regular_user not in locale_result["active_translators"]

    assert regular_user in locale_result["active_contributors"]
    assert manager_user not in locale_result["active_contributors"]
    assert translator_user not in locale_result["active_contributors"]
