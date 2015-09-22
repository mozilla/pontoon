from django_nose.tools import assert_equal, assert_true
from django.test.utils import override_settings

from pontoon.base.models import Translation, User
from pontoon.base.tests import (
    assert_attributes_equal,
    IdenticalTranslationFactory,
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


class UserTranslationManagerTests(TestCase):
    @override_settings(EXCLUDE=('excluded@example.com',))
    def test_excluded_contributors(self):
        """
        Checks if contributors with mails in settings.EXCLUDE are excluded
        from top contributors list.
        """
        included_contributor = TranslationFactory.create(user__email='included@example.com').user
        excluded_contributor = TranslationFactory.create(user__email='excluded@example.com').user

        top_contributors = User.translators.with_translation_counts()
        assert_true(included_contributor in top_contributors)
        assert_true(excluded_contributor not in top_contributors)

    def test_users_without_translations(self):
        """
        Checks if user contributors without translations aren't returned.
        """
        active_contributor = TranslationFactory.create(user__email='active@example.com').user
        inactive_contributor = UserFactory.create(email='inactive@example.com')

        top_contributors = User.translators.with_translation_counts()
        assert_true(active_contributor in top_contributors)
        assert_true(inactive_contributor not in top_contributors)

    def test_unique_translations(self):
        """
        Checks if contributors with identical translations are returned.
        """

        unique_translator = TranslationFactory.create().user
        identical_translator = IdenticalTranslationFactory.create().user
        top_contributors = User.translators.with_translation_counts()

        assert_true(unique_translator in top_contributors)
        assert_true(identical_translator not in top_contributors)


    def test_contributors_order(self):
        """
        Checks if users are ordered by count of contributions.
        """
        contributors = [
            self.create_contributor_with_translation_counts(2),
            self.create_contributor_with_translation_counts(4),
            self.create_contributor_with_translation_counts(9),
            self.create_contributor_with_translation_counts(1),
            self.create_contributor_with_translation_counts(6),
        ]

        assert_equal(list(User.translators.with_translation_counts()), [
            contributors[2],
            contributors[4],
            contributors[1],
            contributors[0],
            contributors[3]])

    def test_contributors_limit(self):
        """
        Checks if proper count of user is returned.
        """
        TranslationFactory.create_batch(110)

        top_contributors = User.translators.with_translation_counts()

        assert_equal(top_contributors.count(), 100)

    def create_contributor_with_translation_counts(self, approved=0, unapproved=0, needs_work=0, **kwargs):
        """
        Helper method, creates contributor with given translations counts.
        """
        contributor = UserFactory.create()
        TranslationFactory.create_batch(approved, user=contributor, approved=True, **kwargs)
        TranslationFactory.create_batch(unapproved, user=contributor, approved=False, fuzzy=False, **kwargs)
        TranslationFactory.create_batch(needs_work, user=contributor, fuzzy=True, **kwargs)
        return contributor

    def test_translation_counts(self):
        """
        Checks if translation counts are calculated properly.
        Tests creates 3 contributors with different numbers translations and checks if their counts match.
        """

        first_contributor = self.create_contributor_with_translation_counts(approved=7, unapproved=3, needs_work=2)
        second_contributor = self.create_contributor_with_translation_counts(approved=5, unapproved=9, needs_work=2)
        third_contributor = self.create_contributor_with_translation_counts(approved=1, unapproved=2, needs_work=5)

        top_contributors = User.translators.with_translation_counts()
        assert_equal(top_contributors.count(), 3)

        assert_equal(top_contributors[0], second_contributor)
        assert_equal(top_contributors[1], first_contributor)
        assert_equal(top_contributors[2], third_contributor)

        assert_attributes_equal(top_contributors[0], translations_count=16,
            translations_approved_count=5, translations_unapproved_count=9,
            translations_needs_work_count=2)
        assert_attributes_equal(top_contributors[1], translations_count=12,
            translations_approved_count=7, translations_unapproved_count=3,
            translations_needs_work_count=2)
        assert_attributes_equal(top_contributors[2], translations_count=8,
            translations_approved_count=1, translations_unapproved_count=2,
            translations_needs_work_count=5)

    def test_period_filters(self):
        """
        Total counts should be filtered by given date.
        Test creates 2 contributors with different activity periods and checks if they are filtered properly.
        """

        first_contributor = self.create_contributor_with_translation_counts(approved=12, unapproved=1, needs_work=2,
            date=aware_datetime(2015, 3, 2))
        second_contributor = self.create_contributor_with_translation_counts(approved=2, unapproved=11, needs_work=2,
            date=aware_datetime(2015, 6, 1))

        TranslationFactory.create_batch(5, approved=True, user=first_contributor, date=aware_datetime(2015, 7, 2))

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 6, 10))

        assert_equal(top_contributors.count(), 1)
        assert_attributes_equal(top_contributors[0], translations_count=5,
            translations_approved_count=5, translations_unapproved_count=0,
            translations_needs_work_count=0)

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 5, 10))

        assert_equal(top_contributors.count(), 2)
        assert_attributes_equal(top_contributors[0], translations_count=15,
            translations_approved_count=2, translations_unapproved_count=11,
            translations_needs_work_count=2)
        assert_attributes_equal(top_contributors[1], translations_count=5,
            translations_approved_count=5, translations_unapproved_count=0,
            translations_needs_work_count=0)

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 1, 10))

        assert_equal(top_contributors.count(), 2)
        assert_attributes_equal(top_contributors[0], translations_count=20,
            translations_approved_count=17, translations_unapproved_count=1,
            translations_needs_work_count=2)
        assert_attributes_equal(top_contributors[1], translations_count=15,
            translations_approved_count=2, translations_unapproved_count=11,
            translations_needs_work_count=2)
