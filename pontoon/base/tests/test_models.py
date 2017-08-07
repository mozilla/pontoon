# -*- coding: utf-8 -*-
import os.path
from collections import defaultdict

from django.core.management import call_command
from django_nose.tools import (
    assert_equal,
    assert_false,
    assert_is_none,
    assert_raises,
    assert_true,
)
from django.db.models import Q

from mock import call, Mock, patch

from pontoon.base.models import (
    Entity,
    ProjectLocale,
    TranslationMemoryEntry,
    User
)
from pontoon.base.tests import (
    assert_attributes_equal,
    ChangedEntityLocaleFactory,
    EntityFactory,
    LocaleFactory,
    PluralEntityFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    RepositoryFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    SubpageFactory,
    TestCase,
    TranslationFactory,
    UserFactory
)
from pontoon.base.utils import aware_datetime
from pontoon.sync import KEY_SEPARATOR


class CreateUserTests(TestCase):
    def test_create_super_user(self):
        """
        Check if that's possible to create user.
        Test against possible regressions in User model.
        """
        username = 'superuser@example.com'
        call_command('createsuperuser', email=username, username=username, interactive=False)

        assert User.objects.get(username=username)
        assert User.objects.get(email=username)


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
        repo = RepositoryFactory.create(type='file')
        project = ProjectFactory.create(repositories=[repo])
        assert_false(project.can_commit)

    def test_can_commit_true(self):
        """
        can_commit should be True if there is a repo that can be
        committed to.
        """
        repo = RepositoryFactory.create(type='git')
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
        RepositoryFactory.create(project=project, type='git')
        RepositoryFactory.create(project=project, type='hg')
        assert_equal(project.repository_type, 'git')

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
        repo1, repo2, repo3 = RepositoryFactory.create_batch(3)
        project = ProjectFactory.create(repositories=[repo1, repo2, repo3])
        path = os.path.join(repo2.checkout_path, 'foo', 'bar')
        assert_equal(project.repository_for_path(path), repo2)

    def test_needs_sync(self):
        """
        Project.needs_sync should be True if ChangedEntityLocale objects
        exist for its entities or if Project has unsynced locales.
        """
        project = ProjectFactory.create()
        assert_false(project.needs_sync)

        ChangedEntityLocaleFactory.create(entity__resource__project=project)
        assert_true(project.needs_sync)

        project = ProjectFactory.create()
        assert_false(project.needs_sync)

        del project.unsynced_locales
        ProjectLocaleFactory.create(
            project=project,
            locale=LocaleFactory.create()
        )
        assert_true(project.needs_sync)

    def test_get_latest_activity_with_latest(self):
        """
        If the project has a latest_translation and no locale is given,
        return it.
        """
        project = ProjectFactory.create()
        translation = TranslationFactory.create(entity__resource__project=project)
        project.latest_translation = translation
        project.save()

        assert_equal(project.get_latest_activity(), translation.latest_activity)

    def test_get_latest_activity_without_latest(self):
        """
        If the project doesn't have a latest_translation and no locale
        is given, return None.
        """
        project = ProjectFactory.create(latest_translation=None)
        assert_is_none(project.get_latest_activity())

    def test_get_latest_activity_with_locale(self):
        """
        If a locale is given, defer to
        ProjectLocale.get_latest_activity.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        with patch.object(ProjectLocale, 'get_latest_activity') as mock_get_latest_activity:
            mock_get_latest_activity.return_value = 'latest'
            assert_equal(project.get_latest_activity(locale=locale), 'latest')
            mock_get_latest_activity.assert_called_with(project, locale)


class LocalePartsTests(TestCase):
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
        TranslatedResourceFactory.create(resource=self.resource, locale=self.locale)

    def test_parts_stats_no_page_one_resource(self):
        """
        Return resource paths and stats if no subpage and one resource defined.
        """
        details = self.locale.parts_stats(self.project)

        assert_equal(len(details), 2)
        assert_equal(details[0]['title'], '/main/path.po')
        assert_equal(details[0]['translated_strings'], 0)

    def test_parts_stats_no_page_multiple_resources(self):
        """
        Return resource paths and stats for locales resources are available for.
        """
        resource_other = ResourceFactory.create(
            project=self.project,
            path='/other/path.po'
        )
        EntityFactory.create(resource=resource_other)
        TranslatedResourceFactory.create(resource=resource_other, locale=self.locale)
        TranslatedResourceFactory.create(resource=resource_other, locale=self.locale_other)

        details = self.locale.parts_stats(self.project)
        details_other = self.locale_other.parts_stats(self.project)

        assert_equal(details[0]['title'], '/main/path.po')
        assert_equal(details[0]['translated_strings'], 0)
        assert_equal(details[1]['title'], '/other/path.po')
        assert_equal(details[1]['translated_strings'], 0)
        assert_equal(len(details_other), 2)
        assert_equal(details_other[0]['title'], '/other/path.po')
        assert_equal(details_other[0]['translated_strings'], 0)

    def test_parts_stats_pages_not_tied_to_resources(self):
        """
        Return subpage name and stats.
        """
        SubpageFactory.create(project=self.project, name='Subpage')

        details = self.locale.parts_stats(self.project)

        assert_equal(details[0]['title'], 'Subpage')
        assert_equal(details[0]['translated_strings'], 0)

    def test_parts_stats_pages_tied_to_resources(self):
        """
        Return subpage name and stats for locales resources are available for.
        """
        resource_other = ResourceFactory.create(
            project=self.project,
            path='/other/path.po'
        )
        EntityFactory.create(resource=resource_other)
        TranslatedResourceFactory.create(resource=resource_other, locale=self.locale)
        TranslatedResourceFactory.create(resource=resource_other, locale=self.locale_other)
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

        details = self.locale.parts_stats(self.project)
        details_other = self.locale_other.parts_stats(self.project)

        assert_equal(details[0]['title'], 'Other Subpage')
        assert_equal(details[0]['translated_strings'], 0)
        assert_equal(details[1]['title'], 'Subpage')
        assert_equal(details[1]['translated_strings'], 0)
        assert_equal(details_other[0]['title'], 'Other Subpage')
        assert_equal(details_other[0]['translated_strings'], 0)


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
            url='https://example.com/path/{locale_code}/',
            project__slug='test-project',
        )
        locale = LocaleFactory.create(code='test-locale')

        with self.settings(MEDIA_ROOT='/media/root'):
            assert_equal(
                repo.locale_checkout_path(locale),
                '/media/root/projects/test-project/path/test-locale'
            )

    def test_locale_checkout_path_non_multi_locale(self):
        """If the repo isn't multi-locale, throw a ValueError."""
        repo = RepositoryFactory.create()
        locale = LocaleFactory.create()
        with assert_raises(ValueError):
            repo.locale_checkout_path(locale)

    def test_locale_url(self):
        """Fill in the {locale_code} variable in the URL."""
        repo = RepositoryFactory.create(
            url='https://example.com/path/to/{locale_code}/',
        )
        locale = LocaleFactory.create(code='test-locale')

        assert_equal(repo.locale_url(locale), 'https://example.com/path/to/test-locale/')

    def test_locale_url_non_multi_locale(self):
        """If the repo isn't multi-locale, throw a ValueError."""
        repo = RepositoryFactory.create()
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
        )

        with assert_raises(ValueError):
            repo.url_for_path('/media/root/path/to/match/foo/bar.po')

    @patch('pontoon.base.models.update_from_vcs')
    @patch('pontoon.base.models.get_revision')
    def test_pull(self, mock_get_revision, update_from_vcs):
        repo = RepositoryFactory.create(type='git', url='https://example.com')
        mock_get_revision.return_value = 'asdf'
        assert_equal(repo.pull(), {'single_locale': 'asdf'})
        update_from_vcs.assert_called_with(
            'git',
            'https://example.com',
            repo.checkout_path,
            ''
        )

    @patch('pontoon.base.models.update_from_vcs')
    @patch('pontoon.base.models.get_revision')
    def test_pull_multi_locale(self, mock_get_revision, update_from_vcs):
        """
        If the repo is multi-locale, pull all of the repos for the
        active locales.
        """
        locale1 = LocaleFactory.create(code='locale1')
        locale2 = LocaleFactory.create(code='locale2')
        repo = RepositoryFactory.create(
            type='git',
            url='https://example.com/{locale_code}/',
            project__locales=[locale1, locale2]
        )

        repo.locale_url = lambda locale: 'https://example.com/' + locale.code
        repo.locale_checkout_path = lambda locale: '/media/' + locale.code

        # Return path as the revision so different locales return
        # different values.
        mock_get_revision.side_effect = lambda type, path: path

        assert_equal(repo.pull(), {
            'locale1': '/media/locale1',
            'locale2': '/media/locale2'
        })
        update_from_vcs.assert_has_calls([
            call('git', 'https://example.com/locale1', '/media/locale1', ''),
            call('git', 'https://example.com/locale2', '/media/locale2', '')
        ])

    def test_commit(self):
        repo = RepositoryFactory.create(type='git', url='https://example.com')
        with patch('pontoon.base.models.commit_to_vcs') as commit_to_vcs:
            repo.commit('message', 'author', 'path')
            commit_to_vcs.assert_called_with(
                'git',
                'path',
                'message',
                'author',
                '',
                'https://example.com',
            )

    def test_commit_multi_locale(self):
        """
        If the repo is multi-locale, use the url from url_for_path for
        committing.
        """
        repo = RepositoryFactory.create(
            type='git',
            url='https://example.com/{locale_code}/',
        )

        repo.url_for_path = Mock(return_value='https://example.com/for_path')
        with patch('pontoon.base.models.commit_to_vcs') as commit_to_vcs:
            repo.commit('message', 'author', 'path')
            commit_to_vcs.assert_called_with(
                'git',
                'path',
                'message',
                'author',
                '',
                'https://example.com/for_path',
            )
            repo.url_for_path.assert_called_with('path')


