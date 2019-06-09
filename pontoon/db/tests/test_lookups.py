from __future__ import absolute_import

from nose.tools import raises
from django_nose.tools import (
    assert_equal,
    assert_true,
)

from pontoon.db import IContainsCollate  # noqa
from pontoon.base.models import (
    Entity
)
from pontoon.base.tests import (
    TestCase,
    EntityFactory
)


class TestIContainsCollationLookup(TestCase):
    """
    Collation lookups allows a user to set text-collation to search queries.
    """
    def setUp(self):
        # Create a list of instances in order to filter them.
        EntityFactory.create_batch(10, string='qwertyuiop')

    def test_empty_locale(self):
        """Lookup won't add an empty collation to a sql query."""
        entities = Entity.objects.filter(
            string__icontains_collate=('qwertyuiop', '')
        )
        query_sql = entities.query.sql_with_params()[0]

        # Force evaluation of query on the real database.
        assert_equal(entities.count(), 10)
        assert_true('COLLATE' not in query_sql)

    @raises(ValueError)
    def test_arguments_are_in_tuple(self):
        """Check if lookup validates missing collation properly."""
        Entity.objects.filter(
            string__icontains_collate='st'
        )

    @raises(ValueError)
    def test_invalid_number_of_arguments(self):
        """Validate a number of arguments."""
        Entity.objects.filter(
            string__icontains_collate=('qwertyuiop', 'a', 'b')
        )

    def test_collation_query(self):
        """Check if collate is applied to a given lookup."""
        entities = Entity.objects.filter(
            string__icontains_collate=('qwertyuiop', 'C')
        )
        query_sql = entities.query.sql_with_params()[0]

        # Force evaluation of query on the real database.
        assert_equal(entities.count(), 10)
        assert_true(query_sql.endswith('WHERE UPPER("base_entity"."string"::text COLLATE "C") '
                                       'LIKE UPPER(%s COLLATE "C")'))
