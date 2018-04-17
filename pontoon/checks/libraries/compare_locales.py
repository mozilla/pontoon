from __future__ import absolute_import

import re
from collections import namedtuple

from HTMLParser import HTMLParser
from compare_locales.checks import getChecker
from compare_locales.parser import FluentParser
from compare_locales.paths import File

html_unescape = HTMLParser().unescape

CommentEntity = namedtuple(
    'Comment', (
        'all',
    )
)

# Because we can't pass the context to all entities passed to compare locales,
# we have to create our equivalents of compare-locale's internal classes.
ComparePropertiesEntity = namedtuple(
    'ComparePropertiesEntity',
    (
        'key',
        'val',
        'raw_val',
        'pre_comment',
    )
)
CompareDTDEntity = namedtuple(
    'CompareDTDEntity',
    (
        'key',
        'val',
        'raw_val',
        'pre_comment',
        'all',
    )
)


DTD_ENTITY_TMPL = '<!ENTITY %s \"%s\">'


class UnsupportedResourceTypeError(Exception):
    """Raise if compare-locales doesn't support given resource-type."""
    pass


PROPERTIES_ENTITY_ESCAPE_RE = re.compile(
    r'\\((?P<uni>u[0-9a-fA-F]{1,4})|'
    r'(?P<nl>\n\s*)|(?P<single>.))',
    re.M
)
PROPERTIES_KNOWN_ESCAPES = {'n': '\n', 'r': '\r', 't': '\t', '\\': '\\'}


def unescape_properties_entity(raw_value):
    """
    Unescape a raw string.
    """
    def unescape(match):
        found = match.groupdict()
        if found['uni']:
            return unichr(int(found['uni'][1:], 16))
        if found['nl']:
            return ''
        return PROPERTIES_KNOWN_ESCAPES.get(found['single'], found['single'])
    return PROPERTIES_ENTITY_ESCAPE_RE.sub(unescape, raw_value)


def cast_to_compare_locales(resource_ext, entity, string):
    """
    Cast a Pontoon's translation object into Entities supported by `compare-locales`.

    :arg basestring resource_ext: extension of a resource.
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    :arg pontoon.base.models.Locale locale: Locale of a translation
    :return: source entity and translation entity that will be compatible a compare-locales checker.
        Type of those entities depends on the resource_ext.
    """
    if resource_ext == '.properties':
        return (
            ComparePropertiesEntity(
                entity.key,
                unescape_properties_entity(entity.string),
                entity.string,
                CommentEntity(entity.comment)
            ),
            ComparePropertiesEntity(
                entity.key,
                unescape_properties_entity(string),
                string,
                CommentEntity(entity.comment),
            )
        )

    elif resource_ext == '.dtd':
        return (
            CompareDTDEntity(
                entity.key,
                html_unescape(entity.string),
                entity.string,
                CommentEntity(entity.comment),
                DTD_ENTITY_TMPL % (entity.key, entity.string)
            ),
            CompareDTDEntity(
                entity.key,
                html_unescape(string),
                string,
                CommentEntity(entity.comment),
                DTD_ENTITY_TMPL % (entity.key, entity.string)
            )
        )

    elif resource_ext == '.ftl':
        parser = FluentParser()

        parser.readContents(entity.string)
        refEntity, = list(parser)

        parser.readContents(string)
        trEntity, = list(parser)
        return (
            refEntity,
            trEntity,
        )

    raise UnsupportedResourceTypeError(resource_ext)


def run_checks(entity, locale, string):
    """
    Run all compare-locales checks on provided translation and entity.
    :arg pontoon.base.models.Entity entity: Source entity instance
    :arg basestring string: translation string
    :arg pontoon.base.models.Locale locale: Locale of a translation

    :return: Dictionary with the following structure:
        {
            'clErrors': [
                'Error1',
            ],
            'clWarnings': [
                'Warning1',
            ]
        }
        Both keys are optional.
    """
    resource_ext = '.{}'.format(entity.resource.format)

    source_ent, translation_ent = cast_to_compare_locales(
        resource_ext,
        entity,
        string,
    )

    checker = getChecker(
        File(entity.resource.path, entity.resource.path),
        {'android-dtd'}
    )

    # Currently, references are required only by DTD files but that may change in the future.
    if checker.needs_reference:
        references = [
            CompareDTDEntity(
                e.key,
                e.string,
                e.string,
                e.comment,
                DTD_ENTITY_TMPL % (e.key, e.string)
            )
            for e in entity.resource.entities.all()
        ]
        checker.set_reference(references)

    errors = {}

    for (severity, _, message, _) in checker.check(source_ent, translation_ent):
        errors.setdefault('cl%ss' % severity.capitalize(), []).append(message)

    return errors