class UserTranslationManagerTests(TestCase):
    def test_users_without_translations(self):
        """
        Checks if user contributors without translations aren't returned.
        """
        active_contributor = TranslationFactory.create(user__email='active@example.com').user
        inactive_contributor = UserFactory.create(email='inactive@example.com')

        top_contributors = User.translators.with_translation_counts()
        assert_true(active_contributor in top_contributors)
        assert_true(inactive_contributor not in top_contributors)

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

        assert_equal(len(top_contributors), 100)

    def create_contributor_with_translation_counts(
        self, approved=0, unapproved=0, needs_work=0, **kwargs
    ):
        """
        Helper method, creates contributor with given translations counts.
        """
        contributor = UserFactory.create()
        TranslationFactory.create_batch(approved, user=contributor, approved=True, **kwargs)
        TranslationFactory.create_batch(
            unapproved, user=contributor, approved=False, fuzzy=False, **kwargs
        )
        TranslationFactory.create_batch(needs_work, user=contributor, fuzzy=True, **kwargs)
        return contributor

    def test_translation_counts(self):
        """Checks if translation counts are calculated properly.

        Tests creates 3 contributors with different numbers translations and checks if their
        counts match.

        """
        first_contributor = self.create_contributor_with_translation_counts(
            approved=7, unapproved=3, needs_work=2
        )
        second_contributor = self.create_contributor_with_translation_counts(
            approved=5, unapproved=9, needs_work=2
        )
        third_contributor = self.create_contributor_with_translation_counts(
            approved=1, unapproved=2, needs_work=5
        )

        top_contributors = User.translators.with_translation_counts()
        assert_equal(len(top_contributors), 3)

        assert_equal(top_contributors[0], second_contributor)
        assert_equal(top_contributors[1], first_contributor)
        assert_equal(top_contributors[2], third_contributor)

        assert_attributes_equal(
            top_contributors[0],
            translations_count=16,
            translations_approved_count=5,
            translations_unapproved_count=9,
            translations_needs_work_count=2,
        )
        assert_attributes_equal(
            top_contributors[1],
            translations_count=12,
            translations_approved_count=7,
            translations_unapproved_count=3,
            translations_needs_work_count=2,
        )
        assert_attributes_equal(
            top_contributors[2],
            translations_count=8,
            translations_approved_count=1,
            translations_unapproved_count=2,
            translations_needs_work_count=5,
        )

    def test_period_filters(self):
        """Total counts should be filtered by given date.

        Test creates 2 contributors with different activity periods and checks if they are
        filtered properly.

        """
        first_contributor = self.create_contributor_with_translation_counts(
            approved=12, unapproved=1, needs_work=2, date=aware_datetime(2015, 3, 2)
        )

        # Second contributor
        self.create_contributor_with_translation_counts(
            approved=2, unapproved=11, needs_work=2, date=aware_datetime(2015, 6, 1)
        )

        TranslationFactory.create_batch(
            5, approved=True, user=first_contributor, date=aware_datetime(2015, 7, 2)
        )

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 6, 10))

        assert_equal(len(top_contributors), 1)
        assert_attributes_equal(
            top_contributors[0],
            translations_count=5,
            translations_approved_count=5,
            translations_unapproved_count=0,
            translations_needs_work_count=0,
        )

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 5, 10))

        assert_equal(len(top_contributors), 2)
        assert_attributes_equal(
            top_contributors[0],
            translations_count=15,
            translations_approved_count=2,
            translations_unapproved_count=11,
            translations_needs_work_count=2,
        )
        assert_attributes_equal(
            top_contributors[1],
            translations_count=5,
            translations_approved_count=5,
            translations_unapproved_count=0,
            translations_needs_work_count=0,
        )

        top_contributors = User.translators.with_translation_counts(aware_datetime(2015, 1, 10))

        assert_equal(len(top_contributors), 2)
        assert_attributes_equal(
            top_contributors[0],
            translations_count=20,
            translations_approved_count=17,
            translations_unapproved_count=1,
            translations_needs_work_count=2,
        )
        assert_attributes_equal(
            top_contributors[1],
            translations_count=15,
            translations_approved_count=2,
            translations_unapproved_count=11,
            translations_needs_work_count=2,
        )

    def test_query_args_filtering(self):
        """
        Tests if query args are honored properly and contributors are filtered.
        """
        locale_first, locale_second = LocaleFactory.create_batch(2)

        first_contributor = self.create_contributor_with_translation_counts(
            approved=12, unapproved=1, needs_work=2, locale=locale_first)
        second_contributor = self.create_contributor_with_translation_counts(
            approved=11, unapproved=1, needs_work=2, locale=locale_second)
        third_contributor = self.create_contributor_with_translation_counts(
            approved=10, unapproved=12, needs_work=2, locale=locale_first)

        # Testing filtering for the first locale
        top_contributors = User.translators.with_translation_counts(
            aware_datetime(2015, 1, 1),
            Q(locale=locale_first)
        )
        assert_equal(len(top_contributors), 2)
        assert_equal(top_contributors[0], third_contributor)
        assert_attributes_equal(
            top_contributors[0],
            translations_count=24,
            translations_approved_count=10,
            translations_unapproved_count=12,
            translations_needs_work_count=2,
        )

        assert_equal(top_contributors[1], first_contributor)
        assert_attributes_equal(
            top_contributors[1],
            translations_count=15,
            translations_approved_count=12,
            translations_unapproved_count=1,
            translations_needs_work_count=2,
        )

        # Testing filtering for the second locale
        top_contributors = User.translators.with_translation_counts(
            aware_datetime(2015, 1, 1),
            Q(locale=locale_second)
        )

        assert_equal(len(top_contributors), 1)
        assert_equal(top_contributors[0], second_contributor)
        assert_attributes_equal(
            top_contributors[0],
            translations_count=14,
            translations_approved_count=11,
            translations_unapproved_count=1,
            translations_needs_work_count=2,
        )


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
            string_plural='Plural Source String',
            key='Source String'
        )
        self.other_entity = EntityFactory.create(
            resource=self.other_resource,
            string='Other Source String',
            key='Key' + KEY_SEPARATOR + 'Other Source String'
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
        # Obsolete_entity
        EntityFactory.create(
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
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale)
        )

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
                'approved': False,
                'rejected': False
            }, {
                'pk': self.main_translation_plural.pk,
                'fuzzy': False,
                'string': 'Translated Plural String',
                'approved': False,
                'rejected': False
            }],
            'order': 0,
            'source': [],
            'original_plural': 'Plural Source String',
            'marked_plural': 'Plural Source String',
            'pk': self.main_entity.pk,
            'original': 'Source String',
            'visible': False,
            'terms': defaultdict(list),
        })

    def test_for_project_locale_paths(self):
        """
        If paths specified, return project entities from these paths only along
        with their translations for locale.
        """
        paths = ['other.lang']
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale, paths)
        )

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
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale, subpages)
        )

        assert_equal(len(entities), 1)
        self.assert_serialized_entity(
            entities[0], 'main.lang', 'Source String', 'Translated String')

    def test_for_project_locale_plurals(self):
        """
        For pluralized strings, return all available plural forms.
        """
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale)
        )

        assert_equal(entities[0]['original'], 'Source String')
        assert_equal(entities[0]['original_plural'], 'Plural Source String')
        assert_equal(entities[0]['translation'][0]['string'], 'Translated String')
        assert_equal(entities[0]['translation'][1]['string'], 'Translated Plural String')

    def test_for_project_locale_order(self):
        """
        Return entities in correct order.
        """
        # First entity
        EntityFactory.create(
            order=1,
            resource=self.main_resource,
            string='Second String'
        )
        # Second entity
        EntityFactory.create(
            order=0,
            resource=self.main_resource,
            string='First String'
        )
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale)
        )
        assert_equal(entities[1]['original'], 'First String')
        assert_equal(entities[2]['original'], 'Second String')

    def test_for_project_locale_cleaned_key(self):
        """
        If key contais source string and Translate Toolkit separator,
        remove them.
        """
        entities = Entity.map_entities(
            self.locale, Entity.for_project_locale(self.project, self.locale)
        )

        assert_equal(entities[0]['key'], '')
        assert_equal(entities[1]['key'], 'Key')


