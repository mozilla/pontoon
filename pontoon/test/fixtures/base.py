import pytest

from pontoon.test import factories


@pytest.fixture
def user_a():
    return factories.UserFactory(username="user_a")


@pytest.fixture
def user_b():
    return factories.UserFactory(username="user_b")


@pytest.fixture
def user_c():
    return factories.UserFactory(username="user_c")


@pytest.fixture
def member(client, user_a):
    """Provides a `LoggedInMember` with the attributes `user` and `client`
    the `client` is authenticated
    """

    class LoggedInMember(object):
        def __init__(self, user, client):
            client.force_login(user)
            self.client = client
            self.user = user

    return LoggedInMember(user_a, client)


@pytest.fixture
def locale_a():
    return factories.LocaleFactory(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def locale_b():
    return factories.LocaleFactory(
        code="gs",
        name="Geonosian",
    )


@pytest.fixture
def project_a():
    return factories.ProjectFactory(
        slug="project_a", name="Project A", repositories=[],
    )


@pytest.fixture
def project_b():
    return factories.ProjectFactory(
        slug="project_b", name="Project B"
    )


@pytest.fixture
def resource_a(project_a):
    return factories.ResourceFactory(
        project=project_a, path="resource_a.po", format="po"
    )


@pytest.fixture
def resource_b(project_b):
    return factories.ResourceFactory(
        project=project_b, path="resource_b.po", format="po"
    )


@pytest.fixture
def entity_a(resource_a):
    return factories.EntityFactory(
        resource=resource_a, string="entity a"
    )


@pytest.fixture
def entity_b(resource_b):
    return factories.EntityFactory(
        resource=resource_b, string="entity b"
    )


@pytest.fixture
def project_locale_a(project_a, locale_a):
    return factories.ProjectLocaleFactory(
        project=project_a,
        locale=locale_a,
    )


@pytest.fixture
def translation_a(locale_a, project_locale_a, entity_a, user_a):
    '''Return a translation.

    Note that we require the `project_locale_a` fixture because a
    valid ProjectLocale is needed in order to query Translations.

    '''
    return factories.TranslationFactory(
        entity=entity_a,
        locale=locale_a,
        user=user_a,
        string='Translation for entity_a',
    )


@pytest.fixture
def tag_a(resource_a, project_a, locale_a):
    # Tags require a TranslatedResource to work.
    factories.TranslatedResourceFactory.create(
        resource=resource_a, locale=locale_a
    )
    tag = factories.TagFactory.create(slug="tag", name="Tag")
    tag.resources.add(resource_a)
    return tag
