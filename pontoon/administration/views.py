import logging

from backports import csv

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction, IntegrityError
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError

from pontoon.administration.forms import (
    EntityFormSet,
    ExternalResourceInlineFormSet,
    ProjectForm,
    RepositoryInlineFormSet,
    SubpageInlineFormSet,
)
from pontoon.base import utils
from pontoon.base.utils import require_AJAX
from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.sync.models import SyncLog
from pontoon.sync.tasks import sync_project


log = logging.getLogger(__name__)


def admin(request):
    """Admin interface."""
    if not request.user.has_perm('base.can_manage_project'):
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

    if not request.user.has_perm('base.can_manage_project'):
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

    if not request.user.has_perm('base.can_manage_project'):
        raise PermissionDenied

    form = ProjectForm()
    subpage_formset = SubpageInlineFormSet()
    repo_formset = RepositoryInlineFormSet()
    external_resource_formset = ExternalResourceInlineFormSet()
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
            external_resource_formset = ExternalResourceInlineFormSet(
                request.POST, instance=project
            )
            subtitle = 'Edit project'

        # Add a new project
        except MultiValueDictKeyError:
            form = ProjectForm(request.POST)
            # Needed if form invalid
            subpage_formset = SubpageInlineFormSet(request.POST)
            repo_formset = RepositoryInlineFormSet(request.POST)
            external_resource_formset = ExternalResourceInlineFormSet(request.POST)

        if form.is_valid():
            project = form.save(commit=False)
            subpage_formset = SubpageInlineFormSet(request.POST, instance=project)
            repo_formset = RepositoryInlineFormSet(request.POST, instance=project)
            external_resource_formset = ExternalResourceInlineFormSet(
                request.POST, instance=project
            )

            if (
                subpage_formset.is_valid() and
                repo_formset.is_valid() and
                external_resource_formset.is_valid()
            ):
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
                external_resource_formset.save()
                # Properly displays formsets, but removes errors (if valid only)
                subpage_formset = SubpageInlineFormSet(instance=project)
                repo_formset = RepositoryInlineFormSet(instance=project)
                external_resource_formset = ExternalResourceInlineFormSet(instance=project)
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
            external_resource_formset = ExternalResourceInlineFormSet(instance=project)
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
        'slug': slug,
        'form': form,
        'subpage_formset': subpage_formset,
        'repo_formset': repo_formset,
        'external_resource_formset': external_resource_formset,
        'locales_selected': locales_selected,
        'locales_available': Locale.objects.exclude(pk__in=locales_selected),
        'subtitle': subtitle,
        'pk': pk,
        'projects': projects,
        'has_repositories': project and project.repositories.exists()
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


def _get_project_strings_csv(project, entities, output):
    locales = Locale.objects.filter(project_locale__project=project)
    translations = (
        Translation.objects
        .filter(
            entity__resource__project=project,
            approved=True,
        )
        .prefetch_related('locale')
        .prefetch_related('entity')
    )
    all_data = dict((x.id, {'source': x.string}) for x in entities)

    for translation in translations:
        all_data[translation.entity.id][translation.locale.code] = translation.string

    writer = csv.writer(output)
    headers = ['source'] + [x.code for x in locales]
    writer.writerow(headers)
    for string in all_data.values():
        row = [string.get(key, '') for key in headers]
        writer.writerow(row)

    return output


def manage_project_strings(request, slug=None):
    """View to manage the source strings of a project.

    This view is only accessible for projects that do not have a "Source repo". It allows
    admins to add new strings to a project in a batch, and then to edit, remove or comment on
    any strings.

    """
    if not request.user.has_perm('base.can_manage_project'):
        raise PermissionDenied

    try:
        project = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
        raise Http404

    if project.repositories.exists():
        return HttpResponseForbidden(
            'Project %s has a repository, managing strings is forbidden.' % project.name
        )

    entities = Entity.objects.filter(resource__project=project)
    project_has_strings = entities.exists()
    formset = EntityFormSet(queryset=entities)

    if request.GET.get('format') == 'csv':
        # Return a CSV document containing all translations for this project.
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % project.name

        return _get_project_strings_csv(project, entities, response)

    if request.method == 'POST':
        if not project_has_strings:
            # We are receiving new strings in a batch.
            new_string_source = request.POST.get('new_strings', '')
            new_strings = new_string_source.strip().split('\n')

            # Remove empty strings from the list.
            new_strings = [x.strip() for x in new_strings if x.strip()]

            if new_strings:
                # Create a new fake resource for that project.
                resource = Resource(path='all', project=project, total_strings=len(new_strings))
                resource.save()

                # Insert all new strings into Entity objects, associated to the fake resource.
                new_entities = []
                for new_string in new_strings:
                    string = new_string.strip()
                    new_entities.append(Entity(string=string, resource=resource))

                Entity.objects.bulk_create(new_entities)

                # Enable the new Resource for all active locales for that project.
                locales = (
                    ProjectLocale.objects
                    .filter(project=project)
                    .values_list('locale_id', flat=True)
                )
                for locale_id in locales:
                    tr = TranslatedResource(
                        locale_id=locale_id,
                        resource=resource,
                    )
                    tr.save()
                    tr.calculate_stats()

                project_has_strings = True  # we have strings now!
        else:
            # Get all strings, find the ones that changed, update them in the database.
            formset = EntityFormSet(request.POST, queryset=entities)
            if formset.is_valid():
                try:
                    formset.save()
                except IntegrityError:
                    # This happens when the user creates a new string. By default,
                    # it has no resource, and that's a violation of the database
                    # constraints. So, we want to make sure all entries have a resource.
                    new_entities = formset.save(commit=False)
                    resource = Resource.objects.filter(project=project)[0]
                    for entity in new_entities:
                        if not entity.resource_id:
                            entity.resource = resource

                        # Note that we save all entities one by one. That shouldn't be a problem
                        # because we don't expect users to change thousands of strings at once.
                        # Also, django is smart and ``formset.save()`` only returns Entity
                        # objects that have changed.
                        entity.save()

            # Reinitialize the formset.
            formset = EntityFormSet(queryset=entities)

    data = {
        'project': project,
        'entities': entities,
        'project_has_strings': project_has_strings,
        'entities_form': formset,
    }
    return render(request, 'admin_project_strings.html', data)


@login_required(redirect_field_name='', login_url='/403')
@require_AJAX
def manually_sync_project(request, slug):
    if not request.user.has_perm('base.can_manage_project') or not settings.MANUAL_SYNC:
        return HttpResponseForbidden(
            "Forbidden: You don't have permission for syncing projects"
        )

    sync_log = SyncLog.objects.create(start_time=timezone.now())
    project = Project.objects.get(slug=slug)
    sync_project.delay(project.pk, sync_log.pk)

    return HttpResponse('ok')
