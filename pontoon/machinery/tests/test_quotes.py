import pytest

from pontoon.machinery.fix_quotes import fix_quotes
from pontoon.test.factories import LocaleFactory


@pytest.mark.django_db
def test_quotes_html_english():
    locale = LocaleFactory(code="en-XX")
    res = fix_quotes("&quot; foo &quot;", locale)
    assert res == "“foo”"


@pytest.mark.django_db
def test_quotes_guillemets_french():
    locale = LocaleFactory(code="fr-XX")
    res = fix_quotes("«foo»", locale)
    assert res == "«\u202ffoo\u202f»"
