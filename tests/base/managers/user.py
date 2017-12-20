
import pytest

from django.db.models import Q

from pontoon.base.models import User
from pontoon.base.utils import aware_datetime


@pytest.mark.django_db
def test_mgr_user_without_translations(translation0, user0, userX):
    """
    Checks if user contributors without translations aren't returned.
    """
    assert translation0.user == user0
    top_contributors = User.translators.with_translation_counts()
    assert user0 in top_contributors
    assert userX not in top_contributors


@pytest.mark.django_db
def test_mgr_user_contributors_order(user_factory, entity_factory,
                                     translation_factory,
                                     resourceX, locale0, user0, user1):
    """
    Checks if users are ordered by count of contributions.
    """
    user0.delete()
    user1.delete()
    contributors = user_factory(batch=5)
    entities = entity_factory(resource=resourceX, batch=22)

    # create a list of contributors/entity for translations
    contrib_list = sum(
        [[dict(user=contributors[i], entity=entities[i])] * count
         for i, count
         in enumerate([2, 4, 9, 1, 6])],
        [])
    translation_factory(
        locale=locale0,
        batch_kwargs=contrib_list)

    # Ordered by approved count
    assert (
        list(User.translators.with_translation_counts())
        == [contributors[i]
            for i
            in [2, 4, 1, 0, 3]])


@pytest.mark.django_db
def test_mgr_user_contributors_limit(user_factory, entity_factory,
                                     translation_factory, resource0, locale0):
    """
    Checks if proper count of user is returned.
    """
    contributors = user_factory(batch=102)
    entities = entity_factory(
        resource=resource0,
        batch=102)
    translation_factory(
        locale=locale0,
        approved=1,
        batch_kwargs=[
            dict(user=contrib, entity=entities[i])
            for i, contrib
            in enumerate(contributors)])
    top_contributors = User.translators.with_translation_counts()
    assert len(top_contributors) == 100


@pytest.mark.django_db
def test_mgr_user_translation_counts(user_factory, entity_factory, resource0,
                                     locale0, translation_factory,
                                     user0, user1):
    """Checks if translation counts are calculated properly.

    Tests creates 3 contributors with different numbers translations
    and checks if their counts match.

    """
    user0.delete()
    user1.delete()
    contributors = user_factory(batch=3)
    entities = entity_factory(resource=resource0, batch=36)
    batch_kwargs = sum(
        [[dict(user=contributors[0], approved=True)] * 7,
         [dict(user=contributors[0], approved=False, fuzzy=False)] * 3,
         [dict(user=contributors[0], fuzzy=True)] * 2,
         [dict(user=contributors[1], approved=True)] * 5,
         [dict(user=contributors[1], approved=False, fuzzy=False)] * 9,
         [dict(user=contributors[1], fuzzy=True)] * 2,
         [dict(user=contributors[2], approved=True)] * 1,
         [dict(user=contributors[2], approved=False, fuzzy=False)] * 2,
         [dict(user=contributors[2], fuzzy=True)] * 5],
        [])
    [kwa.update(dict(entity=entities[i]))
     for i, kwa
     in enumerate(batch_kwargs)]
    translation_factory(
        locale=locale0,
        batch_kwargs=batch_kwargs)
    top_contribs = User.translators.with_translation_counts()

    assert len(top_contribs) == 3
    assert top_contribs[0] == contributors[1]
    assert top_contribs[1] == contributors[0]
    assert top_contribs[2] == contributors[2]

    assert top_contribs[0].translations_count == 16
    assert top_contribs[0].translations_approved_count == 5
    assert top_contribs[0].translations_unapproved_count == 9
    assert top_contribs[0].translations_needs_work_count == 2

    assert top_contribs[1].translations_count == 12
    assert top_contribs[1].translations_approved_count == 7
    assert top_contribs[1].translations_unapproved_count == 3
    assert top_contribs[1].translations_needs_work_count == 2

    assert top_contribs[2].translations_count == 8
    assert top_contribs[2].translations_approved_count == 1
    assert top_contribs[2].translations_unapproved_count == 2
    assert top_contribs[2].translations_needs_work_count == 5


