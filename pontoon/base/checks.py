import os
from collections import (
    defaultdict,
    namedtuple,
)
from compare_locales.checks import getChecker
from compare_locales.paths import File
from fluent.syntax import FluentParser

# Because we can't pass the context to all entities passed to compare locales,
# we have to create our equivalents of compare-locale's internal classes.
ComparePropertiesEntity = namedtuple(
    'ComparePropertiesEntity',
    (
        'key',
        'val',

        # We'll remove these fields at some point, currently they're required because of the current
        # implementation property files in compare-locales.
        'raw_val',
        'pre_comment',
    )
)
CompareDTDEntity = namedtuple(
    'CompareDTDEntity',
    (
        'key',
        'val',
        'pre_comment',
        'all',
    )
)
CompareFluentEntity = namedtuple(
    'FluentCompareEntity',
    ('entry',)
)

ftl_parser = FluentParser()


DTD_ENTITY_TMPL = '<!ENTITY %s \"%s\">'


def check_translations(resource, check_translations):
    """
    Check resource and don't requ
    """
    failed_checks = defaultdict(list)

    # reference is required by DTD checker,
    if resource.path.lower().endswith('.dtd'):
        reference = [
            CompareDTDEntity(
                e.key,
                e.string,
                e.comment,
                DTD_ENTITY_TMPL % (e.key, e.string)
            )
            for e in resource.entities.all()
        ]
    else:
        reference = []

    checker = getChecker(File(resource.path, resource.path), reference=reference)

    if not checker:
        return failed_checks

    file_ext = os.path.splitext(resource.path.lower())[1]

    if file_ext == '.properties':
        get_string = lambda t: t.entity.string_plural if t.plural_form else t.entity.string

        check_values = [(
            t.pk,
            ComparePropertiesEntity(t.entity.key, get_string(t), get_string(t), t.entity.comment),
            ComparePropertiesEntity(t.entity.key, t.string, t.string, t.entity.comment)
        ) for t in check_translations]

    elif file_ext == '.dtd':
        check_values = [(
            t.pk,
            CompareDTDEntity(
                t.entity.key,
                t.entity.string,
                t.entity.comment,
                DTD_ENTITY_TMPL % (t.entity.key, t.entity.string)
            ),
            CompareDTDEntity(
                t.entity.key,
                t.string,
                t.entity.comment,
                DTD_ENTITY_TMPL % (t.entity.key, t.entity.string)
            ),
        ) for t in check_translations]

    elif file_ext == '.ftl':
        check_values = [(
            t.pk,
            CompareFluentEntity(ftl_parser.parse_entry(t.entity.string)),
            CompareFluentEntity(ftl_parser.parse_entry(t.string)),
        ) for t in check_translations]

    else:
        # File format isn't supported yet.
        check_values = []

    for (translation_pk, refEnt, l10nEnt) in check_values:
        for (severity, _, message, _) in checker.check(refEnt, l10nEnt):
            failed_checks[translation_pk].append(
               (severity, message)
            )

    return failed_checks
