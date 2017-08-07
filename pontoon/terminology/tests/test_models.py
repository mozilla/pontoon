from nose.tools import assert_equal, assert_true, assert_false

from pontoon.base.tests import (
    TestCase,
    EntityFactory,
)
from pontoon.base.utils import get_singulars

from pontoon.terminology.models import (
    Term,
)
from pontoon.terminology.term_indexes import CachedDBTermIndex, DBTermIndex
from pontoon.terminology.tests import TermFactory


class _TestEntityTermMatching(TestCase):
    """
    A set of tests that should be executed agains every available term index.
    """
    term_index_cls = None
    def setUp(self):
        # Save an index in order to restore it later.
        self.original_term_index = Term.objects.term_index

        Term.objects.term_index = self.term_index_cls

    def tearDown(self):
        """
        Some of indexes (e.g. cache-based) require to rebuild their state between tests.
        """
        Term.objects.term_index.reset()

        # Restore original index to the main class.
        Term.objects.term_index = self.original_term_index

    def generate_sample_terms(self, *sample_terms):
        """"""
        terms = []
        for index, source_term in enumerate(sample_terms):
            db_term = {
                'source_term_singulars': ' '.join(get_singulars(source_term)),
                'description': '{} description.'.format(source_term),
                'source_term': source_term,
            }
            terms.append(TermFactory.create(**db_term))
        return terms

    def generate_sample_entities(self, *sample_entities):
        """Generate sample Entities that"""
        entities = []
        for db_entity in sample_entities:
            entity = EntityFactory.create(**db_entity)
            entities.append(entity)
        return entities

    def assert_terms_phrases(self, entity, terms):
        """
        Assert term
        """
        if not terms:
            assert_false(entity.terms.exists())
            return

        for term, expected_phrases in terms:
            entity_terms = entity.terms.filter(term=term)
            assert_true(entity_terms.exists(), term.source_term)

            test_phrases = {et.phrase for et in entity_terms}
            assert_equal(test_phrases, expected_phrases)

            for entity_term in entity_terms:
                assert_true(entity_term.phrase in entity.string or \
                            entity_term.phrase in entity.string)

    def test_matching_single_word_terms(self):
        """
        Check if algorithm is able to match terms with single word.
        """
        browser, mail, desktop = self.generate_sample_terms(
            'browser',
            'mail',
            'desktop'
        )

        entity1, entity2, entity3, entity4 = self.generate_sample_entities(
            {'string': 'Firefox is a browser.'},

            # Matching should match two terms.
            {'string': 'The web is full of browser and mail boxes.'},

            # Matching should be able to match plural strings to their respective terms.
            {'string': 'Developers like to use desktops.'},

            # Matching should be able to match mixed case terms
            {'string': 'Developers like to use Desktops.'},
        )
        self.assert_terms_phrases(entity1, (
            (browser, {'browser'}),
        ))
        self.assert_terms_phrases(entity2, (
            (browser, {'browser'}),
            (mail, {'mail'})
        ))
        self.assert_terms_phrases(entity3, (
            (desktop, {'desktops'}),
        ))
        self.assert_terms_phrases(entity4, (
            (desktop, {'Desktops'}),
        ))

    def test_matching_multi_word_terms(self):
        """
        Check if algorithm is able to match terms with single word.
        """
        browsers, mail_clients, mail, desktops = self.generate_sample_terms(
            'web browser',
            'mail client',
            'mail',
            'PC desktop'
        )

        entity1, entity2, entity3, entity4, entity5 = self.generate_sample_entities(
            {'string': 'Firefox & Chrome are web browsers.'},

            # Matching should match two terms.
            {'string': 'The web is full of web browsers and mail clients.'},

            # Matching should be able to match plural strings to their respective terms.
            {'string': 'Developers like to use pc desktops.'},

            # Matching should be able to match strings with mixed-case phrases
            {'string': 'Developers like to use PC desktops.'},

            # Test if algorithm is able terms
            {'string': 'Mail clients receive mail because that\'s their purpose.'},
        )
        self.assert_terms_phrases(entity1, (
            (browsers, {'web browsers'}),
        ))
        self.assert_terms_phrases(entity2, (
            (browsers, {'web browsers'}),
            (mail_clients, {'mail clients'})
        ))
        self.assert_terms_phrases(entity3, (
            (desktops, {'pc desktops'}),
        ))
        self.assert_terms_phrases(entity4, (
            (desktops, {'PC desktops'}),
        ))
        self.assert_terms_phrases(entity5, (
            (mail_clients, {'Mail clients'}),
            (mail, {'mail'}),
        ))

    def test_phrase_matching(self):
        browsers, mail_clients, desktops = self.generate_sample_terms(
            'web browser',
            'mail client',
            'PC desktop'
        )

        entity1, entity2, entity3 = self.generate_sample_entities(

            # Algorithm will detect only one phrase.
            {'string': 'Firefox & Chrome are web browsers and web browsers.'},

            # Algorithm will detect two matching phrases for browsers because they have different pluralilty.
            {'string': 'The web is full of web browsers, mail clients and a web browser.'},

            {'string': 'Web browsers like to use pc desktops, a web browser and a pc desktop.'},
        )

        self.assert_terms_phrases(entity1, (
            (browsers, {'web browsers'}),
        ))
        self.assert_terms_phrases(entity2, (
            (browsers, {'web browsers',  'web browser'}),
            (mail_clients, {'mail clients'})
        ))
        self.assert_terms_phrases(entity3, (
            (desktops, {'pc desktops', 'pc desktop'}),
            (browsers, {'Web browsers', 'web browser'})
        ))

    def test_no_match(self):
        """
        Create a set of terms that shouldn't be found in the existing entities in database.
        """
        self.generate_sample_terms(
            'browser',
            'mail',
            'desktop'
        )

        entity1, entity2, entity3 = self.generate_sample_entities(
            {'string': 'Hello world!'},
            {'string': 'Thunderbird client'},
            {'string': 'Developers, developers, developers'},
        )
        self.assert_terms_phrases(entity1, tuple())
        self.assert_terms_phrases(entity2, tuple())
        self.assert_terms_phrases(entity3, tuple())


class TestCachedDBTermIndexTest(_TestEntityTermMatching):
    term_index_cls = CachedDBTermIndex

class TestDBTermIndexTest(_TestEntityTermMatching):
    term_index_cls = DBTermIndex
