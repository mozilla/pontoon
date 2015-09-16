from django_nose.tools import assert_equal

from pontoon.base.models import Translation
from pontoon.base.tests import (
    TranslationFactory,
    UserFactory,
    TestCase
)
from pontoon.base.utils import aware_datetime


class TranslationQuerySetTests(TestCase):
    def setUp(self):
        self.user0, self.user1 = UserFactory.create_batch(2)

    def _translation(self, user, submitted, approved):
        return TranslationFactory.create(
            date=aware_datetime(*submitted),
            user=user,
            approved_date=aware_datetime(*approved) if approved else None,
            approved_user=user
        )

    def test_latest_activity_translated(self):
        """
        If latest activity in Translation QuerySet is translation submission,
        return submission date and user.
        """
        latest_submission = self._translation(self.user0, submitted=(1970, 1, 3), approved=None)
        latest_approval = self._translation(self.user1, submitted=(1970, 1, 1), approved=(1970, 1, 2))
        assert_equal(Translation.objects.all().latest_activity(), {
            'date': latest_submission.date,
            'user': latest_submission.user
        })

    def test_latest_activity_approved(self):
        """
        If latest activity in Translation QuerySet is translation approval,
        return approval date and user.
        """
        latest_submission = self._translation(self.user0, submitted=(1970, 1, 2), approved=(1970, 1, 2))
        latest_approval = self._translation(self.user1, submitted=(1970, 1, 1), approved=(1970, 1, 3))
        assert_equal(Translation.objects.all().latest_activity(), {
            'date': latest_approval.date,
            'user': latest_approval.user
        })

    def test_latest_activity_none(self):
        """If empty Translation QuerySet, return None."""
        assert_equal(Translation.objects.none().latest_activity(), None)
