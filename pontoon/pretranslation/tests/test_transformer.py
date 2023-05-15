import pytest
from fluent.syntax import FluentParser, FluentSerializer
from textwrap import dedent

from pontoon.pretranslation.transformer import ApplyPretranslation
from pontoon.test.factories import LocaleFactory


def visit(src):
    def callback(raw, wrapped, locale):
        return (wrapped, locale.code)

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

    assert len(transformer.replacements) == 0


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

    assert len(transformer.replacements) == 0


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

    assert len(transformer.replacements) == 0


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

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ $awesome }"


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

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ -foo }"


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

    assert len(transformer.replacements) == 4
    assert transformer.replacements[0] == "{ $dark }"
    assert transformer.replacements[1] == "{ -wayne-enterprise }"
    assert transformer.replacements[2] == "{ 2 }"
    assert transformer.replacements[3] == "{ 1 }"


@pytest.mark.django_db
def test_transformer_callback(locale_a):
    called = []

    def callback(raw, wrapped, locale):
        called.append((raw, wrapped))
        return ("res: " + wrapped, locale.code)

    entry = FluentParser().parse_entry("title = Hello { $world }!\n")
    transformer = ApplyPretranslation(locale_a, entry, callback)
    transformer.visit(entry)

    assert len(entry.value.elements) == 1
    assert entry.value.elements[0].value == "res: Hello { $world }!"

    assert len(transformer.replacements) == 1
    assert transformer.replacements[0] == "{ $world }"

    assert len(transformer.services) == 1
    assert transformer.services[0] == "kg"

    assert len(called) == 1
    assert called[0][0] == "Hello { $world }!"
    assert called[0][1] == 'Hello <span id="pt-0" translate="no">$world</span>!'


@pytest.mark.django_db
def test_plural_variants(locale_a):
    called = []

    def callback(raw, wrapped, locale):
        called.append((raw, wrapped))
        return ("res: " + wrapped, locale.code)

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
        ("Yo!", "Yo!"),
        ("Hello!", "Hello!"),
        ("{ $num } World!", '<span id="pt-0" translate="no">2</span> World!'),
        ("{ $num } World!", '<span id="pt-1" translate="no">3</span> World!'),
        ("{ $num } World!", '<span id="pt-2" translate="no">14</span> World!'),
    ]
