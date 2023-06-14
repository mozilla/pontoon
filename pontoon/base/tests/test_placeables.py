from pontoon.base.placeables import get_placeables


def test_no_placeables():
    input = "My name is Luka."
    placeables = get_placeables(input)

    assert placeables == []


def test_JsonPlaceholder():
    input = "My $NAME$ is Luka."
    placeables = get_placeables(input)

    assert placeables == ["$NAME$"]

    input = "My $FIRST_NAME$ is Luka."
    placeables = get_placeables(input)

    assert placeables == ["$FIRST_NAME$"]


def test_MozillaPrintfString():
    input = "My %S is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%S"]

    input = "My %1$S is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%1$S"]

    input = "My %@ is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%@"]

    input = "My %2$@ is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%2$@"]


def test_PythonPrintfString():
    input = "My %(name)s is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(name)s"]

    input = "My %(name)d is Luka."
    placeables = get_placeables(input)

    assert placeables == ["%(name)d"]


def test_PythonFormatString():
    input = "My { name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ name }"]


def test_FluentPlaceable():
    input = "My { -name } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ -name }"]

    input = 'My { -name(foo-bar: "now that\'s a value!") } is Luka.'
    placeables = get_placeables(input)

    assert placeables == ['{ -name(foo-bar: "now that\'s a value!") }']

    input = "My { NAME() } is Luka."
    placeables = get_placeables(input)

    assert placeables == ["{ NAME() }"]


def test_multiple_placeables():
    input = "This { STRING() } contains multiple { -string } variables with some { -string } variables repeated."
    placeables = get_placeables(input)

    assert len(placeables) == 2
    assert sorted(placeables) == sorted(["{ STRING() }", "{ -string }"])
