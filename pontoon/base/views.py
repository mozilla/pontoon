import logging
import os

from bulk_update.helper import bulk_update
from datetime import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import (
    condition,
    require_POST
)

from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.models import (
    ChangedEntityLocale,
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
from pontoon.base.utils import (
    build_translation_memory_file,
    split_ints,
    require_AJAX,
)


log = logging.getLogger('pontoon')


def home(request):
    """Home view."""
    project = Project.objects.get(id=1)
    locale = utils.get_project_locale_from_request(
        request, project.locales) or 'en-GB'
    path = Resource.objects.filter(project=project, translatedresources__locale__code=locale)[0].path

    return translate(request, locale, project.slug, path)


def heroku_setup(request):
    """
    Heroku doesn't allow us to set SITE_URL or Site during the build phase of an app.
    Because of that we have to set everything up after build is done and app is
    able to retrieve a domain.
    """
    app_host = request.get_host()
    homepage_url = 'https://{}/'.format(app_host)
    site_domain = Site.objects.get(pk=1).domain

    if not os.environ.get('HEROKU_DEMO') or site_domain != 'example.com':
        return redirect(homepage_url)

    admin_email = os.environ.get('ADMIN_EMAIL')
    admin_password = os.environ.get('ADMIN_PASSWORD')

    User.objects.create_superuser(admin_email, admin_email, admin_password)
    Site.objects.filter(pk=1).update(name=app_host, domain=app_host)

    Project.objects.filter(slug='pontoon-intro').update(
       url='https://{}/intro/'.format(app_host)
    )

    # Clear the cache to ensure that SITE_URL will be regenerated.
    cache.delete(settings.APP_URL_KEY)
    return redirect(homepage_url)


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
        'locales': Locale.objects.available(),
        'part': part,
        'project': project,
        'projects': projects,
    })


@require_AJAX
def locale_projects(request, locale):
    """Get active projects for locale."""
    locale = get_object_or_404(Locale, code=locale)

    return JsonResponse(locale.available_projects_list(), safe=False)


@require_AJAX
def locale_project_parts(request, locale, slug):
    """Get locale-project pages/paths with stats."""
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project, slug=slug)

    return JsonResponse(locale.parts_stats(project), safe=False)


@require_AJAX
def authors_and_time_range(request, locale, slug, part):
    locale = get_object_or_404(Locale, code=locale)
    project = get_object_or_404(Project.objects.available(), slug=slug)
    paths = [part] if part != 'all-resources' else None

    translations = Translation.for_locale_project_paths(locale, project, paths)

    return JsonResponse({
        'authors': translations.authors().serialize(),
        'counts_per_minute': translations.counts_per_minute(),
    }, safe=False)


