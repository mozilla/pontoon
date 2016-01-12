from textwrap import dedent

from nose.tools import (
    assert_equal,
)

from pontoon.base.tests import (
    assert_attributes_equal,
    TestCase
)

from pontoon.sync.formats import l20n
from pontoon.sync.tests.formats import FormatTestsMixin


BASE_L20N_FILE = '''
/*Sample comment*/
<source_string "Translated String">

/*First comment*/
/*Second comment*/
<multiple_comments "Translated Multiple Comments">

<no_comments_or_sources "Translated No Comments or Sources">

/*Multiline
Comment*/
<multiline_comment "Multiline Comment">
'''


class L20NTests(FormatTestsMixin, TestCase):
    parse = staticmethod(l20n.parse)

    supports_keys = False
    supports_source = False
    supports_source_string = False

    def key(self, source_string):
        """
        L20N supports only keys in following format: [_0-9A-Za-z]
        """
        return (super(L20NTests, self).key(source_string)
            .lower()
            .replace(' ', '_')
            .replace('-', '_'))

    def test_parse_basic(self):
        self.run_parse_basic(BASE_L20N_FILE, 0)

    def test_multiple_comments(self):
        self.run_parse_multiple_comments(BASE_L20N_FILE, 1)

    def test_parse_no_comments_no_sources(self):
        self.run_parse_no_comments_no_sources(BASE_L20N_FILE, 2)

    def test_parse_multiline_comment(self):
        path, resource = self.parse_string(BASE_L20N_FILE)
        assert_attributes_equal(
            resource.translations[3],
            comments=["Multiline\nComment"],
            key=self.key('Multiline Comment'),
            strings={None: 'Multiline Comment'},
            order=3,
        )

    def test_parse_hash_entities(self):
        source = '''
        /*Hash comment*/
        <multiple_hash_items {
            one: "One item",
            other: "Other items",
        }>
        '''
        path, resource = self.parse_string(source)
        assert_attributes_equal(resource.translations[0],
            key=self.key('multiple_hash_items'),
            strings={
                0: "One item",
                1: "Other items",
            },
            comments=['Hash comment'],
            order=0
        )


    def test_parse_string_attributes(self):
        source = '''
        <multiple_attributes "Multiple attributes"
        first: "First attribute"
        second: "Second attribute">
        '''
        path, resource = self.parse_string(source)

        assert_attributes_equal(resource.translations[0],
            key=self.key('multiple_attributes'),
            strings={None: 'Multiple attributes'},
            order=0,
        )

        assert_attributes_equal(resource.translations[1],
            key=self.key('multiple_attributes.first'),
            strings={None: 'First attribute'},
            order=1,
        )

        assert_attributes_equal(resource.translations[2],
            key=self.key('multiple_attributes.second'),
            strings={None: 'Second attribute'},
            order=2,
        )

    def test_parse_hash_attributes(self):
        source = '''
        <sample_hash {
            one: "First string",
            other: "Second string"
        }
        first_attr: "First string attribute"
        >
        '''
        _, resource = self.parse_string(source)
        assert_equal(len(resource.translations), 2)
        assert_attributes_equal(resource.translations[0],
            key=self.key('sample_hash'),
            source_string='First string',
            source_string_plural='Second string',
            strings={
                0: 'First string',
                1: 'Second string',
            },
            order=0)
        assert_attributes_equal(resource.translations[1],
            key=self.key('sample_hash.first_attr'),
            source_string='First string attribute',
            strings={None: 'First string attribute'},
            order=1
        )

    def test_parse_hash_with_rule(self):
        source = '''
        <sample_hash[@cldr.global($n)] {
            one: "First string",
            other: "Second string"
        }
        first_attr: "First string attribute"
        >
        '''
        _, resource = self.parse_string(source)
        assert_equal(len(resource.translations), 2)
        assert_attributes_equal(resource.translations[0],
            key=self.key('sample_hash'),
            source_string='First string',
            source_string_plural='Second string',
            strings={
                0: 'First string',
                1: 'Second string',
            },
            order=0)
        assert_attributes_equal(resource.translations[1],
            key=self.key('sample_hash.first_attr'),
            strings={None: 'First string attribute'},
            order=1
        )

    def test_parse_junk(self):
        _, res = self.parse_string(",junky-data,")
        assert len(res.translations) == 0

    def test_save_basic_string(self):
        input_string = dedent('''
        <basic_save "Source string">
        ''')
        expected_string = dedent('''
        <basic_save "New Translated String">
        ''')
        self.run_save_basic(input_string, expected_string, input_string)

    def test_save_multiple_strings(self):
        input_string = dedent('''
        <first_string "First string">
        <second_string "Second string">
        ''')
        expected_string = dedent('''
        <first_string "First string">
        <second_string "Second translated string">
        ''')
        def change_resource(res):
            translation = res.translations[1]
            translation.strings[None] = 'Second translated string'
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)

    def test_save_string_with_attribute(self):
        input_string = """
<first "First string"
first_attr: "aaa"
>
<second "Second string"
second_attr: "bbb"
>
        """
        expected_string = """
<first "First string"
  first_attr: "aaa"
>
<second "Second string"
  second_attr: "ccc"
>
        """
        def change_resource(res):
            translation = res.translations[3]
            translation.strings[None] = 'ccc'
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)


    def test_save_untranslated_attributes(self):
        """
        Entity should be removed if it doesn't have translation and any of its
        attributes arent't translated.
        """
        input_string = """
<first "First string"
first_attr: "aaa"
>
<second "Second string"
second_attr: "bbb"
>
        """
        expected_string = """
<second "Second string"
  second_attr: "bbb"
>
        """
        def change_resource(res):
            res.translations[0].strings = {}
            res.translations[1].strings = {}
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)

    def test_save_basic_hash(self):
        input_string = dedent('''
        <basic_hash {
            one: "One string",
            other: "Other string"
        }>
        ''')
        expected_string = '''
<basic_hash {
  one: "One string",
  other: "Other translated string"
}>'''

        def change_resource(res):
            translation = res.translations[0]
            translation.strings[1] = 'Other translated string'
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)

    def test_save_hash_with_attribute(self):
        input_string = dedent('''
        <basic_hash {
            one: "One string",
            other: "Other string"
        }
        first_attribute: "First attribute">
        ''')
        expected_string = '''
<basic_hash {
  one: "One string",
  other: "Other string"
}
  first_attribute: "Translated attribute"
>'''
        def change_resource(res):
            translation = res.translations[1]
            translation.strings[None] = "Translated attribute"
        self.run_save_basic(input_string, expected_string, source_string=input_string, resource_cb=change_resource)

    def test_save_hash_with_rule(self):
        input_string = dedent('''
        <basic_hash[@cldr.plural] {
            one: "One string",
            other: "Many strings"
        }
        first_attribute: "First attribute">
        ''')
        expected_string = '''
<basic_hash[@cldr.plural] {
  one: "One translated string",
  other: "Many strings"
}
  first_attribute: "Translated attribute"
>'''
        def change_resource(res):
            translation = res.translations[0]
            translation.strings[0] = 'One translated string'
            translation = res.translations[1]
            translation.strings[None] = 'Translated attribute'
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)

    def test_save_override_translation(self):
        source_string = '''
        <first_string "First basic string">
        <second_string "Second basic string">
        '''
        locale_string = '''
        <first_string "Locale translation">
        '''
        expected_string = '''
        <first_string "Changed translation">
        '''
        def change_resource(res):
            translation = res.translations[0]
            translation.strings = {None: 'Changed translation'}
        self.run_save_basic(locale_string, expected_string, source_string, resource_cb=change_resource)

    def test_translate_only_attribute(self):
        input_string = dedent('''
        <first_string "First basic string"
         first_string_attribute: "First attribute"
        >
        <second_string "Second basic string">
        ''')
        expected_string = '''
<first_string 
  first_string_attribute: "First translated attribute"
>
<second_string "Second basic string">
'''
        def change_resource(res):
            res.translations[0].strings = {}
            res.translations[1].strings = {None: 'First translated attribute'}
        self.run_save_basic(input_string, expected_string, input_string, resource_cb=change_resource)

    def test_save_remove_string(self):
        input_string = dedent('''
        <basic_save "Source string">
        <notbasic_save "Some string">
        ''')
        expected_string = '<notbasic_save "Some string">'

        self.run_save_remove(input_string, expected_string, input_string)

    def test_save_remove_string_attribute(self):
        input_string = """
        <basic_string "Source string"
        basic_attribute: "Attribute string">
        """
        expected_string ='''<basic_string "Source string">'''
        def remove_attribute(res):
            attr_translation = res.translations[1]
            attr_translation.strings = {}
        self.run_save_remove(input_string, expected_string, input_string, remove_cb=remove_attribute)

    def test_save_remove_hash(self):
        input_string = """
        <first_hash {
            one: "First hash"
        }>
        <second_hash {
            one: "Second hash"
        }>
        """
        expected_string ='''
<first_hash {
  one: "First hash"
}>
'''
        def remove_hash(res):
            attr_translation = res.translations[1]
            attr_translation.strings = {}
        self.run_save_remove(input_string, expected_string, input_string, remove_cb=remove_hash)

    def test_save_remove_hash_attribute(self):
        input_string = """
        <first_hash {
            one: "First hash"
        }
        first_attribute: "First attribute">
        """
        expected_string ='''
<first_hash {
  one: "First hash"
}>
'''
        def remove_hash(res):
            attr_translation = res.translations[1]
            attr_translation.strings = {}
        self.run_save_remove(input_string, expected_string, input_string, remove_cb=remove_hash)

    def test_save_remove_hash_with_rule(self):
        input_string = """
        <first_hash {
            one: "First hash"
        }>
        <second_hash[@example] {
            one: "Second hash"
        }>
        """
        expected_string ='''
<first_hash {
  one: "First hash"
}>
'''
        def remove_hash(res):
            attr_translation = res.translations[1]
            attr_translation.strings = {}
        self.run_save_remove(input_string, expected_string, input_string, remove_cb=remove_hash)

    def test_save_remove_hash_item(self):
        input_string = """
        <first_hash {
            one: "One item",
            other: "Many items"
        }>
        """
        expected_string ='''
<first_hash {
  one: "One item"
}>
'''
        def remove_item(res):
            del res.translations[0].strings[1]
        self.run_save_remove(input_string, expected_string, input_string, remove_cb=remove_item)
