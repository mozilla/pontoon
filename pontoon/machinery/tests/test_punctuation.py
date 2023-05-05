import pytest

from pontoon.machinery.fix_punctuation import fix_punctuation
from pontoon.test.factories import LocaleFactory


@pytest.mark.django_db
def test_quotes_html_english():
    locale = LocaleFactory(code="en-XX")
    res = fix_punctuation("&quot; foo &quot;", locale)
    assert res == "“foo”"


@pytest.mark.django_db
def test_quotes_guillemets_french():
    locale = LocaleFactory(code="fr-XX")
    res = fix_punctuation("«foo»", locale)
    assert res == "«\u202ffoo\u202f»"


@pytest.mark.django_db
def test_parentheses():
    locale = LocaleFactory(code="en-XX")
    res = fix_punctuation("( foo )", locale)
    assert res == "(foo)"


@pytest.mark.django_db
def test_question_english():
    locale = LocaleFactory(code="en-XX")
    res = fix_punctuation("</foo> ?", locale)
    assert res == "</foo>?"


@pytest.mark.django_db
def test_question_french():
    locale = LocaleFactory(code="fr-FR")
    res = fix_punctuation("foo ?", locale)
    assert res == "foo\u202f?"
