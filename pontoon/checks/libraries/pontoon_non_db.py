from __future__ import absolute_import

from collections import defaultdict


def run_checks(entity, string):
    """
    Group all checks related to the base UI
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    """
    checks = defaultdict(list)

    # Prevent empty translation submissions if supported
    if string == '' and entity.resource.allows_empty_translations:
        checks['pWarnings'].append(
            'Empty translation'
        )

    return checks
