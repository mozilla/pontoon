from __future__ import absolute_import

import pytest

from pontoon.db import IContainsCollate  # noqa
from pontoon.base.models import Entity
from pontoon.base.tests import TestCase, EntityFactory


class TestIContainsCollationLookup(TestCase):
    """
    Collation lookups allows a user to set text-collation to search queries.
    """

    def setUp(self):
        # Create a list of instances in order to filter them.
        EntityFactory.create_batch(10, string="qwertyuiop")

    def test_empty_locale(self):
        """Lookup won't add an empty collation to a sql query."""
        entities = Entity.objects.filter(string__icontains_collate=("qwertyuiop", ""))
        query_sql = entities.query.sql_with_params()[0]

        # Force evaluation of query on the real database.
        assert entities.count() == 10
        assert "COLLATE" not in query_sql

    def test_arguments_are_in_tuple(self):
        """Check if lookup validates missing collation properly."""
        with pytest.raises(ValueError):
            Entity.objects.filter(string__icontains_collate="st")

    def test_invalid_number_of_arguments(self):
        """Validate a number of arguments."""
        with pytest.raises(ValueError):
            Entity.objects.filter(string__icontains_collate=("qwertyuiop", "a", "b"))

    def test_collation_query(self):
        """Check if collate is applied to a given lookup."""
        entities = Entity.objects.filter(string__icontains_collate=("qwertyuiop", "C"))
        query_sql = entities.query.sql_with_params()[0]

        # Force evaluation of query on the real database.
        assert entities.count() == 10
        assert query_sql.endswith(
            'WHERE UPPER("base_entity"."string"::text COLLATE "C") '
            'LIKE UPPER(%s COLLATE "C")'
        )
