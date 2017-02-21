from __future__ import division

import json
import logging
import math
import os
import requests
import urllib
import xml.etree.ElementTree as ET

from bulk_update.helper import bulk_update
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction, DataError
from django.db.models import Count, Q
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from guardian.decorators import permission_required_or_403
from suds.client import Client, WebFault

from pontoon.base import forms
from pontoon.base import utils
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
    Translation,
    TranslationMemoryEntry,
    UserProfile,
)
from pontoon.base.utils import require_AJAX
from pontoon.sync.models import SyncLog
from pontoon.sync.tasks import sync_project


log = logging.getLogger('pontoon')


def home(request):
    """Home view."""
    project = Project.objects.get(id=1)
    locale = utils.get_project_locale_from_request(
        request, project.locales) or 'en-GB'
    path = Resource.objects.filter(project=project, translatedresources__locale__code=locale)[0].path

    return translate(request, locale, project.slug, path)


def locale(request, locale):
    """Locale view."""
    l = get_object_or_404(Locale, code__iexact=locale)

    projects = (
        Project.objects.available()
        .order_by('name')
    )

    if not projects:
        raise Http404

    return render(request, 'locale.html', {
        'projects': projects,
        'locale': l,
    })


@login_required(redirect_field_name='', login_url='/403')
@permission_required_or_403('base.can_manage_locale', (Locale, 'code', 'locale'))
@transaction.atomic
def locale_permissions(request, locale):
    l = get_object_or_404(Locale, code__iexact=locale)
    project_locales = l.project_locale.available()

    if request.method == 'POST':
        locale_form = forms.LocalePermsForm(request.POST, instance=l, prefix='general')
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            request.POST,
            prefix='project-locale',
            queryset=project_locales,
        )

        if locale_form.is_valid() and project_locale_form.is_valid():
            locale_form.save()
            project_locale_form.save()

        else:
            errors = locale_form.errors
            errors.update(project_locale_form.errors_dict)
            return HttpResponseBadRequest(json.dumps(errors))

    else:
        project_locale_form = forms.ProjectLocalePermsFormsSet(
            prefix='project-locale',
            queryset=project_locales,
        )

    managers = l.managers_group.user_set.all()
    translators = l.translators_group.user_set.exclude(pk__in=managers).all()
    all_users = User.objects.exclude(pk__in=managers).exclude(pk__in=translators).exclude(email='')

    contributors = User.translators.filter(translation__locale=l).values_list('email', flat=True).distinct()
    locale_projects = l.projects_permissions
    return render(request, 'locale_permissions.html', {
        'locale': l,
        'all_users': all_users,
        'contributors': contributors,
        'translators': translators,
        'managers': managers,
        'locale_projects': locale_projects,
        'project_locale_form': project_locale_form,
        'all_projects_in_translation': all([x[5] for x in locale_projects])
    })


def locales(request):
    """Localization teams."""
    locales = (
        Locale.objects.available()
    )

    return render(request, 'locales.html', {
        'locales': locales,
    })


def project(request, slug):
    """Project view."""
    project = get_object_or_404(Project.objects.available(), slug=slug)

    locales = (
        project.locales.all()
        .prefetch_latest_translation(project)
        .order_by('name')
    )

    return render(request, 'project.html', {
        'locales': locales,
        'project': project,
    })


def projects(request):
    """Project overview."""
    projects = (
        Project.objects.available()
        .select_related('latest_translation__user')
        .order_by('name')
    )

    return render(request, 'projects.html', {
        'projects': projects,
    })


@login_required(redirect_field_name='', login_url='/403')
@require_AJAX
def manually_sync_project(request, slug):
    if not request.user.has_perm('base.can_manage') or not settings.MANUAL_SYNC:
        return HttpResponseForbidden(
            "Forbidden: You don't have permission for syncing projects"
        )

    sync_log = SyncLog.objects.create(start_time=timezone.now())
    project = Project.objects.get(slug=slug)
    sync_project.delay(project.pk, sync_log.pk)

    return HttpResponse('ok')


