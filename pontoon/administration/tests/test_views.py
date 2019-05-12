# -*- coding: utf-8 -*-

import pytest

from django.core.urlresolvers import reverse

from pontoon.administration.forms import (
    ProjectForm,
)
from pontoon.administration.views import _create_or_update_translated_resources
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
)
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_manage_project_strings(client):
    project = ProjectFactory.create(data_source='database', repositories=[])
    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    # Test with anonymous user.
    response = client.get(url)
    assert response.status_code == 403

    # Test with a user that is not a superuser.
    user = UserFactory.create()
    client.force_login(user)

    response = client.get(url)
    assert response.status_code == 403

    # Test with a superuser.
    user.is_superuser = True
    user.save()

    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_manage_project(client_superuser):
    url = reverse('pontoon.admin.project.new')
    response = client_superuser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_manage_project_strings_bad_request(client_superuser):
    # Tets an unknown project returns a 404 error.
    url = reverse('pontoon.admin.project.strings', args=('unknown',))
    response = client_superuser.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_manage_project_strings_new(client_superuser, locale_a):
    project = ProjectFactory.create(
        data_source='database',
        repositories=[],
        locales=[locale_a],
    )
    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    # Test sending a well-formatted batch of strings.
    new_strings = """Hey, I just met you
        And this is crazy
        But here's my number
        So call me maybe?
    """
    response = client_superuser.post(url, {'new_strings': new_strings})
    assert response.status_code == 200

    # Verify a resource has been created.
    resources = list(Resource.objects.filter(project=project))
    assert len(resources) == 1

    assert resources[0].path == 'database'

    # Verify all strings have been created as entities.
    entities = Entity.for_project_locale(project, locale_a)
    assert len(entities) == 4

    expected_strings = [
        'Hey, I just met you',
        'And this is crazy',
        'But here\'s my number',
        'So call me maybe?',
    ]

    assert expected_strings == [x.string for x in entities]

    # Verify strings have the correct order.
    for index, entity in enumerate(entities):
        assert entity.order == index

    # Verify new strings appear on the page.
    assert 'Hey, I just met you' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_manage_project_strings_existing_resource(client_superuser, locale_a):
    project = ProjectFactory.create(
        data_source='database',
        repositories=[],
        locales=[locale_a],
    )
    ResourceFactory.create(
        path='not_database',
        project=project,
    )
    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    # Test sending a well-formatted batch of strings.
    new_strings = """Hey, I just met you
        And this is crazy
        But here's my number
        So call me maybe?
    """
    response = client_superuser.post(url, {'new_strings': new_strings})
    assert response.status_code == 200

    # Verify no new resources have been created.
    resources = list(Resource.objects.filter(project=project))
    assert len(resources) == 1

    # The preexisting resource has been sucessfully used.
    assert resources[0].path == 'not_database'
    assert resources[0].total_strings == 4


@pytest.mark.django_db
def test_manage_project_strings_translated_resource(client_superuser):
    """Test that adding new strings to a project enables translation of that
    project on all enabled locales.
    """
    locales = [
        LocaleFactory.create(code='kl', name='Klingon'),
        LocaleFactory.create(code='gs', name='Geonosian'),
    ]
    project = ProjectFactory.create(
        data_source='database',
        locales=locales,
        repositories=[]
    )
    locales_count = len(locales)
    _create_or_update_translated_resources(project, locales)

    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    new_strings = """
        Morty, do you know what "Wubba lubba dub dub" means?
        Oh that's just Rick's stupid non-sense catch phrase.
        It's not.
        In my people's tongue, it means "I am in great pain, please help me".
    """
    strings_count = 4
    response = client_superuser.post(url, {'new_strings': new_strings})
    assert response.status_code == 200

    # Verify no strings have been created as entities.
    entities = list(Entity.objects.filter(resource__project=project))
    assert len(entities) == strings_count

    # Verify the resource has the right stats.
    resources = Resource.objects.filter(project=project)
    assert len(resources) == 1
    resource = resources[0]
    assert resource.total_strings == strings_count

    # Verify the correct TranslatedResource objects have been created.
    translated_resources = TranslatedResource.objects.filter(resource__project=project)
    assert len(translated_resources) == locales_count

    # Verify stats have been correctly updated on locale, project and resource.
    for tr in translated_resources:
        assert tr.total_strings == strings_count

    project = Project.objects.get(id=project.id)
    assert project.total_strings == strings_count * locales_count

    for l in locales:
        locale = Locale.objects.get(id=l.id)
        assert locale.total_strings == strings_count


