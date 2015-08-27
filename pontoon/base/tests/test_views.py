from django.core.urlresolvers import reverse
from django.shortcuts import render

from django_nose.tools import assert_equal, assert_true
from mock import patch

from pontoon.base.models import Project
from pontoon.base.tests import (
    assert_redirects,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    StatsFactory,
    TestCase
)


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

        response = self.client.get('/invalid-locale/valid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_invalid_project(self):
        """If the project is invalid, redirect home."""
        LocaleFactory.create(code='fakelocale')

        response = self.client.get('/fakelocale/invalid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_locale_not_available(self):
        """
        If the requested locale is not available for this project,
        redirect home.
        """
        LocaleFactory.create(code='fakelocale')
        ProjectFactory.create(slug='valid-project')

        response = self.client.get('/fakelocale/valid-project/')
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
        ResourceFactory.create(project=project)

        response = self.client.get('/fakelocale/valid-project/')
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

        response = self.client.get('/fakelocale/valid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'redirect': '/fakelocale/valid-project/'})

    def test_no_subpage_multiple_stats_in_current_locale(self):
        """
        If there are multiple stats for a resource available in the current
        locale, and no subpages, set the part to the resource path.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        # Need at least two resources and stats to trigger setting the part value.
        resource1 = ResourceFactory.create(project=project, path='foo1.lang', entity_count=1)
        resource2 = ResourceFactory.create(project=project, path='foo2.lang', entity_count=1)
        StatsFactory.create(resource=resource1, locale=locale)
        StatsFactory.create(resource=resource2, locale=locale)

        self.client_login()
        url = '/{locale.code}/{project.slug}/'.format(locale=locale, project=project)
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_equal(mock_render.call_args[0][2]['part'], 'foo1.lang')

    def test_no_subpage_one_stats_in_current_locale(self):
        """
        If there is just one stats for a resource available in the current
        locale, and no subpages, do not set ctx['part'].
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        # Need two resources to trigger setting the part value.
        resource = ResourceFactory.create(project=project, path='foo.lang', entity_count=1)
        ResourceFactory.create(project=project, entity_count=1)
        StatsFactory.create(resource=resource, locale=locale)

        self.client_login()
        url = '/{locale.code}/{project.slug}/'.format(locale=locale, project=project)
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_true('part' not in mock_render.call_args[0][2])

    def test_no_subpage_no_stats_in_current_locale(self):
        """
        If there are stats for a resource available in other locales but
        not in the current one, and no subpages, do not set ctx['part'].
        """
        locale, locale_no_stats = LocaleFactory.create_batch(2)
        project = ProjectFactory.create(locales=[locale, locale_no_stats])

        # Need two resources to trigger setting the part value.
        resource = ResourceFactory.create(project=project, path='foo.lang', entity_count=1)
        ResourceFactory.create(project=project, entity_count=1)
        StatsFactory.create(resource=resource, locale=locale)

        self.client_login()
        url = '/{locale.code}/{project.slug}/'.format(locale=locale_no_stats, project=project)
        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get(url)
            assert_true('part' not in mock_render.call_args[0][2])
