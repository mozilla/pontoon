from django_nose.tools import assert_equal
from django.test.utils import override_settings

from pontoon.base.models import Translation
from pontoon.base.tests import (
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
        Checks if user contributors without translations are returned.
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
        users = UserFactory.create_batch(5)

        for i, user in enumerate(users):
            TranslationFactory.create_batch(5-i, user=user)

        top_translations_totals = [user.translations_count for user in User.translators.with_translation_counts()]
        assert_equal(top_translations_totals, [5, 4, 3, 2, 1])


    def test_contributors_limit(self):
        """
        Checks if proper count of user is returned.
        """
        TranslationFactory.create_batch(110)

        top_contributors = User.translators.with_translation_counts()

        assert_true(len(top_contributors) == 100)

    def create_contributor_with_translation_counts(self, approved, unapproved, needs_work, **kwargs):
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
        assert_equal(top_contributors[0].translations_count, 16)
        assert_equal(top_contributors[0].translations_approved_count, 5)
        assert_equal(top_contributors[0].translations_unapproved_count, 9)
        assert_equal(top_contributors[0].translations_needs_work_count, 2)

        assert_equal(top_contributors[1], first_contributor)
        assert_equal(top_contributors[1].translations_count, 12)
        assert_equal(top_contributors[1].translations_approved_count, 7)
        assert_equal(top_contributors[1].translations_unapproved_count, 3)
        assert_equal(top_contributors[1].translations_needs_work_count, 2)

        assert_equal(top_contributors[2], third_contributor)
        assert_equal(top_contributors[2].translations_count, 8)
        assert_equal(top_contributors[2].translations_approved_count, 1)
        assert_equal(top_contributors[2].translations_unapproved_count, 2)
        assert_equal(top_contributors[2].translations_needs_work_count, 5)


    def test_period_filters(self):
        """
        Total counts should be filtered by given date.
        Test creates 2 contributors with different activity periods and checks if they are filtered properly.
        """

        first_contributor = self.create_contributor_with_translation_counts(approved=12, unapproved=1, needs_work=2,
            date=datetime(2015, 3, 2))
        second_contributor = self.create_contributor_with_translation_counts(approved=2, unapproved=11, needs_work=2,
            date=datetime(2015, 6, 1))

        TranslationFactory.create_batch(5, approved=True, user=first_contributor, date=datetime(2015, 7, 2))

        top_contributors = User.translators.with_translation_counts(datetime(2015, 6, 10))

        assert_equal(top_contributors.count(), 1)
        assert_equal(top_contributors[0], first_contributor)
        assert_equal(top_contributors[0].translations_count, 5)
        assert_equal(top_contributors[0].translations_approved_count, 5)
        assert_equal(top_contributors[0].translations_unapproved_count, 0)
        assert_equal(top_contributors[0].translations_needs_work_count, 0)

        top_contributors = User.translators.with_translation_counts(datetime(2015, 5, 10))

        assert_equal(top_contributors.count(), 2)
        assert_equal(top_contributors[0], second_contributor)
        assert_equal(top_contributors[0].translations_count, 15)
        assert_equal(top_contributors[0].translations_approved_count, 2)
        assert_equal(top_contributors[0].translations_unapproved_count, 11)
        assert_equal(top_contributors[0].translations_needs_work_count, 2)

        assert_equal(top_contributors[1], first_contributor)
        assert_equal(top_contributors[1].translations_count, 5)
        assert_equal(top_contributors[1].translations_approved_count, 5)
        assert_equal(top_contributors[1].translations_unapproved_count, 0)
        assert_equal(top_contributors[1].translations_needs_work_count, 0)

        top_contributors = User.translators.with_translation_counts(datetime(2015, 1, 10))

        assert_equal(top_contributors.count(), 2)
        assert_equal(top_contributors[0], first_contributor)
        assert_equal(top_contributors[0].translations_count, 20)
        assert_equal(top_contributors[0].translations_approved_count, 17)
        assert_equal(top_contributors[0].translations_unapproved_count, 1)
        assert_equal(top_contributors[0].translations_needs_work_count, 2)

        assert_equal(top_contributors[1], second_contributor)
        assert_equal(top_contributors[1].translations_count, 15)
        assert_equal(top_contributors[1].translations_approved_count, 2)
        assert_equal(top_contributors[1].translations_unapproved_count, 11)
        assert_equal(top_contributors[1].translations_needs_work_count, 2)
