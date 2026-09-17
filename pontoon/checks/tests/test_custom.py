from unittest.mock import MagicMock

import pytest

from pontoon.checks.libraries.custom import run_custom_checks


def mock_entity(
    format: str,
    *,
    string: str = "",
    allows_empty_translations: bool = False,
):
    match format:
        case "android" | "xcode":
            ext = "xml"
        case "fluent":
            ext = "ftl"
        case "gettext":
            ext = "po"
        case "webext":
            ext = "json"
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
    po_entity = mock_entity("gettext", string="Original")
    assert run_custom_checks(po_entity, "Translation\n") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Translation") == {}

    po_entity.string = "Original\n"
    assert run_custom_checks(po_entity, "Translation") == {
        "pErrors": ["Ending newline mismatch"]
    }
    assert run_custom_checks(po_entity, "Translation\n") == {}


def test_empty_translations_allowed():
    """
    Empty translations should be allowed but noted for some extensions.
    """
    assert run_custom_checks(
        mock_entity("properties", allows_empty_translations=True), ""
    ) == {"pndbWarnings": ["Empty translation"]}


def test_empty_translations_not_allowed():
    """
    Empty translations shouldn't be allowed for some extensions.
    """
    po_entity = mock_entity("gettext")
    assert run_custom_checks(po_entity, "") == {"pErrors": empty_error}
    assert run_custom_checks(po_entity, "{{}}") == {"pErrors": empty_error}
    assert run_custom_checks(po_entity, ".input {$n :number} .match $n * {{}}") == {
        "pErrors": empty_error + plural_error
    }
    assert run_custom_checks(
        po_entity, ".input {$n :number} .match $n 1 {{}} * {{other}}"
    ) == {"pErrors": empty_error + plural_error}
    assert run_custom_checks(po_entity, "{{{||}}}") == {}

    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), 'key = { "" }'
    ) == {"pndbWarnings": ["Empty translation"]}

    assert (
        run_custom_checks(mock_entity("fluent", string="key = value"), 'key = { "x" }')
        == {}
    )

    assert run_custom_checks(
        mock_entity("fluent", string="key =\n  .attr = value"),
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
    assert run_custom_checks(mock_entity("android", string="source"), "target") == {}


def test_android_plural():
    assert (
        run_custom_checks(
            mock_entity(
                "android", string=".input {$n :number} .match $n one {{s1}} * {{s*}}"
            ),
            ".input {$n :number} .match $n one {{t1}} * {{t*}}",
        )
        == {}
    )

    assert run_custom_checks(
        mock_entity("android", string="source"),
        ".input {$n :number} .match $n one {{t1}} * {{t*}}",
    ) == {"pErrors": plural_error}


def test_po_newlines():
    assert run_custom_checks(mock_entity("gettext"), "aaa\nbbb") == {}


def test_ftl_parse_error():
    """Invalid FTL strings are not allowed"""
    ftl_entity = mock_entity("fluent", string="key = value")
    assert run_custom_checks(ftl_entity, "key =") == {
        "pErrors": ['Expected message "key" to have a value or attributes']
    }
    assert run_custom_checks(ftl_entity, "key = translation") == {}


def test_ftl_non_localizable_entries():
    """Non-localizable entries are not allowed"""
    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), "[[foo]]"
    ) == {"pErrors": ["Expected an entry start"]}


def test_ftl_id_missmatch():
    """ID of the source string and translation must be the same"""
    assert run_custom_checks(
        mock_entity("fluent", string="key = value"), "key1 = translation"
    ) == {"pErrors": ["Translation key needs to match source string key"]}


