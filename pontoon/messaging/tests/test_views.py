import pytest

from pontoon.base.models import User
from pontoon.messaging.forms import MessageForm
from pontoon.messaging.views import get_recipients
from pontoon.test.factories import TranslationFactory


@pytest.mark.django_db
def test_dismiss_email_consent(member):
    """Test if dismiss_email_consent view works and fails as expected."""
    params = {}
    response = member.client.post("/dismiss-email-consent/", params)
    assert response.status_code == 400
    assert response.json()["message"] == "Bad Request: Value not set"

    params = {
        "value": "false",
    }
    response = member.client.post("/dismiss-email-consent/", params)
    profile = User.objects.get(pk=member.user.pk).profile
    assert profile.email_communications_enabled is False
    assert profile.email_consent_dismissed_at is not None
    assert response.status_code == 200

    params = {
        "value": "true",
    }
    response = member.client.post("/dismiss-email-consent/", params)
    profile = User.objects.get(pk=member.user.pk).profile
    assert profile.email_communications_enabled is True
    assert profile.email_consent_dismissed_at is not None
    assert response.status_code == 200


@pytest.mark.django_db
def test_get_recipients_excludes_system_users(locale_a, entity_a, user_a, tm_user):
    """System users must not show up among the contributors of a message."""
    for user in (user_a, tm_user):
        TranslationFactory.create(locale=locale_a, entity=entity_a, user=user)

    form = MessageForm(
        {
            "subject": "Subject",
            "body": "Body",
            "notification": True,
            "contributors": True,
            "locale_toggle": True,
            "locales": str(locale_a.pk),
        }
    )
    assert form.is_valid()

    recipients = get_recipients(form)
    assert user_a in recipients
    assert tm_user not in recipients


@pytest.mark.django_db
def test_get_recipients_excludes_system_users_with_permissions(
    locale_a, entity_a, user_a, tm_user
):
    """System users must be left out of the manager and translator groups too.

    Those groups are combined with the contributors using `|`, which ORs the
    conditions of both querysets, so each one has to exclude system users.
    """
    for user in (user_a, tm_user):
        TranslationFactory.create(locale=locale_a, entity=entity_a, user=user)

    locale_a.managers_group.user_set.add(user_a)
    locale_a.translators_group.user_set.add(tm_user)

    form = MessageForm(
        {
            "subject": "Subject",
            "body": "Body",
            "notification": True,
            "managers": True,
            "translators": True,
            "locale_toggle": True,
            "locales": str(locale_a.pk),
        }
    )
    assert form.is_valid()

    recipients = get_recipients(form)
    assert user_a in recipients
    assert tm_user not in recipients