@pytest.mark.django_db
def test_manage_project_strings_new_all_empty(client_superuser):
    """Test that sending empty data doesn't create empty strings in the database.
    """
    project = ProjectFactory.create(data_source='database', repositories=[])
    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    # Test sending an empty batch of strings.
    new_strings = "  \n   \n\n"
    response = client_superuser.post(url, {'new_strings': new_strings})
    assert response.status_code == 200

    # Verify no strings have been created as entities.
    entities = list(Entity.objects.filter(resource__project=project))
    assert len(entities) == 0


@pytest.mark.django_db
def test_manage_project_strings_list(client_superuser):
    project = ProjectFactory.create(data_source='database', repositories=[])
    resource = ResourceFactory.create(project=project)
    nb_entities = 2
    entities = EntityFactory.create_batch(nb_entities, resource=resource)

    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    response = client_superuser.get(url)
    assert response.status_code == 200
    for i in range(nb_entities):
        assert 'string %s' % i in response.content.decode('utf-8')

    # Test editing strings and comments.
    form_data = {
        'form-TOTAL_FORMS': nb_entities,
        'form-INITIAL_FORMS': nb_entities,
        'form-MIN_NUM_FORMS': 0,
        'form-MAX_NUM_FORMS': 1000,
        'form-0-id': entities[0].id,
        'form-0-string': 'changed 0',
        'form-0-comment': 'Wubba lubba dub dub',
        'form-1-id': entities[1].id,
        'form-1-string': 'string 1',
        'form-1-obsolete': 'on',  # Remove this one.
    }

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert 'changed 0' in response.content.decode('utf-8')
    assert 'Wubba lubba dub dub' in response.content.decode('utf-8')
    assert 'string 0' not in response.content.decode('utf-8')
    assert 'string 1' not in response.content.decode('utf-8')  # It's been removed.

    total = Entity.objects.filter(
        resource=resource, obsolete=False,
    ).count()
    assert total == nb_entities - 1

    # Test adding a new string.
    form_data = {
        'form-TOTAL_FORMS': nb_entities,
        'form-INITIAL_FORMS': nb_entities - 1,
        'form-MIN_NUM_FORMS': 0,
        'form-MAX_NUM_FORMS': 1000,
        'form-0-id': entities[0].id,
        'form-0-string': 'changed 0',
        'form-0-comment': 'Wubba lubba dub dub',
        'form-1-id': '',
        'form-1-string': 'new string',
        'form-1-comment': 'adding this entity now',
    }

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert 'changed 0' in response.content.decode('utf-8')
    assert 'new string' in response.content.decode('utf-8')
    assert 'adding this entity now' in response.content.decode('utf-8')

    total = Entity.objects.filter(
        resource=resource, obsolete=False,
    ).count()
    assert total == nb_entities

    # Verify the new string has the correct order.
    new_string = Entity.objects.filter(
        resource=resource, obsolete=False, string='new string',
    ).first()
    # The highest order before adding new string was 0,
    # so the order of that new one should be 1.
    assert new_string.order == 1


