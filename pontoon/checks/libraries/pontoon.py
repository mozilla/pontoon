from __future__ import absolute_import

import re

from collections import defaultdict

MAX_LENGTH_RE = re.compile(r'MAX_LENGTH:( *)(\d+)', re.MULTILINE)


def get_max_length(comment):
    """
    Return max length value for an entity with MAX_LENTH.
    """
    max_length = re.findall(MAX_LENGTH_RE, comment or '')

    if max_length:
        return int(max_length[0][1])

    return None


def is_same(same_translations, can_translate):
    """
    Check if translation is the same
    :arg QuerySet `same_translations`: translations that have the same string
        as a suggestion/translation.
    :arg boolean `can_translate`: user is able to submit translations
    :returns: True if translation already exists and won't be submitted to the database.
    """
    if not same_translations:
        return False

    st = same_translations[0]

    if can_translate:
        if st.approved and not st.fuzzy:
            return True

    else:
        if not st.fuzzy:
            return True
    return False


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
            'Translation too long.'
        )

    # Prevent empty translation submissions if not supported
    if resource_ext not in {'properties', 'ini', 'dtd'} and string == '':
        checks['pErrors'].append(
            'Empty translations cannot be submitted.'
        )

    # Newlines are not allowed in .lang files (bug 1190754)
    if resource_ext == 'lang' and '\n' in string:
        checks['pErrors'].append(
            'Newline characters are not allowed.'
        )
    return checks
