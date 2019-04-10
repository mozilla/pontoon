import logging
from datetime import datetime

import waffle

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseForbidden,
    JsonResponse,
    StreamingHttpResponse
)
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    condition,
    require_POST
)
from django.views.generic.edit import FormView

from six.moves.urllib.parse import urlparse

from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
    TranslatedResource,
    Translation,
    UserProfile,
)
from pontoon.base.templatetags.helpers import provider_login_url
from pontoon.checks.libraries import run_checks
from pontoon.checks.utils import are_blocking_checks


log = logging.getLogger(__name__)

# TRANSLATE VIEWs


def translate(request, locale, slug, part):
    """Translate view."""
    # Redirect the user to the Translate.Next app if needed.
    # To be removed as part of bug 1527853.
    user = request.user
    if (
        waffle.switch_is_active('translate_next') and
        user.is_authenticated and
        user.profile.use_translate_next
    ):
        url = reverse(
            'pontoon.translate.next',
            kwargs={
                'project': slug,
                'locale': locale,
                'resource': part,
            }
        )
        query = request.GET.urlencode()
        if query:
            url += '?' + query

        return redirect(url)

    locale = get_object_or_404(Locale, code=locale)

    projects = (
        Project.objects.available()
        .prefetch_related('subpage_set', 'tag_set')
        .order_by('name')
    )

    if slug.lower() == 'all-projects':
        project = Project(name='All Projects', slug=slug.lower())

    else:
        project = get_object_or_404(Project.objects.available(), slug=slug)
        if locale not in project.locales.all():
            raise Http404

    return render(request, 'translate.html', {
        'download_form': forms.DownloadFileForm(),
        'upload_form': forms.UploadFileForm(),
        'locale': locale,
        'locale_projects': locale.available_projects_list(),
        'locales': Locale.objects.available(),
        'part': part,
        'project': project,
        'projects': projects,
        'is_google_translate_supported': bool(settings.GOOGLE_TRANSLATE_API_KEY),
        'is_microsoft_translator_supported': bool(settings.MICROSOFT_TRANSLATOR_API_KEY),
    })


def translate_locale_agnostic(request, slug, part):
    """Locale Agnostic Translate view."""
    user = request.user
    query = urlparse(request.get_full_path()).query
    query = '?%s' % query if query else ''

    if slug.lower() == 'all-projects':
        project_locales = Locale.objects.available()
    else:
        project = get_object_or_404(Project.objects.available(), slug=slug)
        project_locales = project.locales

    if user.is_authenticated():
        locale = user.profile.custom_homepage

        if locale and project_locales.filter(code=locale).exists():
            path = reverse(
                'pontoon.translate',
                kwargs=dict(slug=slug, locale=locale, part=part))
            return redirect("%s%s" % (path, query))

    locale = utils.get_project_locale_from_request(request, project_locales)
    path = (
        reverse(
            'pontoon.translate',
            kwargs=dict(slug=slug, locale=locale, part=part))
        if locale
        else reverse(
            'pontoon.projects.project',
            kwargs=dict(slug=slug)))
    return redirect("%s%s" % (path, query))


@utils.require_AJAX
def locale_projects(request, locale):
    """Get active projects for locale."""
    locale = get_object_or_404(Locale, code=locale)

    return JsonResponse(locale.available_projects_list(), safe=False)


@utils.require_AJAX
def locale_stats(request, locale):
    """Get locale stats used in All Resources part."""
    locale = get_object_or_404(Locale, code=locale)
    return JsonResponse(locale.stats(), safe=False)


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
        'authors': translations.authors(),
        'counts_per_minute': translations.counts_per_minute(),
    }, safe=False)