@csrf_exempt
@require_POST
@require_AJAX
def entities(request):
    """Get entities for the specified project, locale and paths."""
    try:
        project = request.POST['project']
        locale = request.POST['locale']
        paths = request.POST.getlist('paths[]')
        limit = int(request.POST.get('limit', 50))
    except (MultiValueDictKeyError, ValueError) as err:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=err))

    project = get_object_or_404(Project, slug=project)
    locale = get_object_or_404(Locale, code=locale)

    status = request.POST.get('status', '')
    extra = request.POST.get('extra', '')
    time = request.POST.get('time', '')
    author = request.POST.get('author', '')
    search = request.POST.get('search', '')
    exclude_entities = split_ints(request.POST.get('excludeEntities', ''))

    # Only return entities with provided IDs (batch editing)
    entity_ids = split_ints(request.POST.get('entityIds', ''))

    if entity_ids:
        entities = (
            Entity.objects.filter(pk__in=entity_ids)
            .prefetch_resources_translations(locale)
            .distinct()
            .order_by('order')
        )

        return JsonResponse({
            'entities': Entity.map_entities(locale, entities),
            'stats': TranslatedResource.objects.stats(project, paths, locale),
        }, safe=False)

    entities = Entity.for_project_locale(
        project, locale, paths, status, search, exclude_entities, extra, time, author
    )

    # Only return a list of entity PKs (batch editing: select all)
    if request.POST.get('pkOnly', None):
        return JsonResponse({
            'entity_pks': list(entities.values_list('pk', flat=True)),
        })

    visible_entities = []

    # In-place view: load all entities
    if request.POST.get('inplaceEditor', None):
        has_next = False
        entities_to_map = Entity.for_project_locale(
            project, locale, paths, None, None, exclude_entities
        )
        visible_entities = entities.values_list('pk', flat=True)

    # Out-of-context view: paginate entities
    else:
        paginator = Paginator(entities, limit)

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
        entity = request.POST.get('entity', None)
        if entity:
            try:
                entity_pk = int(entity)
            except ValueError as err:
                return HttpResponseBadRequest('Bad Request: {error}'.format(error=err))

            # TODO: entities_to_map.values_list() doesn't return entities from selected page
            if entity_pk not in [e.pk for e in entities_to_map]:
                if entity_pk in entities.values_list('pk', flat=True):
                    entities_to_map = list(entities_to_map) + list(entities.filter(pk=entity_pk))

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities_to_map, visible_entities),
        'has_next': has_next,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    }, safe=False)


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@require_AJAX
@transaction.atomic
def batch_edit_translations(request):
    try:
        l = request.POST['locale']
        action = request.POST['action']
        entity_pks = split_ints(request.POST.get('entities', ''))
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    locale = get_object_or_404(Locale, code=l)

    entities = (
        Entity.objects.filter(pk__in=entity_pks)
        .prefetch_resources_translations(locale)
    )

    if not entities.exists():
        return JsonResponse({'count': 0})

    # Batch editing is only available to translators.
    # Check if user has translate permissions for all of the projects in passed entities.
    projects = Project.objects.filter(pk__in=entities.values_list('resource__project__pk', flat=True).distinct())
    for project in projects:
        if not request.user.can_translate(project=project, locale=locale):
            return HttpResponseForbidden(
                "Forbidden: You don't have permission for batch editing"
            )

    translation_pks = set()

    for entity in entities:
        if entity.string_plural == "":
            translation_pks.add(entity.get_translation()['pk'])

        else:
            for plural_form in range(0, locale.nplurals or 1):
                translation_pks.add(entity.get_translation(plural_form)['pk'])

    translation_pks.discard(None)
    translations = Translation.objects.filter(pk__in=translation_pks)
    latest_translation_pk = None
    changed_translation_pks = []

    # Must be executed before translations set changes, which is why
    # we need to force evaluate QuerySets by wrapping them inside list()
    def get_translations_info(translations):
        count = translations.count()
        translated_resources = list(translations.translated_resources(locale))
        changed_entities = list(Entity.objects.filter(translation__in=translations).distinct())

        return count, translated_resources, changed_entities

    if action == 'approve':
        translations = translations.filter(approved=False)
        changed_translation_pks = list(translations.values_list('pk', flat=True))
        if changed_translation_pks:
            latest_translation_pk = translations.last().pk
        count, translated_resources, changed_entities = get_translations_info(translations)
        translations.update(
            approved=True,
            approved_user=request.user,
            approved_date=timezone.now()
        )

    elif action == 'delete':
        count, translated_resources, changed_entities = get_translations_info(translations)
        translations.delete()

    elif action == 'replace':
        find = request.POST.get('find')
        replace = request.POST.get('replace')

        try:
            translations, changed_translations = translations.find_and_replace(find, replace, request.user)
            changed_translation_pks = [c.pk for c in changed_translations]
            if changed_translation_pks:
                latest_translation_pk = max(changed_translation_pks)
        except Translation.NotAllowed:
            return JsonResponse({
                'error': 'Empty translations not allowed',
            })

        count, translated_resources, changed_entities = get_translations_info(translations)

    if count == 0:
        return JsonResponse({'count': 0})

    # Update stats
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

    # Mark translations as changed
    changed_entities_array = []
    existing = ChangedEntityLocale.objects.values_list('entity', 'locale').distinct()
    for changed_entity in changed_entities:
        key = (changed_entity.pk, locale.pk)

        # Remove duplicate changes to prevent unique constraint violation
        if not key in existing:
            changed_entities_array.append(
                ChangedEntityLocale(entity=changed_entity, locale=locale)
            )
    ChangedEntityLocale.objects.bulk_create(changed_entities_array)

    # Update latest translation
    if latest_translation_pk:
        Translation.objects.get(pk=latest_translation_pk).update_latest_translation()

    # Update translation memory
    memory_entries = [TranslationMemoryEntry(
        source=t.entity.string,
        target=t.string,
        locale=locale,
        entity=t.entity,
        translation=t,
        project=project,
    ) for t in Translation.objects.filter(pk__in=changed_translation_pks).prefetch_related('entity__resource')]
    TranslationMemoryEntry.objects.bulk_create(memory_entries)

    return JsonResponse({
        'count': count
    })


