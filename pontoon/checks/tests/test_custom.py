from unittest.mock import MagicMock

import pytest

from pontoon.checks.libraries.custom import run_custom_checks


@pytest.fixture()
def get_entity_mock():
    """
    Create an entity mock with comment, resource.path and extension.
    """

    def _f(format, comment="", string="", allows_empty_translations=False):
        match format:
            case "fluent":
                ext = "ftl"
            case "gettext":
                ext = "po"
            case _:
                ext = format
        entity = MagicMock()
        entity.comment = comment
        entity.string = string
        entity.resource.format = format
        entity.resource.path = f"test.{ext}"
        entity.resource.allows_empty_translations = allows_empty_translations
        return entity

    yield _f


def test_ending_newline(get_entity_mock):
    """
    Original and translation in a PO file must either both end
    in a newline, or none of them should.
    """
    po_entity = get_entity_mock("gettext")
    assert run_custom_checks(po_entity, "Original", "Translation\n") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Original\n", "Translation") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Original\n", "Translation\n") == {}
    assert run_custom_checks(po_entity, "Original", "Translation") == {}


def test_empty_translations_allowed(get_entity_mock):
    """
    Empty translations should be allowed but noted for some extensions.
    """
    assert run_custom_checks(
        get_entity_mock("properties", allows_empty_translations=True), "", ""
    ) == {"pndbWarnings": ["Empty translation"]}


def test_empty_translations_not_allowed(get_entity_mock):
    """
    Empty translations shouldn't be allowed for some extensions.
    """
    po_entity = get_entity_mock("gettext")
    empty_error = {"pErrors": ["Empty translations are not allowed"]}
    assert run_custom_checks(po_entity, "", "") == empty_error
    assert run_custom_checks(po_entity, "", "{{}}") == empty_error
    assert (
        run_custom_checks(po_entity, "", ".input {$n :number} .match $n * {{}}")
        == empty_error
    )
    assert (
        run_custom_checks(
            po_entity, "", ".input {$n :number} .match $n 1 {{}} * {{other}}"
        )
        == empty_error
    )
    assert run_custom_checks(po_entity, "", "{{{||}}}") == {}

    assert run_custom_checks(
        get_entity_mock("fluent", string="key = value"), "", 'key = { "" }'
    ) == {"pndbWarnings": ["Empty translation"]}

    assert (
        run_custom_checks(
            get_entity_mock("fluent", string="key = value"), "", 'key = { "x" }'
        )
        == {}
    )

    assert run_custom_checks(
        get_entity_mock("fluent", string="key =\n  .attr = value"),
        "",
        """key =
              { $var ->
                  [a] { "" }
                 *[b] { "" }
              }
              .attr = { "" }
            """,
    ) == {"pndbWarnings": ["Empty translation"]}

    assert run_custom_checks(
        get_entity_mock("fluent", string="key =\n  .attr = value"),
        "",
        """key =
              { $var ->
                  [a] { "x" }
                 *[b] { "y" }
              }
              .attr = { "" }
            """,
    ) == {"pndbWarnings": ["Empty translation"]}

    assert run_custom_checks(
        get_entity_mock("fluent", string="key =\n  .attr = value"),
        "",
        """key =
              { $var ->
                  [a] { "x" }
                 *[b] { "" }
              }
              .attr = { "y" }
            """,
    ) == {"pndbWarnings": ["Empty translation"]}

    assert (
        run_custom_checks(
            get_entity_mock("fluent", string="key =\n  .attr = value"),
            "",
            """key =
              { $var ->
                  [a] { "x" }
                 *[b] { "y" }
              }
              .attr = { "z" }
            """,
        )
        == {}
    )


def test_po_newlines(get_entity_mock):
    assert run_custom_checks(get_entity_mock("gettext"), "", "aaa\nbbb") == {}


def test_ftl_parse_error(get_entity_mock):
    """Invalid FTL strings are not allowed"""
    ftl_entity = get_entity_mock("fluent", string="key = value")
    assert run_custom_checks(ftl_entity, "", "key =") == {
        "pErrors": ['Expected message "key" to have a value or attributes']
    }
    assert run_custom_checks(ftl_entity, "", "key = translation") == {}


def test_ftl_non_localizable_entries(get_entity_mock):
    """Non-localizable entries are not allowed"""
    assert run_custom_checks(
        get_entity_mock("fluent", string="key = value"), "", "[[foo]]"
    ) == {"pErrors": ["Expected an entry start"]}


def test_ftl_id_missmatch(get_entity_mock):
    """ID of the source string and translation must be the same"""
    assert run_custom_checks(
        get_entity_mock("fluent", string="key = value"), "", "key1 = translation"
    ) == {"pErrors": ["Translation key needs to match source string key"]}
