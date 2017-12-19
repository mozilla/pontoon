from django.utils import timezone

from pontoon.base.models import (
    Entity,
    Resource,
    Translation,
)


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


def find_and_replace(translations, find, replace, user):
    """Replace text in a set of translation.

    :arg QuerySet translations: a list of Translation objects in which to search
    :arg string find: a string to search for, and replace, in translations
    :arg string replace: what to replace the original string with
    :arg User user: the User making the change

    :returns: a tuple with:
        - a queryset of old translations (changed by this function)
        - a list of newly created translations

    """
    translations = translations.filter(string__contains=find)

    if translations.count() == 0:
        return translations, []

    # Empty translations produced by replace might not be always allowed
    forbidden = (
        translations.filter(string=find)
        .exclude(entity__resource__format__in=Resource.ASYMMETRIC_FORMATS)
    )
    if not replace and forbidden.exists():
        raise Translation.NotAllowed

    # Create translations' clones and replace strings
    now = timezone.now()
    translations_to_create = []
    for translation in translations:
        translation.pk = None  # Create new translation
        translation.string = translation.string.replace(find, replace)
        translation.user = translation.approved_user = user
        translation.date = translation.approved_date = now
        translation.approved = True
        translation.rejected = False
        translation.rejected_date = None
        translation.rejected_user = None
        translation.fuzzy = False
        translations_to_create.append(translation)

    # Unapprove old translations
    translations.update(
        approved=False,
        approved_user=None,
        approved_date=None,
        rejected=True,
        rejected_user=user,
        rejected_date=now,
        fuzzy=False,
    )

    # Create new translations
    changed_translations = Translation.objects.bulk_create(
        translations_to_create
    )
    return translations, changed_translations
