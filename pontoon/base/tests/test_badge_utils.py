import pytest

from pontoon.actionlog.models import ActionLog
from pontoon.base.badge_utils import badges_review_count
from pontoon.test.factories import TranslationFactory


def review(performed_by, translation, **kwargs):
    return ActionLog.objects.create(
        action_type=ActionLog.ActionType.TRANSLATION_APPROVED,
        performed_by=performed_by,
        translation=translation,
        **kwargs,
    )


@pytest.mark.django_db
def test_badges_review_count_counts_peer_reviews(user_a, user_b, entity_a, locale_a):
    translation = TranslationFactory(entity=entity_a, locale=locale_a, user=user_b)
    review(user_a, translation)

    assert badges_review_count(user_a) == 1


@pytest.mark.django_db
def test_badges_review_count_ignores_self_reviews(user_a, entity_a, locale_a):
    own_translation = TranslationFactory(entity=entity_a, locale=locale_a, user=user_a)
    review(user_a, own_translation)

    assert badges_review_count(user_a) == 0


@pytest.mark.django_db
def test_badges_review_count_counts_reviews_of_imported_translations(
    user_a, entity_a, locale_a
):
    imported = TranslationFactory(entity=entity_a, locale=locale_a, user=None)
    review(user_a, imported)

    assert badges_review_count(user_a) == 1


@pytest.mark.django_db
def test_badges_review_count_ignores_implicit_reviews(
    user_a, user_b, entity_a, locale_a
):
    translation = TranslationFactory(entity=entity_a, locale=locale_a, user=user_b)
    review(user_a, translation, is_implicit_action=True)

    assert badges_review_count(user_a) == 0
