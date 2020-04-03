from __future__ import absolute_import

import pytest

from pontoon.terminology.models import Term
from pontoon.test.factories import TermFactory, TermTranslationFactory


@pytest.fixture
def available_terms():
    """This fixture provides:

    - 4 generic terms
    - 6 terms to be used for matching in strings
    """
    for i in range(0, 4):
        TermFactory.create(text="term%s" % i)

    TermFactory.create(text="abnormality")
    TermFactory.create(text="student ambassador")
    TermFactory.create(text="track")
    TermFactory.create(text="sensitive")
    TermFactory.create(text="surf")
    TermFactory.create(text="Channel", case_sensitive=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "string, found_terms",
    [
        (
            "Mozilla detected a serious abnormality in its internal data",
            ["abnormality"],
        ),
        ("Join us as a student ambassador", ["student ambassador"]),
        ("Block third-party content that tracks you around the web", ["track"]),
        ("So avoid sensitive activities when surfing in public", ["sensitive", "surf"]),
        ("You are currently on the Firefox release Channel", ["Channel"]),
        ("You are currently on the Firefox release channel", []),
    ],
)
def test_terms_for_string(string, found_terms, available_terms):
    """
    Find available terms in the given string.
    """
    terms = Term.objects.for_string(string)
    assert len(terms) == len(found_terms)

    for i, term in enumerate(terms):
        term.text = found_terms[i]


@pytest.mark.django_db
def test_term_translation(locale_a):
    """
    Find locale translation of the given term.
    """
    term = TermFactory.create(text="term")
    assert term.translation(locale_a) is None

    TermTranslationFactory.create(
        locale=locale_a, term=term, text="translation",
    )
    assert term.translation(locale_a) == "translation"

    do_not_translate = TermFactory.create(text="term", do_not_translate=True)
    assert do_not_translate.translation(locale_a) == "term"