@pytest.mark.django_db
def test_manage_project_strings_download_csv(client_superuser):
    locale_kl = LocaleFactory.create(code='kl', name='Klingon')
    locale_gs = LocaleFactory.create(code='gs', name='Geonosian')
    project = ProjectFactory.create(
        data_source='database',
        locales=[locale_kl, locale_gs],
        repositories=[]
    )

    url = reverse('pontoon.admin.project.strings', args=(project.slug,))

    new_strings = """
        And on the pedestal these words appear:
        'My name is Ozymandias, king of kings:
        Look on my works, ye Mighty, and despair!'
    """
    response = client_superuser.post(url, {'new_strings': new_strings})
    assert response.status_code == 200

    # Test downloading the data.
    response = client_superuser.get(url, {'format': 'csv'})
    assert response.status_code == 200
    assert response._headers['content-type'] == ('Content-Type', 'text/csv')

    # Verify the original content is here.
    assert 'pedestal' in response.content.decode('utf-8')
    assert 'Ozymandias' in response.content.decode('utf-8')
    assert 'Mighty' in response.content.decode('utf-8')

    # Verify we have the locale columns.
    assert 'kl' in response.content.decode('utf-8')
    assert 'gs' in response.content.decode('utf-8')

    # Now add some translations.
    entity = Entity.objects.filter(string='And on the pedestal these words appear:')[0]
    TranslationFactory.create(
        string='Et sur le piédestal il y a ces mots :',
        entity=entity,
        locale=locale_kl,
        approved=True,
    )
    TranslationFactory.create(
        string='Und auf dem Sockel steht die Schrift: ‚Mein Name',
        entity=entity,
        locale=locale_gs,
        approved=True,
    )

    entity = Entity.objects.filter(string='\'My name is Ozymandias, king of kings:')[0]
    TranslationFactory.create(
        string='"Mon nom est Ozymandias, Roi des Rois.',
        entity=entity,
        locale=locale_kl,
        approved=True,
    )
    TranslationFactory.create(
        string='Ist Osymandias, aller Kön’ge König: –',
        entity=entity,
        locale=locale_gs,
        approved=True,
    )

    entity = Entity.objects.filter(string='Look on my works, ye Mighty, and despair!\'')[0]
    TranslationFactory.create(
        string='Voyez mon œuvre, vous puissants, et désespérez !"',
        entity=entity,
        locale=locale_kl,
        approved=True,
    )
    TranslationFactory.create(
        string='Seht meine Werke, Mächt’ge, und erbebt!‘',
        entity=entity,
        locale=locale_gs,
        approved=True,
    )

    response = client_superuser.get(url, {'format': 'csv'})

    # Verify the translated content is here.
    assert 'pedestal' in response.content.decode('utf-8')
    assert 'piédestal' in response.content.decode('utf-8')
    assert 'Sockel' in response.content.decode('utf-8')

    assert 'Mighty' in response.content.decode('utf-8')
    assert 'puissants' in response.content.decode('utf-8')
    assert 'Mächt’ge' in response.content.decode('utf-8')


@pytest.mark.django_db
def test_project_add_locale(client_superuser):
    locale_kl = LocaleFactory.create(code='kl', name='Klingon')
    locale_gs = LocaleFactory.create(code='gs', name='Geonosian')
    project = ProjectFactory.create(
        data_source='database',
        locales=[locale_kl],
        repositories=[],
    )
    _create_or_update_translated_resources(project, [locale_kl])

    url = reverse('pontoon.admin.project', args=(project.slug,))

    # Boring data creation for FormSets. Django is painful with that,
    # or I don't know how to handle that more gracefully.
    form = ProjectForm(instance=project)
    form_data = dict(form.initial)
    del form_data['width']
    del form_data['deadline']
    del form_data['contact']
    form_data.update({
        'subpage_set-INITIAL_FORMS': '0',
        'subpage_set-TOTAL_FORMS': '1',
        'subpage_set-MIN_NUM_FORMS': '0',
        'subpage_set-MAX_NUM_FORMS': '1000',
        'externalresource_set-TOTAL_FORMS': '1',
        'externalresource_set-MAX_NUM_FORMS': '1000',
        'externalresource_set-MIN_NUM_FORMS': '0',
        'externalresource_set-INITIAL_FORMS': '0',
        'tag_set-TOTAL_FORMS': '1',
        'tag_set-INITIAL_FORMS': '0',
        'tag_set-MAX_NUM_FORMS': '1000',
        'tag_set-MIN_NUM_FORMS': '0',
        'repositories-INITIAL_FORMS': '0',
        'repositories-MIN_NUM_FORMS': '0',
        'repositories-MAX_NUM_FORMS': '1000',
        'repositories-TOTAL_FORMS': '0',
        # These are the values that actually matter.
        'pk': project.pk,
        'locales': [locale_kl.id, locale_gs.id],
    })

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert '. Error.' not in response.content.decode('utf-8')

    # Verify we have the right ProjectLocale objects.
    pl = ProjectLocale.objects.filter(project=project)
    assert len(pl) == 2

    # Verify that TranslatedResource objects have been created.
    resource = Resource.objects.get(project=project, path='database')
    tr = TranslatedResource.objects.filter(resource=resource)
    assert len(tr) == 2
