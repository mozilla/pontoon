from unittest.mock import patch

import pytest

from pontoon.terminology.models import Term
from pontoon.test.factories import EntityFactory, TermFactory, TermTranslationFactory


@pytest.fixture
@patch("pontoon.terminology.models.update_terminology_project_stats")
def available_terms(_):
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


@pytest.fixture
@patch("pontoon.terminology.models.update_terminology_project_stats")
def localizable_term(_):
    """
    This fixture provides a localizable term.
    """
    return TermFactory.create(text="Localizable term")


@pytest.fixture
@patch("pontoon.terminology.models.update_terminology_project_stats")
def non_localizable_term(_):
    """
    This fixture provides a localizable term.
    """
    return TermFactory.create(text="Non-localizable term", do_not_translate=True,)


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
        assert term.text == found_terms[i]


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
def test_term_translation(_, locale_a):
    term = TermFactory.create(text="term")
    assert term.translation(locale_a) is None

    TermTranslationFactory.create(
        locale=locale_a, term=term, text="translation",
    )
    assert term.translation(locale_a) == "translation"

    do_not_translate = TermFactory.create(text="term", do_not_translate=True)
    assert do_not_translate.translation(locale_a) == "term"


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
def test_term_localizable(_):
    term_a = TermFactory.create(text="term A")
    assert term_a.localizable is True

    term_b = TermFactory.create(text="term B")
    term_b.do_not_translate = True
    assert term_b.localizable is False

    term_c = TermFactory.create(text="term C")
    term_c.forbidden = True
    assert term_c.localizable is False

    term_d = TermFactory.create(text="term D")
    term_d.definition = ""
    assert term_d.localizable is False


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
def test_term_entity_comment(_):
    term_a = TermFactory.create(
        text="term", part_of_speech=Term.PartOfSpeech.NOUN, definition="definition",
    )
    assert term_a.entity_comment() == "Noun. Definition."

    term_b = TermFactory.create(
        text="term",
        part_of_speech=Term.PartOfSpeech.NOUN,
        definition="definition",
        usage="usage",
    )
    assert term_b.entity_comment() == "Noun. Definition. E.g. Usage."


@pytest.mark.django_db
@patch("pontoon.terminology.models.Term.handle_term_create")
@patch("pontoon.terminology.models.Term.handle_term_update")
def test_term_save(handle_term_update_mock, handle_term_create_mock):
    # If term created and localizable, call handle_term_create()
    term_a = TermFactory.create()
    assert handle_term_create_mock.call_count == 1
    assert handle_term_update_mock.call_count == 0

    # If term updated, call handle_term_create()
    term_a.definition = "definition"
    term_a.save()
    assert handle_term_create_mock.call_count == 1
    assert handle_term_update_mock.call_count == 1

    # If term created and not localizable, do not call anything
    TermFactory.create(do_not_translate=True)
    assert handle_term_create_mock.call_count == 1
    assert handle_term_update_mock.call_count == 1


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_create(
    create_entity_mock, update_terminology_project_stats_mock, localizable_term,
):
    """
    handle_term_create() calls create_entity() and update_terminology_project_stats().
    """
    localizable_term.handle_term_create()
    assert create_entity_mock.called
    assert update_terminology_project_stats_mock.called


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.obsolete_entity")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_update_stays_non_localizable(
    create_entity_mock,
    obsolete_entity_mock,
    update_terminology_project_stats_mock,
    non_localizable_term,
):
    """
    Non-localizable Term updates that stay non-localizable don't require special handling.
    """
    non_localizable_term.case_sensitive = True
    non_localizable_term.handle_term_update()
    assert create_entity_mock.call_count == 0
    assert obsolete_entity_mock.call_count == 0
    assert update_terminology_project_stats_mock.call_count == 0


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.obsolete_entity")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_update_becomes_non_localizable(
    create_entity_mock,
    obsolete_entity_mock,
    update_terminology_project_stats_mock,
    localizable_term,
):
    """
    If localizable term becomes non-localizable, obsolete its Entity and update stats.
    """
    localizable_term.do_not_translate = True
    localizable_term.handle_term_update()
    assert create_entity_mock.call_count == 0
    assert obsolete_entity_mock.call_count == 1
    assert update_terminology_project_stats_mock.call_count == 1


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.obsolete_entity")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_update_becomes_localizable(
    create_entity_mock,
    obsolete_entity_mock,
    update_terminology_project_stats_mock,
    non_localizable_term,
):
    """
    If non-localizable term becomes localizable, create a corresponding Entity and update stats.
    """
    non_localizable_term.do_not_translate = False
    non_localizable_term.handle_term_update()
    assert create_entity_mock.call_count == 1
    assert obsolete_entity_mock.call_count == 0
    assert update_terminology_project_stats_mock.call_count == 1


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.obsolete_entity")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_update_text(
    create_entity_mock,
    obsolete_entity_mock,
    update_terminology_project_stats_mock,
    localizable_term,
):
    """
    If localizable term's text changes, a new Entity instance gets created,
    the previous one becomes obsolete, and the stats get updated.
    """
    localizable_term.text = "Changed text"
    localizable_term.handle_term_update()
    assert create_entity_mock.call_count == 1
    assert obsolete_entity_mock.call_count == 1
    assert update_terminology_project_stats_mock.call_count == 1


@pytest.mark.django_db
@patch("pontoon.terminology.models.update_terminology_project_stats")
@patch("pontoon.terminology.models.Term.obsolete_entity")
@patch("pontoon.terminology.models.Term.create_entity")
def test_handle_term_update_definition(
    create_entity_mock,
    obsolete_entity_mock,
    update_terminology_project_stats_mock,
    localizable_term,
):
    """
    If localizable term's part_of_speech, definition or usage change,
    Entity.comment gets updated and not other changes are made.
    """
    entity = EntityFactory()
    localizable_term.entity = entity
    localizable_term.definition = "Changed definition"
    localizable_term.handle_term_update()
    assert localizable_term.entity.comment == "Part_of_speech. Changed definition."
    assert create_entity_mock.call_count == 0
    assert obsolete_entity_mock.call_count == 0
    assert update_terminology_project_stats_mock.call_count == 0