class LocaleTests(TestCase):
    def test_get_latest_activity_with_latest(self):
        """
        If the locale has a latest_translation and no project is given,
        return it.
        """
        translation = TranslationFactory.create()
        locale = LocaleFactory.create(latest_translation=translation)

        assert_equal(locale.get_latest_activity(), translation.latest_activity)

    def test_get_latest_activity_without_latest(self):
        """
        If the locale doesn't have a latest_translation and no project
        is given, return None.
        """
        locale = LocaleFactory.create(latest_translation=None)
        assert_is_none(locale.get_latest_activity())

    def test_get_latest_activity_with_project(self):
        """
        If a locale is given, defer to
        ProjectLocale.get_latest_activity.
        """
        locale = LocaleFactory.create()
        project = ProjectFactory.create(locales=[locale])

        with patch.object(ProjectLocale, 'get_latest_activity') as mock_get_latest_activity:
            mock_get_latest_activity.return_value = 'latest'
            assert_equal(locale.get_latest_activity(project=project), 'latest')
            mock_get_latest_activity.assert_called_with(locale, project)

    def test_translators_group(self):
        """
        Tests if user has permission to translate locales after assigment.
        """
        user = UserFactory.create()
        [first_locale, second_locale] = LocaleFactory.create_batch(2)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), False)

        user.groups.add(second_locale.translators_group)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), True)

        user.groups.add(first_locale.translators_group)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), True)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), True)

    def test_managers_group(self):
        """
        Tests if user has permission to manage and translate locales after assigment.
        """
        user = UserFactory.create()
        [first_locale, second_locale] = LocaleFactory.create_batch(2)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), False)
        assert_equal(user.has_perm('base.can_manage_locale'), False)
        assert_equal(user.has_perm('base.can_manage_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_manage_locale', second_locale), False)

        user.groups.add(second_locale.managers_group)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), True)
        assert_equal(user.has_perm('base.can_manage_locale'), False)
        assert_equal(user.has_perm('base.can_manage_locale', first_locale), False)
        assert_equal(user.has_perm('base.can_manage_locale', second_locale), True)

        user.groups.add(first_locale.managers_group)

        assert_equal(user.has_perm('base.can_translate_locale'), False)
        assert_equal(user.has_perm('base.can_translate_locale', first_locale), True)
        assert_equal(user.has_perm('base.can_translate_locale', second_locale), True)
        assert_equal(user.has_perm('base.can_manage_locale'), False)
        assert_equal(user.has_perm('base.can_manage_locale', first_locale), True)
        assert_equal(user.has_perm('base.can_manage_locale', second_locale), True)


