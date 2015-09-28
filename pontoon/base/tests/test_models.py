from django_nose.tools import assert_equal

from pontoon.base.models import Entity, Translation
from pontoon.base.tests import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    SubpageFactory,
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
                'pk': 4,
                'fuzzy': False,
                'string': 'Translated String',
                'approved': False
            }, {
                'pk': 5,
                'fuzzy': False,
                'string': 'Translated Plural String',
                'approved': False
            }],
            'order': 0,
            'source': [],
            'original_plural': 'Plural Source String',
            'marked_plural': 'Plural Source String',
            'pk': 4,
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
