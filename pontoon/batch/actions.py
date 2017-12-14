from django.http import (
    JsonResponse,
)
from django.utils import timezone

from pontoon.base.models import (
    Entity,
    TranslationMemoryEntry,
    Translation,
)


def get_translations_info(translations, locale):
    """Return data about a translations set.

    :arg QuerySet translations: a django QuerySet of Translation objects
    :arg Locale locale: the Locale object of the current locale

    :returns: a tuple with:
              * the number of translations in the QuerySet
              * a list of corresponding TranslatedResource objects
              * a list of corresponding Entity objects

    """
    # Must be executed before translations set changes, which is why
    # we need to force evaluate QuerySets by wrapping them inside list()
    count = translations.count()
    translated_resources = list(translations.translated_resources(locale))
    changed_entities = list(
        Entity.objects.filter(translation__in=translations).distinct()
    )

    return count, translated_resources, changed_entities


def batch_action(form, user, translations, locale):
    """Empty batch action, does nothing, only used for documentation.

    :arg BatchActionsForm form:
        the form containing parameters passed to the view
    :arg User user: the User object of the currently logged-in user
    :arg QuerySet translations:
        the list of translations that should be affected
    :arg Locale locale: the current locale

    :returns: a dict containing:
              * count: the number of affected translations
              * translated_resources: a list of TranslatedResource objects
                associated with the translations
              * changed_entities: a list of Entity objects associated
                with the translations
              * latest_translation_pk: the id of the latest affected
                translation
              * changed_translation_pks: a list of ids of affected translations

    """
    return {
        'count': 0,
        'translated_resources': [],
        'changed_entities': [],
        'latest_translation_pk': None,
        'changed_translation_pks': [],
    }


def batch_approve_translations(form, user, translations, locale):
    """Approve a series of translations.

    For documentation, refer to the `batch_action` function.

    """
    translations = translations.filter(approved=False)
    changed_translation_pks = list(translations.values_list('pk', flat=True))

    latest_translation_pk = None
    if changed_translation_pks:
        latest_translation_pk = translations.last().pk

    count, translated_resources, changed_entities = get_translations_info(
        translations,
        locale,
    )
    translations.update(
        approved=True,
        approved_user=user,
        approved_date=timezone.now(),
        rejected=False,
        rejected_user=None,
        rejected_date=None,
    )

    return {
        'count': count,
        'translated_resources': translated_resources,
        'changed_entities': changed_entities,
        'latest_translation_pk': latest_translation_pk,
        'changed_translation_pks': changed_translation_pks,
    }


def batch_reject_translations(form, user, translations, locale):
    """Reject a series of translations.

    Note that this function doesn't use the `translations` parameter, as it
    needs to impact non-active translations. Hence it will generate its own
    list of suggested translations to work on.

    For documentation, refer to the `batch_action` function.

    """
    suggestions = Translation.objects.filter(
        locale=locale,
        entity__pk__in=form.cleaned_data['entities'],
        approved=False,
        rejected=False
    )
    count, translated_resources, changed_entities = get_translations_info(
        suggestions,
        locale,
    )
    TranslationMemoryEntry.objects.filter(translation__in=suggestions).delete()
    suggestions.update(
        rejected=True,
        rejected_user=user,
        rejected_date=timezone.now(),
        approved=False,
        approved_user=None,
        approved_date=None,
    )

    return {
        'count': count,
        'translated_resources': translated_resources,
        'changed_entities': changed_entities,
        'latest_translation_pk': None,
        'changed_translation_pks': [],
    }


def batch_replace_translations(form, user, translations, locale):
    """Replace characters in a series of translations.

    Replaces all occurences of the content of the `find` parameter with the
    content of the `replace` parameter.

    For documentation, refer to the `batch_action` function.

    """
    find = form.cleaned_data['find']
    replace = form.cleaned_data['replace']

    try:
        translations, changed_translations = translations.find_and_replace(
            find,
            replace,
            user
        )
        translations.update(
            approved=False,
            approved_user=None,
            approved_date=None,
            rejected=True,
            rejected_user=user,
            rejected_date=timezone.now(),
            fuzzy=False,
        )
        changed_translation_pks = [c.pk for c in changed_translations]
        if changed_translation_pks:
            latest_translation_pk = max(changed_translation_pks)
    except Translation.NotAllowed:
        return JsonResponse({
            'error': 'Empty translations not allowed',
        })

    count, translated_resources, changed_entities = get_translations_info(
        translations,
        locale,
    )

    return {
        'count': count,
        'translated_resources': translated_resources,
        'changed_entities': changed_entities,
        'latest_translation_pk': latest_translation_pk,
        'changed_translation_pks': changed_translation_pks,
    }


"""A map of action names to functions.

The keys define the available batch actions in the `batch_edit_translations`
view. All functions must accept the same parameters and return the same dict.
See above for those functions.

"""
ACTIONS_FN_MAP = {
    'approve': batch_approve_translations,
    'reject': batch_reject_translations,
    'replace': batch_replace_translations,
}
