import os.path

from django_nose.tools import assert_equal, assert_false, assert_raises, assert_true
from django.test.utils import override_settings

from mock import call, Mock, patch

from pontoon.base.models import Entity, Repository, Translation, User
from pontoon.base.tests import (
    assert_attributes_equal,
    EntityFactory,
    IdenticalTranslationFactory,
    LocaleFactory,
    ProjectFactory,
    RepositoryFactory,
    ResourceFactory,
    StatsFactory,
    SubpageFactory,
    TestCase,
    TranslationFactory,
    UserFactory
)
from pontoon.base.utils import aware_datetime


class ProjectTests(TestCase):
    def test_can_commit_no_repos(self):
        """can_commit should be False if there are no repos."""
        project = ProjectFactory.create(repositories=[])
        assert_false(project.can_commit)

    def test_can_commit_false(self):
        """
        can_commit should be False if there are no repo that can be
        committed to.
        """
        repo = RepositoryFactory.build(type=Repository.FILE)
        project = ProjectFactory.create(repositories=[repo])
        assert_false(project.can_commit)

    def test_can_commit_true(self):
        """
        can_commit should be True if there is a repo that can be
        committed to.
        """
        repo = RepositoryFactory.build(type=Repository.GIT)
        project = ProjectFactory.create(repositories=[repo])
        assert_true(project.can_commit)

    # We only test type here because the other compatibility methods are
    # basically the same, and they're meant to be removed in the future
    # anyway.

    def test_repository_type_no_repo(self):
        """If a project has no repos, repository_type should be None."""
        project = ProjectFactory.create(repositories=[])
        assert_equal(project.repository_type, None)

    def test_repository_type_first(self):
        """
        If a project has repos, return the type of the repo created
        first.
        """
        project = ProjectFactory.create(repositories=[])
        RepositoryFactory.create(project=project, type=Repository.GIT)
        RepositoryFactory.create(project=project, type=Repository.HG)
        assert_equal(project.repository_type, Repository.GIT)

    def test_repository_for_path_none(self):
        """
        If the project has no matching repositories, raise a ValueError.
        """
        project = ProjectFactory.create(repositories=[])
        with assert_raises(ValueError):
            project.repository_for_path('doesnt/exist')

    def test_repository_for_path(self):
        """
        Return the first repo found with a checkout path that contains
        the given path.
        """
        repo1, repo2, repo3 = RepositoryFactory.build_batch(3)
        project = ProjectFactory.create(repositories=[repo1, repo2, repo3])
        path = os.path.join(repo2.checkout_path, 'foo', 'bar')
        assert_equal(project.repository_for_path(path), repo2)


class ProjectPartsTests(TestCase):
    def setUp(self):
        self.locale, self.locale_other = LocaleFactory.create_batch(2)
        self.project = ProjectFactory.create(
            locales=[self.locale, self.locale_other]
        )
        self.resource = ResourceFactory.create(
            project=self.project,
            path='/main/path.po'
        )
        EntityFactory.create(resource=self.resource)
        StatsFactory.create(resource=self.resource, locale=self.locale)

    def _fetch_locales_parts_stats(self):
        # Fake Prefetch
        resources = Entity.objects.filter(obsolete=False).values('resource')
        self.project.active_resources = self.project.resource_set.filter(
            pk__in=resources
        )

        return self.project.locales_parts_stats

    def test_locales_parts_stats_no_page_one_resource(self):
        """
        Return empty list in no subpage and only one resource defined.
        """
        project_details = self._fetch_locales_parts_stats()
        details = project_details.get(self.locale.code)

        assert_equal(details, [])

    def test_locales_parts_stats_no_page_multiple_resources(self):
        """
        Return resource paths and stats for locales resources are available for.
        """
        resource_other = ResourceFactory.create(
            project=self.project,
            path='/other/path.po'
        )
        EntityFactory.create(resource=resource_other)
        StatsFactory.create(resource=resource_other, locale=self.locale)
        StatsFactory.create(resource=resource_other, locale=self.locale_other)

        project_details = self._fetch_locales_parts_stats()
        details = project_details.get(self.locale.code)
        details_other = project_details.get(self.locale_other.code)

        assert_equal(details[0]['resource__path'], '/main/path.po')
        assert_equal(details[0]['translated_count'], 0)
        assert_equal(details[1]['resource__path'], '/other/path.po')
        assert_equal(details[1]['translated_count'], 0)
        assert_equal(len(details_other), 1)
        assert_equal(details_other[0]['resource__path'], '/other/path.po')
        assert_equal(details_other[0]['translated_count'], 0)

    def test_locales_parts_stats_pages_not_tied_to_resources(self):
        """
        Return subpage name and stats.
        """
        SubpageFactory.create(project=self.project, name='Subpage')

        project_details = self._fetch_locales_parts_stats()
        details = project_details.get(self.locale.code)

        assert_equal(details[0]['resource__path'], 'Subpage')
        assert_equal(details[0]['translated_count'], 0)

    def test_locales_parts_stats_pages_tied_to_resources(self):
        """
        Return subpage name and stats for locales resources are available for.
        """
        resource_other = ResourceFactory.create(
            project=self.project,
            path='/other/path.po'
        )
        EntityFactory.create(resource=resource_other)
        StatsFactory.create(resource=resource_other, locale=self.locale)
        StatsFactory.create(resource=resource_other, locale=self.locale_other)
        SubpageFactory.create(
            project=self.project,
            name='Subpage',
            resources=[self.resource]
        )
        SubpageFactory.create(
            project=self.project,
            name='Other Subpage',
            resources=[resource_other]
        )

        project_details = self._fetch_locales_parts_stats()
        details = project_details.get(self.locale.code)
        details_other = project_details.get(self.locale_other.code)

        assert_equal(details[0]['resource__path'], 'Other Subpage')
        assert_equal(details[0]['translated_count'], 0)
        assert_equal(details[1]['resource__path'], 'Subpage')
        assert_equal(details[1]['translated_count'], 0)
        assert_equal(details_other[0]['resource__path'], 'Other Subpage')
        assert_equal(details_other[0]['translated_count'], 0)