@require_AJAX
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


@require_AJAX
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
    translations = translations.order_by('-approved', '-date')

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


@require_AJAX
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
    if not (request.user.can_translate(project=translation.entity.resource.project, locale=translation.locale)
            or request.user == translation.user
            or translation.approved):
        return HttpResponseForbidden("Forbidden: You can't unapprove this translation.")

    translation.unapprove(request.user)
    latest_translation = translation.entity.translation_set.filter(
        locale=translation.locale,
        plural_form=translation.plural_form,
    ).latest('date').serialize()
    project = translation.entity.resource.project
    locale = translation.locale
    return JsonResponse({
        'translation': latest_translation,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@require_AJAX
@transaction.atomic
def delete_translation(request):
    """Delete given translation."""
    try:
        t = request.POST['translation']
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    translation = get_object_or_404(Translation, pk=t)

    # Non-privileged users can only delete own unapproved translations
    if not request.user.can_translate(translation.locale, translation.entity.resource.project):
        if translation.user == request.user:
            if translation.approved is True:
                return HttpResponseForbidden(
                    "Forbidden: Can't delete approved translations"
                )
        else:
            return HttpResponseForbidden(
                "Forbidden: Can't delete translations from other users"
            )

    translation.delete()

    project = translation.entity.resource.project
    locale = translation.locale

    return JsonResponse({
        'stats': TranslatedResource.objects.stats(project, paths, locale),
    })


@require_POST
@require_AJAX
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
        request.user.can_translate(project=project, locale=l)
        and (not force_suggestions or approve)
    )
    translations = Translation.objects.filter(
        entity=e, locale=l, plural_form=plural_form)

    # Newlines are not allowed in .lang files (bug 1190754)
    if e.resource.format == 'lang' and '\n' in string:
        return HttpResponse('Newline characters are not allowed.')

    # Translations exist
    if len(translations) > 0:

        # Same translation exists
        try:
            t = translations.get(string=string)

            # If added by privileged user, approve and unfuzzy it
            if can_translate:

                # Unless there's nothing to be changed
                if t.user is not None and t.approved and t.approved_user \
                        and t.approved_date and not t.fuzzy:
                    return JsonResponse({
                        'same': True,
                        'message': 'Same translation already exists.',
                    })

                warnings = utils.quality_check(original, string, l, ignore)
                if warnings:
                    return warnings

                translations.update(approved=False, approved_user=None, approved_date=None)
                translations.update(fuzzy=False)

                if t.user is None:
                    t.user = user

                t.approved = True
                t.approved_date = timezone.now()
                t.fuzzy = False

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

                    if t.user is None:
                        t.user = user

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
        except:
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
        TranslationMemoryEntry.objects.filter(
            locale=locale,
            project=project,
            translation__isnull=False,
        ).exclude(Q(source='') | Q(target=''))
    )
    filename = '{code}.{slug}.tmx'.format(code=locale.code, slug=project.slug)

    response = StreamingHttpResponse(
        build_translation_memory_file(
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
