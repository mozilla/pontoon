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
from pontoon.batch.actions import ACTIONS_FN_MAP


log = logging.getLogger(__name__)


def update_stats(translated_resources, entity, locale):
    """Update stats on a list of TranslatedResource.
    """
    for translated_resource in translated_resources:
        translated_resource.calculate_stats(save=False)

    bulk_update(translated_resources, update_fields=[
        'total_strings',
        'approved_strings',
        'fuzzy_strings',
        'unreviewed_strings',
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
    # Also make sure projects are not enabled in read-only mode for a locale.
    projects_pk = entities.values_list('resource__project__pk', flat=True)
    projects = Project.objects.filter(pk__in=projects_pk.distinct())

    readonly = ProjectLocale.objects.filter(
        locale=locale,
        project__in=projects,
        readonly=True,
    ).exists()

    for project in projects:
        if not request.user.can_translate(project=project, locale=locale) or readonly:
            return HttpResponseForbidden(
                "Forbidden: You don't have permission for batch editing"
            )

    active_translation_pks = set()

    # Find all impacted active translations, including plural forms.
    for entity in entities:
        if entity.string_plural == "":
            active_translation_pks.add(entity.get_translation()['pk'])
        else:
            for plural_form in range(0, locale.nplurals or 1):
                active_translation_pks.add(
                    entity.get_translation(plural_form)['pk']
                )

    active_translation_pks.discard(None)

    active_translations = (
        Translation.objects
        .filter(pk__in=active_translation_pks)
    )

    # Execute the actual action.
    action_function = ACTIONS_FN_MAP[form.cleaned_data['action']]
    action_status = action_function(
        form,
        request.user,
        active_translations,
        locale,
    )

    if action_status.get('error'):
        return JsonResponse(action_status)

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
