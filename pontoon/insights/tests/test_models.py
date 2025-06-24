import pytest

from pontoon.base.models import Locale
from pontoon.insights.models import LocaleInsightsSnapshot


@pytest.mark.django_db
def test_missing_strings_property_locale_snapshot():
    snapshot = LocaleInsightsSnapshot.objects.create(
        locale=Locale.objects.create(code="locale-code", name="Locale Name"),
        total_strings=100,
        approved_strings=40,
        pretranslated_strings=20,
        strings_with_errors=5,
        strings_with_warnings=10,
        completion=0.4,
    )

    expected_missing = 100 - 40 - 20 - 5 - 10
    assert snapshot.missing_strings == expected_missing