def test_android_apostrophes():
    original = "Source string"
    translation = "Translation with a straight '"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_percent_signs_same():
    original = "Source string 100%"
    translation = "Translation string 100%"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_percent_signs_more():
    original = "Source string 100%"
    translation = "Translation 100%! string 100%"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_literal_newline():
    original = "Source string"
    translation = r"Translation with an escaped \\n newline"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_same_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$s|}"
    translation = "Translation with a {$arg1 :string @source=|%1$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_plural_placeholders():
    original = """
        .input {$n :number}
        .match $n
        one {{One item}}
        * {{{$arg1 :number @source=|%1$d|} items}}
    """
    translation = """
        .input {$n :number}
        .match $n
        one {{{$arg1 :number @source=|%1$d|} item}}
        many {{{$arg1 :number @source=|%1$d|} items}}
        * {{{$arg1 :number @source=|%1$d|} items}}
    """
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_missing_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$s|}"
    translation = "Translation"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pWarnings": ["Placeholder %1$s not found in translation"]
    }


def test_android_mistyped_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$s|}"
    translation = "Translation %1"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %1 not found in reference"],
        "pWarnings": ["Placeholder %1$s not found in translation"],
    }


def test_android_extra_placeholder():
    original = "Source string"
    translation = "Translation with a {$arg1 :string @source=|%1$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %1$s not found in reference"]
    }


def test_android_extra_placeholder_as_literal():
    original = "Source string"
    translation = "Translation with a %1$s"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %1$s not found in reference"]
    }


def test_android_changed_placeholder():
    original = (
        "New! {$arg :string @source=|%s|} email masks are now available on mobile."
    )
    translation = "Нав! Акнун ниқобҳои почтаи электронии «{$arg1 :string @source=|%@|}» дар дастгоҳҳои мобилӣ дастрасанд."
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %@ not found in reference"],
        "pWarnings": ["Placeholder %s not found in translation"],
    }


def test_android_placeholder_in_element():
    """Source XML: Read the &lt;a href="%1$s"&gt;policy&lt;/a&gt;"""
    original = 'Read the <a href="{$arg1 :string @source=|%1$s|}">policy{|</a>| :html}'
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original) == {}


def test_android_changed_placeholder_in_element():
    """Source XML: Read the &lt;a href="%1$s"&gt;policy&lt;/a&gt;

    Translation XML: Leggi la &lt;a href="https://example.com"&gt;policy&lt;/a&gt;
    """
    original = 'Read the <a href="{$arg1 :string @source=|%1$s|}">policy{|</a>| :html}'
    translation = 'Leggi la <a href="https://example.com">policy{|</a>| :html}'
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ['Element <a href="https://example.com"> not found in reference'],
        "pWarnings": ['Element <a href="%1$s"> not found in translation'],
    }


def test_android_changed_placeholder_in_markup():
    """Source XML: Read the <a href="%1$s">policy</a>

    Translation XML: Leggi la <a href="https://example.com">policy</a>
    """
    original = "Read the {#a href=|%1$s|}policy{/a}"
    translation = "Leggi la {#a href=|https://example.com|}policy{/a}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ['Element <a href="https://example.com"> not found in reference'],
        "pWarnings": ['Element <a href="%1$s"> not found in translation'],
    }


@pytest.mark.parametrize(
    "original",
    [
        # Placeholders in Android tag attributes stay inside the markup token.
        "Hi {$arg :string @source=|%s|} {#a href=|%s|}link{/a}",
        "{#a href=|%s|}{$arg :string @source=|%s|}{/a}",
    ],
)
def test_android_unnumbered_placeholder_in_markup_attribute(original):
    """Source XML: Hi %s <a href="%s">link</a>

    Source XML: <a href="%s">%s</a>
    """
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original) == {}


def test_android_extra_unnumbered_placeholder_with_markup_attribute():
    """Source XML: Hi %s <a href="%s">link</a>

    Translation XML: Hi %s %s <a href="%s">link</a>
    """
    original = "Hi {$arg :string @source=|%s|} {#a href=|%s|}link{/a}"
    translation = (
        "Hi {$arg :string @source=|%s|} {$arg2 :string @source=|%s|} "
        "{#a href=|%s|}link{/a}"
    )
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": [
            "Placeholder %s has more occurrences in translation (expected 2, found 3)"
        ]
    }


