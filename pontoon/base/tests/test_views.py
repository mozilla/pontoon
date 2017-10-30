# -*- coding: utf-8 -*-
from datetime import datetime
import os
import unittest

from django.test import RequestFactory

from django_nose.tools import (
    assert_equal,
    assert_true,
    assert_code,
)

from lxml import etree
from mock import patch

from pontoon.base.models import (
    Project,
    Entity,
    ProjectLocale,
    TranslatedResource,
    Translation,
)
from pontoon.base.tests import (
    assert_json,
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    TranslationMemoryFactory,
    TranslatedResourceFactory,
    TestCase,
    UserFactory,
)
from pontoon.base.utils import build_translation_memory_file


class UserTestCase(TestCase):
    """Default testcase for the views that require logged accounts."""
    def setUp(self):
        self.user = UserFactory.create()
        self.client.force_login(self.user)


class TranslationActionsTests(UserTestCase):
    """Tests actions that can be performed on a translation."""

    def setUp(self):
        super(TranslationActionsTests, self).setUp()
        project = ProjectFactory.create()
        locale = LocaleFactory.create()

        ProjectLocale.objects.create(project=project, locale=locale)

        translation = TranslationFactory.create(locale=locale, entity__resource__project=project)
        translation.approved = True
        translation.save()

        self.translation = translation

    def test_unapprove_translation(self):
        """Check if unapprove view works properly."""
        response = self.client.ajax_post('/unapprove-translation/', {
            'translation': self.translation.pk,
            'paths': [],
        })
        assert_code(response, 200)

        self.translation.refresh_from_db()
        assert_equal(self.translation.approved, False)
        assert_equal(self.translation.unapproved_user, self.user)


class TranslateTests(TestCase):
    def test_invalid_locale_and_project(self):
        """If the locale and project are both invalid, return a 404."""
        response = self.client.get('/invalid-locale/invalid-project/')
        assert_equal(response.status_code, 404)

    def test_invalid_locale_valid_project(self):
        """
        If the project is valid but the locale isn't, redirect home.
        """
        project = ProjectFactory.create(slug='valid-project')
        ResourceFactory.create(project=project)

        response = self.client.get('/invalid-locale/valid-project/path/')
        assert_equal(response.status_code, 404)

    def test_invalid_project(self):
        """If the project is invalid, redirect home."""
        LocaleFactory.create(code='fakelocale')

        response = self.client.get('/fakelocale/invalid-project/path/')
        assert_equal(response.status_code, 404)

    def test_locale_not_available(self):
        """
        If the requested locale is not available for this project,
        redirect home.
        """
        LocaleFactory.create(code='fakelocale')
        ProjectFactory.create(slug='valid-project')

        response = self.client.get('/fakelocale/valid-project/path/')
        assert_equal(response.status_code, 404)

    def test_not_authed_public_project(self):
        """
        If the user is not authenticated and we're translating project
        ID 1, return a 200.
        """
        # Clear out existing project with ID=1 if necessary.
        Project.objects.filter(id=1).delete()
        locale = LocaleFactory.create(code='fakelocale')
        project = ProjectFactory.create(id=1, slug='valid-project', locales=[locale])
        resource = ResourceFactory.create(project=project, path='foo.lang', total_strings=1)
        TranslatedResourceFactory.create(resource=resource, locale=locale)

        response = self.client.get('/fakelocale/valid-project/foo.lang/')
        assert_equal(response.status_code, 200)
        # I'd assertTemplateUsed here but it doesn't work on non-DTL
        # templates.


class ViewTestCase(TestCase):
    def setUp(self):
        """
        We don't call project synchronization during the tests, so we have to
        create dummy resource project to avoid recurse redirect at /.
        """
        ResourceFactory.create(project=Project.objects.get(pk=1))

        self.factory = RequestFactory()


class TranslationUpdateTestCase(UserTestCase):
    def setUp(self):
        super(TranslationUpdateTestCase, self).setUp()

        locale = LocaleFactory.create()
        project = ProjectFactory.create()
        ProjectLocale.objects.create(
            project=project,
            locale=locale,
        )
        resource = ResourceFactory.create(project=project)
        entity = EntityFactory.create(resource=resource)

        self.translation = TranslationFactory.create(entity=entity, locale=locale)
        self.translation.locale.translators_group.user_set.add(self.user)

    def post_translation(self, translation, **params):
        """
        Post translation with given params.
        Returns the last translation object.
        """
        update_params = {
            'locale': self.translation.locale.code,
            'entity': self.translation.entity.pk,
            'translation': translation,
            'plural_form': '-1',
            'ignore_check': 'true',
            'original': self.translation.entity.string,
        }
        update_params.update(params)

        response = self.client.ajax_post('/update/', update_params)
        assert_code(response, 200)

        return Translation.objects.last()

    def test_force_suggestions(self):
        """
        Save/suggest button should always do what the current label says and
        be independent from the user settings in different browser tabs.
        """

        # Check the default behaviour.
        translation = self.post_translation('approved translation')
        assert_true(translation.approved)

        translation = self.post_translation('approved translation2', force_suggestions='false')
        assert_true(translation.approved)

        translation = self.post_translation('unapproved translation', force_suggestions='true')
        assert_true(not(translation.approved))


