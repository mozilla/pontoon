from unittest.mock import patch, call

import pytest

from pontoon.base.models import TranslationMemoryEntry
from pontoon.test.factories import TranslationMemoryFactory


@pytest.fixture
def tm_entry_long():
    return TranslationMemoryFactory.create(source=u"a" * 500,)


@pytest.fixture
def tm_entry_medium():
    return TranslationMemoryFactory.create(source=u"a" * 255,)


@pytest.fixture
def tm_entry_short():
    return TranslationMemoryFactory.create(source=u"a" * 50,)


@pytest.mark.django_db
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.postgres_levenshtein_ratio")
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.python_levenshtein_ratio")
def test_levenshtein_ratio_string_below_255_chars(
    python_mock, postgresql_mock, tm_entry_short
):
    TranslationMemoryEntry.objects.minimum_levenshtein_ratio(tm_entry_short.source,)

    assert not python_mock.called
    assert postgresql_mock.call_args == call(tm_entry_short.source, 0.7, 35, 71,)


@pytest.mark.django_db
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.postgres_levenshtein_ratio")
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.python_levenshtein_ratio")
def test_levenshtein_ratio_string_equals_255_chars(
    python_mock, postgresql_mock, tm_entry_medium
):
    TranslationMemoryEntry.objects.minimum_levenshtein_ratio(tm_entry_medium.source,)

    assert not postgresql_mock.called
    assert python_mock.call_args == call(tm_entry_medium.source, 0.7, 179, 364,)


@pytest.mark.django_db
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.postgres_levenshtein_ratio")
@patch("pontoon.base.models.TranslationMemoryEntryQuerySet.python_levenshtein_ratio")
def test_levenshtein_ratio_string_above_255_chars(
    python_mock, postgresql_mock, tm_entry_long
):
    TranslationMemoryEntry.objects.minimum_levenshtein_ratio(tm_entry_long.source,)

    assert not postgresql_mock.called
    assert python_mock.call_args == call(tm_entry_long.source, 0.7, 350, 714,)


@pytest.mark.django_db
def test_levenshtein_ratio_both_implementations(tm_entry_short):
    """
    Check if postgresql and postgresql return the same results for strings lower than 255.
    """
    postgresql_queryset = list(
        TranslationMemoryEntry.objects.postgres_levenshtein_ratio(
            tm_entry_short.source, 0.7, 35, 71,
        ).values_list("pk", "source", "target", "quality")
    )

    python_queryset = list(
        TranslationMemoryEntry.objects.python_levenshtein_ratio(
            tm_entry_short.source, 0.7, 35, 71,
        ).values_list("pk", "source", "target", "quality")
    )

    expected_results = [
        (tm_entry_short.pk, tm_entry_short.source, tm_entry_short.target, 100),
    ]
    assert postgresql_queryset == expected_results
    assert python_queryset == expected_results


@pytest.mark.django_db
def test_levenshtein_ratio_python_with_too_long_string(tm_entry_long):
    python_results = list(
        TranslationMemoryEntry.objects.python_levenshtein_ratio(
            tm_entry_long.source, 0.7, 350, 714,
        ).values_list("pk", "source", "target", "quality")
    )
    expected_results = [
        (tm_entry_long.pk, tm_entry_long.source, tm_entry_long.target, 100),
    ]
    assert python_results == expected_results
