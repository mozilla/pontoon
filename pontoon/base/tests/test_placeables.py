from django_nose.tools import assert_equal

from pontoon.base.tests import TestCase
from pontoon.base.utils import NewlineEscapePlaceable, mark_placeables


class PlaceablesTests(TestCase):
    def test_newline_escape_placeable(self):
        """Test detecting newline escape sequences"""
        placeable = NewlineEscapePlaceable

        assert_equal(placeable.parse(u'A string\\n')[1], placeable([u'\\n']))
        assert_equal(placeable.parse(u'\\nA string')[0], placeable([u'\\n']))
        assert_equal(placeable.parse(u'A\\nstring')[1], placeable([u'\\n']))
        assert_equal(placeable.parse(u'A string'), None)
        assert_equal(placeable.parse(u'A\nstring'), None)

    def test_mark_newline_escape_placeables(self):
        """Test detecting newline escape sequences"""
        assert_equal(
            mark_placeables(u'A string\\n'),
            u'A string<mark class="placeable" title="Escaped newline">\\n</mark>'
        )
        assert_equal(
            mark_placeables(u'\\nA string'),
            u'<mark class="placeable" title="Escaped newline">\\n</mark>A string'
        )
        assert_equal(
            mark_placeables(u'A\\nstring'),
            u'A<mark class="placeable" title="Escaped newline">\\n</mark>string'
        )
        assert_equal(
            mark_placeables(u'A string'),
            u'A string'
        )
        assert_equal(
            mark_placeables(u'A\nstring'),
            u'A\nstring'
        )
