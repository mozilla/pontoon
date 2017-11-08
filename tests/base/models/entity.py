
import pytest

from pontoon.base.models import Entity


@pytest.mark.django_db
def test_entity_project_locale_filter(entity_test_models, localeX, project1):
    """
    Evaluate entities filtering by locale, project, obsolete.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale0 = tr0.locale
    resource0 = tr0.entity.resource
    project0 = tr0.entity.resource.project
    Entity.objects.create(
        obsolete=True,
        resource=resource0,
        string='Obsolete String')
    assert len(Entity.for_project_locale(project0, localeX)) == 0
    assert len(Entity.for_project_locale(project1, locale0)) == 0
    assert len(Entity.for_project_locale(project0, locale0)) == 2


@pytest.mark.django_db
def test_entity_project_locale_no_paths(entity_test_models, localeX, project1):
    """
    If paths not specified, return all project entities along with their
    translations for locale.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale0 = tr0.locale
    entity0 = tr0.entity
    resource0 = tr0.entity.resource
    project0 = tr0.entity.resource.project
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(project0, locale0))
    assert len(entities) == 2
    assert entities[0]['path'] == resource0.path
    assert entities[0]['original'] == entity0.string
    assert entities[0]['translation'][0]['string'] == tr0.string
    assert entities[1]['path'] == trX.entity.resource.path
    assert entities[1]['original'] == trX.entity.string
    assert entities[1]['translation'][0]['string'] == trX.string

    # Ensure all attributes are assigned correctly
    expected = {
        'comment': '',
        'format': 'po',
        'obsolete': False,
        'marked': unicode(entity0.string),
        'key': '',
        'path': unicode(resource0.path),
        'project': project0.serialize(),
        'translation': [
            {'pk': tr0.pk,
             'fuzzy': False,
             'string': unicode(tr0.string),
             'approved': False,
             'rejected': False},
            {'pk': tr0pl.pk,
             'fuzzy': False,
             'string': unicode(tr0pl.string),
             'approved': False,
             'rejected': False}],
        'order': 0,
        'source': [],
        'original_plural': unicode(entity0.string_plural),
        'marked_plural': unicode(entity0.string_plural),
        'pk': entity0.pk,
        'original': unicode(entity0.string),
        'visible': False}
    assert entities[0] == expected


@pytest.mark.django_db
def test_entity_project_locale_paths(entity_test_models):
    """
    If paths specified, return project entities from these paths only along
    with their translations for locale.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale0 = tr0.locale
    project0 = tr0.entity.resource.project
    paths = ['resourceX.po']
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(
            project0,
            locale0,
            paths))
    assert len(entities) == 1
    assert entities[0]['path'] == trX.entity.resource.path
    assert entities[0]['original'] == trX.entity.string
    assert entities[0]['translation'][0]['string'] == trX.string


@pytest.mark.django_db
def test_entity_project_locale_subpages(entity_test_models):
    """
    If paths specified as subpages, return project entities from paths
    assigned to these subpages only along with their translations for
    locale.
    """
    tr0 = entity_test_models[0]
    subpageX = entity_test_models[3]
    locale0 = tr0.locale
    entity0 = tr0.entity
    resource0 = tr0.entity.resource
    project0 = tr0.entity.resource.project
    subpages = [subpageX.name]
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(
            project0,
            locale0,
            subpages))
    assert len(entities) == 1
    assert entities[0]['path'] == resource0.path
    assert entities[0]['original'] == entity0.string
    assert entities[0]['translation'][0]['string'] == tr0.string


@pytest.mark.django_db
def test_entity_project_locale_plurals(entity_test_models, localeX, project1):
    """
    For pluralized strings, return all available plural forms.
    """
    tr0, tr0pl, trX, subpageX = entity_test_models
    locale0 = tr0.locale
    entity0 = tr0.entity
    project0 = tr0.entity.resource.project
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(
            project0,
            locale0))
    assert entities[0]['original'] == entity0.string
    assert entities[0]['original_plural'] == entity0.string_plural
    assert entities[0]['translation'][0]['string'] == tr0.string
    assert entities[0]['translation'][1]['string'] == tr0pl.string


@pytest.mark.django_db
def test_entity_project_locale_order(entity_test_models):
    """
    Return entities in correct order.
    """
    resource0 = entity_test_models[0].entity.resource
    locale0 = entity_test_models[0].locale
    project0 = resource0.project
    Entity.objects.create(
        order=1,
        resource=resource0,
        string='Second String')
    Entity.objects.create(
        order=0,
        resource=resource0,
        string='First String')
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(
            project0,
            locale0))
    assert entities[1]['original'] == 'First String'
    assert entities[2]['original'] == 'Second String'


@pytest.mark.django_db
def test_entity_project_locale_cleaned_key(entity_test_models):
    """
    If key contanis source string and Translate Toolkit separator,
    remove them.
    """
    resource0 = entity_test_models[0].entity.resource
    locale0 = entity_test_models[0].locale
    project0 = resource0.project
    entities = Entity.map_entities(
        locale0,
        Entity.for_project_locale(
            project0,
            locale0))
    assert entities[0]['key'] == ''
    assert entities[1]['key'] == 'Key'