def locale_project(request, locale, slug):
    """Locale-project overview."""
    l = get_object_or_404(Locale, code__iexact=locale)

    project = get_object_or_404(
        Project.objects.available().prefetch_related('subpage_set'),
        slug=slug
    )

    # Amend the parts dict with latest activity info.
    translatedresources_qs = (
        TranslatedResource.objects
        .filter(resource__project=project, locale=l)
        .select_related('resource', 'latest_translation')
    )

    if not len(translatedresources_qs):
        raise Http404

    translatedresources = {s.resource.path: s for s in translatedresources_qs}
    parts = l.parts_stats(project)

    for part in parts:
        translatedresource = translatedresources.get(part['title'], None)
        if translatedresource and translatedresource.latest_translation:
            part['latest_activity'] = translatedresource.latest_translation.latest_activity
        else:
            part['latest_activity'] = None

        part['chart'] = {
            'translated_strings': part['translated_strings'],
            'fuzzy_strings': part['fuzzy_strings'],
            'total_strings': part['resource__total_strings'],
            'approved_strings': part['approved_strings'],
            'approved_share': round(part['approved_strings'] / part['resource__total_strings'] * 100),
            'translated_share': round(part['translated_strings'] / part['resource__total_strings'] * 100),
            'fuzzy_share': round(part['fuzzy_strings'] / part['resource__total_strings'] * 100),
            'approved_percent': int(math.floor(part['approved_strings'] / part['resource__total_strings'] * 100)),
        }

    return render(request, 'locale_project.html', {
        'locale': l,
        'project': project,
        'parts': parts,
    })


def translate(request, locale, slug, part):
    """Translate view."""
    locale = get_object_or_404(Locale, code__iexact=locale)
    project = get_object_or_404(Project.objects.available(), slug=slug)

    if locale not in project.locales.all():
        raise Http404

    projects = (
        Project.objects.available()
        .prefetch_related('subpage_set')
        .order_by('name')
    )

    paths = [part] if part != 'all-resources' else None
    translations = Translation.for_locale_project_paths(locale, project, paths)

    return render(request, 'translate.html', {
        'download_form': forms.DownloadFileForm(),
        'upload_form': forms.UploadFileForm(),
        'locale': locale,
        'locales': Locale.objects.available(),
        'part': part,
        'project': project,
        'projects': projects,
        'authors': translations.authors().serialize(),
        'counts_per_minute': translations.counts_per_minute(),
    })


@login_required(redirect_field_name='', login_url='/403')
def profile(request):
    """Current user profile."""
    return contributor(request, request.user)


def contributor_email(request, email):
    user = get_object_or_404(User, email=email)
    return contributor(request, user)


def contributor_username(request, username):
    user = get_object_or_404(User, username=username)
    return contributor(request, user)


def contributor_timeline(request, username):
    """Contributor events in the timeline."""
    user = get_object_or_404(User, username=username)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404('Invalid page number.')

    # Exclude obsolete translations
    contributor_translations = (
        user.contributed_translations
            .exclude(entity__obsolete=True)
            .extra({'day': "date(date)"})
            .order_by('-day')
    )

    counts_by_day = contributor_translations.values('day').annotate(count=Count('id'))

    try:
        events_paginator = Paginator(counts_by_day, 10)
        timeline_events = []

        timeline_events = User.objects.map_translations_to_events(
            events_paginator.page(page).object_list,
            contributor_translations
        )

        # Join is the last event in this reversed order.
        if page == events_paginator.num_pages:
            timeline_events.append({
                'date': user.date_joined,
                'type': 'join'
            })

    except EmptyPage:
        # Return the join event if user reaches the last page.
        raise Http404('No events.')

    return render(request, 'user_timeline.html', {
       'events': timeline_events
    })