class ProjectLocaleTests(TestCase):
    def setUp(self):
        super(ProjectLocaleTests, self).setUp()

        self.locale = LocaleFactory.create()
        self.project = ProjectFactory.create()

    def test_get_latest_activity_doesnt_exist(self):
        """
        If no ProjectLocale exists with the given project/locale,
        return None.
        """
        assert_false(ProjectLocale.objects
                     .filter(project=self.project, locale=self.locale)
                     .exists())
        assert_is_none(ProjectLocale.get_latest_activity(self.project, self.locale))

    def test_get_latest_activity_no_latest(self):
        """
        If the matching ProjectLocale has no latest_translation, return
        None.
        """
        ProjectLocaleFactory.create(
            project=self.project,
            locale=self.locale,
            latest_translation=None
        )

        assert_is_none(ProjectLocale.get_latest_activity(self.project, self.locale))

    def test_get_latest_activity_success(self):
        """
        If the matching ProjectLocale has a latest_translation, return
        it's latest_activity.
        """
        translation = TranslationFactory.create(
            locale=self.locale,
            entity__resource__project=self.project
        )
        ProjectLocaleFactory.create(
            project=self.project,
            locale=self.locale,
            latest_translation=translation
        )

        assert_equal(
            ProjectLocale.get_latest_activity(self.project, self.locale),
            translation.latest_activity
        )

    def test_translators_group(self):
        """
        Tests if user has permission to translate project at specific locale after assigment.
        """

        project_locale = ProjectLocaleFactory.create(
            project=self.project,
            locale=self.locale,
            latest_translation=None,
            has_custom_translators=True,
        )
        user = UserFactory.create()

        assert_equal(user.can_translate(locale=self.locale, project=self.project), False)

        user.groups.add(project_locale.translators_group)

        assert_equal(user.can_translate(locale=self.locale, project=self.project), True)

        project_locale.has_custom_translators = False
        project_locale.save()

        assert_equal(user.can_translate(locale=self.locale, project=self.project), False)


