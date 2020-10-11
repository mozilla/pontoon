from __future__ import absolute_import

from graphql import Source, parse as parse_source

from pontoon.api.util import get_fields


class MockResolveInfo:
    """Mock of ResolveInfo with data required by get_fields.

    GraphQL passes ResolveInfo objects to resolvers. They include the name of the field being
    resolved, the query AST, fragments ASTs, the schema, the execution context and others.
    get_fields uses ResolveInfo to introspect the AST and return a flat list of requested fields.
    """

    def __init__(self, query, fragments=None):
        self.field_asts = query.selection_set.selections
        self.fragments = fragments


def parse_graphql_query(query):
    """Return a list of queries and fragments"""
    source = Source(query)
    document = parse_source(source)
    return document.definitions


def test_get_fields_one():
    input = """
        query {
            projects {
                name
            }
        }
    """

    (query,) = parse_graphql_query(input)
    info = MockResolveInfo(query)

    assert get_fields(info) == ["projects", "projects.name"]


def test_get_fields_many():
    input = """
        query {
            projects {
                name
                slug
            }
        }
    """

    (query,) = parse_graphql_query(input)
    info = MockResolveInfo(query)

    assert get_fields(info) == ["projects", "projects.name", "projects.slug"]


def test_get_fields_fragment():
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

    query, frag = parse_graphql_query(input)
    info = MockResolveInfo(query, {"stats": frag})

    assert get_fields(info) == [
        "projects",
        "projects.name",
        "projects.slug",
        "projects.totalStrings",
        "projects.missingStrings",
    ]


def test_get_fields_cyclic():
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

    (query,) = parse_graphql_query(input)
    info = MockResolveInfo(query)

    assert get_fields(info) == [
        "projects",
        "projects.name",
        "projects.slug",
        "projects.localizations",
        "projects.localizations.locale",
        "projects.localizations.locale.localizations",
        "projects.localizations.locale.localizations.totalStrings",
    ]


def test_get_fields_cyclic_with_fragment():
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

    query, frag = parse_graphql_query(input)
    info = MockResolveInfo(query, {"stats": frag})

    assert get_fields(info) == [
        "projects",
        "projects.name",
        "projects.slug",
        "projects.localizations",
        "projects.localizations.locale",
        "projects.localizations.locale.localizations",
        "projects.localizations.locale.localizations.totalStrings",
        "projects.localizations.locale.localizations.missingStrings",
    ]


def test_get_fields_cyclic_in_fragment():
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

    query, frag = parse_graphql_query(input)
    info = MockResolveInfo(query, {"localizations": frag})

    assert get_fields(info) == [
        "projects",
        "projects.name",
        "projects.slug",
        "projects.localizations",
        "projects.localizations.locale",
        "projects.localizations.locale.localizations",
        "projects.localizations.locale.localizations.totalStrings",
        "projects.localizations.locale.localizations.missingStrings",
    ]


def test_get_fields_two_queries():
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

    query1, query2 = parse_graphql_query(input)

    info1 = MockResolveInfo(query1)
    assert get_fields(info1) == ["projects", "projects.name"]

    info2 = MockResolveInfo(query2)
    assert get_fields(info2) == ["locales", "locales.name"]


def test_get_fields_two_fields():
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

    (query,) = parse_graphql_query(input)
    info = MockResolveInfo(query)

    assert get_fields(info) == ["projects", "projects.name", "locales", "locales.name"]
