from django_nose.tools import assert_equal

from pontoon.base.tests import TestCase
from pontoon.base.utils import NewlineEscapePlaceable


class PlaceablesTests(TestCase):
    def test_newline_escape_placeable(self):
        """Test detecting newline escape sequences"""
        placeable = NewlineEscapePlaceable

        assert_equal(placeable.parse(u'A string\\n')[1], placeable([u'\\n']))
        assert_equal(placeable.parse(u'\\nA string')[0], placeable([u'\\n']))
        assert_equal(placeable.parse(u'A\\nstring')[1], placeable([u'\\n']))
        assert_equal(placeable.parse(u'A string'), None)
        assert_equal(placeable.parse(u'A\nstring'), None)
