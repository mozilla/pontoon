import pytest

from django.utils import timezone

from pontoon.base.get_entities import get_entities_for_project_locale
from pontoon.base.models import TranslatedResource
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    TranslationFactory,
)


def _time_interval(date):
    stamp = date.strftime("%Y%m%d%H%M")
    return f"{stamp}-{stamp}"


@pytest.fixture
def reviewed_entities(resource_a, locale_a, user_a, user_b):
    """
    Return two entities reviewed at the same time: one where user_a reviewed
    their own translation, one where user_a reviewed user_b's translation.
    """
    ProjectLocaleFactory.create(project=resource_a.project, locale=locale_a)
    TranslatedResource.objects.create(resource=resource_a, locale=locale_a)

    now = timezone.now()
    entities = {}

    for key, author in (("self", user_a), ("peer", user_b)):
        entity = EntityFactory.create(resource=resource_a, string=f"{key} string")
        TranslationFactory.create(
            entity=entity,
            locale=locale_a,
            user=author,
            approved=True,
            approved_user=user_a,
            approved_date=now,
            date=now,
        )
        entities[key] = entity

    return entities, now


@pytest.mark.django_db
def test_reviewer_filter_excludes_self_reviews(
    reviewed_entities, resource_a, locale_a, user_a
):
    """Approving your own translation is not a review performed."""
    entities, now = reviewed_entities

    matches = get_entities_for_project_locale(
        user_a,
        resource_a.project,
        locale_a,
        reviewer=user_a.email,
        review_time=_time_interval(now),
    )

    assert list(matches) == [entities["peer"]]


@pytest.mark.django_db
def test_author_review_time_filter_excludes_self_reviews(
    reviewed_entities, resource_a, locale_a, user_a, user_b
):
    """Approving your own translation is not a review received."""
    entities, now = reviewed_entities

    # user_a authored the self-reviewed translation, so they received no review
    assert not list(
        get_entities_for_project_locale(
            user_a,
            resource_a.project,
            locale_a,
            author=user_a.email,
            review_time=_time_interval(now),
        )
    )

    # user_b's translation was reviewed by user_a
    assert list(
        get_entities_for_project_locale(
            user_a,
            resource_a.project,
            locale_a,
            author=user_b.email,
            review_time=_time_interval(now),
        )
    ) == [entities["peer"]]


@pytest.mark.django_db
def test_self_reviewed_strings_shown_without_review_filters(
    reviewed_entities, resource_a, locale_a, user_a
):
    """The exclusion is scoped to the review filters, and doesn't leak elsewhere."""
    entities, now = reviewed_entities

    matches = get_entities_for_project_locale(
        user_a,
        resource_a.project,
        locale_a,
        author=user_a.email,
        time=_time_interval(now),
    )

    assert list(matches) == [entities["self"]]
