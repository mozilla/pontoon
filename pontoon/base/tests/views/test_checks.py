import pytest

from mock import patch

from pontoon.base.models import Translation
from pontoon.checks.models import Warning


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
def properties_entity(entity_a, properties_resource):
    """
    An entity from properties_resource.
    """
    entity_a.translation_set.all().delete()
    entity_a.string = 'something %s'
    entity_a.save()

    yield entity_a


@patch('pontoon.base.views.utils.is_same')
@pytest.mark.django_db
def test_run_checks_during_translation_update(
    is_same_mock,
    properties_entity,
    member,
    locale_a,
    project_locale_a,
    request_update_translation,
):
    # Mock return value for is_same
    is_same_mock.return_value = False

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
    (
        Translation.objects
        .filter(pk=translation_pk)
        .update(approved=False, fuzzy=True)
    )

    # Make sure user can_translate
    (
        Translation.objects
        .get(pk=translation_pk)
        .locale.translators_group.user_set.add(member.user)
    )

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
