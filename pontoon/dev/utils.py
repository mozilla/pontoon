"""
Author: phlax

Usage:
with debug_sql():
    code_with_some_db_action()
"""

import logging
from contextlib import contextmanager
from django.db import connection


log = logging.getLogger(__name__)


def log_new_queries(queries):
    new_queries = list(connection.queries[queries:])

    for query in new_queries:
        log.debug(query["time"])
        log.debug("\t%s", query["sql"])

    log.debug("total db calls: %s", len(new_queries))


@contextmanager
def debug_sql():
    queries = len(connection.queries)

    try:
        yield
    finally:
        log_new_queries(queries)
