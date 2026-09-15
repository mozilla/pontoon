from textwrap import dedent

from moz.l10n.formats.fluent import fluent_parse_entry

from pontoon.base.fluent_utils import (
    get_references,
    get_selector_variants,
)


def test_get_references_from_source_string():
    """Test that a Fluent source string is parsed and its references collected."""
    source = "message = Welcome to { -brand-name }, { $user }!"

    assert get_references(source) == {"-brand-name"}


def test_get_references_invalid_source_string():
    """Test unparseable Fluent source strings produce an empty set."""
    source = "no valid fluent here ]["

    assert get_references(source) == set()


def test_get_references_from_entry():
    """Test that references are collected from the parsed entry itself."""
    source = "message = Welcome to { -brand-name }, { $user }!"
    entry = fluent_parse_entry(source, with_linepos=False)

    assert get_references(entry) == {"-brand-name"}


def test_get_references_no_placeholders():
    """Test a string with no terms collects no references."""
    source = "message = Simple string"

    assert get_references(source) == set()


def test_get_references_from_attributes():
    """Test terms can be extracted from attributes."""
    source = dedent(
        """\
        message =
            .gender = { -brand-name(case: "genitive") }
            .tooltip = { $count }
        """
    )

    assert get_references(source) == {"-brand-name"}


def test_get_references_from_declarations_and_select_variants():
    """Test references from select variants are picked up."""
    source = dedent(
        """\
        message =
            { $count ->
                [one] { -brand-short-name } blocked one tracker
                *[other] { -brand-short-name } blocked many trackers
            }
        """
    )

    assert get_references(source) == {"-brand-short-name"}


def test_get_selector_variants_no_selectors():
    """Test extracting variants from a term with no selector."""
    source = "message = Welcome to { -brand-name }!"

    assert get_selector_variants(source) == []


def test_get_selector_variants_from_value():
    """Test extracting variants from a selector."""
    source = dedent(
        """\
        message =
            { $count ->
                [one] One tracker blocked
               *[other] Trackers blocked
            }
        """
    )

    assert get_selector_variants(source) == [
        {"name": "count", "values": ["one", "other"]}
    ]


def test_get_selector_variants_multiple_selectors():
    """Test extracting variants from nested selectors."""
    source = dedent(
        """\
        message =
            { $gender ->
                [masculine] { $count ->
                    [one] One
                    *[other] Many
                }
               *[feminine] Feminine
            }
        """
    )

    assert get_selector_variants(source) == [
        {"name": "gender", "values": ["masculine", "feminine"]},
        {"name": "count", "values": ["one", "other"]},
    ]


def test_get_selector_variants_from_attributes():
    """Test extracting variants from attribute selectors."""
    source = dedent(
        """\
        message =
            .accesskey = value with no selector
            .tooltip =
                { $case ->
                    [nominative] Nominative
                    [genitive] Genitive
                   *[other] Other
                }
        """
    )

    assert get_selector_variants(source) == [
        {"name": "case", "values": ["nominative", "genitive", "other"]}
    ]


def test_get_selector_variants_sorting():
    """Test extracting variants from a selector keeps the default at the end."""
    source = dedent(
        """\
        message =
            { $count ->
                *[other] Trackers blocked
                [one] One tracker blocked
            }
        """
    )

    assert get_selector_variants(source) == [
        {"name": "count", "values": ["one", "other"]}
    ]


def test_get_selector_variants_invalid_source_string():
    """Test unparseable Fluent source strings produce an empty list."""
    source = "no valid fluent here ]["

    assert get_selector_variants(source) == []
