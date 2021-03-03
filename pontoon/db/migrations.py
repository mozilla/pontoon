"""
Django 1.10.5 doesn't support migrations/updates for fulltext fields, django-pg-fts isn't
actively maintained and current codebase is broken between various versions of Django.

Because of that I decided to implement our migrations with intent to drop it when django develops
its own solution.
"""
import copy

from django.db.migrations.operations.base import Operation


class BaseSQL(Operation):
    """
    Allows to create parameterized sql migrations.
    """

    forward_sql = None
    backward_sql = None
    sql_opts = {}

    @property
    def sql(self):
        return self.forward_sql.format(**self.sql_opts)

    @property
    def reverse_sql(self):
        return self.backward_sql.format(**self.sql_opts)

    def __init__(self, **kwargs):
        sql_opts = copy.copy(self.sql_opts)
        sql_opts.update(kwargs)
        self.sql_opts = sql_opts

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(self.sql)

    def database_backwards(self, app_label, schema_editor, from_state, to_state):
        schema_editor.execute(self.reverse_sql)

    def state_forwards(self, app_label, state):
        pass


class GINIndex(BaseSQL):
    """
    RunIndex operations share some parts like e.g. drop of an index.
    """

    forward_sql = """
        CREATE INDEX {table}_{field}_{index_suffix} ON \"{table}\"
        USING GIN({expression} {index_opts})
    """

    backward_sql = """
        DROP INDEX {table}_{field}_{index_suffix}
    """

    sql_opts = {
        "index_opts": "",
    }


class MultiFieldTRGMIndex(GINIndex):
    """
    Create a gin-based trigram index on a set of fields.
    """

    sql_opts = {"index_opts": "", "index_suffix": "trigram_index"}

    @property
    def sql(self):
        def index_field(field_name):
            return f"UPPER({field_name}) gin_trgm_ops"

        self.sql_opts["expression"] = ",".join(
            map(index_field, self.sql_opts["from_fields"])
        )
        return self.forward_sql.format(**self.sql_opts)
