import unittest
from graphql import Source, parse as parse_source

from pontoon.api.util import get_fields


class MockResolveInfo:
    def __init__(self, query, fragments=None):
        self.field_asts = query.selection_set.selections
        self.fragments = fragments


def parse(query):
    """Return a list of queries and fragments"""
    source = Source(query)
    document = parse_source(source)
    return document.definitions


class TestUtil(unittest.TestCase):
    def test_get_fields_one(self):
        input = """
            query {
                projects {
                    name
                }
            }
        """

        query, = parse(input)
        info = MockResolveInfo(query)

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
            ]
        )

    def test_get_fields_many(self):
        input = """
            query {
                projects {
                    name
                    slug
                }
            }
        """

        query, = parse(input)
        info = MockResolveInfo(query)

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'projects.slug',
            ]
        )

    def test_get_fields_fragment(self):
        input = """
            query {
                projects {
                    name
                    slug
                    ...stats
                }
            }

            fragment stats on Project {
                totalStrings
                missingStrings
            }
        """

        query, frag = parse(input)
        info = MockResolveInfo(query, {'stats': frag})

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'projects.slug',
                'projects.totalStrings',
                'projects.missingStrings'
            ]
        )

    def test_get_fields_cyclic(self):
        input = """
            query {
                projects {
                    name
                    slug
                    localizations {
                        locale {
                            localizations {
                                totalStrings
                            }
                        }
                    }
                }
            }
        """

        query, = parse(input)
        info = MockResolveInfo(query)

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'projects.slug',
                'projects.localizations',
                'projects.localizations.locale',
                'projects.localizations.locale.localizations',
                'projects.localizations.locale.localizations.totalStrings',
            ]
        )

    def test_get_fields_cyclic_with_fragment(self):
        input = """
            query {
                projects {
                    name
                    slug
                    localizations {
                        locale {
                            localizations {
                                ...stats
                            }
                        }
                    }
                }
            }

            fragment stats on ProjectLocale {
                totalStrings
                missingStrings
            }
        """

        query, frag = parse(input)
        info = MockResolveInfo(query, {'stats': frag})

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'projects.slug',
                'projects.localizations',
                'projects.localizations.locale',
                'projects.localizations.locale.localizations',
                'projects.localizations.locale.localizations.totalStrings',
                'projects.localizations.locale.localizations.missingStrings',
            ]
        )

    def test_get_fields_cyclic_in_fragment(self):
        input = """
            query {
                projects {
                    name
                    slug
                    localizations {
                        locale {
                            ...localizations
                        }
                    }
                }
            }

            fragment localizations on Locale {
                localizations {
                    totalStrings
                    missingStrings
                }
            }
        """

        query, frag = parse(input)
        info = MockResolveInfo(query, {'localizations': frag})

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'projects.slug',
                'projects.localizations',
                'projects.localizations.locale',
                'projects.localizations.locale.localizations',
                'projects.localizations.locale.localizations.totalStrings',
                'projects.localizations.locale.localizations.missingStrings',
            ]
        )

    def test_get_fields_two_queries(self):
        input = """
            query {
                projects {
                    name
                }
            }

            query {
                locales {
                    name
                }
            }
        """

        query1, query2 = parse(input)

        info1 = MockResolveInfo(query1)
        self.assertEqual(
            get_fields(info1),
            [
                'projects',
                'projects.name',
            ]
        )

        info2 = MockResolveInfo(query2)
        self.assertEqual(
            get_fields(info2),
            [
                'locales',
                'locales.name',
            ]
        )

    def test_get_fields_two_fields(self):
        input = """
            query {
                projects {
                    name
                }
                locales {
                    name
                }
            }
        """

        query, = parse(input)
        info = MockResolveInfo(query)

        self.assertEqual(
            get_fields(info),
            [
                'projects',
                'projects.name',
                'locales',
                'locales.name',
            ]
        )
