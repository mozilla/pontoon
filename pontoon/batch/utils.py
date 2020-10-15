from copy import deepcopy

from django.utils import timezone

from pontoon.base.models import Entity
from pontoon.checks import DB_FORMATS

from pontoon.checks.libraries import run_checks

from fluent.syntax import (
    ast,
    FluentParser,
    FluentSerializer,
)


parser = FluentParser()
serializer = FluentSerializer()


def get_translations_info(translations, locale):
    """Return data about a translations set.

    :arg QuerySet translations: a django QuerySet of Translation objects
    :arg Locale locale: the Locale object of the current locale

    :returns: a tuple with:
        - the number of translations in the QuerySet
        - a list of corresponding TranslatedResource objects
        - a list of corresponding Entity objects

    """
    # Must be executed before translations set changes, which is why
    # we need to force evaluate QuerySets by wrapping them inside list()
    count = translations.count()
    translated_resources = list(translations.translated_resources(locale))
    changed_entities = list(
        Entity.objects.filter(translation__in=translations).distinct()
    )

    return count, translated_resources, changed_entities


def ftl_find_and_replace(string, find, replace):
    """Replace text values in an FTL string.

    :arg string string: a serialized FTL string
    :arg string find: a string to search for, and replace, in translations
    :arg string replace: what to replace the original string with

    :returns: a serialized FTL string

    """

    def replace_text_elements(node):
        """Perform find and replace on text values only"""
        if type(node) == ast.TextElement:
            node.value = node.value.replace(find, replace)
        return node

    old_ast = parser.parse_entry(string)
    new_ast = old_ast.traverse(replace_text_elements)

    return serializer.serialize_entry(new_ast)


def find_and_replace(translations, find, replace, user):
    """Replace text in a set of translation.

    :arg QuerySet translations: a list of Translation objects in which to search
    :arg string find: a string to search for, and replace, in translations
    :arg string replace: what to replace the original string with
    :arg User user: the User making the change

    :returns: a tuple with:
        - a queryset of old translations to be changed
        - a list of new translations to be created
        - a list of PKs of translations with errors

    """
    translations = translations.filter(string__contains=find)

    # No matches found
    if translations.count() == 0:
        return translations, [], []

    # Create translations' clones and replace strings
    now = timezone.now()
    translations_to_create = []
    translations_with_errors = []

    # To speed-up error checks, translations will prefetch additional fields
    translations = translations.for_checks(only_db_formats=False)

    for translation in translations:
        # Cache the old value to identify changed translations
        new_translation = deepcopy(translation)

        if translation.entity.resource.format == "ftl":
            new_translation.string = ftl_find_and_replace(
                translation.string, find, replace
            )
        else:
            new_translation.string = translation.string.replace(find, replace)

        # Quit early if no changes are made
        if new_translation.string == translation.string:
            continue

        new_translation.pk = None  # Create new translation
        new_translation.user = new_translation.approved_user = user
        new_translation.date = new_translation.approved_date = now
        new_translation.approved = True
        new_translation.rejected = False
        new_translation.rejected_date = None
        new_translation.rejected_user = None
        new_translation.fuzzy = False

        if new_translation.entity.resource.format in DB_FORMATS:
            errors = run_checks(
                new_translation.entity,
                new_translation.locale.code,
                new_translation.entity.string,
                new_translation.string,
                use_tt_checks=False,
            )
        else:
            errors = {}

        if errors:
            translations_with_errors.append(translation.pk)
        else:
            translations_to_create.append(new_translation)

    if translations_with_errors:
        translations = translations.exclude(pk__in=translations_with_errors)

    return (
        translations,
        translations_to_create,
        translations_with_errors,
    )