def test_android_paired_element_in_text():
    """Source XML: Read the <b>policy</b>"""
    original = "Read the {#b}policy{/b}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, "Leggi la {#b}policy{/b}") == {}
    checks = run_custom_checks(entity, "Leggi la policy")
    assert sorted(checks["pWarnings"]) == [
        "Element </b> not found in translation",
        "Element <b> not found in translation",
    ]


def test_android_literal_angle_brackets():
    """Escaped brackets around a non-element word are literal text.

    Source XML: Press &lt;Enter&gt; to continue
    """
    entity = mock_entity("android", string="Press {|<Enter>| :html} to continue")
    assert run_custom_checks(entity, "Premi {|<Invio>| :html} per continuare") == {}
    assert run_custom_checks(entity, "Premi Invio per continuare") == {}


def test_android_literal_element_name():
    """A bare tag is literal text even when it names a real HTML element.

    Source XML: Type &lt;br&gt; for a break
    """
    entity = mock_entity("android", string="Type {|<br>| :html} for a break")
    assert run_custom_checks(entity, "Digita per andare a capo") == {}
    assert run_custom_checks(entity, "Digita {|<br>| :html} per andare a capo") == {}


def test_android_escaped_element_pair():
    """Escaped brackets that pair up are markup, whatever they're named.

    Source XML: &lt;myTag&gt;text&lt;/myTag&gt;
    """
    entity = mock_entity("android", string="{|<myTag>| :html}text{|</myTag>| :html}")
    assert run_custom_checks(entity, "{|<myTag>| :html}testo{|</myTag>| :html}") == {}
    checks = run_custom_checks(entity, "testo")
    assert sorted(checks["pWarnings"]) == [
        "Element </myTag> not found in translation",
        "Element <myTag> not found in translation",
    ]


def test_android_escaped_element_with_attributes():
    """A tag with attributes is markup even if its name is unknown.

    Source XML: &lt;myTag id="1"&gt;text&lt;/myTag&gt;
    """
    entity = mock_entity(
        "android", string='{|<myTag id="1">| :html}text{|</myTag>| :html}'
    )
    assert run_custom_checks(entity, "testo") == {
        "pWarnings": [
            "Element </myTag> not found in translation",
            'Element <myTag id="1"> not found in translation',
        ]
    }


def test_android_mismatched_elements_in_text():
    """Tags that don't pair up are markup, whatever they're named.

    Translation XML: &lt;foo&gt;testo&lt;/bar&gt;
    """
    entity = mock_entity("android", string="text")
    checks = run_custom_checks(entity, "{|<foo>| :html}testo{|</bar>| :html}")
    assert sorted(checks["pErrors"]) == [
        "Element </bar> not found in reference",
        "Element <foo> not found in reference",
    ]


def test_android_stray_angle_brackets():
    """Source XML: 5 &lt; 10 and x &gt; y"""
    entity = mock_entity("android", string="5 {|< 10 and x >| :html} y")
    assert run_custom_checks(entity, "5 {|< 10 e x >| :html} y") == {}


def test_xcode_literal_angle_brackets():
    """Unlike Android, xliff keeps escaped brackets as literal text.

    Source XLIFF: Press &lt;Enter&gt; to continue
    """
    entity = mock_entity("xcode", string="Press <Enter> to continue")
    assert run_custom_checks(entity, "Premi <Invio> per continuare") == {}


def test_android_protections_with_shared_substring():
    """Source XML:
    Hi <xliff:g id="a">Name</xliff:g> and <xliff:g id="b">FullName</xliff:g>
    """
    original = (
        "Hi {$a :xliff:g id=a @translate=no @source=Name} "
        "and {$b :xliff:g id=b @translate=no @source=FullName}"
    )
    entity = mock_entity("android", string=original)
    checks = run_custom_checks(entity, "Salve")
    assert list(checks) == ["pWarnings"]
    assert sorted(checks["pWarnings"]) == [
        "Placeholder FullName not found in translation",
        "Placeholder Name not found in translation",
    ]


def test_android_multi_digit_placeholder():
    """Source XML: Hi %10$s and %2$s"""
    original = "Hi {$a :string @source=|%10$s|} and {$b :string @source=|%2$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, original) == {}


def test_android_changed_multi_digit_placeholder():
    """Source XML: Hi %10$s and %2$s

    Translation XML: Ciao %11$s e %2$s
    """
    original = "Hi {$a :string @source=|%10$s|} and {$b :string @source=|%2$s|}"
    translation = "Ciao {$a :string @source=|%11$s|} e {$b :string @source=|%2$s|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %11$s not found in reference"],
        "pWarnings": ["Placeholder %10$s not found in translation"],
    }


