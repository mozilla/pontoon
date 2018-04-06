from __future__ import absolute_import

import re

from collections import defaultdict

MAX_LENGTH_RE = re.compile(r'MAX_LENGTH: (\d+)$', re.MULTILINE)


def run_checks(entity, string):
    """
    Group all checks related to the base UI

    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    """
    checks = defaultdict(list)
    resource_ext = entity.resource.format

    max_length = re.findall(MAX_LENGTH_RE, entity.comment or '')
    if max_length and len(string) > int(max_length[0]):
        checks['pErrors'].append(
            'Translation too long.'
        )

    # Prevent empty translation submissions if not supported
    if resource_ext in {'properties', 'ini', 'dtd', 'ftl'} and string == '':
        checks['pErrors'].append(
            'Empty translations cannot be submitted.'
        )

    # Newlines are not allowed in .lang files (bug 1190754)
    if resource_ext == 'lang' and '\n' in string:
        checks['pErrors'].append(
            u'Newline characters are not allowed.'
        )
    return checks
