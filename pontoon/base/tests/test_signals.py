from django_nose.tools import assert_false

from pontoon.base.models import ProjectLocale
from pontoon.base.tests import (
    ProjectFactory,
    LocaleFactory,
    TestCase,
    TranslationFactory,
)


class SignalTests(TestCase):
    def test_project_locale_modified(self):
        """
        If ProjectLocale is modified (like setting the
        latest_translation), has_changed should not be modified.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])
        project.has_changed = False
        project.save()

        project.refresh_from_db()
        assert_false(project.has_changed)

        project_locale = ProjectLocale.objects.get(project=project, locale=locale)
        project_locale.latest_translation = TranslationFactory.create(
            entity__resource__project=project, locale=locale)
        project_locale.save()

        project.refresh_from_db()
        assert_false(project.has_changed)
