from django.utils import timezone

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    TranslationMemoryEntry,
    Translation,
)
from pontoon.batch import utils


def batch_action_template(form, user, translations, locale):
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
              * invalid_translation_pks: a list of ids of translations that have
                errors or changes on them could introduce new errors e.g. after find & replace

    """
    return {
        "count": 0,
        "translated_resources": [],
        "changed_entities": [],
        "latest_translation_pk": None,
        "changed_translation_pks": [],
        "invalid_translation_pks": [],
    }


def approve_translations(form, user, translations, locale):
    """Approve a series of translations.

    For documentation, refer to the `batch_action_template` function.

    """
    invalid_translation_pks = list(
        translations.filter(approved=False, errors__isnull=False,).values_list(
            "pk", flat=True
        )
    )

    translations = translations.filter(approved=False, errors__isnull=True,)
    changed_translation_pks = list(translations.values_list("pk", flat=True))

    latest_translation_pk = None
    if changed_translation_pks:
        latest_translation_pk = translations.last().pk

    count, translated_resources, changed_entities = utils.get_translations_info(
        translations, locale,
    )

    # Log approving actions
    actions_to_log = [
        ActionLog(action_type="translation:approved", performed_by=user, translation=t,)
        for t in translations
    ]
    ActionLog.objects.bulk_create(actions_to_log)

    # Approve translations.
    translations.update(
        approved=True,
        approved_user=user,
        approved_date=timezone.now(),
        rejected=False,
        rejected_user=None,
        rejected_date=None,
        fuzzy=False,
    )

    return {
        "count": count,
        "translated_resources": translated_resources,
        "changed_entities": changed_entities,
        "latest_translation_pk": latest_translation_pk,
        "changed_translation_pks": changed_translation_pks,
        "invalid_translation_pks": invalid_translation_pks,
    }


def reject_translations(form, user, translations, locale):
    """Reject a series of translations.

    Note that this function doesn't use the `translations` parameter, as it
    needs to impact non-active translations. Hence it will generate its own
    list of suggested translations to work on.

    For documentation, refer to the `batch_action_template` function.

    """
    suggestions = Translation.objects.filter(
        locale=locale,
        entity__pk__in=form.cleaned_data["entities"],
        approved=False,
        rejected=False,
    )
    count, translated_resources, changed_entities = utils.get_translations_info(
        suggestions, locale,
    )
    TranslationMemoryEntry.objects.filter(translation__in=suggestions).delete()

    # Log rejecting actions
    actions_to_log = [
        ActionLog(action_type="translation:rejected", performed_by=user, translation=t,)
        for t in translations
    ]
    ActionLog.objects.bulk_create(actions_to_log)

    # Reject translations.
    suggestions.update(
        active=False,
        rejected=True,
        rejected_user=user,
        rejected_date=timezone.now(),
        approved=False,
        approved_user=None,
        approved_date=None,
        fuzzy=False,
    )

    return {
        "count": count,
        "translated_resources": translated_resources,
        "changed_entities": changed_entities,
        "latest_translation_pk": None,
        "changed_translation_pks": [],
        "invalid_translation_pks": [],
    }


def replace_translations(form, user, translations, locale):
    """Replace characters in a series of translations.

    Replaces all occurences of the content of the `find` parameter with the
    content of the `replace` parameter.

    For documentation, refer to the `batch_action_template` function.

    """
    find = form.cleaned_data["find"]
    replace = form.cleaned_data["replace"]
    latest_translation_pk = None

    (
        old_translations,
        translations_to_create,
        invalid_translation_pks,
    ) = utils.find_and_replace(translations, find, replace, user)

    count, translated_resources, changed_entities = utils.get_translations_info(
        old_translations, locale,
    )

    # Log rejecting actions
    actions_to_log = [
        ActionLog(action_type="translation:rejected", performed_by=user, translation=t,)
        for t in old_translations
    ]
    ActionLog.objects.bulk_create(actions_to_log)

    # Deactivate and unapprove old translations
    old_translations.update(
        active=False,
        approved=False,
        approved_user=None,
        approved_date=None,
        rejected=True,
        rejected_user=user,
        rejected_date=timezone.now(),
        fuzzy=False,
    )

    # Create new translations
    changed_translations = Translation.objects.bulk_create(translations_to_create,)

    # Log creating actions
    actions_to_log = [
        ActionLog(action_type="translation:created", performed_by=user, translation=t,)
        for t in changed_translations
    ]
    ActionLog.objects.bulk_create(actions_to_log)

    changed_translation_pks = [c.pk for c in changed_translations]

    if changed_translation_pks:
        latest_translation_pk = max(changed_translation_pks)

    return {
        "count": count,
        "translated_resources": translated_resources,
        "changed_entities": changed_entities,
        "latest_translation_pk": latest_translation_pk,
        "changed_translation_pks": changed_translation_pks,
        "invalid_translation_pks": invalid_translation_pks,
    }


"""A map of action names to functions.

The keys define the available batch actions in the `batch_edit_translations`
view. All functions must accept the same parameters and return the same dict.
See above for those functions.

"""
ACTIONS_FN_MAP = {
    "approve": approve_translations,
    "reject": reject_translations,
    "replace": replace_translations,
}
