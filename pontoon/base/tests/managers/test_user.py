import pytest

from django.db.models import Q

from pontoon.base.utils import aware_datetime
from pontoon.contributors.utils import users_with_translations_counts

from pontoon.test.factories import (
    EntityFactory,
    TranslationFactory,
    UserFactory,
)


@pytest.mark.django_db
def test_mgr_user_without_translations(translation_a, user_a, user_b):
    """
    Checks if user contributors without translations aren't returned.
    """
    assert translation_a.user == user_a
    top_contributors = users_with_translations_counts()
    assert user_a in top_contributors
    assert user_b not in top_contributors


@pytest.mark.django_db
def test_mgr_user_contributors_order(
    resource_b, locale_a,
):
    """
    Checks if users are ordered by count of contributions.
    """
    contributors = UserFactory.create_batch(size=5)
    entities = EntityFactory.create_batch(size=22, resource=resource_b)

    # create a list of contributors/entity for translations
    for i, count in enumerate([2, 4, 9, 1, 6]):
        for j in range(count):
            TranslationFactory.create(
                locale=locale_a, user=contributors[i], entity=entities[i],
            )

    # Ordered by approved count
    assert list(users_with_translations_counts()) == [
        contributors[i] for i in [2, 4, 1, 0, 3]
    ]


@pytest.mark.django_db
def test_mgr_user_contributors_limit(
    resource_a, locale_a,
):
    """
    Checks if proper count of user is returned.
    """
    contributors = UserFactory.create_batch(size=102)
    entities = EntityFactory.create_batch(size=102, resource=resource_a,)
    for i, contrib in enumerate(contributors):
        TranslationFactory.create(
            locale=locale_a, approved=True, user=contrib, entity=entities[i],
        )
    top_contributors = users_with_translations_counts()
    assert len(top_contributors) == 100


@pytest.mark.django_db
def test_mgr_user_translation_counts(
    resource_a, locale_a,
):
    """Checks if translation counts are calculated properly.

    Tests creates 3 contributors with different numbers translations
    and checks if their counts match.

    """
    contributors = UserFactory.create_batch(size=3)
    entities = EntityFactory.create_batch(size=36, resource=resource_a)
    batch_kwargs = sum(
        [
            [dict(user=contributors[0], approved=True)] * 7,
            [dict(user=contributors[0], approved=False, fuzzy=False, rejected=True)]
            * 3,
            [dict(user=contributors[0], fuzzy=True)] * 2,
            [dict(user=contributors[1], approved=True)] * 5,
            [dict(user=contributors[1], approved=False, fuzzy=False, rejected=True)]
            * 9,
            [dict(user=contributors[1], fuzzy=True)] * 2,
            [dict(user=contributors[2], approved=True)] * 1,
            [dict(user=contributors[2], approved=False, fuzzy=False)] * 2,
            [dict(user=contributors[2], fuzzy=True)] * 5,
        ],
        [],
    )

    for i, kwa in enumerate(batch_kwargs):
        kwa.update(dict(entity=entities[i]))

    for args in batch_kwargs:
        TranslationFactory.create(
            locale=locale_a,
            user=args["user"],
            approved=args.get("approved", False),
            rejected=args.get("rejected", False),
            fuzzy=args.get("fuzzy", False),
        )

    top_contribs = users_with_translations_counts()

    assert len(top_contribs) == 3
    assert top_contribs[0] == contributors[1]
    assert top_contribs[1] == contributors[0]
    assert top_contribs[2] == contributors[2]

    assert top_contribs[0].translations_count == 16
    assert top_contribs[0].translations_approved_count == 5
    assert top_contribs[0].translations_rejected_count == 9
    assert top_contribs[0].translations_unapproved_count == 0
    assert top_contribs[0].translations_needs_work_count == 2

    assert top_contribs[1].translations_count == 12
    assert top_contribs[1].translations_approved_count == 7
    assert top_contribs[1].translations_rejected_count == 3
    assert top_contribs[1].translations_unapproved_count == 0
    assert top_contribs[1].translations_needs_work_count == 2

    assert top_contribs[2].translations_count == 8
    assert top_contribs[2].translations_approved_count == 1
    assert top_contribs[2].translations_rejected_count == 0
    assert top_contribs[2].translations_unapproved_count == 2
    assert top_contribs[2].translations_needs_work_count == 5


