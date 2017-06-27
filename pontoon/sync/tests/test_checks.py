from textwrap import dedent

from nose.tools import assert_equal

from base.checks import check_translations
from pontoon.base.tests import (
    TestCase,
    TranslationFactory,
    ResourceFactory, EntityFactory, ProjectFactory)


class TestFailingChecks(TestCase):
    def setUp(self):
        self.project = ProjectFactory.create()

    def generate_resource_translations(self, resource_path, *translations):
        """
        Generate translation and return a tuple that will create a data-set
        ready to use in check_translation method.
        """
        resource_translations = []
        resource = ResourceFactory.create(path=resource_path, project=self.project)
        for t in translations:
            entity_data = {k[7:]: v for k, v in t.items() if k.startswith('entity_')}
            translation_data = {k: v for k, v in t.items() if not k.startswith('entity_')}
            entity = EntityFactory.create(
                resource=resource,
                **entity_data
            )

            resource_translations.append(
                TranslationFactory.create(
                    entity=entity,
                    **translation_data
                )
            )

        return (resource, resource_translations)

    def test_valid_translations(self):
        """
        Test if check functiono won't return any weird false positives.
        """
        resource_valid_translations = self.generate_resource_translations(
            'resource2.properties',
            # A set of valid translations from the second resource.
            dict(
                entity_string='Foobar2',
                string='Barfoo2',
            ),
            dict(
                entity_string='Mozilla',
                entity_string_plural='Mozillas',
                string='Allizom',
                plural_form=1
            ),
        )

        # Translation check should return an empty dict if there's no errors.
        assert_equal(check_translations(*resource_valid_translations), {})

    def test_invalid_properties_translations(self):
        resource_invalid_translations = self.generate_resource_translations(
            'resource1.properties',
            dict(
                entity_string='%s Foo %s bar %s',
                string='%d Bar %d foo %d \q %',
            ),

            # Plural form should be matched against the string plural
            dict(
                entity_string='%s Foo %s bar %s %',
                entity_string_plural='Plural setting  %s \p',
                string='%d Bar %d foo %d',
                plural_form=1
            ),

            # A valid translation to check if check_translations won't produce false positives
            dict(
                entity_string='Valid entity',
                string='Valid translation',
            ),

            # Check if comments are passed to our checker properly
            dict(
                entity_string='Invalid #1 entity',
                entity_comment='Localization_and_Plurals',
                string='Invalid #1 translation #2',
            ),
        )

        translations = resource_invalid_translations[1]
        assert_equal(
            check_translations(*resource_invalid_translations),
            {
                translations[0].pk: [
                    ('warning', u'unknown escape sequence, \\q'),
                    ('error', 'Found single %'),
                ],
                translations[1].pk: [
                    ('error', u'argument 1 `d` should be `s`')
                ],
                translations[3].pk: [
                    ('error', 'unreplaced variables in l10n')
                ]
            }
         )

    def test_invalid_dtd_translations(self):
        resource_invalid_translations = self.generate_resource_translations(
            'resource1.dtd',
            dict(
                entity_string='2005',
                string='not a number',
            ),

            dict(
                entity_string='Second &aa; entity',
                string='Testing &NonExistingKey; translation',
            ),

            dict(
                entity_string='Valid entity',
                string='&validProductName; translation',
            ),

            dict(
                entity_string='&validProductName; - 2017',
                entity_comment='Some comment',
                string='Valid translation',
            ),

            dict(
                entity_string='&validProductName; - 2017',
                entity_comment='Some comment',
                string='< translation',
            ),
        )
        translations = resource_invalid_translations[1]

        assert_equal(
            check_translations(*resource_invalid_translations),
            {
                translations[0].pk: [
                    ('warning', 'reference is a number'),
                ],
                translations[1].pk: [
                    ('warning',
                     u'Referencing unknown entity `NonExistingKey` (aa used in context, validProductName known)'),
                ],
                translations[4].pk: [
                    ('error', 'not well-formed (invalid token)')
                ]

            }
        )

    def test_invalid_fluent_translations(self):
        resource_invalid_translations = self.generate_resource_translations(
            'resource1.ftl',
            dict(
                entity_string=dedent("""
                brandName = Firefox
                    .bar = foo
                """),
                string=dedent("""
                brandName = Quantum
                """),
            ),
            dict(
                entity_string=dedent("""
                windowTitle = Old translations
                """),
                string=dedent("""
                windowTitle = New translations
                    .baz = Fuz
                """),
            ),

            # Valid translation to check if check won't produce false positives.
            dict(
                entity_string=dedent("""
                windowTitle = Old translations
                """),
                string=dedent("""
                windowTitle = New translations
                """),
            ),

            dict(
                entity_string=dedent("""
                windowTitle = Old translations
                    .bar = Foo
                """),
                string=dedent("""
                windowTitle
                    .bar = New Foo
                """),
            ),
            dict(
                entity_string=dedent("""
                windowTitle = Old translations
                    .pontoon = is cool
                """),
                string=dedent("""
                windowTitle = New translations
                    .pontoon = pontoon1
                    .pontoon = pontoon2
                """),
            ),
        )
        translations = resource_invalid_translations[1]

        assert_equal(
            check_translations(*resource_invalid_translations),
            {
                translations[0].pk: [
                    ('error', 'Missing attribute: bar'),
                ],
                translations[1].pk: [
                    ('error', 'Obsolete attribute: baz'),
                ],
                translations[3].pk: [
                    ('error', 'Missing value'),
                ],
                translations[4].pk: [
                    ('warning', 'Attribute "pontoon" occurs 2 times')
                ]

            }
        )
