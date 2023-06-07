from pontoon.base.placeables import get_placeables


def test_no_placeables():
    input = "My name is Luka."
    placeables = get_placeables(input)

    assert placeables == []


def test_PythonFormatNamedString():
    input = "My %(name)s is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(name)s"]


def test_PythonFormatString():
    input = "My { name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ name }"]


def test_FluentTerm():
    input = "My { -name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ -name }"]


def test_FluentFunction():
    input = "My { NAME() } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ NAME() }"]
