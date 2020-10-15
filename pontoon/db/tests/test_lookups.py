"""
Collation lookups allow a user to set text-collation to search queries.
"""
import pytest

from pontoon.db import IContainsCollate  # noqa
from pontoon.base.models import Entity
from pontoon.base.tests import EntityFactory


@pytest.fixture
@pytest.mark.django_db
def collation_entities():
    # Create a list of instances in order to filter them.
    EntityFactory.create_batch(10, string="qwertyuiop")


@pytest.mark.django_db
def test_empty_locale(collation_entities):
    """Lookup won't add an empty collation to a sql query."""
    entities = Entity.objects.filter(string__icontains_collate=("qwertyuiop", ""))
    query_sql = entities.query.sql_with_params()[0]

    # Force evaluation of query on the real database.
    assert entities.count() == 10
    assert "COLLATE" not in query_sql


@pytest.mark.django_db
def test_arguments_are_in_tuple(collation_entities):
    """Check if lookup validates missing collation properly."""
    with pytest.raises(ValueError):
        Entity.objects.filter(string__icontains_collate="st")


@pytest.mark.django_db
def test_invalid_number_of_arguments(collation_entities):
    """Validate a number of arguments."""
    with pytest.raises(ValueError):
        Entity.objects.filter(string__icontains_collate=("qwertyuiop", "a", "b"))


@pytest.mark.django_db
def test_collation_query(collation_entities):
    """Check if collate is applied to a given lookup."""
    entities = Entity.objects.filter(string__icontains_collate=("qwertyuiop", "C"))
    query_sql = entities.query.sql_with_params()[0]

    # Force evaluation of query on the real database.
    assert entities.count() == 10
    assert query_sql.endswith(
        'WHERE UPPER("base_entity"."string"::text COLLATE "C") '
        'LIKE UPPER(%s COLLATE "C")'
    )
