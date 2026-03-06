import json

import pytest

from django.contrib.auth.models import User

from pontoon.base.views import get_users
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_get_users_excludes_system_users(rf, admin):
    request = rf.get("/get-users/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    request.user = admin
    response = get_users(request)
    data = json.loads(response.content)
    usernames = [u["username"] for u in data]

    system_users = User.objects.filter(profile__system_user=True)
    for u in system_users:
        assert u.username not in usernames


@pytest.mark.django_db
def test_get_users_sorted_by_locale_activity(rf, admin):
    locale = LocaleFactory()
    project = ProjectFactory(locales=[locale])
    resource = ResourceFactory(project=project)
    entity = EntityFactory(resource=resource)

    other_locale = LocaleFactory()

    # create a user that is from a different locale, not the current one
    other_locale_user = UserFactory(first_name="Michael", last_name="OtherLocale")
    TranslationFactory(user=other_locale_user, locale=other_locale, entity=entity)

    # create a user active in the current locale
    locale_user = UserFactory(first_name="Alice", last_name="ActiveLocale")
    TranslationFactory(user=locale_user, locale=locale, entity=entity)

    request = rf.get(
        "/get-users/",
        {"locale": locale.code, "project": project.pk},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    request.user = admin
    response = get_users(request)
    data = json.loads(response.content)

    names = [u["name"] for u in data]
    assert names.index(locale_user.name_or_email) < names.index(
        other_locale_user.name_or_email
    )


# project & locale activity should be prioritized over alphabetic order
# for users that are both active in the project or locale


@pytest.mark.django_db
def test_get_users_sorted_by_project_and_locale_activity(rf, admin):
    locale = LocaleFactory()
    project = ProjectFactory(locales=[locale])
    resource = ResourceFactory(project=project)
    entity = EntityFactory(resource=resource)

    # create a user that is active in the current locale and project
    active_user = UserFactory(first_name="Zara", last_name="ActiveUser")
    TranslationFactory(user=active_user, locale=locale, entity=entity)

    # create a user that is active in the current locale but not the project
    other_project_user = UserFactory(first_name="Bob", last_name="OtherProject")
    TranslationFactory(user=other_project_user, locale=locale)

    # create a user that is active in the current project but not the locale
    other_locale_user = UserFactory(first_name="Charlie", last_name="OtherLocale")
    TranslationFactory(user=other_locale_user, entity=entity)

    request = rf.get(
        "/get-users/",
        {"locale": locale.code, "project": project.pk},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    request.user = admin
    response = get_users(request)
    data = json.loads(response.content)

    names = [u["name"] for u in data]
    assert (
        names.index(active_user.name_or_email)
        < names.index(other_project_user.name_or_email)
        < names.index(other_locale_user.name_or_email)
    )
