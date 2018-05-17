import pytest

from pontoon.base.models import Translation
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    UserFactory,
)
from pontoon.checks.models import Warning


@pytest.fixture
def user_a():
    return UserFactory(
        username="user_a",
        email="user_a@example.org"
    )


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
    return LocaleFactory(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project_a():
    return ProjectFactory(
        slug="project_a", name="Project A", repositories=[],
    )


@pytest.fixture
def project_locale_a(project_a, locale_a):
    return ProjectLocaleFactory(
        project=project_a,
        locale=locale_a,
    )


@pytest.fixture
def resource_a(locale_a, project_a):
    return ResourceFactory(
        project=project_a, path="resource_a.po", format="po"
    )


@pytest.fixture
def entity_a(resource_a, project_locale_a):
    return EntityFactory(
        resource=resource_a, string="entity"
    )


@pytest.yield_fixture
def properties_resource(resource_a):
    """
    A resource to trigger Translate Toolkit and compare-locales checks at once.
    """
    resource_a.format = 'properties'
    resource_a.path = 'test1.properties'
    resource_a.save()

    yield resource_a


@pytest.yield_fixture
def request_update_translation():
    """
    Call /update/ view to push a translation/suggestion etc.
    """
    def func(client, **args):
        update_params = {
            'translation': 'approved translation',
            'plural_form': '-1',
            'ignore_check': 'true',
        }
        update_params.update(args)

        return client.post(
            '/update/',
            update_params,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
    return func


@pytest.yield_fixture
def properties_entity(entity_a, properties_resource):
    """
    An entity from properties_resource.
    """
    entity_a.translation_set.all().delete()
    entity_a.string = 'something %s'
    entity_a.save()

    yield entity_a


@pytest.mark.django_db
def test_run_checks_during_translation_update(
    properties_entity,
    member,
    locale_a,
    request_update_translation,
):
    """
    The backend shouldn't allow to post translations with critical errors.
    """
    response = request_update_translation(
        member.client,
        locale=locale_a.code,
        entity=properties_entity.pk,
        translation='bad  suggestion',
        original=properties_entity.string,
        ignore_warnings='false',
    )

    assert response.status_code == 200
    assert response.json() == {
        u'failedChecks': {
            u'clWarnings': [u'trailing argument 1 `s` missing'],
            u'ttWarnings': [u'Double spaces'],
        },
    }

    # User decides to ignore checks (but there are errors)
    response = request_update_translation(
        member.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale_a.code,
        translation='bad suggestion \q %q',
        ignore_warnings='true',
    )

    assert response.status_code == 200
    assert response.json() == {
        u'failedChecks': {
            u'clErrors': [u'Found single %'],
            u'clWarnings': [u'unknown escape sequence, \q'],
        },
    }

    # User decides to ignore checks (there are only warnings)
    response = request_update_translation(
        member.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale_a.code,
        translation='bad suggestion',
        ignore_warnings='true',
    )

    assert response.status_code == 200
    assert response.json()['type'] == 'saved'

    translation_pk = response.json()['translation']['pk']
    assert Translation.objects.get(pk=translation_pk).approved is False

    warning, = Warning.objects.all()

    assert warning.translation_id == translation_pk
    assert warning.library == 'cl'
    assert warning.message == 'trailing argument 1 `s` missing'

    # Update shouldn't duplicate warnings
    Translation.objects.filter(pk=translation_pk).update(approved=False, fuzzy=True)

    response = request_update_translation(
        member.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale_a.code,
        translation='bad suggestion',
        ignore_warnings='true'
    )

    assert response.status_code == 200
    assert response.json()['type'] == 'updated'

    warning, = Warning.objects.all()

    assert warning.translation_id == translation_pk
    assert warning.library == 'cl'
    assert warning.message == 'trailing argument 1 `s` missing'
