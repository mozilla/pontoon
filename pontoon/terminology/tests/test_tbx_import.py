# coding: utf-8

from nose.tools import assert_equal, assert_raises
from pyexpat import ExpatError

from pontoon.base.tests import TestCase

from pontoon.terminology.formats import tbx
from pontoon.terminology.models import Term


class TestTBXFormatParser(TestCase):
    """
    TBX format is curretly handled in a very minimal effort to create
    """
    def parse_sample(self, sample_path):
        return tbx.parse_terms(
            self.get_sample(sample_path).encode('utf-8')
        )

    def import_tbx(self, sample_path):
        """
        Helper, imports the contents of a sample file and returns imported database state.
        """
        Term.objects.import_tbx_terms(
            {t.term_id: t for t in self.parse_sample(sample_path)}
        )
        terms = []
        for term in Term.objects.all().order_by('term_id'):
            term_json = term.serialize(None)
            term_json[u'term_id'] = term.term_id
            term_json[u'translations'] = {
                tt.locale.code: tt.text for tt in term.translations.all()
            }
            terms.append(term_json)
        return terms

    def test_valid_mozilla_terminology_file(self):
        """
        Integration tests that tries to import a tbx structure.
        """
        assert_equal(
            self.import_tbx('valid_mozilla_terminology.tbx'),
            [
                {
                    u'term_id': u'0717_0001',
                    u'term': u'abnormality',
                    u'note': u'Noun',
                    u'description': u'Mozilla detected a serious abnormality in its internal data',
                    u'translations': {
                        u'pl': u'nieprawidłowość'
                    }
                },
                {
                    u'term_id': u'0717_0002',
                    u'term': u'abort',
                    u'note': u'Noun',
                    u'description': u'Do you want to abort this download',
                    u'translations': {
                        u'pl': u'przerwać'
                    }
                },
                {
                    u'term_id': u'0717_0003',
                    u'term': u'abuse',
                    u'note': u'Noun',
                    u'description': (u'Special thanks to all of you '
                                     u'who help report abuses of Mozilla mark'),
                    u'translations': {
                        u'pl': u'nadużycie'
                    }
                },
                {
                    u'term_id': u'0717_0004',
                    u'term': u'abuse',
                    u'note': u'Verb',
                    u'description': (
                        u'In addition any participants who abuse the reporting process '
                        u'will be considered '
                        u'to be in violation of these guidelines'
                    ),
                    u'translations': {
                        u'pl': u'nadużywać'
                    }
                },
            ]
        )

    def test_invalid_file_raises_an_error(self):
        """
        Test if import_tbx raises an error if contents of file aren't xml.
        """
        with assert_raises(ExpatError):
            self.import_tbx('broken_terminology.tbx')