def contributor(request, user):
    """Contributor profile."""

    return render(request, 'user.html', {
        'contributor': user,
        'translations': user.contributed_translations
    })


class ContributorsMixin(object):
    def contributors_filter(self, **kwargs):
        """
        Return Q() filters for fetching contributors. Fetches all by default.
        """
        return None

    def get_context_data(self, **kwargs):
        """Top contributors view."""
        context = super(ContributorsMixin, self).get_context_data(**kwargs)
        try:
            period = int(self.request.GET['period'])
            if period <= 0:
                raise ValueError
            start_date = (timezone.now() + relativedelta(months=-period))
        except (KeyError, ValueError):
            period = None
            start_date = None

        context['contributors'] = User.translators.with_translation_counts(start_date, self.contributors_filter(**kwargs))
        context['period'] = period
        return context


class ContributorsView(ContributorsMixin, TemplateView):
    """
    View returns top contributors.
    """
    template_name = 'users.html'


class LocaleContributorsView(ContributorsMixin, DetailView):
    """
    View renders page of the contributors for the locale.
    """
    template_name = 'locale_contributors.html'
    model = Locale
    slug_field = 'code__iexact'
    slug_url_kwarg = 'code'

    def get_context_object_name(self, obj):
        return 'locale'

    def contributors_filter(self, **kwargs):
        return Q(translation__locale=self.object)


class ProjectContributorsView(ContributorsMixin, DetailView):
    """
    Renders an subpage of the project and displays its contributors.
    """
    template_name = 'project_contributors.html'
    model = Project

    def get_context_object_name(self, obj):
        return 'project'

    def contributors_filter(self, **kwargs):
        return Q(translation__entity__resource__project=self.object)


