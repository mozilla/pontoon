from pontoon.base.placeables import get_placeables


def test_no_placeables():
    input = "My name is Luka."
    placeables = get_placeables(input)

    assert placeables == []


def test_PythonFormatNamedString():
    input = "My %(name)s is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(name)s"]

    input = "My %(number)D is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(number)D"]


def test_PythonFormatString():
    input = "My { name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ name }"]


def test_PythonFormattingVariable():
    input = "My %(name)d is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(name)d"]


def test_FluentTerm():
    input = "My { -name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ -name }"]


def test_FluentParametrizedTerm():
    input = "My { -name(foo-bar: 'now that's a value!') } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ -name(foo-bar: 'now that's a value!') }"]


def test_FluentFunction():
    input = "My { NAME() } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ NAME() }"]
