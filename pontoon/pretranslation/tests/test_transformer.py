import pytest
from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent

from pontoon.pretranslation.transformer import ApplyPretranslation
from pontoon.test.factories import LocaleFactory


def visit(src):
    def callback(source, locale, preserve_placeables):
        return (source, locale.code)

    locale = LocaleFactory(code="en-XX")
    ast = FluentParser().parse_entry(dedent(src))
    transformer = ApplyPretranslation(locale, ast, callback)
    transformer.visit(ast)
    return ast, transformer


@pytest.mark.django_db
def test_transformer_value_single_element():
    # Do not modify value with single element
    res, transformer = visit(
        """
        title = My Title
    """,
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My Title"


@pytest.mark.django_db
def test_transformer_attribute_single_element():
    # Do not modify attributes with single element
    res, transformer = visit(
        """
        title =
            .foo = Bar
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar"


@pytest.mark.django_db
def test_transformer_single_select_expression():
    # Do not modify value with a single select expression
    res, transformer = visit(
        """
        my-entry =
            { PLATFORM() ->
                [variant] Hello!
                *[another-variant] World!
            }
    """
    )

    assert len(res.value.elements) == 1
    assert (
        res.value.elements[0].expression.variants[0].value.elements[0].value == "Hello!"
    )
    assert (
        res.value.elements[0].expression.variants[1].value.elements[0].value == "World!"
    )


@pytest.mark.django_db
def test_transformer_value_several_elements():
    # Flatten value with several elements
    res, transformer = visit(
        """
        title = My { $awesome } Title
    """
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "My { $awesome } Title"


@pytest.mark.django_db
def test_transformer_attribute_several_elements():
    # Flatten attribute with several elements
    res, transformer = visit(
        """
        title =
            .foo = Bar { -foo } Baz
    """
    )

    assert len(res.attributes) == 1
    assert len(res.attributes[0].value.elements) == 1
    assert res.attributes[0].value.elements[0].value == "Bar { -foo } Baz"


@pytest.mark.django_db
def test_transformer_value_and_attributes():
    # Flatten value and attributes
    res, transformer = visit(
        """
        batman = The { $dark } Knight
            .weapon = Brain and { -wayne-enterprise }
            .history = Lost { 2 } parents, has { 1 } "$alfred"
    """
    )

    assert len(res.value.elements) == 1
    assert res.value.elements[0].value == "The { $dark } Knight"

    assert len(res.attributes) == 2

    assert len(res.attributes[0].value.elements) == 1
    assert (
        res.attributes[0].value.elements[0].value == "Brain and { -wayne-enterprise }"
    )

    assert len(res.attributes[1].value.elements) == 1
    assert (
        res.attributes[1].value.elements[0].value
        == 'Lost { 2 } parents, has { 1 } "$alfred"'
    )


@pytest.mark.django_db
def test_transformer_callback(locale_a):
    called = []

    def callback(source, locale, preserve_placeables):
        called.append(source)
        return ("res: " + source, locale.code)

    entry = FluentParser().parse_entry("title = Hello { $world }!\n")
    transformer = ApplyPretranslation(locale_a, entry, callback)
    transformer.visit(entry)

    assert len(entry.value.elements) == 1
    assert entry.value.elements[0].value == "res: Hello { $world }!"

    assert len(transformer.services) == 1
    assert transformer.services[0] == "kg"

    assert len(called) == 1
    assert called[0] == "Hello { $world }!"


@pytest.mark.django_db
def test_plural_variants(locale_a):
    called = []

    def callback(source, locale, preserve_placeables):
        called.append(source)
        return ("res: " + source, locale.code)

    input = dedent(
        """
            my-entry =
                { $num ->
                    [0] Yo!
                    [one] Hello!
                   *[other] { $num } World!
                }
        """
    )
    entry = FluentParser().parse_entry(input)

    locale_a.code = "tlh"
    locale_a.cldr_plurals = "1,2,3,5"
    transformer = ApplyPretranslation(locale_a, entry, callback)
    transformer.visit(entry)

    expected = FluentParser().parse_entry(
        dedent(
            """
                my-entry =
                    { $num ->
                        [0] res: Yo!
                        [one] res: Hello!
                        [two] res: { $num } World!
                        [few] res: { $num } World!
                       *[other] res: { $num } World!
                    }
            """
        )
    )

    serializer = FluentSerializer()
    assert serializer.serialize_entry(entry) == serializer.serialize_entry(expected)

    assert called == [
        "Yo!",
        "Hello!",
        "{ $num } World!",
        "{ $num } World!",
        "{ $num } World!",
    ]
