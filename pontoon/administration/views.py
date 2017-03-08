import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.administration.forms import (
    ProjectForm,
    RepositoryInlineFormSet,
    SubpageInlineFormSet,
)
from pontoon.base import utils
from pontoon.base.utils import require_AJAX
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Resource,
)
from pontoon.sync.models import SyncLog
from pontoon.sync.tasks import sync_project


log = logging.getLogger('pontoon')


def admin(request, template='admin.html'):
    """Admin interface."""
    if not request.user.has_perm('base.can_manage'):
        raise PermissionDenied

    projects = (
        Project.objects.all()
        .prefetch_related('latest_translation__user')
        .order_by('name')
    )

    return render(request, 'admin.html', {
        'admin': True,
        'projects': projects,
    })


def get_slug(request):
    """Convert project name to slug."""
    log.debug("Convert project name to slug.")

    if not request.user.has_perm('base.can_manage'):
        log.error("Insufficient privileges.")
        return HttpResponse("error")

    if not request.is_ajax():
        log.error("Non-AJAX request")
        return HttpResponse("error")

    try:
        name = request.GET['name']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Name: " + name)

    slug = slugify(name)
    log.debug("Slug: " + slug)
    return HttpResponse(slug)


@transaction.atomic
def manage_project(request, slug=None, template='admin_project.html'):
    """Admin project."""
    log.debug("Admin project.")

    if not request.user.has_perm('base.can_manage'):
        raise PermissionDenied

    form = ProjectForm()
    subpage_formset = SubpageInlineFormSet()
    repo_formset = RepositoryInlineFormSet()
    locales_selected = []
    subtitle = 'Add project'
    pk = None
    project = None

    # Save project
    if request.method == 'POST':
        locales_selected = Locale.objects.filter(
            pk__in=request.POST.getlist('locales'))

        # Update existing project
        try:
            pk = request.POST['pk']
            project = Project.objects.get(pk=pk)
            form = ProjectForm(request.POST, instance=project)
            # Needed if form invalid
            subpage_formset = SubpageInlineFormSet(request.POST, instance=project)
            repo_formset = RepositoryInlineFormSet(request.POST, instance=project)
            subtitle = 'Edit project'

        # Add a new project
        except MultiValueDictKeyError:
            form = ProjectForm(request.POST)
            # Needed if form invalid
            subpage_formset = SubpageInlineFormSet(request.POST)
            repo_formset = RepositoryInlineFormSet(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            subpage_formset = SubpageInlineFormSet(request.POST, instance=project)
            repo_formset = RepositoryInlineFormSet(request.POST, instance=project)

            if subpage_formset.is_valid() and repo_formset.is_valid():
                project.save()

                # Manually save ProjectLocales due to intermediary
                # model.
                locales = form.cleaned_data.get('locales', [])
                (ProjectLocale.objects
                    .filter(project=project)
                    .exclude(locale__pk__in=[l.pk for l in locales])
                    .delete())
                for locale in locales:
                    ProjectLocale.objects.get_or_create(project=project, locale=locale)

                subpage_formset.save()
                repo_formset.save()
                # Properly displays formsets, but removes errors (if valid only)
                subpage_formset = SubpageInlineFormSet(instance=project)
                repo_formset = RepositoryInlineFormSet(instance=project)
                subtitle += '. Saved.'
                pk = project.pk
            else:
                subtitle += '. Error.'
        else:
            subtitle += '. Error.'

    # If URL specified and found, show edit, otherwise show add form
    elif slug is not None:
        try:
            project = Project.objects.get(slug=slug)
            pk = project.pk
            form = ProjectForm(instance=project)
            subpage_formset = SubpageInlineFormSet(instance=project)
            repo_formset = RepositoryInlineFormSet(instance=project)
            locales_selected = project.locales.all()
            subtitle = 'Edit project'
        except Project.DoesNotExist:
            form = ProjectForm(initial={'slug': slug})

    # Override default label suffix
    form.label_suffix = ''

    projects = []
    for p in Project.objects.prefetch_related('locales').order_by('name'):
        projects.append({
            'name': p.name,
            # Cannot use values_list() here, because it hits the DB again
            'locales': [l.pk for l in p.locales.all()],
        })

    data = {
        'form': form,
        'subpage_formset': subpage_formset,
        'repo_formset': repo_formset,
        'locales_selected': locales_selected,
        'locales_available': Locale.objects.exclude(pk__in=locales_selected),
        'subtitle': subtitle,
        'pk': pk,
        'projects': projects,
    }

    # Set locale in Translate link
    if hasattr(project, 'locales') and locales_selected:
        locale = utils.get_project_locale_from_request(
            request, project.locales) or locales_selected[0].code
        if locale:
            data['translate_locale'] = locale

    if Resource.objects.filter(project=project).exists():
        data['ready'] = True

    return render(request, template, data)


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
