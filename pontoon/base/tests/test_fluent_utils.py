from textwrap import dedent

from moz.l10n.formats.fluent import fluent_parse_entry

from pontoon.base.fluent_utils import (
    get_references,
    get_selector_variants,
)


def test_get_references_no_placeholders():
    entry = fluent_parse_entry("message = Simple string", with_linepos=False)

    assert get_references(entry) == set()


def test_get_references_from_value():
    """Test message/term references are collected (and not variables)."""
    entry = fluent_parse_entry(
        "message = Welcome to { -brand-name }, { $user }!", with_linepos=False
    )

    assert get_references(entry) == {"-brand-name"}


def test_get_references_from_attributes():
    """Test terms can be extracted from attributes."""
    entry = fluent_parse_entry(
        dedent("""\
            message =
                .gender = { -brand-name(case: "genitive") }
                .tooltip = { $count }
            """),
        with_linepos=False,
    )

    assert get_references(entry) == {"-brand-name"}


def test_get_references_from_declarations_and_select_variants():
    """Test references from select variants are picked up."""
    entry = fluent_parse_entry(
        dedent("""\
            message =
                { $count ->
                    [one] { -brand-short-name } blocked one tracker
                    *[other] { -brand-short-name } blocked many trackers
                }
            """),
        with_linepos=False,
    )

    assert get_references(entry) == {"-brand-short-name"}


def test_get_selector_variants_no_selectors():
    """Test extracting variants from a term with no selector."""
    entry = fluent_parse_entry(
        "message = Welcome to { -brand-name }!", with_linepos=False
    )

    assert get_selector_variants(entry) == []


def test_get_selector_variants_from_value():
    """Test extracting variants from a selector."""
    entry = fluent_parse_entry(
        dedent("""\
            message =
                { $count ->
                    [one] One tracker blocked
                   *[other] Trackers blocked
                }
            """),
        with_linepos=False,
    )

    assert get_selector_variants(entry) == [
        {"name": "count", "values": ["one", "other"]}
    ]


def test_get_selector_variants_multiple_selectors():
    """Test extracting variants from nested selectors."""
    entry = fluent_parse_entry(
        dedent("""\
            message =
                { $gender ->
                    [masculine] { $count ->
                        [one] One
                        *[other] Many
                    }
                   *[feminine] Feminine
                }
            """),
        with_linepos=False,
    )

    assert get_selector_variants(entry) == [
        {"name": "gender", "values": ["masculine", "feminine"]},
        {"name": "count", "values": ["one", "other"]},
    ]


def test_get_selector_variants_from_attributes():
    """Test extracting variants from attribute selectors."""
    entry = fluent_parse_entry(
        dedent("""\
            message =
                .accesskey = value with no selector
                .tooltip =
                    { $case ->
                        [nominative] Nominative
                        [genitive] Genitive
                       *[other] Other
                    }
            """),
        with_linepos=False,
    )

    assert get_selector_variants(entry) == [
        {"name": "case", "values": ["nominative", "genitive", "other"]}
    ]


def test_get_selector_variants_sorting():
    """Test extracting variants from a selector keeps the default at the end."""
    entry = fluent_parse_entry(
        dedent(
            """\
        message =
            { $count ->
                *[other] Trackers blocked
                [one] One tracker blocked
            }
        """
        )
    )

    assert get_selector_variants(entry) == [
        {"name": "count", "values": ["one", "other"]}
    ]
