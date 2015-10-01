from django_nose.tools import assert_false, assert_true

from pontoon.base.tests import TestCase
from pontoon.base.utils import extension_in


class UtilsTests(TestCase):
    def test_extension_in(self):
        assert_true(extension_in('filename.txt', ['bat', 'txt']))
        assert_true(extension_in('filename.biff', ['biff']))
        assert_true(extension_in('filename.tar.gz', ['gz']))

        assert_false(extension_in('filename.txt', ['png', 'jpg']))
        assert_false(extension_in('.dotfile', ['bat', 'txt']))

        # Unintuitive, but that's how splitext works.
        assert_false(extension_in('filename.tar.gz', ['tar.gz']))
