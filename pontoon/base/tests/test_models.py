from django_nose.tools import assert_equal

from pontoon.base.models import Translation
from pontoon.base.tests import (
    assert_redirects,
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
    TestCase
)
from pontoon.base.utils import aware_datetime


class LocaleTests(TestCase):
    def test_latest_activity_translated(self):
        """
        If latest activity in Translation QuerySet is translation submission,
        return submission date and user.
        """
        user0 = UserFactory.create()
        user1 = UserFactory.create()

        translation0 = TranslationFactory.create(
            date=aware_datetime(1970, 1, 1),
            user=user0,
            approved_date=aware_datetime(1970, 1, 1),
            approved_user=user0
        )
        translation1 = TranslationFactory.create(
            date=aware_datetime(1970, 1, 2),
            user=user1,
            approved_date=aware_datetime(1970, 1, 2),
            approved_user=user1
        )

        translations = Translation.objects.filter(id__in=[translation0.id, translation1.id])
        assert_equal(translations.latest_activity(), {
            'date': translation1.date,
            'user': translation1.user
        })

    def test_latest_activity_approved(self):
        """
        If latest activity in Translation QuerySet is translation approval,
        return approval date and user.
        """
        user0 = UserFactory.create()
        user1 = UserFactory.create()

        translation0 = TranslationFactory.create(
            date=aware_datetime(1970, 1, 2),
            user=user0,
            approved_date=aware_datetime(1970, 1, 2),
            approved_user=user0
        )
        translation1 = TranslationFactory.create(
            date=aware_datetime(1970, 1, 1),
            user=user1,
            approved_date=aware_datetime(1970, 1, 3),
            approved_user=user1
        )

        translations = Translation.objects.filter(id__in=[translation0.id, translation1.id])
        assert_equal(translations.latest_activity(), {
            'date': translation1.date,
            'user': translation1.user
        })

    def test_latest_activity_none(self):
        """If empty Translation QuerySet, return None."""
        translations = Translation.objects.none()
        assert_equal(translations.latest_activity(), None)
