import json
import logging

from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
    StreamingHttpResponse
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    condition,
    require_POST
)
from django.views.generic.edit import FormView

from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslationMemoryEntry,
    TranslatedResource,
    Translation,
    UserProfile,
)


log = logging.getLogger(__name__)


def home(request):
    """Home view."""

    user = request.user
    project = Project.objects.get(id=1)

    # Redirect user to the selected home page or '/'.
    if user.is_authenticated() and user.profile.custom_homepage != '':
        # If custom homepage not set yet, set it to the most contributed locale team page
        if user.profile.custom_homepage is None:
            if user.top_contributed_locale:
                user.profile.custom_homepage = user.top_contributed_locale
                user.profile.save(update_fields=['custom_homepage'])

        if user.profile.custom_homepage:
            return redirect('pontoon.teams.team', locale=user.profile.custom_homepage)

    locale = utils.get_project_locale_from_request(request, project.locales) or 'en-GB'
    path = Resource.objects.filter(
        project=project,
        translatedresources__locale__code=locale
    ).values_list('path', flat=True)[0]

    return translate(request, locale, project.slug, path)


# TRANSLATE VIEWs


def translate(request, locale, slug, part):
    """Translate view."""
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project.objects.available(), slug=slug)

    if locale not in project.locales.all():
        raise Http404

    projects = (
        Project.objects.available()
        .prefetch_related('subpage_set')
        .order_by('name')
    )

    return render(request, 'translate.html', {
        'download_form': forms.DownloadFileForm(),
        'upload_form': forms.UploadFileForm(),
        'locale': locale,
        'locale_projects': locale.available_projects_list(),
        'locales': Locale.objects.available(),
        'part': part,
        'project': project,
        'projects': projects,
    })


def translate_locale_agnostic(request, slug, part):
    """Locale Agnostic Translate view."""
    user = request.user
    project = get_object_or_404(Project.objects.available(), slug=slug)

    if user.is_authenticated():
        locale = user.profile.custom_homepage

        if locale and project.locales.filter(code=locale).exists():
            return redirect('pontoon.translate', slug=slug, locale=locale, part=part)

    locale = utils.get_project_locale_from_request(request, project.locales)

    if locale:
        return redirect('pontoon.translate', slug=slug, locale=locale, part=part)
    else:
        return redirect('pontoon.projects.project', slug=slug)


@utils.require_AJAX
def locale_projects(request, locale):
    """Get active projects for locale."""
    locale = get_object_or_404(Locale, code=locale)

    return JsonResponse(locale.available_projects_list(), safe=False)


@utils.require_AJAX
def locale_project_parts(request, locale, slug):
    """Get locale-project pages/paths with stats."""
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project, slug=slug)

    try:
        return JsonResponse(locale.parts_stats(project), safe=False)
    except ProjectLocale.DoesNotExist:
        raise Http404('Locale not enabled for selected project.')


@utils.require_AJAX
def authors_and_time_range(request, locale, slug, part):
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project.objects.available(), slug=slug)
    paths = [part] if part != 'all-resources' else None

    translations = Translation.for_locale_project_paths(locale, project, paths)

    return JsonResponse({
        'authors': translations.authors().serialize(),
        'counts_per_minute': translations.counts_per_minute(),
    }, safe=False)


def _get_entities_list(locale, project, form):
    """Return a specific list of entities, as defined by the `entity_ids` field of the form.

    This is used for batch editing.
    """
    entities = (
        Entity.objects.filter(pk__in=form.cleaned_data['entity_ids'])
        .prefetch_related('resource')
        .prefetch_translations(locale)
        .distinct()
        .order_by('order')
    )

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities),
        'stats': TranslatedResource.objects.stats(
            project, form.cleaned_data['paths'], locale
        ),
    }, safe=False)


def _get_all_entities(locale, project, form, entities):
    """Return entities without pagination.

    This is used by the in-context mode of the Translate page.
    """
    has_next = False
    entities_to_map = Entity.for_project_locale(
        project,
        locale,
        paths=form.cleaned_data['paths'],
        exclude_entities=form.cleaned_data['exclude_entities']
    )
    visible_entities = entities.values_list('pk', flat=True)

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities_to_map, visible_entities),
        'has_next': has_next,
        'stats': TranslatedResource.objects.stats(
            project, form.cleaned_data['paths'], locale
        ),
    }, safe=False)