class TranslateMemoryTests(ViewTestCase):
    def test_best_quality_entry(self):
        """
        Translation memory should return results entries aggregated by
        translation string.
        """
        new_locale = LocaleFactory.create()
        memory_entry = TranslationMemoryFactory.create(
            source="aaa", target="ccc", locale=new_locale
        )
        TranslationMemoryFactory.create(source="aaa", target="ddd", locale=new_locale)
        TranslationMemoryFactory.create(source="bbb", target="ccc", locale=new_locale)

        response = self.client.get('/translation-memory/', {
            'text': 'aaa',
            'pk': memory_entry.entity.pk,
            'locale': new_locale.code
        })
        assert_json(response, [{"count": 1, "source": "aaa", "quality": 100.0, "target": "ddd"}])

    def test_translation_counts(self):
        """
        Translation memory should aggregate identical translations strings
        from the different entities and count up their occurrences.
        """
        new_locale = LocaleFactory.create()
        memory_entry = TranslationMemoryFactory.create(
            source="aaaa", target="ccc", locale=new_locale
        )
        TranslationMemoryFactory.create(source="abaa", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="aaab", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="aaab", target="ccc", locale=new_locale)

        response = self.client.get('/translation-memory/', {
            'text': 'aaaa',
            'pk': memory_entry.entity.pk,
            'locale': memory_entry.locale.code
        })

        result = response.json()
        src_string = result[0].pop('source')

        assert_true(src_string in ('abaa', 'aaab', 'aaab'))
        assert_equal(
            result,
            [{
                u'count': 3,
                u'quality': 75.0,
                u'target': u'ccc',
            }]
        )

    def test_exclude_entity(self):
        """
        Exclude entity from results to avoid false positive results.
        """
        memory_entry = TranslationMemoryFactory.create(source="Pontoon Intro")
        response = self.client.get('/translation-memory/', {
            'text': 'Pontoon Intro',
            'pk': memory_entry.entity.pk,
            'locale': memory_entry.locale.code
        })
        assert_code(response, 200)
        assert_equal(response.content, '[]')

    def test_minimal_quality(self):
        """
        View shouldn't return any entries if 70% of quality at minimum.
        """
        # Generate some random entries that shouldn't be similar
        TranslationMemoryFactory.create_batch(5)

        response = self.client.get('/translation-memory/', {
            'text': 'no match',
            'pk': 2,
            'locale': 'en-GB'
        })
        assert_code(response, 200)
        assert_equal(response.content, '[]')


class EntityViewTests(TestCase):
    """
    Tests related to the get_entity view.
    """

    def setUp(self):
        self.resource = ResourceFactory.create()
        self.locale = LocaleFactory.create()
        ProjectLocale.objects.create(project=self.resource.project, locale=self.locale)
        TranslatedResource.objects.create(resource=self.resource, locale=self.locale)
        self.entities = EntityFactory.create_batch(3, resource=self.resource)
        self.entities_pks = [e.pk for e in self.entities]

    def test_inplace_mode(self):
        """
        Inplace mode of get_entites, should return all entities in a single batch.
        """
        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'inplace_editor': True,
            # Inplace mode shouldn't respect paging or limiting page
            'limit': 1,
        })

        assert_code(response, 200)
        assert_equal(response.json()['has_next'], False)
        assert_equal([e['pk'] for e in response.json()['entities']], self.entities_pks)

    @unittest.skip('Mocking of the methods is now very hard.')
    def test_entity_filters(self):
        """
        Tests if right filter calls right method in the Entity manager.
        """
        filters = (
            'missing',
            'fuzzy',
            'suggested',
            'translated',
            'unchanged',
            'has-suggestions',
            'rejected',
        )

        for filter_ in filters:
            filter_name = filter_.replace('-', '_')
            params = {
                'project': self.resource.project.slug,
                'locale': self.locale.code,
                'paths[]': [self.resource.path],
                'limit': 1,
            }

            if filter_ in ('unchanged', 'has-suggestions', 'rejected'):
                params['extra'] = filter_

            else:
                params['status'] = filter_

            with patch(
                'pontoon.base.models.Entity.objects.{}'.format(filter_name),
                return_value=getattr(Entity.objects, filter_name)(self.locale)
            ) as filter_mock:
                self.client.ajax_post('/get-entities/', params)
                assert_true(filter_mock.called)

    def test_exclude_entities(self):
        """
        Excluded entities shouldn't returned by get_entities.
        """
        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'exclude_entities': [self.entities[1].pk],
            'limit': 1,
        })

        assert_code(response, 200)

        assert_equal(response.json()['has_next'], True)
        assert_equal([e['pk'] for e in response.json()['entities']], [self.entities[0].pk, ])

        exclude_entities = ','.join(map(str, [
            self.entities[0].pk,
            self.entities[1].pk
        ]))

        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'exclude_entities': exclude_entities,
            'limit': 1,
        })

        assert_code(response, 200)

        assert_equal(response.json()['has_next'], False)
        assert_equal([e['pk'] for e in response.json()['entities']], [self.entities[2].pk])


