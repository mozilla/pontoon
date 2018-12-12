"""
Test consistency of calculations between `calculate_stats` and `translation.save()`.
"""
import pytest
from pontoon.base.models import TranslatedResource

def recalculate_stats(translation):
    translation.save(update_stats=False)
    translated_resource = TranslatedResource.objects.get(
        resource=translation.entity.resource,
        locale=translation.locale,
    )
    translated_resource.calculate_stats()

def diff_stats(t):
    t.save()

@pytest.fixture(
    params=(
        recalculate_stats,
        diff_stats,
    )
)
def stats_update(db, request):
    return request.param

@pytest.fixture
def get_stats():
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

def test_translation_fuzzy(stats_update):
    assert False

def test_translation_with_errors(stats_update):
    assert False

def test_translation_with_warnings(stats_update):
    assert False

def test_translation_unreviewed(stats_update):
    assert False

def test_plural_translation_approved(stats_update):
    assert False

def test_plural_translation_fuzzy(stats_update):
    assert False

def test_plural_translation_with_errors(stats_update):
    assert False

def test_plural_translation_with_warnings(stats_update):
    assert False

def test_plural_translation_unreviewed(stats_update):
    assert False