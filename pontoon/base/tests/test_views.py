from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.timezone import now

from django_nose.tools import assert_equal, assert_true, assert_code
from mock import patch

from pontoon.base.models import Project
from pontoon.base.utils import aware_datetime
from pontoon.base.tests import (
    assert_redirects,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    StatsFactory,
    TestCase,
)

from pontoon.base import views


class TranslateTests(TestCase):
    def test_invalid_locale_and_project(self):
        """If the locale and project are both invalid, return a 404."""
        response = self.client.get('/invalid-locale/invalid-project/')
        assert_equal(response.status_code, 404)

    def test_invalid_locale_valid_project(self):
        """
        If the project is valid but the locale isn't, redirect home.
        """
        project = ProjectFactory.create(slug='valid-project')
        ResourceFactory.create(project=project)

        response = self.client.get('/invalid-locale/valid-project/path/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_invalid_project(self):
        """If the project is invalid, redirect home."""
        LocaleFactory.create(code='fakelocale')

        response = self.client.get('/fakelocale/invalid-project/path/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_locale_not_available(self):
        """
        If the requested locale is not available for this project,
        redirect home.
        """
        LocaleFactory.create(code='fakelocale')
        ProjectFactory.create(slug='valid-project')

        response = self.client.get('/fakelocale/valid-project/path/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_not_authed_public_project(self):
        """
        If the user is not authenticated and we're translating project
        ID 1, return a 200.
        """
        # Clear out existing project with ID=1 if necessary.
        Project.objects.filter(id=1).delete()
        locale = LocaleFactory.create(code='fakelocale')
        project = ProjectFactory.create(id=1, slug='valid-project', locales=[locale])
        resource = ResourceFactory.create(project=project, path='foo.lang', entity_count=1)
        StatsFactory.create(resource=resource, locale=locale)

        response = self.client.get('/fakelocale/valid-project/foo.lang/')
        assert_equal(response.status_code, 200)
        # I'd assertTemplateUsed here but it doesn't work on non-DTL
        # templates.

    def test_not_authed_nonpublic_project(self):
        """
        If the user is not authenticated and we're not translating
        project ID 1, redirect home.
        """
        # Clear out existing project with ID=1 if necessary.
        Project.objects.filter(id=2).delete()
        locale = LocaleFactory.create(code='fakelocale')
        project = ProjectFactory.create(id=2, slug='valid-project', locales=[locale])
        ResourceFactory.create(project=project)

        response = self.client.get('/fakelocale/valid-project/path/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'redirect': '/fakelocale/valid-project/path/'})

    def test_no_subpage_multiple_stats_in_current_locale(self):
        """
        If there are multiple stats for a resource available in the current
        locale, and no subpages, set the part to the resource path.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        resource1 = ResourceFactory.create(project=project, path='foo1.lang', entity_count=1)
        resource2 = ResourceFactory.create(project=project, path='foo2.lang', entity_count=1)
        StatsFactory.create(resource=resource1, locale=locale)
        StatsFactory.create(resource=resource2, locale=locale)

        self.client_login()
        url = '/' + '/'.join([locale.code, project.slug, resource1.path]) + '/'
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_equal(mock_render.call_args[0][2]['part'], 'foo1.lang')

    def test_no_subpage_one_stats_in_current_locale(self):
        """
        If there is just one stats for a resource available in the current
        locale, and no subpages, set the part to the resource path.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        resource = ResourceFactory.create(project=project, path='foo.lang', entity_count=1)
        StatsFactory.create(resource=resource, locale=locale)

        self.client_login()
        url = '/{}/'.format('/'.join([locale.code, project.slug, resource.path]))
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_equal(mock_render.call_args[0][2]['part'], 'foo.lang')

    def test_no_subpage_no_stats_in_current_locale(self):
        """
        If there are stats for a resource available in other locales but
        not in the current one, and no subpages, do not set ctx['part'].
        """
        locale, locale_no_stats = LocaleFactory.create_batch(2)
        project = ProjectFactory.create(locales=[locale, locale_no_stats])

        resource = ResourceFactory.create(project=project, path='foo.lang', entity_count=1)
        ResourceFactory.create(project=project, entity_count=1)
        StatsFactory.create(resource=resource, locale=locale)

        self.client_login()
        url = '/{}/'.format('/'.join([locale_no_stats.code, project.slug, resource.path]))
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_true('part' not in mock_render.call_args[0][2])


class ContributorsTests(TestCase):
    def setUp(self):
        mock_render = patch.object(views.ContributorsView, 'render_to_response', return_value=HttpResponse(''))
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

        mock_translations_manager = patch('pontoon.base.models.UserTranslationsManager.with_translation_counts')
        self.mock_translations_manager = mock_translations_manager.start()
        self.addCleanup(mock_translations_manager.stop)

    def test_default_period(self):
        """
        Calling the top_contributors should result in period being None.
        """
        self.client.get('/contributors/')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

    def test_invalid_period(self):
        """
        Checks how view handles invalid period, it result in period being None - displays all data.  """
        # If period parameter is invalid value
        self.client.get('/contributors/?period=invalidperiod')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

        # Period shouldn't be negative integer
        self.client.get('/contributors/?period=-6')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

    def test_given_period(self):
        """
        Checks if view sets and returns data for right period.
        """
        with patch('django.utils.timezone.now', wraps=now, return_value=aware_datetime(2015, 7, 5)):
            self.client.get('/contributors/?period=6')
            assert_equal(self.mock_render.call_args[0][0]['period'], 6)
            assert_equal(self.mock_translations_manager.call_args[0][0], aware_datetime(2015, 1, 5))


class ViewTestCase(TestCase):
    def setUp(self):
        """
        We don't call update_projects during the tests, so we have to
        create dummy resource project to avoid recurse redirect at /.
        """
        ResourceFactory.create(project=Project.objects.get(pk=1))


class ProjectTests(ViewTestCase):
    def test_project_doesnt_exist(self):
        """
        Checks if view is returning error when project slug is invalid.
        """
        assert_code(self.client.get('/projects/project_doesnt_exist/'), 404)

    def test_project_view(self):
        """
        Checks if project page is returned properly.
        """
        project = ProjectFactory.create()
        ResourceFactory.create(project=project)

        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get('/projects/{}/'.format(project.slug))
            assert_equal(mock_render.call_args[0][2]['project'], project)


class ProjectContributorsTests(ViewTestCase):
    def test_project_doesnt_exist(self):
        """
        Checks if view handles invalid project.
        """
        assert_code(self.client.get('/projects/project_doesnt_exist/contributors'), 404)

    def test_project_contributors(self):
        """
        Tests if view returns contributors specific for given project.
        """
        first_project = ProjectFactory.create()
        ResourceFactory.create(project=first_project)
        first_project_contributor = TranslationFactory.create(entity__resource__project=first_project).user

        second_project = ProjectFactory.create()
        ResourceFactory.create(project=second_project)
        second_project_contributor = TranslationFactory.create(entity__resource__project=second_project).user

        with patch.object(views.ProjectContributorsView, 'render_to_response', return_value=HttpResponse('')) as mock_render:

            self.client.get('/projects/{}/contributors'.format(first_project.slug))
            assert_equal(mock_render.call_args[0][0]['project'], first_project)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [first_project_contributor])

            self.client.get('/projects/{}/contributors'.format(second_project.slug))
            assert_equal(mock_render.call_args[0][0]['project'], second_project)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [second_project_contributor])


class LocaleTests(ViewTestCase):
    def test_locale_doesnt_exist(self):
        """
        Tests if view is returning an error on the missing locale.
        """
        assert_code(self.client.get('/missing-locale/'), 404)

    def test_locale_view(self):
        """
        Checks if locale page is returned properly.
        """
        locale = LocaleFactory.create()

        # Locale requires valid project with resources
        ResourceFactory.create(project__locales=[locale])

        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get('/{}/'.format(locale.code))
            assert_equal(mock_render.call_args[0][2]['locale'], locale)


class LocaleContributorsTests(ViewTestCase):
    def test_locale_doesnt_exist(self):
        """
        Tests if view is returning an error on the missing locale.
        """
        assert_code(self.client.get('/missing-locale/contributors'), 404)

    def test_locale_contributors(self):
        """
        Tests if view returns contributors specific for given locale.
        """
        first_locale = LocaleFactory.create()
        first_locale_contributor = TranslationFactory.create(locale=first_locale,
            entity__resource__project__locales=[first_locale]).user

        second_locale = LocaleFactory.create()
        second_locale_contributor = TranslationFactory.create(locale=second_locale,
            entity__resource__project__locales=[second_locale]).user

        with patch.object(views.LocaleContributorsView, 'render_to_response', return_value=HttpResponse('')) as mock_render:
            self.client.get('/{}/contributors'.format(first_locale.code))
            assert_equal(mock_render.call_args[0][0]['locale'], first_locale)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [first_locale_contributor])

            self.client.get('/{}/contributors'.format(second_locale.code))
            assert_equal(mock_render.call_args[0][0]['locale'], second_locale)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [second_locale_contributor])

