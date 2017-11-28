# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from django_nose.tools import (
    assert_code,
    assert_contains,
    assert_equal,
    assert_not_contains,
)

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TestCase,
    UserFactory,
)


class SuperuserTestCase(TestCase):
    """TestCase for tests that require a superuser to be logged in. """

    def setUp(self):
        self.user = UserFactory.create(is_superuser=True)
        self.client.force_login(self.user)


class AdministrationViewsTests(TestCase):
    """Test views of the administration app without having a logged in superuser.
    """

    def test_manage_project_strings(self):
        project = ProjectFactory.create(data_source='database', repositories=[])
        url = reverse('pontoon.admin.project.strings', args=(project.slug,))

        # Test with anonymous user.
        response = self.client.get(url)
        assert_code(response, 403)

        # Test with a user that is not a superuser.
        user = UserFactory.create()
        self.client.force_login(user)

        response = self.client.get(url)
        assert_code(response, 403)

        # Test with a superuser.
        user.is_superuser = True
        user.save()

        response = self.client.get(url)
        assert_code(response, 200)


class AdministrationViewsWithSuperuserTests(SuperuserTestCase):
    """Test views of the administration app with a superuser logged in by default.
    """

    def test_manage_project(self):
        url = reverse('pontoon.admin.project.new')
        response = self.client.get(url)
        assert_code(response, 200)

    def test_manage_project_strings_bad_request(self):
        # Tets an unknown project returns a 404 error.
        url = reverse('pontoon.admin.project.strings', args=('unknown',))
        response = self.client.get(url)
        assert_code(response, 404)

    def test_manage_project_strings_new(self):
        project = ProjectFactory.create(data_source='database', repositories=[])
        url = reverse('pontoon.admin.project.strings', args=(project.slug,))

        # Test sending a well-formatted batch of strings.
        new_strings = """Hey, I just met you
            And this is crazy
            But here's my number
            So call me maybe?
        """
        response = self.client.post(url, {'new_strings': new_strings})
        assert_code(response, 200)

        # Verify a resource has been created.
        resources = list(Resource.objects.filter(project=project))
        assert_equal(len(resources), 1)

        assert_equal(resources[0].path, 'database')

        # Verify all strings have been created as entities.
        entities = list(Entity.objects.filter(resource__project=project))
        assert_equal(len(entities), 4)

        expected_strings = [
            'Hey, I just met you',
            'And this is crazy',
            'But here\'s my number',
            'So call me maybe?',
        ]

        assert_equal(sorted(expected_strings), sorted(x.string for x in entities))

        # Verify new strings appear on the page.
        assert_contains(response, 'Hey, I just met you')

    def test_manage_project_strings_translated_resource(self):
        """Test that adding new strings to a project enables translation of that
        project on all enabled locales.
        """
        locale_kl = LocaleFactory.create(code='kl', name='Klingon')
        locale_gs = LocaleFactory.create(code='gs', name='Geonosian')
        project = ProjectFactory.create(
            data_source='database',
            locales=[locale_kl, locale_gs],
            repositories=[]
        )
        locales_count = 2

        url = reverse('pontoon.admin.project.strings', args=(project.slug,))

        new_strings = """
            Morty, do you know what "Wubba lubba dub dub" means?
            Oh that's just Rick's stupid non-sense catch phrase.
            It's not.
            In my people's tongue, it means "I am in great pain, please help me".
        """
        strings_count = 4
        response = self.client.post(url, {'new_strings': new_strings})
        assert_code(response, 200)

        # Verify no strings have been created as entities.
        entities = list(Entity.objects.filter(resource__project=project))
        assert_equal(len(entities), strings_count)

        # Verify the resource has the right stats.
        resources = Resource.objects.filter(project=project)
        assert_equal(len(resources), 1)
        resource = resources[0]
        assert_equal(resource.total_strings, strings_count)

        # Verify the correct TranslatedResource objects have been created.
        translated_resources = TranslatedResource.objects.filter(resource__project=project)
        assert_equal(len(translated_resources), locales_count)

        # Verify stats have been correctly updated on locale, project and resource.
        for tr in translated_resources:
            assert_equal(tr.total_strings, strings_count)

        project = Project.objects.get(id=project.id)
        assert_equal(project.total_strings, strings_count * locales_count)

        locale_kl = Locale.objects.get(id=locale_kl.id)
        assert_equal(locale_kl.total_strings, strings_count)

        locale_gs = Locale.objects.get(id=locale_gs.id)
        assert_equal(locale_gs.total_strings, strings_count)

    def test_manage_project_strings_new_all_empty(self):
        """Test that sending empty data doesn't create empty strings in the database.
        """
        project = ProjectFactory.create(data_source='database', repositories=[])
        url = reverse('pontoon.admin.project.strings', args=(project.slug,))

        # Test sending a well-formatted batch of strings.
        new_strings = "  \n   \n\n"
        response = self.client.post(url, {'new_strings': new_strings})
        assert_code(response, 200)

        # Verify no strings have been created as entities.
        entities = list(Entity.objects.filter(resource__project=project))
        assert_equal(len(entities), 0)

    def test_manage_project_strings_list(self):
        project = ProjectFactory.create(data_source='database', repositories=[])
        resource = ResourceFactory.create(project=project)
        nb_entities = 2
        entities = EntityFactory.create_batch(nb_entities, resource=resource)

        url = reverse('pontoon.admin.project.strings', args=(project.slug,))

        response = self.client.get(url)
        assert_code(response, 200)
        for i in range(nb_entities):
            assert_contains(response, 'string %s' % i)

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

        response = self.client.post(url, form_data)
        assert_code(response, 200)
        assert_contains(response, 'changed 0')
        assert_contains(response, 'Wubba lubba dub dub')
        assert_not_contains(response, 'string 0')
        assert_not_contains(response, 'string 1')  # It's been removed.

    def test_manage_project_strings_download_csv(self):
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
        response = self.client.post(url, {'new_strings': new_strings})
        assert_code(response, 200)

        # Test downloading the data.
        response = self.client.get(url, {'format': 'csv'})
        assert_code(response, 200)
        assert_equal(response._headers['content-type'], ('Content-Type', 'text/csv'))

        # Verify the original content is here.
        assert_contains(response, 'pedestal')
        assert_contains(response, 'Ozymandias')
        assert_contains(response, 'Mighty')

        # Verify we have the locale columns.
        assert_contains(response, 'kl')
        assert_contains(response, 'gs')

        # Now add some translations.
        entity = Entity.objects.filter(string='And on the pedestal these words appear:')[0]
        Translation(
            string='Et sur le piédestal il y a ces mots :',
            entity=entity,
            locale=locale_kl,
            approved=True,
        ).save()
        Translation(
            string='Und auf dem Sockel steht die Schrift: ‚Mein Name',
            entity=entity,
            locale=locale_gs,
            approved=True,
        ).save()

        entity = Entity.objects.filter(string='\'My name is Ozymandias, king of kings:')[0]
        Translation(
            string='"Mon nom est Ozymandias, Roi des Rois.',
            entity=entity,
            locale=locale_kl,
            approved=True,
        ).save()
        Translation(
            string='Ist Osymandias, aller Kön’ge König: –',
            entity=entity,
            locale=locale_gs,
            approved=True,
        ).save()

        entity = Entity.objects.filter(string='Look on my works, ye Mighty, and despair!\'')[0]
        Translation(
            string='Voyez mon œuvre, vous puissants, et désespérez !"',
            entity=entity,
            locale=locale_kl,
            approved=True,
        ).save()
        Translation(
            string='Seht meine Werke, Mächt’ge, und erbebt!‘',
            entity=entity,
            locale=locale_gs,
            approved=True,
        ).save()

        response = self.client.get(url, {'format': 'csv'})

        # Verify the translated content is here.
        assert_contains(response, 'pedestal')
        assert_contains(response, 'piédestal')
        assert_contains(response, 'Sockel')

        assert_contains(response, 'Mighty')
        assert_contains(response, 'puissants')
        assert_contains(response, 'Mächt’ge')