class TranslationTests(TestCase):
    def assert_latest_translation(self, instance, translation):
        instance.refresh_from_db()
        assert_equal(instance.latest_translation, translation)

    def test_save_latest_translation_update(self):
        """
        When a translation is saved, update the latest_translation
        attribute on the related project, locale, translatedresource,
        and project_locale objects.
        """
        locale = LocaleFactory.create(latest_translation=None)
        project = ProjectFactory.create(locales=[locale], latest_translation=None)
        resource = ResourceFactory.create(project=project)
        translatedresource = TranslatedResourceFactory.create(
            locale=locale, resource=resource, latest_translation=None
        )
        project_locale = ProjectLocale.objects.get(locale=locale, project=project)

        assert_is_none(locale.latest_translation)
        assert_is_none(project.latest_translation)
        assert_is_none(translatedresource.latest_translation)
        assert_is_none(project_locale.latest_translation)

        translation = TranslationFactory.create(
            locale=locale,
            entity__resource=resource,
            date=aware_datetime(1970, 1, 1)
        )
        self.assert_latest_translation(locale, translation)
        self.assert_latest_translation(project, translation)
        self.assert_latest_translation(translatedresource, translation)
        self.assert_latest_translation(project_locale, translation)

        # Ensure translation is replaced for newer translations
        newer_translation = TranslationFactory.create(
            locale=locale,
            entity__resource=resource,
            date=aware_datetime(1970, 2, 1)
        )
        self.assert_latest_translation(locale, newer_translation)
        self.assert_latest_translation(project, newer_translation)
        self.assert_latest_translation(translatedresource, newer_translation)
        self.assert_latest_translation(project_locale, newer_translation)

        # Ensure translation isn't replaced for older translations.
        TranslationFactory.create(
            locale=locale,
            entity__resource=resource,
            date=aware_datetime(1970, 1, 5)
        )
        self.assert_latest_translation(locale, newer_translation)
        self.assert_latest_translation(project, newer_translation)
        self.assert_latest_translation(translatedresource, newer_translation)
        self.assert_latest_translation(project_locale, newer_translation)

        # Ensure approved_date is taken into consideration as well.
        newer_approved_translation = TranslationFactory.create(
            locale=locale,
            entity__resource=resource,
            approved_date=aware_datetime(1970, 3, 1)
        )
        self.assert_latest_translation(locale, newer_approved_translation)
        self.assert_latest_translation(project, newer_approved_translation)
        self.assert_latest_translation(translatedresource, newer_approved_translation)
        self.assert_latest_translation(project_locale, newer_approved_translation)

    def test_save_latest_translation_missing_project_locale(self):
        """
        If a translation is saved for a locale that isn't active on the
        project, do not fail due to a missing ProjectLocale.
        """
        locale = LocaleFactory.create(latest_translation=None)
        project = ProjectFactory.create(latest_translation=None)
        resource = ResourceFactory.create(project=project)
        translatedresource = TranslatedResourceFactory.create(
            locale=locale, resource=resource, latest_translation=None
        )

        # This calls .save, this should fail if we're not properly
        # handling the missing ProjectLocale.
        translation = TranslationFactory.create(
            locale=locale,
            entity__resource=resource,
            date=aware_datetime(1970, 1, 1)
        )

        self.assert_latest_translation(locale, translation)
        self.assert_latest_translation(project, translation)
        self.assert_latest_translation(translatedresource, translation)

    def test_approved_translation_in_memory(self):
        """
        Every save of approved translation should generate a new
        entry in the translation memory.
        """
        translation = TranslationFactory.create(approved=True)
        assert TranslationMemoryEntry.objects.get(
            source=translation.entity.string,
            target=translation.string,
            locale=translation.locale
        )

    def test_unapproved_translation_not_in_memory(self):
        """
        Unapproved translation shouldn't be in the translation memory.
        """
        translation = TranslationFactory.create(approved=False)
        with assert_raises(TranslationMemoryEntry.DoesNotExist):
            TranslationMemoryEntry.objects.get(
                source=translation.entity.string,
                target=translation.string,
                locale=translation.locale
            )

    def test_rejected_translation_not_in_memory(self):
        """
        When translation is deleted, its corresponding TranslationMemoryEntry
        needs to be deleted, too.
        """
        translation = TranslationFactory.create(rejected=True)
        with assert_raises(TranslationMemoryEntry.DoesNotExist):
            TranslationMemoryEntry.objects.get(
                source=translation.entity.string,
                target=translation.string,
                locale=translation.locale
            )


