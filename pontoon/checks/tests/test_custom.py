from unittest.mock import MagicMock

from pontoon.checks.libraries.custom import run_custom_checks


def mock_entity(
    format: str,
    *,
    string: str = "",
    allows_empty_translations: bool = False,
):
    match format:
        case "android":
            ext = "xml"
        case "fluent":
            ext = "ftl"
        case "gettext":
            ext = "po"
        case _:
            ext = format
    entity = MagicMock()
    entity.string = string
    entity.resource.format = format
    entity.resource.path = f"test.{ext}"
    entity.resource.allows_empty_translations = allows_empty_translations
    return entity


empty_error = ["Empty translations are not allowed"]
plural_error = ["Plural translation requires plural source"]


def test_ending_newline():
    """
    Original and translation in a PO file must either both end
    in a newline, or none of them should.
    """
    po_entity = mock_entity("gettext")
    assert run_custom_checks(po_entity, "Original", "Translation\n") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Original\n", "Translation") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Original\n", "Translation\n") == {}
    assert run_custom_checks(po_entity, "Original", "Translation") == {}


def test_empty_translations_allowed():
    """
    Empty translations should be allowed but noted for some extensions.
    """
    assert run_custom_checks(
        mock_entity("properties", allows_empty_translations=True), "", ""
    ) == {"pndbWarnings": ["Empty translation"]}


def test_empty_translations_not_allowed():
    """
    Empty translations shouldn't be allowed for some extensions.
    """
    po_entity = mock_entity("gettext")
    assert run_custom_checks(po_entity, "", "") == {"pErrors": empty_error}
    assert run_custom_checks(po_entity, "", "{{}}") == {"pErrors": empty_error}
    assert run_custom_checks(po_entity, "", ".input {$n :number} .match $n * {{}}") == {
        "pErrors": empty_error + plural_error
    }
    assert run_custom_checks(
        po_entity, "", ".input {$n :number} .match $n 1 {{}} * {{other}}"
    ) == {"pErrors": empty_error + plural_error}
    assert run_custom_checks(po_entity, "", "{{{||}}}") == {}

    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), "", 'key = { "" }'
    ) == {"pndbWarnings": ["Empty translation"]}

    assert (
        run_custom_checks(
            mock_entity("fluent", string="key = value"), "", 'key = { "x" }'
        )
        == {}
    )

    assert run_custom_checks(
        mock_entity("fluent", string="key =\n  .attr = value"),
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
        mock_entity("fluent", string="key =\n  .attr = value"),
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
        mock_entity("fluent", string="key =\n  .attr = value"),
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
            mock_entity("fluent", string="key =\n  .attr = value"),
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


def test_android_simple():
    assert run_custom_checks(mock_entity("android"), "source", "target") == {}


def test_android_plural():
    assert (
        run_custom_checks(
            mock_entity("android"),
            ".input {$n :number} .match $n one {{s1}} * {{s*}}",
            ".input {$n :number} .match $n one {{t1}} * {{t*}}",
        )
        == {}
    )

    assert run_custom_checks(
        mock_entity("android"),
        "source",
        ".input {$n :number} .match $n one {{t1}} * {{t*}}",
    ) == {"pErrors": plural_error}


def test_po_newlines():
    assert run_custom_checks(mock_entity("gettext"), "", "aaa\nbbb") == {}


def test_ftl_parse_error():
    """Invalid FTL strings are not allowed"""
    ftl_entity = mock_entity("fluent", string="key = value")
    assert run_custom_checks(ftl_entity, "", "key =") == {
        "pErrors": ['Expected message "key" to have a value or attributes']
    }
    assert run_custom_checks(ftl_entity, "", "key = translation") == {}


def test_ftl_non_localizable_entries():
    """Non-localizable entries are not allowed"""
    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), "", "[[foo]]"
    ) == {"pErrors": ["Expected an entry start"]}


def test_ftl_id_missmatch():
    """ID of the source string and translation must be the same"""
    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), "", "key1 = translation"
    ) == {"pErrors": ["Translation key needs to match source string key"]}


def test_android_apostrophes():
    original = "Source string"
    translation = "Translation with a straight '"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original, translation) == {}


def test_android_same_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$s|}"
    translation = "Translation with a {$arg1 :string @source=|%1$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original, translation) == {}


def test_android_missing_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$s|}"
    translation = "Translation"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original, translation) == {
        "pndbWarnings": ["Placeholder %1$s not found in translation"]
    }


def test_android_extra_placeholder():
    original = "Source string"
    translation = "Translation with a {$arg1 :string @source=|%1$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original, translation) == {
        "pErrors": ["Placeholder %1$s not found in reference"]
    }


def test_android_extra_placeholder_as_literal():
    original = "Source string"
    translation = "Translation with a %1$s"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original, translation) == {
        "pErrors": ["Placeholder %1$s not found in reference"]
    }