def search(request):
    """Terminology search view."""
    locale = utils.get_project_locale_from_request(
        request, Locale.objects) or 'en-GB'

    return render(request, 'search.html', {
        'locale': Locale.objects.get(code__iexact=locale),
        'locales': Locale.objects.all(),
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
    locale = get_object_or_404(Locale, code__iexact=locale)

    status = request.POST.get('status', '')
    extra = request.POST.get('extra', '')
    time = request.POST.get('time', '')
    author = request.POST.get('author', '')
    search = request.POST.get('search', '')
    exclude_entities = request.POST.getlist('excludeEntities[]', [])

    # Only return entities with provided IDs (batch editing)
    entity_ids = request.POST.getlist('entityIds[]', [])
    if entity_ids:
        entities = (
            Entity.objects.filter(pk__in=entity_ids)
            .prefetch_resources_translations(locale)
            .distinct()
            .order_by('order')
        )
        translations = Translation.for_locale_project_paths(locale, project, paths)

        return JsonResponse({
            'entities': Entity.map_entities(locale, entities),
            'stats': TranslatedResource.objects.stats(project, paths, locale),
            'authors': translations.authors().serialize(),
            'counts_per_minute': translations.counts_per_minute(),
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

    translations = Translation.for_locale_project_paths(locale, project, paths)

    return JsonResponse({
        'entities': Entity.map_entities(locale, entities_to_map, visible_entities),
        'has_next': has_next,
        'stats': TranslatedResource.objects.stats(project, paths, locale),
        'authors': translations.authors().serialize(),
        'counts_per_minute': translations.counts_per_minute(),
    }, safe=False)


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@require_AJAX
@transaction.atomic
def batch_edit_translations(request):
    try:
        l = request.POST['locale']
        action = request.POST['action']
        entity_pks = request.POST.getlist('entities[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    locale = get_object_or_404(Locale, code=l)

    entities = (
        Entity.objects.filter(pk__in=entity_pks)
        .prefetch_resources_translations(locale)
    )

    if not entities.exists():
        return JsonResponse({'count': 0})


    projects = Project.objects.filter(pk__in=entities.values_list('resource__project__pk', flat=True).distinct())

    # Batch editing is only available to translators.
    # Check if user has translate permissions for all of the projects in passed entities.
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

    # Must be executed before translations set changes, which is why
    # we need to force evaluate QuerySets by wrapping them inside list()
    def get_translations_info(translations):
        count = translations.count()
        translated_resources = list(translations.translated_resources(locale))
        changed_entities = list(Entity.objects.filter(translation__in=translations).distinct())

        return count, translated_resources, changed_entities

    if action == 'approve':
        translations = translations.filter(approved=False)
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
            translations = translations.find_and_replace(find, replace, request.user)
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
    locales = entity.resource.project.locales.exclude(code__iexact=locale)
    plural_form = None if entity.string_plural == "" else 0

    translations = Translation.objects.filter(
        entity=entity,
        locale__in=locales,
        plural_form=plural_form,
        approved=True
    )

    payload = list(translations.values('locale__code', 'locale__name', 'string'))
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
    locale = get_object_or_404(Locale, code__iexact=locale)

    translations = Translation.objects.filter(entity=entity, locale=locale)
    if plural_form != "-1":
        translations = translations.filter(plural_form=plural_form)
    translations = translations.order_by('-approved', '-date')

    payload = []
    offset = timezone.now().strftime('%z')

    for t in translations:
        u = t.user
        payload.append({
            "id": t.id,
            "user": "Imported" if u is None else u.name_or_email,
            "uid": "" if u is None else u.id,
            "username": "" if u is None else u.username,
            "translation": t.string,
            "date": t.date.strftime('%b %d, %Y %H:%M'),
            "date_iso": t.date.isoformat() + offset,
            "approved": t.approved,
            "approved_user": User.display_name_or_blank(t.approved_user),
            "unapproved_user": User.display_name_or_blank(t.unapproved_user),
            "fuzzy": t.fuzzy,
        })

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
    translations = Translation.for_locale_project_paths(locale, project, paths)

    return JsonResponse({
        'stats': TranslatedResource.objects.stats(project, paths, locale),
        'authors': translations.authors().serialize(),
        'counts_per_minute': translations.counts_per_minute(),
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
        approve = json.loads(request.POST['approve'])
        paths = request.POST.getlist('paths[]')
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as error:
        log.error(str(error))
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code__iexact=locale)
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
        and (not request.user.profile.force_suggestions or approve)
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

                translations = Translation.for_locale_project_paths(l, project, paths)

                return JsonResponse({
                    'type': 'updated',
                    'translation': t.serialize(),
                    'stats': TranslatedResource.objects.stats(project, paths, l),
                    'authors': translations.authors().serialize(),
                    'counts_per_minute': translations.counts_per_minute(),
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

                    translations = Translation.for_locale_project_paths(l, project, paths)

                    return JsonResponse({
                        'type': 'updated',
                        'translation': t.serialize(),
                        'stats': TranslatedResource.objects.stats(project, paths, l),
                        'authors': translations.authors().serialize(),
                        'counts_per_minute': translations.counts_per_minute(),
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

            translations = Translation.for_locale_project_paths(l, project, paths)

            return JsonResponse({
                'type': 'added',
                'translation': active.serialize(),
                'stats': TranslatedResource.objects.stats(project, paths, l),
                'authors': translations.authors().serialize(),
                'counts_per_minute': translations.counts_per_minute(),
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

        translations = Translation.for_locale_project_paths(l, project, paths)

        return JsonResponse({
            'type': 'saved',
            'translation': t.serialize(),
            'stats': TranslatedResource.objects.stats(project, paths, l),
            'authors': translations.authors().serialize(),
            'counts_per_minute': translations.counts_per_minute(),
        })


def translation_memory(request):
    """Get translations from internal translations memory."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        pk = request.GET['pk']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    max_results = 5
    locale = get_object_or_404(Locale, code__iexact=locale)
    entries = TranslationMemoryEntry.objects.minimum_levenshtein_ratio(text).filter(locale=locale)

    # Exclude existing entity
    if pk:
        entries = entries.exclude(entity__pk=pk)

    entries = entries.values('source', 'target', 'quality').order_by('-quality')
    suggestions = defaultdict(lambda: {'count': 0, 'quality': 0})

    try:
        for entry in entries:
            if entry['target'] not in suggestions or entry['quality'] > suggestions[entry['target']]['quality']:
                suggestions[entry['target']].update(entry)
            suggestions[entry['target']]['count'] += 1
    except DataError as e:
        # Catches 'argument exceeds the maximum length of 255 bytes' Error
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    return JsonResponse(sorted(suggestions.values(), key=lambda e: e['count'], reverse=True)[:max_results], safe=False)


def machine_translation(request):
    """Get translation from machine translation service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        api_key = settings.MICROSOFT_TRANSLATOR_API_KEY
    else:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return HttpResponse("apikey")

    obj = {}

    # On first run, check if target language supported
    if check == "true":
        supported = False
        languages = settings.MICROSOFT_TRANSLATOR_LOCALES

        if locale in languages:
            supported = True

        else:
            for lang in languages:
                if lang.startswith(locale.split("-")[0]):  # Neutral locales
                    supported = True
                    locale = lang
                    break

        if not supported:
            return HttpResponse("not-supported")

        obj['locale'] = locale

    url = "http://api.microsofttranslator.com/V2/Http.svc/Translate"
    payload = {
        "appId": api_key,
        "text": text,
        "from": "en",
        "to": locale,
        "contentType": "text/html",
    }

    try:
        r = requests.get(url, params=payload)

        # Parse XML response
        root = ET.fromstring(r.content)
        translation = root.text
        obj['translation'] = translation

        return JsonResponse(obj)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def microsoft_terminology(request):
    """Get translations from Microsoft Terminology Service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
        check = request.GET['check']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    obj = {}
    locale = locale.lower()
    url = 'http://api.terminology.microsoft.com/Terminology.svc?singleWsdl'
    client = Client(url)

    # On first run, check if target language supported
    if check == "true":
        supported = False
        languages = settings.MICROSOFT_TERMINOLOGY_LOCALES

        if locale in languages:
            supported = True

        elif "-" not in locale:
            temp = locale + "-" + locale  # Try e.g. "de-de"
            if temp in languages:
                supported = True
                locale = temp

            else:
                for lang in languages:
                    if lang.startswith(locale + "-"):  # Try e.g. "de-XY"
                        supported = True
                        locale = lang
                        break

        if not supported:
            return HttpResponse("not-supported")

        obj['locale'] = locale

    sources = client.factory.create('ns0:TranslationSources')
    sources["TranslationSource"] = ['Terms', 'UiStrings']

    payload = {
        'text': text,
        'from': 'en-US',
        'to': locale,
        'sources': sources,
        'maxTranslations': 5
    }

    try:
        r = client.service.GetTranslations(**payload)
        translations = []

        if len(r) != 0:
            for translation in r.Match:
                translations.append({
                    'source': translation.OriginalText,
                    'target': translation.Translations[0][0].TranslatedText,
                    'quality': translation.ConfidenceLevel,
                })

            obj['translations'] = translations

        return JsonResponse(obj)

    except WebFault as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def amagama(request):
    """Get open source translations from amaGama service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        text = urllib.quote(text.encode('utf-8'))
    except KeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    # No trailing slash at the end or slash becomes part of the source text
    url = (
        u'https://amagama-live.translatehouse.org/api/v1/en/{locale}/unit/'
        .format(locale=locale)
    )

    payload = {
        'source': text,
        'max_candidates': 5,
        'min_similarity': 70,
    }

    try:
        r = requests.get(url, params=payload)
        return JsonResponse(r.json(), safe=False)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


def transvision(request):
    """Get Mozilla translations from Transvision service."""
    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    try:
        text = urllib.quote(text.encode('utf-8'))
    except KeyError as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))

    url = (
        u'https://transvision.mozfr.org/api/v1/tm/global/en-US/{locale}/{text}/'
        .format(locale=locale, text=text)
    )

    payload = {
        'max_results': 5,
        'min_quality': 70,
    }

    try:
        r = requests.get(url, params=payload)
        if 'error' in r.json():
            error = r.json()['error']
            log.error('Transvision error: {error}'.format(error))
            return HttpResponseBadRequest('Bad Request: {error}'.format(error=error))

        return JsonResponse(r.json(), safe=False)

    except Exception as e:
        return HttpResponseBadRequest('Bad Request: {error}'.format(error=e))


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


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def toggle_user_profile_attribute(request, username):
    user = get_object_or_404(User, username=username)
    if user != request.user:
        return HttpResponseForbidden("Forbidden: You don't have permission to edit this user")

    attribute = request.POST.get('attribute', None)
    if attribute not in ['quality_checks', 'force_suggestions']:
        return HttpResponseForbidden('Forbidden: Attribute not allowed')

    value = request.POST.get('value', None)
    if not value:
        return HttpResponseBadRequest('Bad Request: Value not set')

    profile = user.profile
    setattr(profile, attribute, json.loads(value))
    profile.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
@require_POST
@transaction.atomic
def save_user_name(request):
    """Save user name."""
    profile_form = forms.UserProfileForm(request.POST, instance=request.user)

    if not profile_form.is_valid():
        return HttpResponseBadRequest(u'\n'.join(profile_form.errors['first_name']))

    profile_form.save()

    return HttpResponse('ok')


@login_required(redirect_field_name='', login_url='/403')
@require_POST
def request_projects(request, locale):
    """Request projects to be added to locale."""
    slug_list = request.POST.getlist('projects[]')
    locale = get_object_or_404(Locale, code__iexact=locale)

    # Validate projects
    project_list = Project.objects.available().filter(slug__in=slug_list)
    if not project_list:
        return HttpResponseBadRequest('Bad Request: Non-existent projects specified')

    projects = ''.join('- {} ({})\n'.format(p.name, p.slug) for p in project_list)
    user = request.user

    if settings.PROJECT_MANAGERS[0] != '':
        EmailMessage(
            subject=u'Project request for {locale} ({code})'.format(locale=locale.name, code=locale.code),
            body=u'''
            Please add the following projects to {locale} ({code}):
            {projects}
            Requested by {user}, {user_role}:
            {user_url}
            '''.format(
                locale=locale.name, code=locale.code, projects=projects,
                user=user.display_name_and_email,
                user_role=user.locale_role(locale),
                user_url=request.build_absolute_uri(user.profile_url)
            ),
            from_email='pontoon@mozilla.com',
            to=settings.PROJECT_MANAGERS,
            cc=locale.managers_group.user_set.exclude(pk=user.pk).values_list('email', flat=True),
            reply_to=[user.email]).send()
    else:
        raise ImproperlyConfigured("ADMIN not defined in settings. Email recipient unknown.")

    return HttpResponse('ok')


@require_AJAX
def get_csrf(request):
    """Get CSRF token."""
    return HttpResponse(request.csrf_token)


@login_required(redirect_field_name='', login_url='/403')
def user_settings(request):
    """View and edit user settings."""
    if request.method == 'POST':
        form = forms.UserLocalesSettings(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings saved.')
            return redirect(request.POST.get('return_url', '/'))

    selected_locales = list(request.user.profile.sorted_locales)
    available_locales = Locale.objects.exclude(pk__in=[l.pk for l in selected_locales])
    return render(request, 'user_settings.html', {
        'available_locales': available_locales,
        'selected_locales': selected_locales,
    })


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
