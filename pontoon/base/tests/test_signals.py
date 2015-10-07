from django_nose.tools import assert_false, assert_true

from pontoon.base.tests import ProjectFactory, LocaleFactory, TestCase


class SignalTests(TestCase):
    def test_project_locale_added(self):
        """
        When a locale is added to a project, has_changed should be set
        to True.
        """
        project = ProjectFactory.create(locales=[], has_changed=False)
        assert_false(project.has_changed)

        locale = LocaleFactory.create()
        project.locales.add(locale)
        project.refresh_from_db()
        assert_true(project.has_changed)
