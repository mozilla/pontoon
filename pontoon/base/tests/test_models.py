# -*- coding: utf-8 -*-

from django_nose.tools import (
    assert_equal,
    assert_true,
)
from django.db.models import Q

from pontoon.base.models import (
    Entity,
    User
)
from pontoon.base.tests import (
    assert_attributes_equal,
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    SubpageFactory,
    TestCase,
    TranslationFactory,
    UserFactory
)
from pontoon.base.utils import aware_datetime
from pontoon.sync import KEY_SEPARATOR


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
