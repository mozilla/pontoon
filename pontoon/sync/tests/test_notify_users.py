from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from notifications.models import Notification

from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)
from pontoon.sync.core import notify_users


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_excludes_system_users(
    mock_notify, locale_a, project_a, project_locale_a, user_a, tm_user
):
    """System users that authored translations in a project must not be
    notified about new strings landing in that project."""
    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource)

    TranslationFactory.create(locale=locale_a, entity=entity, user=user_a)
    TranslationFactory.create(locale=locale_a, entity=entity, user=tm_user)

    notify_users(
        project_a, count=1, now=datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    )

    recipients = {call.kwargs["recipient"] for call in mock_notify.call_args_list}
    assert user_a in recipients
    assert tm_user not in recipients


@pytest.mark.django_db
def test_notify_users_stores_created_time():
    """
    notify_users() records the sync timestamp on notification.data as
    created_time (YYYYMMDDHHmm), so the bell menu and digest template can
    link to the precise batch of entities created in that sync.
    """
    locale = LocaleFactory.create()
    project = ProjectFactory.create(locales=[locale])
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=user)

    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    notify_users(project, count=3, now=now)

    notifications = list(Notification.objects.filter(recipient=user))
    assert len(notifications) == 1
    n = notifications[0]
    assert n.verb == "updated with 3 new strings"
    assert n.data == {
        "category": "new_string",
        "created_time": "202605240444",
    }


@pytest.mark.django_db
def test_notify_users_singular_verb():
    """One added string uses the singular form in the verb."""
    locale = LocaleFactory.create()
    project = ProjectFactory.create(locales=[locale])
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=user)

    notify_users(project, count=1, now=datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc))

    n = Notification.objects.get(recipient=user)
    assert n.verb == "updated with 1 new string"
    assert n.data["created_time"] == "202601020304"


@pytest.mark.django_db
def test_notify_users_skips_unsubscribed():
    """Users without new_string_notifications enabled are not notified."""
    locale = LocaleFactory.create()
    project = ProjectFactory.create(locales=[locale])
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource)

    user = UserFactory.create()
    user.profile.new_string_notifications = False
    user.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=user)

    notify_users(
        project, count=2, now=datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    )

    assert Notification.objects.filter(recipient=user).count() == 0
