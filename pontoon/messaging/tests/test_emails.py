from collections import defaultdict
from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest

from django.core import mail
from django.template import TemplateSyntaxError
from django.test.client import RequestFactory
from django.urls import NoReverseMatch

from pontoon.base.models import User
from pontoon.insights.models import LocaleInsightsSnapshot
from pontoon.messaging.emails import (
    _get_monthly_locale_stats,
    send_inactive_contributor_emails,
    send_inactive_manager_emails,
    send_inactive_translator_emails,
    send_onboarding_email_1,
    send_onboarding_emails_2,
    send_onboarding_emails_3,
    send_verification_email,
)
from pontoon.messaging.models import EmailContent
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
        mock_tz.now.return_value = datetime(2025, 11, 1, 6, 30, 0, tzinfo=timezone.utc)
        result = _get_monthly_locale_stats(months_ago=1)

    assert locale.pk in result
    assert result[locale.pk].pk == snapshot_nov_1.pk
    assert result[locale.pk].approved_strings == 100
    assert result[locale.pk].completion == 100.0


@pytest.mark.django_db
def test_send_onboarding_email_1(user_a):
    try:
        send_onboarding_email_1(user_a)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'onboarding_1' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]


@pytest.mark.django_db
def test_send_onboarding_emails_2(user_a):

    users = User.objects.filter(pk=user_a.pk)

    try:
        send_onboarding_emails_2(users)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'onboarding_2' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]


@pytest.mark.django_db
def test_send_onboarding_emails_3(user_a):

    users = User.objects.filter(pk=user_a.pk)

    try:
        send_onboarding_emails_3(users)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'onboarding_3' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]


@pytest.mark.django_db
def test_send_inactive_contributor_emails(user_a):

    users = User.objects.filter(pk=user_a.pk)

    try:
        send_inactive_contributor_emails(users)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'inactive_contributor' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]


@pytest.mark.django_db
def test_send_inactive_translator_emails(user_a, locale_a):
    translators = defaultdict(set)

    users = User.objects.filter(pk=user_a.pk)
    translators[user_a.pk].add(locale_a)
    try:
        send_inactive_translator_emails(users, translators)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'inactive_translator' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]


@pytest.mark.django_db
def test_send_inactive_manager_emails(user_a, locale_a):
    managers = defaultdict(set)

    users = User.objects.filter(pk=user_a.pk)
    managers[user_a.pk].add(locale_a)

    try:
        send_inactive_manager_emails(users, managers)
    except EmailContent.DoesNotExist:
        pytest.fail("EmailContent for 'inactive_manager' is missing from the DB.")
    except NoReverseMatch as e:
        pytest.fail(f"URL resolution failed: check URL config: {e}")
    except TemplateSyntaxError as e:
        pytest.fail(f"Template is broken: {e}")
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    assert len(mail.outbox) == 2
    assert mail.outbox[0].to == [user_a.contact_email]