class SearchQueryTests(TestCase):
    """
    Test search queries.
    """
    def setUp(self):
        super(SearchQueryTests, self).setUp()
        self.project = ProjectFactory.create()
        self.locale = LocaleFactory.create()
        entities = [
            {
                'key': 'access.key',
                'string': 'First entity string',
                'string_plural': 'First plural string',
                'comment': 'random notes'
            },
            {
                'key': 'second.key',
                'string': 'Second entity string',
                'string_plural': 'Second plural string',
                'comment': 'random'
            },
            {
                'key': 'third.key',
                'string': u'Third entity string with some twist: ZAŻÓŁĆ GĘŚLĄ',
                'string_plural': 'Third plural',
                'comment': 'even more random notes'
            },
        ]
        translations = [
            {
                'string': 'First translation',
            },
            {
                'string': 'Second translation',
            },
            {
                'string': 'Third translation',
            },
        ]
        self.entities = [
            EntityFactory.create(resource__project=self.project, **e)
            for e in entities
        ]

        self.translations = [
            TranslationFactory.create(
                locale=self.locale,
                entity=self.entities[i],
                entity__resource__project=self.project,
                **t
            )
            for (i, t) in enumerate(translations)
        ]

    def search(self, query):
        """
        Helper method for shorter search syntax.
        """
        return list(Entity.for_project_locale(
            self.project,
            self.locale,
            search=query,
        ))

    def test_invalid_query(self):
        """
        We shouldn't return any records if there aren't any matching rows.
        """
        assert_equal(self.search("localization"), [])
        assert_equal(self.search("testing search queries"), [])
        assert_equal(self.search(u"Ń"), [])

    def test_search_entities(self):
        """
        Search via querystrings available in entities.
        """
        assert_equal(self.search('e'), self.entities)
        assert_equal(self.search('entity string'), self.entities)

        assert_equal(self.search(u'first entity'), [self.entities[0]])
        assert_equal(self.search(u'second entity'), [self.entities[1]])
        assert_equal(self.search(u'third entity'), [self.entities[2]])

        # Check if we're able search by unicode characters.
        assert_equal(self.search(u'gęślą'), [self.entities[2]])

    def test_search_translation(self):
        """
        Search entities by contents of their translations.
        """
        assert_equal(self.search('translation'), self.entities)
        assert_equal(self.search('first translation'), [self.entities[0]])
        assert_equal(self.search('second translation'), [self.entities[1]])
        assert_equal(self.search('third translation'), [self.entities[2]])