def assert_xml(xml_content, expected_xml=None, dtd_path=None):
    """Provided xml_content should be a valid XML string and be equal to expected_xml."""

    def to_xml(string):
        """
        A shortcut function to load xml.
        """
        return etree.fromstring(string)

    def normalize_xml(xml_string):
        """
        Helps to normalize different xml to the same format, indentation etc.
        At the same time, content is validated.
        """
        return etree.tostring(to_xml(xml_content))

    validated_xml = normalize_xml(xml_content)

    if dtd_path:
        dtd = etree.DTD(dtd_path)
        if not dtd.validate(to_xml(xml_content)):
            raise AssertionError(dtd.error_log)

    if expected_xml is not None:
        assert_equal(validated_xml, normalize_xml(expected_xml))


class TMXDownloadViewTests(TestCase):
    """
    Backend should be able to return a valid (and empty) TMX file.
    """
    def setUp(self):
        self.project = EntityFactory.create().resource.project
        self.locale = LocaleFactory.create()

    def get_tmx_file(self, locale, project):
        """Shortcut function to request tmx contents from server."""
        response = self.client.get(
            '/{locale}/{project}/{locale}.{project}.tmx'.format(
                locale=locale,
                project=project
            )
        )
        return response

    def test_locale_file_download(self):
        """By download the data."""
        response = self.get_tmx_file(self.locale.code, self.project.slug)

        assert_code(response, 200)
        assert_xml(''.join(response.streaming_content).encode('utf-8'))

    def test_invalid_parameters(self):
        """Validate locale code and don't return data."""

        assert_code(self.get_tmx_file('invalidlocale', 'invalidproject'), 404)
        assert_code(self.get_tmx_file(self.locale.code, 'invalidproject'), 404)


class TMXFileGeneratorTests(TestCase):
    @property
    def samples_root(self):
        """Path to the folder with artifacts required to test TMX functionality."""

        tests_root = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(tests_root, 'samples')

    def get_sample(self, file_path):
        """
        Retrieve contents of artifact that is required to run/assert a part of test.
        """

        with open(os.path.join(self.samples_root, file_path), 'rU') as f:
            return f.read().decode('utf-8')

    def test_empty_tmx_file(self):
        tmx_contents = build_translation_memory_file(
            datetime(2010, 01, 01),
            'sl',
            ()
        )
        assert_xml(
            ''.join(tmx_contents).encode('utf-8'),
            self.get_sample('tmx/no_entries.tmx'),
            os.path.join(self.samples_root, 'tmx/tmx14.dtd')
        )

    def test_valid_entries(self):
        tmx_contents = build_translation_memory_file(
            datetime(2010, 01, 01),
            'sl',
            (
                ('aa/bb/ccc', 'xxx', 'source string', 'translation', 'Pontoon App', 'pontoon'),

                # Test escape of characters
                (
                    'aa/bb/ccc', 'x&x&x#"', 'source string', 'translation', 'Pontoon & App',
                    'pontoon'
                ),

                # Handle unicode characters
                (
                    'aa/bb/ccc', 'xxx', u'source string łążśźć', u'translation łążśźć', 'pontoon',
                    'pontoon'
                ),

                # Handle html content
                (
                    'aa/bb/ccc', 'xxx', u'<p>source <strong>string</p>',
                    u'<p>translation łążśźć</p>', 'pontoon', 'pontoon'
                ),
            )
        )
        assert_xml(
            ''.join(tmx_contents).encode('utf-8'),
            self.get_sample('tmx/valid_entries.tmx'),
            os.path.join(self.samples_root, 'tmx/tmx14.dtd')
        )


class UserRoleLogLocaleTest(TestCase):
    """
    Check if The Locale Permissions Form saves logs of changes on users groups they are
    assigned to.
    """
    def test_add_user_to_group(self):
        # Check idempotency
        assert False

    def test_remove_user_from_group(self):
        assert False
