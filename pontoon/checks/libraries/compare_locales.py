from __future__ import absolute_import

from collections import namedtuple

from HTMLParser import HTMLParser
from compare_locales.checks import getChecker
from compare_locales.parser.fluent import FluentParser
from compare_locales.parser.properties import PropertiesEntityMixin
from compare_locales.parser.dtd import DTDEntityMixin

from compare_locales.paths import File

CommentEntity = namedtuple(
    'Comment', (
        'all',
    )
)


# Because we can't pass the context to all entities passed to compare locales,
# we have to create our equivalents of compare-locale's internal classes.

class ComparePropertiesEntity(PropertiesEntityMixin):
    def __init__(self, key, raw_val, pre_comment):
        self.key = key
        self.raw_val = raw_val
        self.pre_comment = pre_comment

    def __repr__(self):
        return 'ComparePropertiesEntity<key="{}",raw_val="{}",pre_comment="{}">'.format(
            self.key,
            self.raw_val,
            self.pre_comment.all,
        )


class CompareDTDEntity(DTDEntityMixin):
    def __init__(self, key, raw_val, pre_comment):
        self.key = key
        self.raw_val = raw_val
        self.pre_comment = pre_comment

    @property
    def all(self):
        return '<!ENTITY {} \"{}\">'.format(self.key, self.raw_val)

    def __repr__(self):
        return 'CompareDTDEntity<key="{}",raw_val="{}",pre_comment="{}">'.format(
            self.key,
            self.raw_val,
            self.pre_comment.all,
        )



class UnsupportedResourceTypeError(Exception):
    """Raise if compare-locales doesn't support given resource-type."""
    pass


def cast_to_compare_locales(resource_ext, entity, string):
    """
    Cast a Pontoon's translation object into Entities supported by `compare-locales`.

    :arg basestring resource_ext: extension of a resource.
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring string: a translation
    :arg pontoon.base.models.Locale locale: Locale of a translation
    :return: source entity and translation entity that will be compatible with
        a compare-locales checker. Type of those entities depends on the resource_ext.
    """
    if resource_ext == '.properties':
        return (
            ComparePropertiesEntity(
                entity.key,
                entity.string,
                CommentEntity(entity.comment)
            ),
            ComparePropertiesEntity(
                entity.key,
                string,
                CommentEntity(entity.comment),
            )
        )

    elif resource_ext == '.dtd':
        return (
            CompareDTDEntity(
                entity.key,
                entity.string,
                CommentEntity(entity.comment),
            ),
            CompareDTDEntity(
                entity.key,
                string,
                CommentEntity(entity.comment),
            )
        )

    elif resource_ext == '.ftl':
        parser = FluentParser()

        parser.readUnicode(entity.string)
        refEntity, = list(parser)

        parser.readUnicode(string)
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
        File(entity.resource.path, entity.resource.path, locale=locale),
        {'android-dtd'}
    )

    # Currently, references are required only by DTD files but that may change in the future.
    if checker.needs_reference:
        references = [
            CompareDTDEntity(
                e.key,
                e.string,
                e.comment,
            )
            for e in entity.resource.entities.all()
        ]
        checker.set_reference(references)

    errors = {}

    for (severity, _, message, _) in checker.check(source_ent, translation_ent):
        errors.setdefault('cl%ss' % severity.capitalize(), []).append(message)

    return errors