class RepositoryTests(TestCase):
    def test_checkout_path(self):
        """checkout_path should be determined by the repo URL."""
        repo = RepositoryFactory.create(
            url='https://example.com/path/to/locale/',
            project__slug='test-project'
        )
        with self.settings(MEDIA_ROOT='/media/root'):
            assert_equal(
                repo.checkout_path,
                '/media/root/projects/test-project/path/to/locale'
            )

    def test_checkout_path_multi_locale(self):
        """
        The checkout_path for multi-locale repos should not include the
        locale_code variable.
        """
        repo = RepositoryFactory.create(
            url='https://example.com/path/to/{locale_code}/',
            project__slug='test-project',
            multi_locale=True
        )
        with self.settings(MEDIA_ROOT='/media/root'):
            assert_equal(
                repo.checkout_path,
                '/media/root/projects/test-project/path/to'
            )

    def test_checkout_path_source_repo(self):
        """
        The checkout_path for a source repo should end with a templates
        directory.
        """
        repo = RepositoryFactory.create(
            url='https://example.com/path/to/locale/',
            project__slug='test-project',
            source_repo=True
        )
        with self.settings(MEDIA_ROOT='/media/root'):
            assert_equal(
                repo.checkout_path,
                '/media/root/projects/test-project/path/to/locale/templates'
            )

    def test_locale_checkout_path(self):
        """Append the locale code the the project's checkout_path."""
        repo = RepositoryFactory.create(
            url='https://example.com/path/',
            project__slug='test-project',
            multi_locale=True
        )
        locale = LocaleFactory.create(code='test-locale')

        with self.settings(MEDIA_ROOT='/media/root'):
            assert_equal(
                repo.locale_checkout_path(locale),
                '/media/root/projects/test-project/path/test-locale'
            )

    def test_locale_checkout_path_non_multi_locale(self):
        """If the repo isn't multi-locale, throw a ValueError."""
        repo = RepositoryFactory.create(multi_locale=False)
        locale = LocaleFactory.create()
        with assert_raises(ValueError):
            repo.locale_checkout_path(locale)

    def test_locale_url(self):
        """Fill in the {locale_code} variable in the URL."""
        repo = RepositoryFactory.create(
            url='https://example.com/path/to/{locale_code}/',
            multi_locale=True
        )
        locale = LocaleFactory.create(code='test-locale')

        assert_equal(repo.locale_url(locale), 'https://example.com/path/to/test-locale/')

    def test_locale_url_non_multi_locale(self):
        """If the repo isn't multi-locale, throw a ValueError."""
        repo = RepositoryFactory.create(multi_locale=False)
        locale = LocaleFactory.create()
        with assert_raises(ValueError):
            repo.locale_url(locale)

    def test_url_for_path(self):
        """
        Return the first locale_checkout_path for locales active for the
        repo's project that matches the given path.
        """
        matching_locale = LocaleFactory.create(code='match')
        non_matching_locale = LocaleFactory.create(code='nomatch')
        repo = RepositoryFactory.create(
            project__locales=[matching_locale, non_matching_locale],
            project__slug='test-project',
            url='https://example.com/path/to/{locale_code}/',
            multi_locale=True
        )

        with self.settings(MEDIA_ROOT='/media/root'):
            test_path = '/media/root/projects/test-project/path/to/match/foo/bar.po'
            assert_equal(repo.url_for_path(test_path), 'https://example.com/path/to/match/')

    def test_url_for_path_no_match(self):
        """
        If no active locale matches the given path, raise a ValueError.
        """
        repo = RepositoryFactory.create(
            project__locales=[],
            url='https://example.com/path/to/{locale_code}/',
            multi_locale=True
        )

        with assert_raises(ValueError):
            repo.url_for_path('/media/root/path/to/match/foo/bar.po')

    def test_pull(self):
        repo = RepositoryFactory.create(type=Repository.GIT, url='https://example.com')
        with patch('pontoon.base.models.update_from_vcs') as update_from_vcs, \
             patch('pontoon.base.models.get_revision') as mock_get_revision:
            mock_get_revision.return_value = 'asdf'
            assert_equal(repo.pull(), {'single_locale': 'asdf'})
            update_from_vcs.assert_called_with(
                Repository.GIT,
                'https://example.com',
                repo.checkout_path
            )

    def test_pull_multi_locale(self):
        """
        If the repo is multi-locale, pull all of the repos for the
        active locales.
        """
        locale1 = LocaleFactory.create(code='locale1')
        locale2 = LocaleFactory.create(code='locale2')
        repo = RepositoryFactory.create(
            type=Repository.GIT,
            url='https://example.com/{locale_code}/',
            multi_locale=True,
            project__locales=[locale1, locale2]
        )

        repo.locale_url = lambda locale: 'https://example.com/' + locale.code
        repo.locale_checkout_path = lambda locale: '/media/' + locale.code

        with patch('pontoon.base.models.update_from_vcs') as update_from_vcs, \
             patch('pontoon.base.models.get_revision') as mock_get_revision:
            # Return path as the revision so different locales return
            # different values.
            mock_get_revision.side_effect = lambda type, path: path

            assert_equal(repo.pull(), {
                'locale1': '/media/locale1',
                'locale2': '/media/locale2'
            })
            update_from_vcs.assert_has_calls([
                call(Repository.GIT, 'https://example.com/locale1', '/media/locale1'),
                call(Repository.GIT, 'https://example.com/locale2', '/media/locale2')
            ])

    def test_commit(self):
        repo = RepositoryFactory.create(type=Repository.GIT, url='https://example.com')
        with patch('pontoon.base.models.commit_to_vcs') as commit_to_vcs:
            repo.commit('message', 'author', 'path')
            commit_to_vcs.assert_called_with(
                Repository.GIT,
                'path',
                'message',
                'author',
                'https://example.com',
            )

    def test_commit_multi_locale(self):
        """
        If the repo is multi-locale, use the url from url_for_path for
        committing.
        """
        repo = RepositoryFactory.create(
            type=Repository.GIT,
            url='https://example.com/{locale_code}/',
            multi_locale=True
        )

        repo.url_for_path = Mock(return_value='https://example.com/for_path')
        with patch('pontoon.base.models.commit_to_vcs') as commit_to_vcs:
            repo.commit('message', 'author', 'path')
            commit_to_vcs.assert_called_with(
                Repository.GIT,
                'path',
                'message',
                'author',
                'https://example.com/for_path',
            )
            repo.url_for_path.assert_called_with('path')


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


