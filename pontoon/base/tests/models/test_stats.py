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
    Error.objects.create(
        translation=translation_a,
        library='p',
        message='error'
    )
    return translation_a


@pytest.fixture
def translation_with_warning(translation_a):
    Warning.objects.create(
        translation=translation_a,
        library='p',
        message='warning',
    )
    return translation_a


def recalculate_stats(translation):
    """
    Make the full recalculate stats on a TranslatedResource.
    """
    translation.save(update_stats=False)
    translated_resource = TranslatedResource.objects.get(
        resource=translation.entity.resource,
        locale=translation.locale,
    )
    translated_resource.calculate_stats()


def diff_stats(t):
    """
    Update only necessary stats by calculating difference between stats.
    """
    t.save()


@pytest.fixture(
    params=(
        recalculate_stats,
        diff_stats,
    )
)
def stats_update(db, request):
    """
    Wrapper fixture which allows to test both implementations of stats calculations.
    """
    return request.param


@pytest.fixture
def get_stats():
    """
    Fixture wrapper for function to get_stats of a TranslatedResource assigned to a translation.
    """
    def f(translation):
        return TranslatedResource.objects.stats(
            translation.entity.resource.project,
            None,
            translation.locale,
        )
    return f


@pytest.fixture
def stats_dict():
    def f(**override_stats):
        stats = {
            'approved': 0,
            'fuzzy': 0,
            'total': 0,
            'unreviewed': 0,
            'warnings': 0,
            'errors': 0,
        }
        stats.update(override_stats)
        return stats
    return f


def test_translation_approved(stats_update, get_stats, stats_dict, user_a, translation_a):
    translation_a.approved = True
    stats_update(translation_a)

    assert get_stats(translation_a) == stats_dict(
        approved=1,
        total=1,
    )

    translation_a.unapprove(user_a, save=False)
    stats_update(translation_a)

    assert get_stats(translation_a) == stats_dict(
        unreviewed=1,
        total=1,
    )


def test_translation_fuzzy(stats_update, get_stats, stats_dict, user_a, translation_a):
    translation_a.fuzzy = True
    stats_update(translation_a)

    assert get_stats(translation_a) == stats_dict(
        fuzzy=1,
        total=1,
    )

    translation_a.reject(user_a, save=False)
    stats_update(translation_a)

    assert get_stats(translation_a) == stats_dict(
        total=1,
    )


def test_translation_with_error(stats_update, get_stats, stats_dict, translation_with_error):
    translation_with_error.approved = True
    stats_update(translation_with_error)

    assert get_stats(translation_with_error) == stats_dict(
        errors=1,
        total=1,
    )

    translation_with_error.fuzzy = True
    stats_update(translation_with_error)

    assert get_stats(translation_with_error) == stats_dict(
        errors=1,
        total=1,
    )


def test_translation_with_warning(stats_update, get_stats, stats_dict, translation_with_warning):
    translation_with_warning.approved = True
    stats_update(translation_with_warning)

    assert get_stats(translation_with_warning) == stats_dict(
        warnings=1,
        total=1,
    )

    translation_with_warning.fuzzy = True
    stats_update(translation_with_warning)

    assert get_stats(translation_with_warning) == stats_dict(
        warnings=1,
        total=1,
    )