def test_android_protection_matching_element_text():
    """Source XML:
    Hi <xliff:g id="a">Name</xliff:g>, see &lt;a title="Name"&gt;link&lt;/a&gt;
    """
    original = (
        "Hi {$a :xliff:g id=a @translate=no @source=Name}, "
        'see {|<a title="Name">| :html}link{|</a>| :html}'
    )
    translation = 'Ciao, vedi {|<a title="Name">| :html}link{|</a>| :html}'
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pWarnings": ["Placeholder Name not found in translation"]
    }


def test_android_protections():
    original = "Source {$string :xliff:g id=string @translate=no @source=String} with {$variable :xliff:g id=variable example=5 @translate=no @source=|%1$s|}"
    translation = "Translation String with %1$s"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pWarnings": ["Placeholder String not found in translation"]
    }


def test_android_good_html():
    original = "Source with a {|<b>| :html}line{|<br>| :html}break{|</b>| :html}"
    translation = (
        "Translation with a {|<b>| :html}line{|<br>| :html}break{|</b>| :html}"
    )
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_good_html_as_markup():
    """Source XML: Source with a <b>line<br/>break</b>"""
    original = "Source with a {#b}line{#br}{/br}break{/b}"
    translation = "Translation with a {#b}line{#br}{/br}break{/b}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_android_bad_html():
    original = "Source {|<b>| :html}string{|</b>| :html}"
    translation = "Translation with a {|<a>| :html}tag mismatch{|</b>| :html}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Element <a> not found in reference"],
        "pWarnings": ["Element <b> not found in translation"],
    }


def test_android_extra_percent():
    original = "Source percent"
    translation = "Translation {|%| @source=|%%|}"
    entity = mock_entity("android", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_webext_literal_index_placeholder_as_placeholder():
    original = "Source string with a {$arg1 @source=|$1|}"
    translation = "Translation with a {$arg1 @source=|$1|}"
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_webext_literal_index_placeholder_as_literal():
    original = "Source string with a {$arg1 @source=|$1|}"
    translation = "Translation with a $1"
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_webext_literal_named_placeholder_as_placeholder():
    original = (
        ".local $FOO = {$arg1 @source=|$1|}\n"
        + "{{Source string with a {$FOO @source=|$FOO$|}}}"
    )
    translation = (
        ".local $FOO = {$arg1 @source=|$1|}\n"
        + "{{Translation with a {$FOO @source=|$FOO$|}}}"
    )
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_webext_literal_named_placeholder_as_literal():
    original = (
        ".local $FOO = {$arg1 @source=|$1|}\n"
        + "{{Source string with a {$FOO @source=|$FOO$|}}}"
    )
    translation = "Translation with a $FOO$"
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_webext_extra_index_placeholder():
    original = "Source string"
    translation = "Translation with a $1"
    entity = mock_entity("webext", string=original)
    # This should probably also be caught
    assert run_custom_checks(entity, translation) == {}


def test_webext_extra_named_placeholder_as_literal():
    original = "Source string"
    translation = "Translation with a $FOO$"
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder $FOO$ not found in reference"]
    }


def test_webext_extra_named_placeholder_as_placeholder():
    original = "Source string"
    translation = (
        ".local $FOO = {$arg1 @source=|$1|}\n"
        + "{{Translation with a {$FOO @source=|$FOO$|}}}"
    )
    entity = mock_entity("webext", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder $FOO$ not found in reference"]
    }


