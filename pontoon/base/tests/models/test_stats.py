"""
Test consistency of calculations between `calculate_stats` and `translation.save()`.
"""
import pytest
from pontoon.base.models import TranslatedResource
from pontoon.checks.models import (
    Error,
    Warning,
)


@pytest.fixture
def translation_with_error(translation_a):
    Error.objects.create(translation=translation_a, library="p", message="error")
    return translation_a


@pytest.fixture
def translation_with_warning(translation_a):
    Warning.objects.create(
        translation=translation_a, library="p", message="warning",
    )
    return translation_a


def recalculate_stats(translation):
    """
    Make the full recalculate stats on a TranslatedResource.
    """
    translation.save(update_stats=False)
    translated_resource = TranslatedResource.objects.get(
        resource=translation.entity.resource, locale=translation.locale,
    )
    translated_resource.calculate_stats()


def diff_stats(t):
    """
    Update only necessary stats by calculating difference between stats.
    """
    t.save()


@pytest.fixture(params=(recalculate_stats, diff_stats,))
def stats_update(db, request):
    """
    Wrapper fixture which allows to test both implementations of stats calculations.
    """
    return request.param


@pytest.fixture
def get_stats():
    def f(translation):
        return TranslatedResource.objects.filter(
            resource=translation.entity.resource, locale=translation.locale,
        ).aggregated_stats()

    return f


def test_translation_approved(stats_update, get_stats, translation_a):
    translation_a.approved = True
    stats_update(translation_a)

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 1,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.approved = False
    stats_update(translation_a)

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


def test_translation_fuzzy(stats_update, get_stats, translation_a):
    translation_a.fuzzy = True
    stats_update(translation_a)

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 1,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.fuzzy = False
    translation_a.rejected = True
    stats_update(translation_a)

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }


def test_translation_with_error(stats_update, get_stats, translation_with_error):
    translation_with_error.approved = True
    stats_update(translation_with_error)

    assert get_stats(translation_with_error) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_with_error.approved = False
    translation_with_error.fuzzy = True
    stats_update(translation_with_error)

    assert get_stats(translation_with_error) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_with_error.fuzzy = False
    stats_update(translation_with_error)

    assert get_stats(translation_with_error) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


def test_translation_with_warning(stats_update, get_stats, translation_with_warning):
    translation_with_warning.approved = True
    stats_update(translation_with_warning)

    assert get_stats(translation_with_warning) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_with_warning.approved = False
    translation_with_warning.fuzzy = True
    stats_update(translation_with_warning)

    assert get_stats(translation_with_warning) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_with_warning.fuzzy = False
    stats_update(translation_with_warning)

    assert get_stats(translation_with_warning) == {
        "total": 1,
        "approved": 0,
        "fuzzy": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }
