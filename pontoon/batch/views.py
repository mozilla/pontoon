import logging

from bulk_update.helper import bulk_update

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import (
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import (
    require_POST
)

from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
    Translation,
)
from pontoon.base.utils import (
    require_AJAX,
)
from pontoon.batch import forms


log = logging.getLogger('pontoon')


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


def update_stats(translated_resources, entity, locale):
    """Update stats on a list of TranslatedResource.
    """
    for translated_resource in translated_resources:
        translated_resource.calculate_stats(save=False)

    bulk_update(translated_resources, update_fields=[
        'total_strings',
        'approved_strings',
        'fuzzy_strings',
        'translated_strings',
    ])

    project = entity.resource.project
    project.aggregate_stats()
    locale.aggregate_stats()
    ProjectLocale.objects.get(locale=locale, project=project).aggregate_stats()


def mark_changed_translation(changed_entities, locale):
    """Mark entities as changed, for later sync.
    """
    changed_entities_array = []
    existing = (
        ChangedEntityLocale.objects
        .values_list('entity', 'locale')
        .distinct()
    )
    for changed_entity in changed_entities:
        key = (changed_entity.pk, locale.pk)

        # Remove duplicate changes to prevent unique constraint violation.
        if key not in existing:
            changed_entities_array.append(
                ChangedEntityLocale(entity=changed_entity, locale=locale)
            )

    ChangedEntityLocale.objects.bulk_create(changed_entities_array)


def update_translation_memory(changed_translation_pks, project, locale):
    """Update translation memory for a list of translations.
    """
    memory_entries = [
        TranslationMemoryEntry(
            source=t.entity.string,
            target=t.string,
            locale=locale,
            entity=t.entity,
            translation=t,
            project=project,
        ) for t in (
            Translation.objects
            .filter(pk__in=changed_translation_pks)
            .prefetch_related('entity__resource')
        )
    ]
    TranslationMemoryEntry.objects.bulk_create(memory_entries)


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@require_AJAX
@transaction.atomic
def batch_edit_translations(request):
    """Perform an action on a list of translations.

    Available actions are defined in `ACTIONS_FN_MAP`. Arguments to this view
    are defined in `models.BatchActionsForm`.

    """
    form = forms.BatchActionsForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors.as_json())

    locale = get_object_or_404(Locale, code=form.cleaned_data['locale'])

    entities = (
        Entity.objects
        .filter(pk__in=form.cleaned_data['entities'])
        .prefetch_translations(locale)
    )

    if not entities.exists():
        return JsonResponse({'count': 0})

    # Batch editing is only available to translators. Check if user has
    # translate permissions for all of the projects in passed entities.
    projects_pk = entities.values_list('resource__project__pk', flat=True)
    projects = Project.objects.filter(pk__in=projects_pk.distinct())
    for project in projects:
        if not request.user.can_translate(project=project, locale=locale):
            return HttpResponseForbidden(
                "Forbidden: You don't have permission for batch editing"
            )

    translation_pks = set()

    # Find all impacted translations, including plural forms.
    for entity in entities:
        if entity.string_plural == "":
            translation_pks.add(entity.get_translation()['pk'])
        else:
            for plural_form in range(0, locale.nplurals or 1):
                translation_pks.add(entity.get_translation(plural_form)['pk'])

    translation_pks.discard(None)
    translations = Translation.objects.filter(pk__in=translation_pks)

    # Execute the actual action.
    action_function = ACTIONS_FN_MAP[form.cleaned_data['action']]
    action_status = action_function(
        form,
        request.user,
        translations,
        locale,
    )

    if action_status['count'] == 0:
        return JsonResponse({'count': 0})

    update_stats(action_status['translated_resources'], entity, locale)
    mark_changed_translation(action_status['changed_entities'], locale)

    # Update latest translation.
    if action_status['latest_translation_pk']:
        Translation.objects.get(
            pk=action_status['latest_translation_pk']
        ).update_latest_translation()

    update_translation_memory(
        action_status['changed_translation_pks'],
        project,
        locale
    )

    return JsonResponse({
        'count': action_status['count']
    })