def test_xcode_same_placeholder():
    original = "Source string with a {$arg1 :string @source=|%1$@|}"
    translation = "Translation with a {$arg1 :string @source=|%1$@|}"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_xcode_missing_placeholder():
    original = "Source string with a {$arg :string @source=|%@|}"
    translation = "Translation"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pWarnings": ["Placeholder %@ not found in translation"]
    }


def test_xcode_mistyped_placeholder():
    original = "Source string with a {$arg :string @source=|%@|}"
    translation = "Translation % @"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder % @ not found in reference"],
        "pWarnings": ["Placeholder %@ not found in translation"],
    }


def test_xcode_extra_placeholder():
    original = "Source string"
    translation = "Translation with a {$arg :string @source=|%@|}"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ["Placeholder %@ not found in reference"]
    }


def test_xcode_html():
    """Source XLIFF: Read the &lt;b&gt;policy&lt;/b&gt;"""
    original = "Read the <b>policy</b>"
    translation = "Leggi la <b>policy</b>"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_xcode_placeholder_in_element():
    """Source XLIFF: Read the &lt;a href="%1$@"&gt;policy&lt;/a&gt;"""
    original = 'Read the <a href="{$arg1 :string @source=|%1$@|}">policy</a>'
    translation = 'Leggi la <a href="{$arg1 :string @source=|%1$@|}">policy</a>'
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {}


def test_xcode_changed_placeholder_in_element():
    """Source XLIFF: Read the &lt;a href="%1$@"&gt;policy&lt;/a&gt;

    Translation XLIFF: Leggi la &lt;a href="https://example.com"&gt;policy&lt;/a&gt;
    """
    original = 'Read the <a href="{$arg1 :string @source=|%1$@|}">policy</a>'
    translation = 'Leggi la <a href="https://example.com">policy</a>'
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ['Element <a href="https://example.com"> not found in reference'],
        "pWarnings": ['Element <a href="%1$@"> not found in translation'],
    }


def test_xcode_changed_placeholder_in_markup():
    """Source XLIFF: Read the <a href="%1$@">policy</a>

    Translation XLIFF: Leggi la <a href="https://example.com">policy</a>
    """
    original = "Read the {#a href=|%1$@|}policy{/a}"
    translation = "Leggi la {#a href=|https://example.com|}policy{/a}"
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pErrors": ['Element <a href="https://example.com"> not found in reference'],
        "pWarnings": ['Element <a href="%1$@"> not found in translation'],
    }


def test_xcode_placeholder_in_and_outside_element():
    """Source XLIFF: Visit &lt;a href="%@"&gt;%@&lt;/a&gt; for details

    Translation XLIFF: Click &lt;a href="%@"&gt;here&lt;/a&gt; for details
    """
    original = (
        'Visit <a href="{$arg1 :string @source=|%@|}">'
        "{$arg2 :string @source=|%@|}</a> for details"
    )
    translation = 'Click <a href="{$arg1 :string @source=|%@|}">here</a> for details'
    entity = mock_entity("xcode", string=original)
    assert run_custom_checks(entity, translation) == {
        "pWarnings": ["Placeholder %@ not found in translation"]
    }


@pytest.mark.parametrize(
    "format, placeholder",
    [("xcode", "%@"), ("android", "%s"), ("android", "%02d"), ("xcode", "%#x")],
)
@pytest.mark.parametrize("count", [0, 1, 2])
def test_repeated_unnumbered_placeholder(format, placeholder, count):
    """Source XLIFF: Hello %@ and %@ (or %#x); Source XML: Hello %s and %s (or %02d)

    Translation: Hello / Hello %@ / Hello %@ and %@
    """
    first = "{$arg1 :string @source=|" + placeholder + "|}"
    second = "{$arg2 :string @source=|" + placeholder + "|}"
    entity = mock_entity(format, string=f"Hello {first} and {second}")
    translation = "Hello " + " and ".join([first, second][:count])
    expected = {}
    if count == 0:
        expected = {
            "pWarnings": [f"Placeholder {placeholder} not found in translation"]
        }
    elif count == 1:
        expected = {
            "pWarnings": [
                f"Placeholder {placeholder} has fewer occurrences in translation "
                "(expected 2, found 1)"
            ]
        }
    assert run_custom_checks(entity, translation) == expected


