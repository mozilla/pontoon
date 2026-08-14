from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from notifications.models import Notification

from pontoon.base.models import Project
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslatedResourceFactory,
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
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource, date_created=now)

    TranslationFactory.create(locale=locale_a, entity=entity, user=user_a)
    TranslationFactory.create(locale=locale_a, entity=entity, user=tm_user)

    notify_users(project_a, now)

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
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale], visibility=Project.Visibility.PUBLIC
    )
    resource = ResourceFactory.create(project=project)
    entities = EntityFactory.create_batch(3, resource=resource, date_created=now)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.save()
    TranslationFactory.create(entity=entities[0], locale=locale, user=user)

    notify_users(project, now)

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
    now = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale], visibility=Project.Visibility.PUBLIC
    )
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource, date_created=now)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=user)

    notify_users(project, now)

    n = Notification.objects.get(recipient=user)
    assert n.verb == "updated with 1 new string"
    assert n.data["created_time"] == "202601020304"


@pytest.mark.django_db
def test_notify_users_skips_unsubscribed():
    """Users without new_string_notifications enabled are not notified."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale], visibility=Project.Visibility.PUBLIC
    )
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource, date_created=now)

    user = UserFactory.create()
    user.profile.new_string_notifications = False
    user.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=user)

    notify_users(project, now)

    assert Notification.objects.filter(recipient=user).count() == 0


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_skips_locales_without_new_strings(mock_notify):
    """If the locale doesn't have any new strings, translator is not notified."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale_1 = LocaleFactory.create()
    locale_2 = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale_1, locale_2], visibility=Project.Visibility.PUBLIC
    )

    # New resource added this sync, but available only for locale_1.
    new_resource = ResourceFactory.create(project=project)
    new_entity = EntityFactory.create(resource=new_resource, date_created=now)
    user_1 = UserFactory.create()
    user_1.profile.new_string_notifications = True
    user_1.profile.save()
    TranslationFactory.create(entity=new_entity, locale=locale_1, user=user_1)

    # Old resource available to locale_2 (no new strings this sync).
    old_resource = ResourceFactory.create(project=project)
    old_entity = EntityFactory.create(
        resource=old_resource,
        date_created=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    user_2 = UserFactory.create()
    user_2.profile.new_string_notifications = True
    user_2.profile.save()
    TranslationFactory.create(entity=old_entity, locale=locale_2, user=user_2)

    notify_users(project, now)

    recipients = {c.kwargs["recipient"] for c in mock_notify.call_args_list}
    assert user_1 in recipients
    assert user_2 not in recipients


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_per_locale_counts(mock_notify):
    """Each translator's notification reports the count for their own locale,
    not the project-wide total (accurate under syncs involving project
    configuration and files exposed to a subset of locales)."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale_1 = LocaleFactory.create()
    locale_2 = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale_1, locale_2], visibility=Project.Visibility.PUBLIC
    )

    # Shared resource (5 new strings), available to both locales.
    shared = ResourceFactory.create(project=project)
    shared_entities = EntityFactory.create_batch(5, resource=shared, date_created=now)
    TranslatedResourceFactory.create(resource=shared, locale=locale_1)
    TranslatedResourceFactory.create(resource=shared, locale=locale_2)

    # Resource with 3 more new strings, available to locale_1 only.
    only_1 = ResourceFactory.create(project=project)
    EntityFactory.create_batch(3, resource=only_1, date_created=now)
    TranslatedResourceFactory.create(resource=only_1, locale=locale_1)

    user_1 = UserFactory.create()
    user_1.profile.new_string_notifications = True
    user_1.profile.save()
    TranslationFactory.create(entity=shared_entities[0], locale=locale_1, user=user_1)

    user_2 = UserFactory.create()
    user_2.profile.new_string_notifications = True
    user_2.profile.save()
    TranslationFactory.create(entity=shared_entities[0], locale=locale_2, user=user_2)

    notify_users(project, now)

    verbs = {
        call.kwargs["recipient"]: call.kwargs["verb"]
        for call in mock_notify.call_args_list
    }
    # locale_1 sees both resources (5 + 3), locale_2 only the shared one (5).
    assert verbs[user_1] == "updated with 8 new strings"
    assert verbs[user_2] == "updated with 5 new strings"


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_uses_homepage_count(mock_notify):
    """A multi-locale translator gets a single notification, reporting the
    count for the locale they selected as homepage."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale_1 = LocaleFactory.create()
    locale_2 = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale_1, locale_2], visibility=Project.Visibility.PUBLIC
    )

    # 8 new strings for locale_1, 5 for locale_2.
    resource_1 = ResourceFactory.create(project=project)
    entities_1 = EntityFactory.create_batch(8, resource=resource_1, date_created=now)
    resource_2 = ResourceFactory.create(project=project)
    entities_2 = EntityFactory.create_batch(5, resource=resource_2, date_created=now)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.custom_homepage = locale_2.code
    user.profile.save()
    TranslationFactory.create(entity=entities_1[0], locale=locale_1, user=user)
    TranslationFactory.create(entity=entities_2[0], locale=locale_2, user=user)

    notify_users(project, now)

    assert mock_notify.call_count == 1
    # Homepage is locale_2, so report its count (5) rather than the max (8).
    assert mock_notify.call_args.kwargs["verb"] == "updated with 5 new strings"


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_falls_back_to_max_without_homepage(mock_notify):
    """Without a defined homepage, a multi-locale translator will receive a
    notification with the largest count among their locales."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale_1 = LocaleFactory.create()
    locale_2 = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale_1, locale_2], visibility=Project.Visibility.PUBLIC
    )

    resource_1 = ResourceFactory.create(project=project)
    entities_1 = EntityFactory.create_batch(8, resource=resource_1, date_created=now)
    resource_2 = ResourceFactory.create(project=project)
    entities_2 = EntityFactory.create_batch(5, resource=resource_2, date_created=now)

    user = UserFactory.create()
    user.profile.new_string_notifications = True
    user.profile.save()  # no custom_homepage
    TranslationFactory.create(entity=entities_1[0], locale=locale_1, user=user)
    TranslationFactory.create(entity=entities_2[0], locale=locale_2, user=user)

    notify_users(project, now)

    assert mock_notify.call_count == 1
    assert mock_notify.call_args.kwargs["verb"] == "updated with 8 new strings"


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_private_project_only_superusers(mock_notify):
    """A private project is only visible to superusers, so other past
    contributors are not notified about new strings."""
    now = datetime(2026, 5, 24, 4, 44, tzinfo=timezone.utc)
    locale = LocaleFactory.create()
    project = ProjectFactory.create(
        locales=[locale], visibility=Project.Visibility.PRIVATE
    )
    resource = ResourceFactory.create(project=project)
    entity = EntityFactory.create(resource=resource, date_created=now)

    regular = UserFactory.create()
    regular.profile.new_string_notifications = True
    regular.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=regular)

    admin = UserFactory.create(is_superuser=True)
    admin.profile.new_string_notifications = True
    admin.profile.save()
    TranslationFactory.create(entity=entity, locale=locale, user=admin)

    notify_users(project, now)

    recipients = {c.kwargs["recipient"] for c in mock_notify.call_args_list}
    assert admin in recipients
    assert regular not in recipients