class EntityTests(TestCase):
    def setUp(self):
        self.locale = LocaleFactory.create(
            cldr_plurals="0,1"
        )
        self.project = ProjectFactory.create(
            locales=[self.locale]
        )
        self.main_resource = ResourceFactory.create(
            project=self.project,
            path='main.lang'
        )
        self.other_resource = ResourceFactory.create(
            project=self.project,
            path='other.lang'
        )
        self.main_entity = EntityFactory.create(
            resource=self.main_resource,
            string='Source String',
            string_plural='Plural Source String'
        )
        self.other_entity = EntityFactory.create(
            resource=self.other_resource,
            string='Other Source String'
        )
        self.main_translation = TranslationFactory.create(
            entity=self.main_entity,
            locale=self.locale,
            plural_form=0,
            string='Translated String'
        )
        self.main_translation_plural = TranslationFactory.create(
            entity=self.main_entity,
            locale=self.locale,
            plural_form=1,
            string='Translated Plural String'
        )
        self.other_translation = TranslationFactory.create(
            entity=self.other_entity,
            locale=self.locale,
            string='Other Translated String'
        )
        self.subpage = SubpageFactory.create(
            project=self.project,
            name='Subpage',
            resources=[self.main_resource]
        )

    def assert_serialized_entity(self, entity, path, original, translation):
        assert_equal(entity['path'], path)
        assert_equal(entity['original'], original)
        assert_equal(entity['translation'][0]['string'], translation)

    def test_for_project_locale_filter(self):
        """
        Evaluate entities filtering by locale, project, obsolete.
        """
        other_locale = LocaleFactory.create()
        other_project = ProjectFactory.create(
            locales=[self.locale, other_locale]
        )
        obsolete_entity = EntityFactory.create(
            obsolete=True,
            resource=self.main_resource,
            string='Obsolete String'
        )
        entities = Entity.for_project_locale(self.project, other_locale)
        assert_equal(len(entities), 0)
        entities = Entity.for_project_locale(other_project, self.locale)
        assert_equal(len(entities), 0)
        entities = Entity.for_project_locale(self.project, self.locale)
        assert_equal(len(entities), 2)

    def test_for_project_locale_no_paths(self):
        """
        If paths not specified, return all project entities along with their
        translations for locale.
        """
        entities = Entity.for_project_locale(self.project, self.locale)

        assert_equal(len(entities), 2)
        self.assert_serialized_entity(
            entities[0], 'main.lang', 'Source String', 'Translated String')
        self.assert_serialized_entity(
            entities[1], 'other.lang', 'Other Source String', 'Other Translated String')

        # Ensure all attributes are assigned correctly
        assert_equal(entities[0], {
            'comment': '',
            'format': 'po',
            'obsolete': False,
            'marked': 'Source String',
            'key': '',
            'path': 'main.lang',
            'translation': [{
                'pk': self.main_translation.pk,
                'fuzzy': False,
                'string': 'Translated String',
                'approved': False
            }, {
                'pk': self.main_translation_plural.pk,
                'fuzzy': False,
                'string': 'Translated Plural String',
                'approved': False
            }],
            'order': 0,
            'source': [],
            'original_plural': 'Plural Source String',
            'marked_plural': 'Plural Source String',
            'pk': self.main_entity.pk,
            'original': 'Source String'
        })

    def test_for_project_locale_paths(self):
        """
        If paths specified, return project entities from these paths only along
        with their translations for locale.
        """
        paths = ['other.lang']
        entities = Entity.for_project_locale(self.project, self.locale, paths)

        assert_equal(len(entities), 1)
        self.assert_serialized_entity(
            entities[0], 'other.lang', 'Other Source String', 'Other Translated String')

    def test_for_project_locale_subpages(self):
        """
        If paths specified as subpages, return project entities from paths
        assigned to these subpages only along with their translations for
        locale.
        """
        subpages = [self.subpage.name]
        entities = Entity.for_project_locale(self.project, self.locale, subpages)

        assert_equal(len(entities), 1)
        self.assert_serialized_entity(
            entities[0], 'main.lang', 'Source String', 'Translated String')

    def test_for_project_locale_plurals(self):
        """
        For pluralized strings, return all available plural forms.
        """
        entities = Entity.for_project_locale(self.project, self.locale)

        assert_equal(entities[0]['original'], 'Source String')
        assert_equal(entities[0]['original_plural'], 'Plural Source String')
        assert_equal(entities[0]['translation'][0]['string'], 'Translated String')
        assert_equal(entities[0]['translation'][1]['string'], 'Translated Plural String')

    def test_for_project_locale_order(self):
        """
        Return entities in correct order.
        """
        entity_second = EntityFactory.create(
            order=1,
            resource=self.main_resource,
            string='Second String'
        )
        entity_first = EntityFactory.create(
            order=0,
            resource=self.main_resource,
            string='First String'
        )
        entities = Entity.for_project_locale(self.project, self.locale)

        assert_equal(entities[2]['original'], 'First String')
        assert_equal(entities[3]['original'], 'Second String')