@pytest.mark.parametrize(
    "format, placeholder",
    [
        ("xcode", "%1$@"),
        ("android", "%1$s"),
        ("xcode", "%#@items@"),
    ],
)
def test_repeated_reusable_placeholder(format, placeholder):
    """Source XLIFF: Hello %1$@ and %1$@ (or %#@items@); Source XML: Hello %1$s and %1$s

    Translation: Hello %1$@
    """
    argument = "{$arg1 :string @source=|" + placeholder + "|}"
    entity = mock_entity(format, string=f"Hello {argument} and {argument}")
    assert run_custom_checks(entity, f"Hello {argument}") == {}


def test_repeated_unnumbered_placeholder_outside_element():
    """Source XLIFF: &lt;a href="%@"&gt;%@ and %@&lt;/a&gt;

    Translation XLIFF: &lt;a href="%@"&gt;%@&lt;/a&gt;
    """
    element = '<a href="{$arg1 :string @source=|%@|}">'
    first = "{$arg2 :string @source=|%@|}"
    second = "{$arg3 :string @source=|%@|}"
    entity = mock_entity("xcode", string=f"{element}{first} and {second}</a>")
    assert run_custom_checks(entity, f"{element}{first}</a>") == {
        "pWarnings": [
            "Placeholder %@ has fewer occurrences in translation (expected 3, found 2)"
        ]
    }


@pytest.mark.parametrize("missing", [False, True])
def test_repeated_unnumbered_placeholder_plural_variants(missing):
    """Source XML: <plurals> with "For %s and %s" for quantity one and other

    Translation XML: <plurals> with "For %s" (missing) or "For %s and %s" for
    quantity one, few and other
    """
    first = "{$arg1 :string @source=|%s|}"
    second = "{$arg2 :string @source=|%s|}"
    original = (
        ".input {$n :number} .match $n "
        "one {{For " + first + " and " + second + "}} "
        "* {{For " + first + " and " + second + "}}"
    )
    pattern = first if missing else first + " and " + second
    translation = (
        ".input {$n :number} .match $n "
        "one {{For " + pattern + "}} "
        "few {{For " + pattern + "}} "
        "* {{For " + pattern + "}}"
    )
    entity = mock_entity("android", string=original)
    expected = (
        {
            "pWarnings": [
                "Placeholder %s has fewer occurrences in translation "
                "(expected 2, found 1)"
            ]
        }
        if missing
        else {}
    )
    assert run_custom_checks(entity, translation) == expected


def test_repeated_unnumbered_placeholder_extra_occurrence():
    """Source XLIFF: Hello %@ and %@

    Translation XLIFF: Hello %@, %@ and %@
    """
    first = "{$arg1 :string @source=|%@|}"
    second = "{$arg2 :string @source=|%@|}"
    third = "{$arg3 :string @source=|%@|}"
    entity = mock_entity("xcode", string=f"Hello {first} and {second}")
    assert run_custom_checks(entity, f"Hello {first}, {second} and {third}") == {
        "pErrors": [
            "Placeholder %@ has more occurrences in translation (expected 2, found 3)"
        ]
    }


def test_repeated_unnumbered_placeholder_fewer_source_variants():
    """Translations can have fewer plural forms than the source.

    Source XML: <plurals> with "%s of %s" for quantity one and "%s items" for other

    Translation XML: <plurals> with "%s items" for quantity other
    """
    first = "{$arg1 :string @source=|%s|}"
    second = "{$arg2 :string @source=|%s|}"
    original = (
        ".input {$n :number} .match $n "
        "one {{" + first + " of " + second + "}} "
        "* {{" + first + " items}}"
    )
    entity = mock_entity("android", string=original)
    translation = ".input {$n :number} .match $n * {{" + first + " items}}"
    assert run_custom_checks(entity, translation) == {}