def _get_entities_list(locale, project, form):
    """Return a specific list of entities, as defined by the `entity_ids` field of the form.

    This is used for batch editing.
    """
    entities = (
        Entity.objects.filter(pk__in=form.cleaned_data['entity_ids'])
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
        })

    has_next = entities_page.has_next()
    entities_to_map = entities_page.object_list

    # If requested entity not on the first page
    if form.cleaned_data['entity']:
        entity_pk = form.cleaned_data['entity']
        entities_to_map_pks = [e.pk for e in entities_to_map]

        # TODO: entities_to_map.values_list() doesn't return entities from selected page
        if entity_pk not in entities_to_map_pks:
            if entity_pk in entities.values_list('pk', flat=True):
                entities_to_map_pks.append(entity_pk)
                entities_to_map = entities.filter(pk__in=entities_to_map_pks)

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
        return JsonResponse({
            'status': False,
            'message': '{error}'.format(error=form.errors.as_json(escape_html=True)),
        }, status=400)

    locale = get_object_or_404(Locale, code=form.cleaned_data['locale'])

    project_slug = form.cleaned_data['project']
    if project_slug == 'all-projects':
        project = Project(slug=project_slug)
    else:
        project = get_object_or_404(Project, slug=project_slug)

    # Only return entities with provided IDs (batch editing)
    if form.cleaned_data['entity_ids']:
        return _get_entities_list(locale, project, form)

    # `Entity.for_project_locale` only requires a subset of the fields the form contains. We thus
    # make a new dict with only the keys we want to pass to that function.
    restrict_to_keys = (
        'paths', 'status', 'search', 'exclude_entities', 'extra', 'time', 'author', 'tag',
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
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

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
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    entity = get_object_or_404(Entity, pk=entity)
    locale = get_object_or_404(Locale, code=locale)

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-active', 'rejected', '-date')

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
def approve_translation(request):
    """Approve given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale
    user = request.user

    # Read-only translations cannot be approved
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    if translation.approved:
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This translation is already approved.',
        }, status=403)

    # Only privileged users can approve translations
    if not user.can_translate(locale, project):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You don't have permission to approve this translation.",
        }, status=403)

    # Check for errors.
    # Checks are disabled for the tutorial.
    use_checks = project.slug != 'tutorial'

    if use_checks and translation.errors.exists():
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This translation has errors.',
        }, status=403)

    translation.approve(user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def unapprove_translation(request):
    """Unapprove given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be un-approved
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Only privileged users or authors can un-approve translations
    if not (
        request.user.can_translate(locale, project) or
        request.user == translation.user or
        translation.approved
    ):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You can't unapprove this translation.",
        }, status=403)

    translation.unapprove(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def reject_translation(request):
    """Reject given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be rejected
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Non-privileged users can only reject own unapproved translations
    if not request.user.can_translate(locale, project):
        if translation.user == request.user:
            if translation.approved is True:
                return JsonResponse({
                    'status': False,
                    'message': "Forbidden: You can't reject approved translations.",
                }, status=403)
        else:
            return JsonResponse({
                'status': False,
                'message': "Forbidden: You can't reject translations from other users.",
            }, status=403)

    translation.reject(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
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
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be un-rejected
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Only privileged users or authors can un-reject translations
    if not (
        request.user.can_translate(locale, project) or
        request.user == translation.user or
        translation.approved
    ):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You can't unreject this translation.",
        }, status=403)

    translation.unreject(request.user)

    active_translation = translation.entity.reset_active_translation(
        locale=locale,
        plural_form=translation.plural_form,
    )

    return JsonResponse({
        'translation': active_translation.serialize(),
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def delete_translation(request):
    """Delete given translation."""
    try:
        t = request.POST['translation']
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    translation = get_object_or_404(Translation, pk=t)
    project = translation.entity.resource.project
    locale = translation.locale

    # Read-only translations cannot be deleted
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    # Only privileged users or authors can delete translations
    if not translation.rejected or not (
        request.user.can_translate(locale, project) or
        request.user == translation.user or
        translation.approved
    ):
        return JsonResponse({
            'status': False,
            'message': "Forbidden: You can't delete this translation.",
        }, status=403)

    translation.delete()

    return JsonResponse({
        'status': True,
    })


@utils.require_AJAX
def perform_checks(request):
    """Perform quality checks and return a list of any failed ones."""
    try:
        entity = request.POST['entity']
        locale_code = request.POST['locale_code']
        original = request.POST['original']
        string = request.POST['string']
        ignore_warnings = request.POST.get('ignore_warnings', 'false') == 'true'
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    try:
        entity = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    try:
        use_ttk_checks = UserProfile.objects.get(user=request.user).quality_checks
    except UserProfile.DoesNotExist:
        use_ttk_checks = True

    failed_checks = run_checks(
        entity,
        locale_code,
        original,
        string,
        use_ttk_checks,
    )

    if are_blocking_checks(failed_checks, ignore_warnings):
        return JsonResponse({
            'failedChecks': failed_checks,
        })
    else:
        return JsonResponse({
            'status': True,
        })


@require_POST
@utils.require_AJAX
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def update_translation(request):
    """Update entity translation for the specified locale and user.

    Note that this view is also used to approve a translation by the old
    Translate app. Once we migrate to Translate.Next, we'll want to rework
    this view to remove the bits about approving a translation, because that
    has been delegated to the `approve_translation` view.

    """
    try:
        entity = request.POST['entity']
        string = request.POST['translation']
        locale = request.POST['locale']
        plural_form = request.POST['plural_form']
        original = request.POST['original']
        ignore_warnings = request.POST.get('ignore_warnings', 'false') == 'true'
        approve = request.POST.get('approve', 'false') == 'true'
        force_suggestions = request.POST.get('force_suggestions', 'false') == 'true'
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        return JsonResponse({
            'status': False,
            'message': 'Bad Request: {error}'.format(error=e),
        }, status=400)

    if plural_form == "-1":
        plural_form = None

    user = request.user
    project = e.resource.project

    # Read-only translations cannot saved
    if utils.readonly_exists(project, locale):
        return JsonResponse({
            'status': False,
            'message': 'Forbidden: This string is in read-only mode.',
        }, status=403)

    try:
        use_ttk_checks = UserProfile.objects.get(user=user).quality_checks
    except UserProfile.DoesNotExist:
        use_ttk_checks = True

    # Disable checks for tutorial project.
    if project.slug == 'tutorial':
        use_ttk_checks = False

    now = timezone.now()
    can_translate = (
        request.user.can_translate(project=project, locale=locale) and
        (not force_suggestions or approve)
    )
    translations = Translation.objects.filter(
        entity=e, locale=locale, plural_form=plural_form)

    same_translations = translations.filter(string=string).order_by(
        '-active', 'rejected', '-date'
    )

    # If same translation exists in the DB, don't save it again.
    if utils.is_same(same_translations, can_translate):
        return JsonResponse({
            'same': True,
        })

    failed_checks = run_checks(
        e,
        locale.code,
        original,
        string,
        use_ttk_checks,
    )

    if are_blocking_checks(failed_checks, ignore_warnings):
        return JsonResponse({
            'failedChecks': failed_checks,
        })

    # Translations exist
    if len(translations) > 0:
        # Same translation exists
        if len(same_translations) > 0:
            t = same_translations[0]

            # If added by privileged user, approve and unfuzzy it
            if can_translate and (t.fuzzy or not t.approved):
                if not t.active:
                    translations.filter(active=True).update(active=False)
                    t.active = True

                t.approved = True
                t.fuzzy = False
                t.rejected = False
                t.rejected_user = None
                t.rejected_date = None

                if t.approved_user is None:
                    t.approved_user = user
                    t.approved_date = now

                t.save(failed_checks=failed_checks)

                return JsonResponse({
                    'type': 'updated',
                    'translation': t.serialize(),
                    'stats': TranslatedResource.objects.stats(project, paths, locale),
                })

        # Different translation added
        else:
            t = Translation(
                entity=e,
                locale=locale,
                plural_form=plural_form,
                string=string,
                user=user,
                date=now,
                approved=can_translate,
            )

            if can_translate:
                t.approved_user = user
                t.approved_date = now

            t.save(failed_checks=failed_checks)

            active_translation = e.reset_active_translation(
                locale=locale,
                plural_form=plural_form,
            )

            return JsonResponse({
                'type': 'added',
                'translation': active_translation.serialize(),
                'stats': TranslatedResource.objects.stats(project, paths, locale),
            })

    # No translations saved yet
    else:
        t = Translation(
            entity=e,
            locale=locale,
            plural_form=plural_form,
            string=string,
            user=user,
            date=now,
            active=True,
            approved=can_translate,
        )

        if can_translate:
            t.approved_user = user
            t.approved_date = now

        t.save(failed_checks=failed_checks)

        return JsonResponse({
            'type': 'saved',
            'translation': t.serialize(),
            'stats': TranslatedResource.objects.stats(project, paths, locale),
        })


@transaction.atomic
def download(request):
    """Download translated resource."""
    try:
        slug = request.GET['slug']
        code = request.GET['code']
        part = request.GET['part']
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

    if (
        not request.user.can_translate(project=project, locale=locale)
        or utils.readonly_exists(project, locale)
    ):
        return HttpResponseForbidden("You don't have permission to upload files.")

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

    if slug.lower() == 'all-projects':
        project_filter = Q()
    else:
        project = get_object_or_404(Project.objects.available(), slug=slug)
        project_filter = Q(project=project)

    tm_entries = (
        TranslationMemoryEntry.objects
        .filter(project_filter)
        .filter(locale=locale, translation__isnull=False)
        .exclude(Q(source='') | Q(target=''))
        .exclude(translation__approved=False, translation__fuzzy=False)
    )
    filename = '{code}.{slug}.tmx'.format(code=locale.code, slug=slug)

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


@utils.require_AJAX
def user_data(request):
    user = request.user

    if not user.is_authenticated:
        if settings.DJANGO_LOGIN:
            login_url = reverse('standalone_login')
        else:
            login_url = provider_login_url(request)

        return JsonResponse({
            'is_authenticated': False,
            'login_url': login_url,
        })

    if settings.DJANGO_LOGIN:
        logout_url = reverse('standalone_logout')
    else:
        logout_url = reverse('account_logout')

    return JsonResponse({
        'is_authenticated': True,
        'is_admin': user.has_perm('base.can_manage_project'),
        'id': user.id,
        'email': user.email,
        'display_name': user.display_name,
        'name_or_email': user.name_or_email,
        'username': user.username,
        'manager_for_locales': list(
            user.managed_locales.values_list('code', flat=True)
        ),
        'translator_for_locales': list(
            user.translated_locales.values_list('code', flat=True)
        ),
        'translator_for_projects': user.translated_projects,
        'settings': {
            'quality_checks': user.profile.quality_checks,
            'force_suggestions': user.profile.force_suggestions,
        },
        'preferred_locales': user.profile.sorted_locales_codes,
        'logout_url': logout_url,
        'gravatar_url_small': user.gravatar_url(44),
        'gravatar_url_big': user.gravatar_url(88),
        'notifications': user.serialized_notifications,
    })


# To be removed as part of bug 1527853.
@login_required(redirect_field_name='', login_url='/403')
@transaction.atomic
def toggle_use_translate_next(request):
    profile = request.user.profile
    profile.use_translate_next = not profile.use_translate_next
    profile.save()

    next = request.GET.get('next')
    if next:
        return redirect(next)

    return redirect(reverse('pontoon.homepage'))


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
        return JsonResponse(dict(errors=form.errors), status=400)

    def form_valid(self, form):
        return JsonResponse(dict(data=form.save()))


class AjaxFormPostView(AjaxFormView):
    """An Ajax form view that only allows POST requests"""

    def get(self, *args, **kwargs):
        raise Http404
