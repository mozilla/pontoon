from django_nose.tools import assert_equal, assert_false, assert_is_none, assert_true

from pontoon.base.tests import ProjectFactory, TestCase
from pontoon.base.models import Project
from pontoon.base.utils import (
    aware_datetime,
    extension_in,
    get_object_or_none,
    latest_datetime,
)


class UtilsTests(TestCase):
    def test_extension_in(self):
        assert_true(extension_in('filename.txt', ['bat', 'txt']))
        assert_true(extension_in('filename.biff', ['biff']))
        assert_true(extension_in('filename.tar.gz', ['gz']))

        assert_false(extension_in('filename.txt', ['png', 'jpg']))
        assert_false(extension_in('.dotfile', ['bat', 'txt']))

        # Unintuitive, but that's how splitext works.
        assert_false(extension_in('filename.tar.gz', ['tar.gz']))

    def test_get_object_or_none(self):
        project = ProjectFactory.create(slug='exists')
        assert_is_none(get_object_or_none(Project, slug='does-not-exist'))
        assert_equal(get_object_or_none(Project, slug='exists'), project)

    def test_latest_datetime(self):
        larger = aware_datetime(2015, 1, 1)
        smaller = aware_datetime(2014, 1, 1)

        assert_is_none(latest_datetime([None, None, None]))
        assert_equal(latest_datetime([None, larger]), larger)
        assert_equal(latest_datetime([None, smaller, larger]), larger)
