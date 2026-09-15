from textwrap import dedent

import pytest

from moz.l10n.formats.fluent import fluent_parse_entry

from pontoon.terminology.models import Term, TermTranslation
from pontoon.terminology.utils import (
    get_all_message_text,
    get_terms_for_text,
    join_text_fragments,
)
from pontoon.test.factories import LocaleFactory


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


def test_join_text_fragments():
    assert join_text_fragments(["Open a tab", "Close a tab", "Open a tab"]) == (
        "Open a tab\nClose a tab"
    )


@pytest.mark.django_db
def test_get_terms_for_text():
    locale = LocaleFactory(code="kg", name="Klingon")
    term_open = Term.objects.create(
        text="open", part_of_speech="verb", definition="Allow access"
    )
    Term.objects.create(text="close", part_of_speech="verb", definition="Block access")

    TermTranslation.objects.create(term=term_open, locale=locale, text="odpri")

    terms = get_terms_for_text(locale, "Open a new tab.")

    assert [term.text for term in terms] == ["open"]
    assert [t.text for t in terms[0].filtered_translations] == ["odpri"]


@pytest.mark.django_db
def test_get_terms_for_text_translation_in_other_locale():
    locale = LocaleFactory(code="kg", name="Klingon")
    other_locale = LocaleFactory(code="gs", name="Geonosian")
    term = Term.objects.create(
        text="open", part_of_speech="verb", definition="Allow access"
    )
    TermTranslation.objects.create(term=term, locale=other_locale, text="opena")

    terms = get_terms_for_text(locale, "Open a new tab.")

    assert terms[0].filtered_translations == []


@pytest.mark.django_db
def test_get_terms_for_text_no_match_across_fragments():
    locale = LocaleFactory(code="kg", name="Klingon")
    Term.objects.create(text="new tab", part_of_speech="noun", definition="A fresh tab")

    text = join_text_fragments(["Open a new", "tab in the background"])
    assert get_terms_for_text(locale, text) == []

    text = join_text_fragments(["Open a new tab", "in the background"])
    assert [term.text for term in get_terms_for_text(locale, text)] == ["new tab"]