@pytest.mark.django_db
def test_mgr_user_period_filters(
    locale_a, resource_a,
):
    """Total counts should be filtered by given date.

    Test creates 2 contributors with different activity periods and checks
    if they are filtered properly.
    """
    contributors = UserFactory.create_batch(size=2)
    entities = EntityFactory.create_batch(size=35, resource=resource_a)
    batch_kwargs = sum(
        [
            [
                dict(
                    user=contributors[0],
                    date=aware_datetime(2015, 3, 2),
                    approved=True,
                )
            ]
            * 12,
            [
                dict(
                    user=contributors[0],
                    date=aware_datetime(2015, 7, 2),
                    approved=True,
                )
            ]
            * 5,
            [
                dict(
                    user=contributors[0],
                    date=aware_datetime(2015, 3, 2),
                    approved=False,
                    fuzzy=False,
                )
            ]
            * 1,
            [dict(user=contributors[0], date=aware_datetime(2015, 3, 2), fuzzy=True,)]
            * 2,
            [
                dict(
                    user=contributors[1],
                    date=aware_datetime(2015, 6, 1),
                    approved=True,
                )
            ]
            * 2,
            [
                dict(
                    user=contributors[1],
                    date=aware_datetime(2015, 6, 1),
                    approved=False,
                    fuzzy=False,
                )
            ]
            * 11,
            [dict(user=contributors[1], date=aware_datetime(2015, 6, 1), fuzzy=True,)]
            * 2,
        ],
        [],
    )

    for i, kwa in enumerate(batch_kwargs):
        kwa.update(dict(entity=entities[i]))

    for args in batch_kwargs:
        TranslationFactory.create(
            locale=locale_a,
            user=args["user"],
            date=args["date"],
            approved=args.get("approved", False),
            fuzzy=args.get("fuzzy", False),
        )

    top_contribs = users_with_translations_counts(aware_datetime(2015, 6, 10))
    assert len(top_contribs) == 1
    assert top_contribs[0].translations_count == 5
    assert top_contribs[0].translations_approved_count == 5
    assert top_contribs[0].translations_rejected_count == 0
    assert top_contribs[0].translations_unapproved_count == 0
    assert top_contribs[0].translations_needs_work_count == 0

    top_contribs = users_with_translations_counts(aware_datetime(2015, 5, 10))
    assert len(top_contribs) == 2
    assert top_contribs[0].translations_count == 15
    assert top_contribs[0].translations_approved_count == 2
    assert top_contribs[0].translations_rejected_count == 0
    assert top_contribs[0].translations_unapproved_count == 11
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1].translations_count == 5
    assert top_contribs[1].translations_approved_count == 5
    assert top_contribs[1].translations_rejected_count == 0
    assert top_contribs[1].translations_unapproved_count == 0
    assert top_contribs[1].translations_needs_work_count == 0

    top_contribs = users_with_translations_counts(aware_datetime(2015, 1, 10))
    assert len(top_contribs) == 2
    assert top_contribs[0].translations_count == 20
    assert top_contribs[0].translations_approved_count == 17
    assert top_contribs[0].translations_rejected_count == 0
    assert top_contribs[0].translations_unapproved_count == 1
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1].translations_count == 15
    assert top_contribs[1].translations_approved_count == 2
    assert top_contribs[1].translations_rejected_count == 0
    assert top_contribs[1].translations_unapproved_count == 11
    assert top_contribs[1].translations_needs_work_count == 2


@pytest.mark.django_db
def test_mgr_user_query_args_filtering(
    locale_a, resource_a, locale_b,
):
    """
    Tests if query args are honored properly and contributors are filtered.
    """
    contributors = UserFactory.create_batch(size=3)
    entities = EntityFactory.create_batch(size=53, resource=resource_a)

    batch_kwargs = sum(
        [
            [dict(user=contributors[0], locale=locale_a, approved=True)] * 12,
            [dict(user=contributors[0], locale=locale_a, approved=False, fuzzy=False)]
            * 1,
            [dict(user=contributors[0], locale=locale_a, fuzzy=True)] * 2,
            [dict(user=contributors[1], locale=locale_b, approved=True)] * 11,
            [dict(user=contributors[1], locale=locale_b, approved=False, fuzzy=False)]
            * 1,
            [dict(user=contributors[1], locale=locale_b, fuzzy=True)] * 2,
            [dict(user=contributors[2], locale=locale_a, approved=True)] * 10,
            [dict(user=contributors[2], locale=locale_a, approved=False, fuzzy=False)]
            * 12,
            [dict(user=contributors[2], locale=locale_a, fuzzy=True)] * 2,
        ],
        [],
    )

    for i, kwa in enumerate(batch_kwargs):
        kwa.update(dict(entity=entities[i]))

    for args in batch_kwargs:
        TranslationFactory.create(
            locale=args["locale"],
            user=args["user"],
            approved=args.get("approved", False),
            fuzzy=args.get("fuzzy", False),
        )

    top_contribs = users_with_translations_counts(
        aware_datetime(2015, 1, 1), Q(locale=locale_a),
    )
    assert len(top_contribs) == 2
    assert top_contribs[0] == contributors[2]
    assert top_contribs[0].translations_count == 24
    assert top_contribs[0].translations_approved_count == 10
    assert top_contribs[0].translations_rejected_count == 0
    assert top_contribs[0].translations_unapproved_count == 12
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1] == contributors[0]
    assert top_contribs[1].translations_count == 15
    assert top_contribs[1].translations_approved_count == 12
    assert top_contribs[1].translations_rejected_count == 0
    assert top_contribs[1].translations_unapproved_count == 1
    assert top_contribs[1].translations_needs_work_count == 2

    top_contribs = users_with_translations_counts(
        aware_datetime(2015, 1, 1), Q(locale=locale_b),
    )
    assert len(top_contribs) == 1
    assert top_contribs[0] == contributors[1]
    assert top_contribs[0].translations_count == 14
    assert top_contribs[0].translations_approved_count == 11
    assert top_contribs[0].translations_rejected_count == 0
    assert top_contribs[0].translations_unapproved_count == 1
    assert top_contribs[0].translations_needs_work_count == 2
