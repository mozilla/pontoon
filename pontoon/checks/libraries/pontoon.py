from __future__ import absolute_import

import re

from collections import defaultdict
from fluent.syntax import FluentParser, ast


MAX_LENGTH_RE = re.compile(r'MAX_LENGTH:( *)(\d+)', re.MULTILINE)
parser = FluentParser()


def get_max_length(comment):
    """
    Return max length value for an entity with MAX_LENTH.
    """
    max_length = re.findall(MAX_LENGTH_RE, comment or '')

    if max_length:
        return int(max_length[0][1])

    return None


def run_checks(entity, string):
    """
    Group all checks related to the base UI

    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    """
    checks = defaultdict(list)
    resource_ext = entity.resource.format
    max_length = get_max_length(entity.comment)

    if max_length and len(string) > max_length:
        checks['pErrors'].append(
            'Translation too long'
        )

    # Prevent empty translation submissions if not supported
    if resource_ext not in {'properties', 'ini', 'dtd'} and string == '':
        checks['pErrors'].append(
            'Empty translations cannot be submitted'
        )

    # Newlines are not allowed in .lang files (bug 1190754)
    if resource_ext == 'lang' and '\n' in string:
        checks['pErrors'].append(
            'Newline characters are not allowed'
        )

    # FTL checks
    if resource_ext == 'ftl':
        translation_ast = parser.parse_entry(string)
        entity_ast = parser.parse_entry(entity.string)

        # Parse error
        if isinstance(translation_ast, ast.Junk):
            checks['pErrors'].append(
                translation_ast.annotations[0].message
            )

        # Message ID mismatch
        elif entity_ast.id.name != translation_ast.id.name:
            checks['pErrors'].append(
                'Translation key needs to match source string key'
            )

    return checks