def _get_paginated_entities(locale, project, form, entities):
    """Return a paginated list of entities.

    This is used by the regular mode of the Translate page.
    """
    paginator = Paginator(entities, form.cleaned_data['limit'])

    try:
        entities_page = paginator.page(1)
    except EmptyPage:
        return JsonResponse({
            'has_next': False,
            'stats': {},
            'authors': [],
            'counts_per_minute': [],
        })

    has_next = entities_page.has_next()
    entities_to_map = entities_page.object_list

    # If requested entity not on the first page
    if form.cleaned_data['entity']:
        entity_pk = form.cleaned_data['entity']

        # TODO: entities_to_map.values_list() doesn't return entities from selected page
        if entity_pk not in [e.pk for e in entities_to_map]:
            if entity_pk in entities.values_list('pk', flat=True):
                entities_to_map = list(entities_to_map) + list(entities.filter(pk=entity_pk))

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities_to_map, []),
        'has_next': has_next,
        'stats': TranslatedResource.objects.stats(
            project, form.cleaned_data['paths'], locale
        ),
    }, safe=False)


@csrf_exempt
@require_POST
@utils.require_AJAX
def entities(request):
    """Get entities for the specified project, locale and paths."""
    form = forms.GetEntitiesForm(request.POST)
    if not form.is_valid():
        return HttpResponseBadRequest(form.errors.as_json())

    project = get_object_or_404(Project, slug=form.cleaned_data['project'])
    locale = get_object_or_404(Locale, code=form.cleaned_data['locale'])

    # Only return entities with provided IDs (batch editing)
    if form.cleaned_data['entity_ids']:
        return _get_entities_list(locale, project, form)

    # `Entity.for_project_locale` only requires a subset of the fields the form contains. We thus
    # make a new dict with only the keys we want to pass to that function.
    restrict_to_keys = (
        'paths', 'status', 'search', 'exclude_entities', 'extra', 'time', 'author',
    )
    form_data = {k: form.cleaned_data[k] for k in restrict_to_keys if k in form.cleaned_data}

    entities = Entity.for_project_locale(project, locale, **form_data)

    # Only return a list of entity PKs (batch editing: select all)
    if form.cleaned_data['pk_only']:
        return JsonResponse({
            'entity_pks': list(entities.values_list('pk', flat=True)),
        })

    # In-place view: load all entities
    if form.cleaned_data['inplace_editor']:
        return _get_all_entities(locale, project, form, entities)

    # Out-of-context view: paginate entities
    return _get_paginated_entities(locale, project, form, entities)


@utils.require_AJAX
def get_translations_from_other_locales(request):
    """Get entity translations for all but specified locale."""
    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    entity = get_object_or_404(Entity, pk=entity)
    locales = entity.resource.project.locales.exclude(code=locale)
    plural_form = None if entity.string_plural == "" else 0

    translations = Translation.objects.filter(
        entity=entity,
        locale__in=locales,
        plural_form=plural_form,
        approved=True
    ).order_by('locale__name')

    payload = list(translations.values(
        'locale__code', 'locale__name', 'locale__direction', 'locale__script', 'string'
    ))
    return JsonResponse(payload, safe=False)


