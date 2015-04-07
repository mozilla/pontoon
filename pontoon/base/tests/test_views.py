from django.core.urlresolvers import reverse

from django_nose.tools import assert_equal

from pontoon.base.models import Project
from pontoon.base.tests import (
    assert_redirects,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
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
        LocaleFactory.create(code='en-gb')

        response = self.client.get('/en-gb/invalid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_locale_not_available(self):
        """
        If the requested locale is not available for this project,
        redirect home.
        """
        LocaleFactory.create(code='en-gb')
        ProjectFactory.create(slug='valid-project')

        response = self.client.get('/en-gb/valid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'none': None})

    def test_not_authed_public_project(self):
        """
        If the user is not authenticated and we're translating project
        ID 1, return a 200.
        """
        # Clear out existing project with ID=1 if necessary.
        Project.objects.filter(id=1).delete()
        locale = LocaleFactory.create(code='en-gb')
        project = ProjectFactory.create(id=1, slug='valid-project', locales=[locale])
        ResourceFactory.create(project=project)

        response = self.client.get('/en-gb/valid-project/')
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
        locale = LocaleFactory.create(code='en-gb')
        project = ProjectFactory.create(id=2, slug='valid-project', locales=[locale])
        ResourceFactory.create(project=project)

        response = self.client.get('/en-gb/valid-project/')
        assert_redirects(response, reverse('pontoon.home'))
        assert_equal(self.client.session['translate_error'], {'redirect': '/en-gb/valid-project/'})
