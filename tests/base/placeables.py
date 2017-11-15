
from pontoon.base.utils import NewlineEscapePlaceable, mark_placeables


def test_placeable_base_newline_escape():
    """Test detecting newline escape sequences"""
    placeable = NewlineEscapePlaceable
    assert placeable.parse(u'A string\\n')[1] == placeable([u'\\n'])
    assert placeable.parse(u'\\nA string')[0] == placeable([u'\\n'])
    assert placeable.parse(u'A\\nstring')[1] == placeable([u'\\n'])
    assert placeable.parse(u'A string') is None
    assert placeable.parse(u'A\nstring') is None


def test_placeable_base_mark_newline_escape():
    """Test detecting newline escape sequences"""
    assert (
        mark_placeables(u'A string\\n')
        == (u'A string<mark class="placeable" '
            'title="Escaped newline">\\n</mark>'))
    assert (
        mark_placeables(u'\\nA string')
        == (u'<mark class="placeable" '
            'title="Escaped newline">\\n</mark>A string'))
    assert (
        mark_placeables(u'A\\nstring')
        == (u'A<mark class="placeable" '
            'title="Escaped newline">\\n</mark>string'))
    assert (
        mark_placeables(u'A string')
        == u'A string')
    assert (
        mark_placeables(u'A\nstring')
        == u'A\nstring')


def test_placeable_base_python_new_format():
    """Test detection of the new format string in python strings."""
    assert (
        mark_placeables(u'Hello {name}')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">{name}</mark>'))
    assert (
        mark_placeables(u'Hello {name!s}')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">{name!s}</mark>'))
    assert (
        mark_placeables(u'Hello {someone.name}')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">{someone.name}</mark>'))
    assert (
        mark_placeables(u'Hello {name[0]}')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">{name[0]}</mark>'))
    assert (
        mark_placeables(u'Hello {someone.name[0]}')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">{someone.name[0]}</mark>'))


def test_placeable_base_format_named():
    """Test detection of format string with named placeables."""
    assert (
        mark_placeables(u'Hello %(name)s')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">%(name)s</mark>'))
    assert (
        mark_placeables(u'Rolling %(number)d dices')
        == (u'Rolling <mark class="placeable" '
            'title="Python format string">%(number)d</mark> dices'))
    assert (
        mark_placeables(u'Hello %(name)S')
        == (u'Hello <mark class="placeable" '
            'title="Python format string">%(name)S</mark>'))
    assert (
        mark_placeables(u'Rolling %(number)D dices')
        == (u'Rolling <mark class="placeable" '
            'title="Python format string">%(number)D</mark> dices'))
