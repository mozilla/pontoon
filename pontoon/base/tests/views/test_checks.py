import pytest

from pontoon.base.models import Translation
from pontoon.checks.models import Warning


@pytest.yield_fixture
def properties_resource(resource0):
    """
    A resource to trigger Translate Toolkit and compare-locales checks at once.
    """
    resource0.format = 'properties'
    resource0.path = 'test1.properties'
    resource0.save()

    yield resource0


@pytest.yield_fixture
def properties_entity(entity0, properties_resource):
    """
    An entity from properties_resource.
    """
    entity0.translation_set.all().delete()
    entity0.string = 'something %s'
    entity0.save()

    yield entity0


@pytest.mark.django_db
def test_run_checks_during_translation_update(
    properties_entity,
    member0,
    locale0,
    request_update_translation,
):
    """
    The backend shouldn't allow to post translations with critical errors.
    """
    response = request_update_translation(
        member0.client,
        locale=locale0.code,
        entity=properties_entity.pk,
        translation='bad  suggestion',
        original=properties_entity.string,
        ignore_warnings='false'
    )

    assert response.status_code == 200
    assert response.json() == {
        u'failedChecks': {
            u'clWarnings': [u'trailing argument 1 `s` missing'],
            u'ttWarnings': [u'Double spaces']
        },
    }

    # User decides to ignore checks (but there are errors)
    response = request_update_translation(
        member0.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale0.code,
        translation='bad suggestion \q %q',
        ignore_warnings='true'
    )

    assert response.status_code == 200
    assert response.json() == {
        u'failedChecks': {
            u'clErrors': [u'Found single %'],
            u'clWarnings': [u'unknown escape sequence, \q']
        },
    }

    # User decides to ignore checks (there are only warnings)
    response = request_update_translation(
        member0.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale0.code,
        translation='bad suggestion',
        ignore_warnings='true'
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
        member0.client,
        entity=properties_entity.pk,
        original=properties_entity.string,
        locale=locale0.code,
        translation='bad suggestion',
        ignore_warnings='true'
    )

    assert response.status_code == 200
    assert response.json()['type'] == 'updated'

    warning, = Warning.objects.all()

    assert warning.translation_id == translation_pk
    assert warning.library == 'cl'
    assert warning.message == 'trailing argument 1 `s` missing'
