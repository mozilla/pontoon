import pytest

from pontoon.checks.libraries.pontoon_db import run_checks
from unittest.mock import MagicMock


@pytest.fixture()
def get_entity_mock():
    """
    Create an entity mock with comment, resource.path and extension.
    """

    def _f(extension, comment="", string="", allows_empty_translations=False):
        entity = MagicMock()
        entity.comment = comment
        entity.string = string
        entity.resource.format = extension
        entity.resource.path = "test." + extension
        entity.resource.allows_empty_translations = allows_empty_translations
        return entity

    yield _f


def test_ending_newline(get_entity_mock):
    """
    Original and translation in a PO file must either both end
    in a newline, or none of them should.
    """
    assert run_checks(get_entity_mock("po"), "Original", "Translation\n") == {
        "pErrors": ["Ending newline mismatch"]
    }

    assert run_checks(get_entity_mock("po"), "Original\n", "Translation") == {
        "pErrors": ["Ending newline mismatch"]
    }

    assert run_checks(get_entity_mock("po"), "Original\n", "Translation\n") == {}

    assert run_checks(get_entity_mock("po"), "Original", "Translation") == {}


def test_empty_translations(get_entity_mock):
    """
    Empty translations shouldn't be allowed for some extensions.
    """
    assert run_checks(get_entity_mock("po"), "", "") == {
        "pErrors": ["Empty translations are not allowed"]
    }

    assert run_checks(
        get_entity_mock("ftl", string="key = value"), "", 'key = { "" }'
    ) == {"pndbWarnings": ["Empty translation"]}

    assert (
        run_checks(get_entity_mock("ftl", string="key = value"), "", 'key = { "x" }')
        == {}
    )

    assert run_checks(
        get_entity_mock("ftl", string="key =\n  .attr = value"),
        "",
        """key =
              { $var ->
                  [a] { "" }
                 *[b] { "" }
              }
              .attr = { "" }
            """,
    ) == {"pndbWarnings": ["Empty translation"]}

    assert run_checks(
        get_entity_mock("ftl", string="key =\n  .attr = value"),
        "",
        """key =
              { $var ->
                  [a] { "x" }
                 *[b] { "y" }
              }
              .attr = { "" }
            """,
    ) == {"pndbWarnings": ["Empty translation"]}

    assert run_checks(
        get_entity_mock("ftl", string="key =\n  .attr = value"),
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
        run_checks(
            get_entity_mock("ftl", string="key =\n  .attr = value"),
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
    assert run_checks(get_entity_mock("po"), "", "aaa\nbbb") == {}


def test_ftl_parse_error(get_entity_mock):
    """Invalid FTL strings are not allowed"""
    assert run_checks(get_entity_mock("ftl", string="key = value"), "", "key =") == {
        "pErrors": ['Expected message "key" to have a value or attributes']
    }

    assert (
        run_checks(
            get_entity_mock("ftl", string="key = value"), "", "key = translation"
        )
        == {}
    )


def test_ftl_non_localizable_entries(get_entity_mock):
    """Non-localizable entries are not allowed"""
    assert run_checks(get_entity_mock("ftl", string="key = value"), "", "[[foo]]") == {
        "pErrors": ["Expected an entry start"]
    }


def test_ftl_id_missmatch(get_entity_mock):
    """ID of the source string and translation must be the same"""
    assert run_checks(
        get_entity_mock("ftl", string="key = value"), "", "key1 = translation"
    ) == {"pErrors": ["Translation key needs to match source string key"]}
