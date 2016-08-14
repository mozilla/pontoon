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

    def test_python_new_format_placeables(self):
        """Test detection of the new format string in python strings."""
        assert_equal(
            mark_placeables(u'Hello {name}'),
            u'Hello <mark class="placeable" title="Python format string">{name}</mark>'
        )

        assert_equal(
            mark_placeables(u'Hello {name!s}'),
            u'Hello <mark class="placeable" title="Python format string">{name!s}</mark>'
        )

        assert_equal(
            mark_placeables(u'Hello {someone.name}'),
            u'Hello <mark class="placeable" title="Python format string">{someone.name}</mark>'
        )

        assert_equal(
            mark_placeables(u'Hello {name[0]}'),
            u'Hello <mark class="placeable" title="Python format string">{name[0]}</mark>'
        )

        assert_equal(
            mark_placeables(u'Hello {someone.name[0]}'),
            u'Hello <mark class="placeable" title="Python format string">{someone.name[0]}</mark>'
        )

    def test_python_format_named_placeables(self):
        """Test detection of format string with named placeables."""
        assert_equal(
            mark_placeables(u'Hello %(name)s'),
            u'Hello <mark class="placeable" title="Python format string">%(name)s</mark>'
        )

        assert_equal(
            mark_placeables(u'Rolling %(number)d dices'),
            u'Rolling <mark class="placeable" title="Python format string">%(number)d</mark> dices'
        )

        assert_equal(
            mark_placeables(u'Hello %(name)S'),
            u'Hello <mark class="placeable" title="Python format string">%(name)S</mark>'
        )

        assert_equal(
            mark_placeables(u'Rolling %(number)D dices'),
            u'Rolling <mark class="placeable" title="Python format string">%(number)D</mark> dices'
        )