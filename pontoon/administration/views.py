import base64
import json
import logging
import os
import shutil
import traceback

from django.core.urlresolvers import reverse
from django.contrib import messages
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template.defaultfilters import slugify
from django.utils.datastructures import MultiValueDictKeyError
from pontoon.administration import files
from pontoon.base import utils

from pontoon.base.models import (
    Entity,
    Locale,
    Project,
    ProjectForm,
    Resource,
    Subpage,
    Translation,
    UserProfile,
    get_projects_with_stats,
)


log = logging.getLogger('pontoon')


def admin(request, template='admin.html'):
    """Admin interface."""
    log.debug("Admin interface.")

    if not request.user.has_perm('base.can_manage'):
        return render(request, '403.html', status=403)

    projects = Project.objects.all().order_by("name")

    data = {
        'projects': get_projects_with_stats(projects),
        'admin': True,
    }

    return render(request, template, data)


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


def manage_project(request, slug=None, template='admin_project.html'):
    """Admin project."""
    log.debug("Admin project.")

    if not request.user.has_perm('base.can_manage'):
        return render(request, '403.html', status=403)

    SubpageInlineFormSet = inlineformset_factory(
        Project, Subpage, extra=1, fields=('project', 'name', 'url'))

    form = ProjectForm()
    formset = SubpageInlineFormSet()
    locales_selected = []
    subtitle = 'Add project'
    pk = None
    project = None
    message = 'Please wait while strings are imported from the repository.'
    autoupdate = False

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
            formset = SubpageInlineFormSet(request.POST, instance=project)
            subtitle = 'Edit project'

        # Add a new project
        except MultiValueDictKeyError:
            form = ProjectForm(request.POST)
            # Needed if form invalid
            formset = SubpageInlineFormSet(request.POST)
            autoupdate = True

        if form.is_valid():
            if project and set(project.locales.all()) != set(locales_selected):
                autoupdate = True

            project = form.save(commit=False)
            formset = SubpageInlineFormSet(request.POST, instance=project)
            if formset.is_valid():
                project.save()
                # http://bit.ly/1glKN50
                form.save_m2m()
                formset.save()
                # Properly displays formset, but removes errors (if valid only)
                formset = SubpageInlineFormSet(instance=project)
                subtitle += '. Saved.'
                pk = project.pk
                if autoupdate:
                    messages.warning(request, message)
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
            formset = SubpageInlineFormSet(instance=project)
            locales_selected = project.locales.all()
            subtitle = 'Edit project'
            if not Resource.objects.filter(project=project).exists():
                autoupdate = True
                messages.warning(request, message)
        except Project.DoesNotExist:
            form = ProjectForm(initial={'slug': slug})

    # Override default label suffix
    form.label_suffix = ''

    data = {
        'form': form,
        'formset': formset,
        'locales_selected': locales_selected,
        'locales_available': Locale.objects.exclude(pk__in=locales_selected),
        'REPOSITORY_TYPE_CHOICES': Project.REPOSITORY_TYPE_CHOICES,
        'subtitle': subtitle,
        'pk': pk,
        'autoupdate': autoupdate,
    }

    # Set locale in Translate link
    if project and locales_selected:
        locale = utils.get_project_locale_from_request(
            request, project.locales) or locales_selected[0].code
        if locale:
            data['translate_locale'] = locale

    if Resource.objects.filter(project=project).exists():
        data['ready'] = True

    return render(request, template, data)


def delete_project(request, pk, template=None):
    """Delete project."""
    try:
        log.debug("Delete project.")

        if not request.user.has_perm('base.can_manage'):
            return render(request, '403.html', status=403)

        with transaction.atomic():
            project = Project.objects.get(pk=pk)
            project.delete()

            path = files.get_repository_path_master(project)
            if os.path.exists(path):
                shutil.rmtree(path)

        return HttpResponseRedirect(reverse('pontoon.admin'))
    except Exception as e:
        log.error(
            "Admin interface: delete project error.\n%s"
            % unicode(e), exc_info=True)
        messages.error(
            request,
            "There was an error during deleting this project.")
        return HttpResponseRedirect(reverse(
            'pontoon.admin.project',
            args=[project.slug]))


def update_from_repository(request, template=None):
    """Update all project locales from repository."""
    log.debug("Update all project locales from repository.")

    if not request.user.has_perm('base.can_manage'):
        return render(request, '403.html', status=403)

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        pk = request.POST['pk']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': 'Project primary key not provided.',
        }), content_type='application/json')

    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': str(e),
        }), content_type='application/json')

    try:
        files.update_from_repository(project)
        files.extract_to_database(project)

    except Exception as e:
        log.error("Exception: " + str(e))
        log.debug(traceback.format_exc())
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': str(e),
        }), content_type='application/json')

    except IOError as e:
        log.error("IOError: " + str(e))
        log.debug(traceback.format_exc())
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': str(e),
        }), content_type='application/json')

    return HttpResponse("200")


def update_from_transifex(request, template=None):
    """Update all project locales from Transifex repository."""
    log.debug("Update all project locales from Transifex repository.")

    if not request.user.has_perm('base.can_manage'):
        return render(request, '403.html', status=403)

    if request.method != 'POST':
        log.error("Non-POST request")
        raise Http404

    try:
        pk = request.POST['pk']
        transifex_project = request.POST['transifex_project']
        transifex_resource = request.POST['transifex_resource']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile = UserProfile.objects.get(user=request.user)
    username = request.POST.get(
        'transifex_username', profile.transifex_username)
    password = request.POST.get(
        'transifex_password', base64.decodestring(profile.transifex_password))

    if len(username) == 0 or len(password) == 0:
        return HttpResponse("authenticate")

    for l in p.locales.all():
        """Make GET request to Transifex API."""
        response = utils.req('get', transifex_project, transifex_resource,
                             l.code, username, password)

        """Save or update Transifex data to DB."""
        if hasattr(response, 'status_code') and response.status_code == 200:
            entities = json.loads(response.content)
            for entity in entities:
                _save_entity(project=p, string=entity["key"],
                             comment=entity["comment"])
                if len(entity["translation"]) > 0:
                    e = Entity.objects.get(project=p, string=entity["key"])
                    _save_translation(
                        entity=e, locale=l, string=entity["translation"])
            log.debug("Transifex data for " + l.name + " saved to DB.")
        else:
            return HttpResponse(response)

    """Save Transifex username and password."""
    if 'remember' in request.POST and request.POST['remember'] == "on":
        profile.transifex_username = request.POST['transifex_username']
        profile.transifex_password = base64.encodestring(
            request.POST['transifex_password'])
        profile.save()

    return HttpResponse(response.status_code)
