from datetime import date
from unittest.mock import patch

import pytest

from django.test.client import RequestFactory
from django.utils import timezone

from pontoon.insights.models import LocaleInsightsSnapshot
from pontoon.messaging.emails import (
    _get_monthly_locale_stats,
    send_verification_email,
)
from pontoon.test.factories import LocaleFactory


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
def test_get_monthly_locale_stats_uses_end_of_month_snapshot():
    locale = LocaleFactory(code="x-test", name="Test Language")

    # Simulate 6 strings added on October 30.
    LocaleInsightsSnapshot.objects.create(
        locale=locale,
        created_at=date(2025, 10, 31),
        total_strings=100,
        approved_strings=94,
        completion=94.0,
    )

    # Nov 1 snapshot is taken at midnight, capturing end of Oct 31.
    # The 6 strings were translated.
    snapshot_nov_1 = LocaleInsightsSnapshot.objects.create(
        locale=locale,
        created_at=date(2025, 11, 1),
        total_strings=100,
        approved_strings=100,
        completion=100.0,
    )

    with patch("pontoon.messaging.emails.timezone") as mock_tz:
        mock_tz.now.return_value = timezone.datetime(
            2025, 11, 1, 6, 30, 0, tzinfo=timezone.utc
        )
        result = _get_monthly_locale_stats(months_ago=1)

    assert locale.pk in result
    assert result[locale.pk].pk == snapshot_nov_1.pk
    assert result[locale.pk].approved_strings == 100
    assert result[locale.pk].completion == 100.0
