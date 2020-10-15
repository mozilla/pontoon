from collections import defaultdict


def run_checks(entity, string):
    """
    Group all checks related to the base UI that do not get stored in the DB
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    """
    checks = defaultdict(list)

    # Prevent empty translation submissions if supported
    if string == "" and entity.resource.allows_empty_translations:
        checks["pndbWarnings"].append("Empty translation")

    return checks