@utils.require_AJAX
def get_translation_history(request):
    """Get history of translations of given entity to given locale."""
    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
        plural_form = request.GET['plural_form']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code=locale)

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-approved', 'rejected', '-date')

    payload = []
    offset = timezone.now().strftime('%z')

    for t in translations:
        u = t.user
        translation_dict = t.serialize()
        translation_dict.update({
            "user": "Imported" if u is None else u.name_or_email,
            "uid": "" if u is None else u.id,
            "username": "" if u is None else u.username,
            "date": t.date.strftime('%b %d, %Y %H:%M'),
            "date_iso": t.date.isoformat() + offset,
            "approved_user": User.display_name_or_blank(t.approved_user),
            "unapproved_user": User.display_name_or_blank(t.unapproved_user),
        })
        payload.append(translation_dict)

    return JsonResponse(payload, safe=False)


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def unapprove_translation(request):
    """Unapprove given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    translation = Translation.objects.get(pk=t)

    # Only privileged users or authors can un-approve translations
    if not (
        request.user.can_translate(
            project=translation.entity.resource.project,
            locale=translation.locale
        ) or
        request.user == translation.user or
        translation.approved
    ):
        return HttpResponseForbidden("Forbidden: You can't unapprove this translation.")

    translation.unapprove(request.user)
    latest_translation = translation.entity.translation_set.filter(
        locale=translation.locale,
        plural_form=translation.plural_form,
    ).order_by('-approved', 'rejected', '-date')[0].serialize()
    project = translation.entity.resource.project
    locale = translation.locale
    return JsonResponse({
        'translation': latest_translation,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@transaction.atomic
def reject_translation(request):
    """Reject given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    translation = get_object_or_404(Translation, pk=t)
    locale = translation.locale

    # Non-privileged users can only reject own unapproved translations
    if not request.user.can_translate(
        translation.locale, translation.entity.resource.project
    ):
        if translation.user == request.user:
            if translation.approved is True:
                return HttpResponseForbidden(
                    "Forbidden: Can't reject approved translations"
                )
        else:
            return HttpResponseForbidden(
                "Forbidden: Can't reject translations from other users"
            )

    # Check if translation was approved. We must do this before unapproving it.
    if translation.approved or translation.fuzzy:
        translation.entity.mark_changed(locale)
        TranslatedResource.objects.get(
            resource=translation.entity.resource,
            locale=locale
        ).calculate_stats()

    translation.rejected = True
    translation.rejected_user = request.user
    translation.rejected_date = timezone.now()
    translation.approved = False
    translation.approved_user = None
    translation.approved_date = None
    translation.fuzzy = False
    translation.save()

    latest_translation = translation.entity.translation_set.filter(
        locale=translation.locale,
        plural_form=translation.plural_form,
    ).order_by('-approved', 'rejected', '-date')[0].serialize()
    project = translation.entity.resource.project

    TranslationMemoryEntry.objects.filter(translation=translation).delete()

    return JsonResponse({
        'translation': latest_translation,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def unreject_translation(request):
    """Unreject given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    translation = Translation.objects.get(pk=t)

    # Only privileged users or authors can un-reject translations
    if not (
        request.user.can_translate(
            project=translation.entity.resource.project,
            locale=translation.locale
        ) or
        request.user == translation.user or
        translation.approved
    ):
        return HttpResponseForbidden(
            "Forbidden: You can't unreject this translation."
        )

    translation.unreject(request.user)
    latest_translation = translation.entity.translation_set.filter(
        locale=translation.locale,
        plural_form=translation.plural_form,
    ).order_by('-approved', 'rejected', '-date')[0].serialize()
    project = translation.entity.resource.project
    locale = translation.locale
    return JsonResponse({
        'translation': latest_translation,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@require_POST
@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def update_translation(request):
    """Update entity translation for the specified locale and user."""

    try:
        entity = request.POST['entity']
        string = request.POST['translation']
        locale = request.POST['locale']
        plural_form = request.POST['plural_form']
        original = request.POST['original']
        ignore_check = request.POST['ignore_check']
        approve = request.POST.get('approve', 'false') == 'true'
        force_suggestions = request.POST.get('force_suggestions', 'false') == 'true'
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as error:
        log.error(str(error))
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as error:
        log.error(str(error))
        return HttpResponse("error")

    if plural_form == "-1":
        plural_form = None

    user = request.user
    project = e.resource.project

    try:
        quality_checks = UserProfile.objects.get(user=user).quality_checks
    except UserProfile.DoesNotExist as error:
        quality_checks = True

    ignore = False
    if ignore_check == 'true' or not quality_checks:
        ignore = True

    now = timezone.now()
    can_translate = (
        request.user.can_translate(project=project, locale=l) and
        (not force_suggestions or approve)
    )
    translations = Translation.objects.filter(
        entity=e, locale=l, plural_form=plural_form)

    # Newlines are not allowed in .lang files (bug 1190754)
    if e.resource.format == 'lang' and '\n' in string:
        return HttpResponse('Newline characters are not allowed.')

    # Translations exist
    if len(translations) > 0:

        # Same translation exists
        same_translations = translations.filter(string=string).order_by(
            '-approved', 'rejected', '-date'
        )
        if len(same_translations) > 0:
            t = same_translations[0]

            # If added by privileged user, approve and unfuzzy it
            if can_translate:

                # Unless there's nothing to be changed
                if t.approved and not t.fuzzy:
                    return JsonResponse({
                        'same': True,
                        'message': 'Same translation already exists.',
                    })

                warnings = utils.quality_check(original, string, l, ignore)
                if warnings:
                    return warnings

                translations.update(
                    approved=False,
                    approved_user=None,
                    approved_date=None,
                    rejected=True,
                    rejected_user=request.user,
                    rejected_date=timezone.now(),
                    fuzzy=False,
                )

                t.approved = True
                t.fuzzy = False
                t.rejected = False
                t.rejected_user = None
                t.rejected_date = None

                if t.approved_user is None:
                    t.approved_user = user
                    t.approved_date = now

                t.save()

                return JsonResponse({
                    'type': 'updated',
                    'translation': t.serialize(),
                    'stats': TranslatedResource.objects.stats(project, paths, l),
                })

            # If added by non-privileged user, unfuzzy it
            else:
                if t.fuzzy:
                    warnings = utils.quality_check(original, string, l, ignore)
                    if warnings:
                        return warnings

                    t.approved = False
                    t.approved_user = None
                    t.approved_date = None
                    t.fuzzy = False

                    t.save()

                    return JsonResponse({
                        'type': 'updated',
                        'translation': t.serialize(),
                        'stats': TranslatedResource.objects.stats(project, paths, l),
                    })

                return JsonResponse({
                    'same': True,
                    'message': 'Same translation already exists.',
                })

        # Different translation added
        else:
            warnings = utils.quality_check(original, string, l, ignore)
            if warnings:
                return warnings

            if can_translate:
                translations.update(approved=False, approved_user=None, approved_date=None)

            translations.update(fuzzy=False)

            t = Translation(
                entity=e, locale=l, user=user, string=string,
                plural_form=plural_form, date=now,
                approved=can_translate)

            if can_translate:
                t.approved_user = user
                t.approved_date = now

            t.save()

            # Return active (approved or latest) translation
            try:
                active = translations.filter(approved=True).latest("date")
            except Translation.DoesNotExist:
                active = translations.latest("date")

            return JsonResponse({
                'type': 'added',
                'translation': active.serialize(),
                'stats': TranslatedResource.objects.stats(project, paths, l),
            })

    # No translations saved yet
    else:
        warnings = utils.quality_check(original, string, l, ignore)
        if warnings:
            return warnings

        t = Translation(
            entity=e, locale=l, user=user, string=string,
            plural_form=plural_form, date=now,
            approved=can_translate)

        if can_translate:
            t.approved_user = user
            t.approved_date = now

        t.save()

        return JsonResponse({
            'type': 'saved',
            'translation': t.serialize(),
            'stats': TranslatedResource.objects.stats(project, paths, l),
        })


@require_POST
@transaction.atomic
def download(request):
    """Download translated resource."""
    try:
        slug = request.POST['slug']
        code = request.POST['code']
        part = request.POST['part']
    except MultiValueDictKeyError:
        raise Http404

    content, filename = utils.get_download_content(slug, code, part)

    if content is None:
        raise Http404

    response = HttpResponse()
    response.content = content
    response['Content-Type'] = 'text/plain'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    return response


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def upload(request):
    """Upload translated resource."""
    try:
        slug = request.POST['slug']
        code = request.POST['code']
        part = request.POST['part']
    except MultiValueDictKeyError:
        raise Http404

    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(Project, slug=slug)

    if not request.user.can_translate(project=project, locale=locale):
        return HttpResponseForbidden("Forbidden: You don't have permission to upload files")

    form = forms.UploadFileForm(request.POST, request.FILES)

    if form.is_valid():
        f = request.FILES['uploadfile']
        utils.handle_upload_content(slug, code, part, f, request.user)
        messages.success(request, 'Translations updated from uploaded file.')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)

    return translate(request, code, slug, part)


@condition(etag_func=None)
def download_translation_memory(request, locale, slug, filename):
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project, slug=slug)

    tm_entries = (
        TranslationMemoryEntry.objects
        .filter(locale=locale, project=project, translation__isnull=False)
        .exclude(Q(source='') | Q(target=''))
        .exclude(translation__approved=False, translation__fuzzy=False)
    )
    filename = '{code}.{slug}.tmx'.format(code=locale.code, slug=project.slug)

    response = StreamingHttpResponse(
        utils.build_translation_memory_file(
            datetime.now(),
            locale.code,
            tm_entries.values_list(
                'entity__resource__path',
                'entity__key',
                'source',
                'target',
                'project__name',
                'project__slug'
            ).order_by('project__slug', 'source')
        ),
        content_type='text/xml'
    )
    response['Content-Disposition'] = 'attachment; filename="{filename}"'.format(filename=filename)
    return response


class AjaxFormView(FormView):
    """A form view that when the form is submitted, it will return a json
    response containing either an ``errors`` object with a bad response status
    if the form fails, or a ``result`` object supplied by the form's save
    method
    """

    @method_decorator(utils.require_AJAX)
    def get(self, *args, **kwargs):
        return super(AjaxFormView, self).get(*args, **kwargs)

    @method_decorator(utils.require_AJAX)
    def post(self, *args, **kwargs):
        return super(AjaxFormView, self).post(*args, **kwargs)

    def form_invalid(self, form):
        return HttpResponseBadRequest(
            json.dumps(dict(errors=form.errors)),
            content_type='application/json')

    def form_valid(self, form):
        return JsonResponse(dict(result=form.save()))


class AjaxFormPostView(AjaxFormView):
    """An Ajax form view that only allows POST requests"""

    def get(self, *args, **kwargs):
        raise Http404
