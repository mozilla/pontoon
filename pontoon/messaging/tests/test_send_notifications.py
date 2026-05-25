from datetime import timedelta
from unittest.mock import patch

import pytest

from django.utils import timezone

from pontoon.messaging.management.commands.send_deadline_notifications import (
    Command as DeadlineCommand,
)
from pontoon.messaging.management.commands.send_review_notifications import (
    Command as ReviewCommand,
)
from pontoon.messaging.management.commands.send_suggestion_notifications import (
    Command as SuggestionCommand,
)
from pontoon.messaging.notifications import send_badge_notification
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslationFactory,
)


@pytest.mark.django_db
def test_get_suggestions_excludes_system_projects(
    locale_a, project_a, system_project_a
):
    # regular project with suggestions included
    resource_regular = ResourceFactory.create(project=project_a)
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)
    entity_regular = EntityFactory.create(resource=resource_regular)
    regular_translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_regular,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
    )

    # system suggestions excluded
    resource_system = ResourceFactory.create(project=system_project_a)
    ProjectLocaleFactory.create(project=system_project_a, locale=locale_a)
    entity_system = EntityFactory.create(resource=resource_system)
    system_translation = TranslationFactory.create(
        locale=locale_a,
        entity=entity_system,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
    )

    suggestions = SuggestionCommand().get_suggestions()
    assert regular_translation in suggestions
    assert system_translation not in suggestions


@patch(
    "pontoon.messaging.management.commands.send_suggestion_notifications.notify.send"
)
@pytest.mark.django_db
def test_send_suggestion_notifications_excludes_system_users(
    mock_notify,
    locale_a,
    project_a,
    project_locale_a,
    user_a,
    tm_user,
):
    """System users with matching translations must not receive
    unreviewed-suggestion notifications."""
    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource)

    TranslationFactory.create(
        locale=locale_a,
        entity=entity,
        user=user_a,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
    )

    TranslationFactory.create(
        locale=locale_a,
        entity=entity,
        user=tm_user,
        approved=False,
        pretranslated=False,
        rejected=False,
        fuzzy=False,
        date=timezone.now() - timedelta(days=30),
    )

    SuggestionCommand().handle(force=True)

    recipients = {call.kwargs["recipient"] for call in mock_notify.call_args_list}
    assert tm_user not in recipients


@patch("pontoon.messaging.management.commands.send_review_notifications.notify.send")
@pytest.mark.django_db
def test_send_review_notifications_excludes_system_users(
    mock_notify,
    locale_a,
    project_a,
    project_locale_a,
    user_a,
    tm_user,
):
    """When a system user's suggestion is reviewed, no review recap should be
    sent to the system user."""
    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource)

    now = timezone.now()
    TranslationFactory.create(
        locale=locale_a,
        entity=entity,
        user=tm_user,
        approved=True,
        approved_user=user_a,
        approved_date=now,
    )

    TranslationFactory.create(
        locale=locale_a,
        entity=entity,
        user=user_a,
        approved=True,
        approved_user=user_a,
        approved_date=now,
    )

    ReviewCommand().handle()

    recipients = {call.kwargs["recipient"] for call in mock_notify.call_args_list}
    assert tm_user not in recipients


@patch("pontoon.messaging.management.commands.send_deadline_notifications.notify.send")
@pytest.mark.django_db
def test_send_deadline_notifications_excludes_system_users(
    mock_notify,
    locale_a,
    project_a,
    project_locale_a,
    user_a,
    tm_user,
):
    """System users that have contributed to a project must not receive
    target-date notifications."""
    project_a.deadline = (timezone.now() + timedelta(days=7)).date()
    project_a.save()

    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource)

    TranslationFactory.create(locale=locale_a, entity=entity, user=user_a)
    TranslationFactory.create(locale=locale_a, entity=entity, user=tm_user)

    DeadlineCommand().handle()

    recipients = {call.kwargs["recipient"] for call in mock_notify.call_args_list}
    assert tm_user not in recipients


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_send_badge_notification_skips_system_users(mock_notify, tm_user, user_a):
    send_badge_notification(tm_user, "Translation Champion", 1)
    assert mock_notify.call_count == 0

    send_badge_notification(user_a, "Translation Champion", 1)
    assert mock_notify.call_count == 1
