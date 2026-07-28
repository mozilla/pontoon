from collections import defaultdict
from datetime import date, datetime, timezone
from unittest.mock import patch

import pytest

from notifications.signals import notify

from django.core import mail
from django.template import TemplateSyntaxError
from django.test.client import RequestFactory
from django.urls import NoReverseMatch

from pontoon.base.models import User
from pontoon.base.templatetags.helpers import full_url
from pontoon.insights.models import LocaleInsightsSnapshot
from pontoon.messaging.emails import (
    _get_monthly_locale_stats,
    send_inactive_contributor_emails,
    send_inactive_manager_emails,
    send_inactive_translator_emails,
    send_monthly_activity_summary,
    send_notification_digest,
    send_onboarding_email_1,
    send_onboarding_emails_2,
    send_onboarding_emails_3,
    send_verification_email,
)
from pontoon.messaging.models import EmailContent
from pontoon.test.factories import LocaleFactory, UserFactory


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
def test_send_monthly_activity_summary_excludes_system_users(member, sync_user):
    """System users must not receive Monthly activity summary emails."""
    for user in (member.user, sync_user):
        user.profile.monthly_activity_summary = True
        user.profile.save()

    # Discard the onboarding email sent when the member fixture is created
    mail.outbox.clear()
    send_monthly_activity_summary()

    recipients = [address for message in mail.outbox for address in message.to]
    assert recipients == [member.user.contact_email]


@pytest.mark.django_db
def test_send_notification_digest_excludes_system_users(member, sync_user):
    """System users must not receive notification email digests."""
    for user in (member.user, sync_user):
        user.profile.notification_email_frequency = "Daily"
        user.profile.comment_notifications_email = True
        user.profile.save()
        # Bypasses messaging.notifications.send_notification, which already
        # skips system users.
        notify.send(
            user,
            recipient=user,
            verb="has pinned a comment",
            category="comment",
        )

    # Discard the onboarding email sent when the member fixture is created
    mail.outbox.clear()
    send_notification_digest(frequency="Daily")

    recipients = [address for message in mail.outbox for address in message.to]
    assert recipients == [member.user.contact_email]


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
def test_send_monthly_health_report_emails(locale_a):
    subscribed_admin = UserFactory.create(
        username="admin_subscribed", is_superuser=True
    )
    subscribed_admin.profile.monthly_health_report = True
    subscribed_admin.profile.save()

    UserFactory.create(username="admin_unsubscribed", is_superuser=True)

    subscribed_contributor = UserFactory.create(username="contributor")
    subscribed_contributor.profile.monthly_health_report = True
    subscribed_contributor.profile.save()

    report = {
        "locale_rows": [
            {
                "locale": locale_a,
                "previous_chs": 50,
                "current_chs": 60,
                "delta": 10,
                "percentage": 20,
            }
        ],
        "month": "June",
        "year": 2025,
        "threshold": 2,
    }

    sent_before = len(mail.outbox)
    send_monthly_health_report_emails(report)
    sent = mail.outbox[sent_before:]

    assert [message.to for message in sent] == [[subscribed_admin.contact_email]]
    assert sent[0].subject == "Monthly locale health report for June 2025"
    assert f"{locale_a.name} ({locale_a.code})" in sent[0].body
    assert full_url("pontoon.teams.team", locale_a.code) in sent[0].body
    assert "20%" in sent[0].alternatives[0][0]


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