class EntityFilterTests(TestCase):
    """
    Tests all filters provided by the entity manager.
    """
    def setUp(self):
        self.locale = LocaleFactory.create()
        self.plural_locale = LocaleFactory.create(cldr_plurals='1,5')

    def test_translated(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=True
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            fuzzy=True
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity,
            approved=True
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.translated(self.locale))
            )
        )

    def test_translated_plurals(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            plural_form=1
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=second_entity,
            approved=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=True,
            plural_form=1
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.translated(self.plural_locale))
            )
        )

    def test_fuzzy(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            fuzzy=True
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=True
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity,
            fuzzy=True
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.fuzzy(self.locale))
            )
        )

    def test_fuzzy_plurals(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            fuzzy=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            fuzzy=True,
            plural_form=1
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=second_entity,
            fuzzy=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            fuzzy=True,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            fuzzy=True,
            plural_form=1
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.fuzzy(self.plural_locale))
            )
        )

    def test_missing(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=True
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity
        )

        assert_equal(
            {second_entity},
            set(
                Entity.objects
                .filter(Entity.objects.missing(self.locale))
            )
        )

    def test_partially_translated_plurals(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(
            3,
            string='Unchanged string',
            string_plural='Unchanged plural string'
        )

        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            plural_form=0
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            plural_form=1
        )

        TranslationFactory.create(
            locale=self.plural_locale,
            entity=second_entity,
            plural_form=0
        )

        assert_equal(
            {second_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.missing(self.plural_locale))
            )
        )

    def test_suggested(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=False,
            fuzzy=False,
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
        )

        assert_equal(
            {second_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.suggested(self.locale))
            )
        )

    def test_unchanged(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(
            3,
            string='Unchanged string'
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=True,
            string='Unchanged string'
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity,
            fuzzy=True,
            string='Unchanged string'
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.unchanged(self.locale))
            )
        )

    def test_missing_plural(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            fuzzy=True,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            fuzzy=True,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=True,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=True,
            plural_form=1,
        )

        assert_equal(
            {second_entity},
            set(
                Entity.objects
                .filter(Entity.objects.missing(self.plural_locale))
            )
        )

    def test_suggested_plural(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=False,
            fuzzy=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=False,
            fuzzy=False,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            plural_form=1,
        )

        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.suggested(self.plural_locale))
            )
        )

    def test_unchanged_plural(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(
            3,
            string='Unchanged string',
            string_plural='Unchanged plural string'
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            plural_form=0,
            string='Unchanged string'
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            plural_form=1,
            string='Unchanged plural string'
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            fuzzy=True,
            plural_form=0,
            string='Unchanged string'
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            fuzzy=True,
            plural_form=1,
            string='Unchanged plural string'
        )
        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.unchanged(self.plural_locale))
            )
        )

    def test_has_suggestions_plural(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(
            3,
            string='Unchanged string',
            string_plural='Unchanged plural string'
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            fuzzy=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=False,
            fuzzy=False,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=True,
            fuzzy=False,
            plural_form=1,
        )
        assert_equal(
            {first_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.has_suggestions(self.plural_locale))
            )
        )

    def test_rejected(self):
        first_entity, second_entity, third_entity = EntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=False,
            fuzzy=False,
            rejected=True,
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=True,
            fuzzy=False,
            rejected=False,
        )

        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=True,
            fuzzy=False,
            rejected=False,
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=False,
            fuzzy=False,
            rejected=True,
        )
        TranslationFactory.create(
            locale=self.locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            rejected=False,
        )
        assert_equal(
            {first_entity, second_entity},
            set(
                Entity.objects
                .filter(Entity.objects.rejected(self.locale))
            )
        )

    def test_rejected_plural(self):
        first_entity, second_entity, third_entity = PluralEntityFactory.create_batch(3)
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            fuzzy=False,
            rejected=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=first_entity,
            approved=True,
            fuzzy=False,
            rejected=False,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=second_entity,
            approved=True,
            fuzzy=False,
            rejected=False,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=second_entity,
            approved=False,
            fuzzy=False,
            rejected=True,
            plural_form=1,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            rejected=True,
            plural_form=0,
        )
        TranslationFactory.create(
            locale=self.plural_locale,
            entity=third_entity,
            approved=False,
            fuzzy=False,
            rejected=True,
            plural_form=1,
        )
        assert_equal(
            {second_entity, third_entity},
            set(
                Entity.objects
                .filter(Entity.objects.rejected(self.plural_locale))
            )
        )

    def test_combined_filters(self):
        """
        All filters should be joined by AND instead of OR.
        Tests filters against bug introduced by bug 1243115.
        """
        contributor = UserFactory.create()
        project = ProjectFactory.create()
        first_entity, second_entity = EntityFactory.create_batch(2, resource__project=project)

        TranslationFactory.create(
            locale=self.locale,
            entity=first_entity,
            approved=True,
            fuzzy=False,
            user=contributor,
        )

        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=True,
            fuzzy=False,
            user=contributor
        )

        TranslationFactory.create(
            locale=self.locale,
            entity=second_entity,
            approved=False,
            fuzzy=False,
            user=contributor,
        )

        assert_equal(
            list(Entity.for_project_locale(
                project,
                self.locale,
                status='suggested',
                author=contributor.email
            )),
            []
        )
        assert_equal(
            list(Entity.for_project_locale(
                project,
                self.locale,
                status='suggested',
                time='201001010100-205001010100'
            )),
            []
        )