def test_unnumbered_placeholder_moved_outside_element():
    """Source XLIFF: &lt;a href="%@"&gt;%@&lt;/a&gt;

    Translation XLIFF: %@ %@
    """
    first = "{$arg1 :string @source=|%@|}"
    second = "{$arg2 :string @source=|%@|}"
    entity = mock_entity("xcode", string=f'<a href="{first}">{second}</a>')
    checks = run_custom_checks(entity, f"{first} {second}")
    assert list(checks) == ["pWarnings"]
    assert sorted(checks["pWarnings"]) == [
        "Element </a> not found in translation",
        'Element <a href="%@"> not found in translation',
    ]


@pytest.mark.parametrize("source_count, target_count", [(2, 1), (1, 2), (2, 2)])
def test_repeated_element_with_unnumbered_placeholder(source_count, target_count):
    """Source XLIFF: &lt;a href="%@"&gt;link&lt;/a&gt;, repeated source_count times

    Translation XLIFF: the same element, repeated target_count times
    """
    element = '<a href="{$arg1 :string @source=|%@|}">link</a>'
    entity = mock_entity("xcode", string=" ".join([element] * source_count))
    expected = {}
    if source_count != target_count:
        fewer = target_count < source_count
        direction = "fewer" if fewer else "more"
        expected = {
            "pWarnings" if fewer else "pErrors": [
                f"Placeholder %@ has {direction} occurrences in translation "
                f"(expected {source_count}, found {target_count})"
            ]
        }
    assert run_custom_checks(entity, " ".join([element] * target_count)) == expected


def test_missing_element_suppresses_unnumbered_placeholder_warning():
    """Source XLIFF: Read &lt;a href="%@"&gt;link&lt;/a&gt;

    Translation XLIFF: Read link&lt;/a&gt;
    """
    entity = mock_entity(
        "xcode", string='Read <a href="{$arg1 :string @source=|%@|}">link</a>'
    )
    assert run_custom_checks(entity, "Read link</a>") == {
        "pWarnings": ['Element <a href="%@"> not found in translation']
    }


@pytest.mark.parametrize("count", [1, 3])
def test_unnumbered_placeholder_mismatch_in_one_plural_variant(count):
    """Source stringsdict: "%@ %@" for one and other

    Translation stringsdict: "%@" or "%@ %@ %@" for one, "%@ %@" for other
    """
    argument = "{$arg1 :string @source=|%@|}"
    pair = argument + " " + argument
    original = ".input {$n :number} .match $n one {{" + pair + "}} * {{" + pair + "}}"
    changed = " ".join([argument] * count)
    translation = (
        ".input {$n :number} .match $n one {{" + changed + "}} * {{" + pair + "}}"
    )
    direction = "fewer" if count == 1 else "more"
    assert run_custom_checks(mock_entity("xcode", string=original), translation) == {
        "pWarnings" if count == 1 else "pErrors": [
            f"Placeholder %@ has {direction} occurrences in translation "
            f"(expected 2, found {count})"
        ]
    }


def test_missing_elements_in_different_source_variants():
    """Source stringsdict: &lt;a href="%@"&gt;link&lt;/a&gt; for one,
    &lt;a title="%@"&gt;link&lt;/a&gt; for other

    Translation stringsdict: link&lt;/a&gt; for other
    """
    argument = "{$arg1 :string @source=|%@|}"
    original = (
        '.input {$n :number} .match $n one {{<a href="'
        + argument
        + '">link</a>}} * {{<a title="'
        + argument
        + '">link</a>}}'
    )
    translation = ".input {$n :number} .match $n * {{link</a>}}"
    checks = run_custom_checks(mock_entity("xcode", string=original), translation)
    assert list(checks) == ["pWarnings"]
    assert sorted(checks["pWarnings"]) == [
        'Element <a href="%@"> not found in translation',
        'Element <a title="%@"> not found in translation',
    ]