@pytest.mark.django_db
def test_mgr_user_period_filters(user_factory, entity_factory, locale0,
                                 translation_factory, resource0,
                                 user0, user1):
    """Total counts should be filtered by given date.

    Test creates 2 contributors with different activity periods and checks
    if they are filtered properly.
    """
    user0.delete()
    user1.delete()
    contributors = user_factory(batch=2)
    entities = entity_factory(resource=resource0, batch=35)
    batch_kwargs = sum(
        [[dict(
            user=contributors[0],
            date=aware_datetime(2015, 3, 2),
            approved=True)] * 12,
         [dict(
             user=contributors[0],
             date=aware_datetime(2015, 7, 2),
             approved=True)] * 5,
         [dict(
             user=contributors[0],
             date=aware_datetime(2015, 3, 2),
             approved=False,
             fuzzy=False)] * 1,
         [dict(
             user=contributors[0],
             date=aware_datetime(2015, 3, 2),
             fuzzy=True)] * 2,
         [dict(
             user=contributors[1],
             date=aware_datetime(2015, 6, 1),
             approved=True)] * 2,
         [dict(
             user=contributors[1],
             date=aware_datetime(2015, 6, 1),
             approved=False,
             fuzzy=False)] * 11,
         [dict(
             user=contributors[1],
             date=aware_datetime(2015, 6, 1),
             fuzzy=True)] * 2],
        [])
    [kwa.update(dict(entity=entities[i]))
     for i, kwa
     in enumerate(batch_kwargs)]
    translation_factory(
        locale=locale0,
        batch_kwargs=batch_kwargs)

    top_contribs = User.translators.with_translation_counts(
        aware_datetime(2015, 6, 10))
    assert len(top_contribs) == 1
    assert top_contribs[0].translations_count == 5
    assert top_contribs[0].translations_approved_count == 5
    assert top_contribs[0].translations_unapproved_count == 0
    assert top_contribs[0].translations_needs_work_count == 0

    top_contribs = User.translators.with_translation_counts(
        aware_datetime(2015, 5, 10))
    assert len(top_contribs) == 2
    assert top_contribs[0].translations_count == 15
    assert top_contribs[0].translations_approved_count == 2
    assert top_contribs[0].translations_unapproved_count == 11
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1].translations_count == 5
    assert top_contribs[1].translations_approved_count == 5
    assert top_contribs[1].translations_unapproved_count == 0
    assert top_contribs[1].translations_needs_work_count == 0

    top_contribs = User.translators.with_translation_counts(
        aware_datetime(2015, 1, 10))
    assert len(top_contribs) == 2
    assert top_contribs[0].translations_count == 20
    assert top_contribs[0].translations_approved_count == 17
    assert top_contribs[0].translations_unapproved_count == 1
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1].translations_count == 15
    assert top_contribs[1].translations_approved_count == 2
    assert top_contribs[1].translations_unapproved_count == 11
    assert top_contribs[1].translations_needs_work_count == 2


@pytest.mark.django_db
def test_mgr_user_query_args_filtering(user_factory, entity_factory,
                                       translation_factory, locale0,
                                       resource0, locale1, user0, user1):
    """
    Tests if query args are honored properly and contributors are filtered.
    """
    user0.delete()
    user1.delete()
    contributors = user_factory(batch=3)
    entities = entity_factory(resource=resource0, batch=53)
    batch_kwargs = sum(
        [[dict(
            user=contributors[0],
            locale=locale0,
            approved=True)] * 12,
         [dict(
             user=contributors[0],
             locale=locale0,
             approved=False,
             fuzzy=False)] * 1,
         [dict(
             user=contributors[0],
             locale=locale0,
             fuzzy=True)] * 2,
         [dict(
             user=contributors[1],
             locale=locale1,
             approved=True)] * 11,
         [dict(
             user=contributors[1],
             locale=locale1,
             approved=False,
             fuzzy=False)] * 1,
         [dict(
             user=contributors[1],
             locale=locale1,
             fuzzy=True)] * 2,
         [dict(
             user=contributors[2],
             locale=locale0,
             approved=True)] * 10,
         [dict(
             user=contributors[2],
             locale=locale0,
             approved=False,
             fuzzy=False)] * 12,
         [dict(
             user=contributors[2],
             locale=locale0,
             fuzzy=True)] * 2],
        [])
    [kwa.update(dict(entity=entities[i]))
     for i, kwa
     in enumerate(batch_kwargs)]
    translation_factory(
        batch_kwargs=batch_kwargs)

    top_contribs = User.translators.with_translation_counts(
        aware_datetime(2015, 1, 1),
        Q(locale=locale0))
    assert len(top_contribs) == 2
    assert top_contribs[0] == contributors[2]
    assert top_contribs[0].translations_count == 24
    assert top_contribs[0].translations_approved_count == 10
    assert top_contribs[0].translations_unapproved_count == 12
    assert top_contribs[0].translations_needs_work_count == 2
    assert top_contribs[1] == contributors[0]
    assert top_contribs[1].translations_count == 15
    assert top_contribs[1].translations_approved_count == 12
    assert top_contribs[1].translations_unapproved_count == 1
    assert top_contribs[1].translations_needs_work_count == 2

    top_contribs = User.translators.with_translation_counts(
        aware_datetime(2015, 1, 1),
        Q(locale=locale1))
    assert len(top_contribs) == 1
    assert top_contribs[0] == contributors[1]
    assert top_contribs[0].translations_count == 14
    assert top_contribs[0].translations_approved_count == 11
    assert top_contribs[0].translations_unapproved_count == 1
    assert top_contribs[0].translations_needs_work_count == 2
