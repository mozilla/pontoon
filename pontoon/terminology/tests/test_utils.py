from textwrap import dedent

from moz.l10n.formats.fluent import fluent_parse_entry

from pontoon.terminology.utils import get_all_message_text


def test_all_message_text():
    entry = fluent_parse_entry(
        dedent("""\
            warning =
                .heading = Heads up!
                .message = { $count ->
                    [one] One tracker blocked
                   *[other] Trackers blocked
                }
                .duplicate = Trackers blocked
            """),
        with_linepos=False,
    )

    messages = [entry.value, *entry.properties.values()]
    assert get_all_message_text(messages) == (
        "Heads up!\nOne tracker blocked\nTrackers blocked"
    )


def test_all_message_text_simple():
    entry = fluent_parse_entry("message = Simple string", with_linepos=False)

    assert get_all_message_text([entry.value]) == "Simple string"


def test_all_message_text_excludes_placeholders():
    entry = fluent_parse_entry(
        "message = Welcome to { -brand-name }, { $user }!", with_linepos=False
    )

    # Placeholders are left out, and the surrounding text is not joined into a
    # single line, so that terms are not matched across a placeholder.
    assert get_all_message_text([entry.value]) == "Welcome to \n, \n!"
