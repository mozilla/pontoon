
import base64
import commonware
import datetime
import fnmatch
import json
import os
import polib
import pysvn
import silme.core, silme.format.properties

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from pontoon.base.models import Locale, Project, Subpage, Entity, Translation, ProjectForm, UserProfile
from pontoon.base.views import _request

from mercurial import commands, hg, ui, error
from mobility.decorators import mobile_template


log = commonware.log.getLogger('playdoh')


@mobile_template('{mobile/}admin.html')
def admin(request, template=None):
    """Admin interface."""
    log.debug("Admin interface.")

    if not (request.user.is_authenticated() and request.user.has_perm('base.can_manage')):
        raise Http404

    data = {
        'projects': Project.objects.all(),
    }

    return render(request, template, data)

@mobile_template('{mobile/}project.html')
def manage_project(request, name=None, template=None):
    """Admin interface: manage project."""
    log.debug("Admin interface: manage project.")

    if not (request.user.is_authenticated() and request.user.has_perm('base.can_manage')):
        raise Http404

    SubpageInlineFormSet = inlineformset_factory(Project, Subpage, extra=1)
    form = ProjectForm()
    formset = SubpageInlineFormSet()
    locales_selected = []
    subtitle = 'Add project'
    pk = None
    warning = None

    if request.method == 'POST':
        locales_selected = Locale.objects.filter(pk__in=request.POST.getlist('locales'))
        # Update existing project
        try:
            pk = request.POST['pk']
            project = Project.objects.get(pk=pk)
            form = ProjectForm(request.POST, instance=project)
            formset = SubpageInlineFormSet(request.POST, instance=project) # Needed if form invalid
            subtitle = 'Edit project'

        # Add a new project
        except MultiValueDictKeyError:
            form = ProjectForm(request.POST)
            formset = SubpageInlineFormSet(request.POST) # Needed if form invalid

        if form.is_valid():
            project = form.save(commit=False)
            formset = SubpageInlineFormSet(request.POST, instance=project)
            if formset.is_valid():
                project.save()
                form.save_m2m() # https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#the-save-method
                formset.save()
                formset = SubpageInlineFormSet(instance=project) # Properly displays formset, but removes errors (only usable if valid)
                subtitle += '. Saved.'
                pk = project.pk
                if len(Entity.objects.filter(project=project)) is 0:
                    warning = 'Before localizing the project, you need to import strings from the repository.'
            else:
                subtitle += '. Error.'
        else:
            subtitle += '. Error.'

    # If URL specified and found, show edit, otherwise show add form
    elif name is not None:
        try:
            project = Project.objects.get(name=name)
            pk = project.pk
            form = ProjectForm(instance=project)
            formset = SubpageInlineFormSet(instance=project)
            locales_selected = project.locales.all()
            subtitle = 'Edit project'
            if len(Entity.objects.filter(project=project)) is 0:
                warning = 'Before localizing the project, you need to import strings from the repository.'
        except Project.DoesNotExist:
            form = ProjectForm(initial={'name': name})

    data = {
        'form': form,
        'formset': formset,
        'locales_selected': locales_selected,
        'locales_available': Locale.objects.exclude(pk__in=locales_selected),
        'subtitle': subtitle,
        'pk': pk,
        'warning': warning
    }

    return render(request, template, data)

def delete_project(request, pk, template=None):
    """Admin interface: delete project."""
    log.debug("Admin interface: delete project.")

    Project.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse('pontoon.admin'))

def _updateDB(project, locale, original, comment, translation, author):
    """Admin interface: save or update data in DB."""

    try: # Update entity
        e = Entity.objects.get(project=project, string=original)
    except Entity.DoesNotExist: # New entity
        e = Entity(project=project, string=original)

    if len(comment) > 0:
        e.comment = comment
    e.save()

    if len(translation) > 0:
        try: # Update translation
            t = Translation.objects.get(entity=e, locale=locale)
            t.string = translation
            t.author = author
            t.date = datetime.datetime.now()
        except Translation.DoesNotExist: # New translation
            t = Translation(entity=e, locale=locale, string=translation,
                author=author, date=datetime.datetime.now())
        t.save()

def update_from_repository(request, template=None):
    """Update all project locales from repository."""
    log.debug("Update all project locales from repository.")

    if not request.is_ajax():
        raise Http404

    try:
        pk = request.GET['pk']
        url_repository = request.GET['repository']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    if url_repository.find('://hg') > 0:
        """ Mercurial """
        software = 'hg'
        locales = [Locale.objects.get(code="en-US")]
        locales.extend(p.locales.all())

        for l in locales:
            path = str(os.path.join(settings.MEDIA_ROOT, software, p.name, l.code))
            url_locale = str(os.path.join(url_repository, l.code))
            try:
                repo = hg.repository(ui.ui(), path)
                commands.update(ui.ui(), repo)
                log.debug("Mercurial: Repository for " + l.name + " updated.")
            except error.RepoError, e:
                log.debug("Mercurial: " + str(e))
                try:
                    commands.clone(ui.ui(), url_locale, path)
                except Exception, e:
                    log.debug("Mercurial: " + str(e))
                    return HttpResponse("error")

            """Save or update repository data to DB."""
            files = []
            for root, dirnames, filenames in os.walk(path + '/apps'):
              for filename in fnmatch.filter(filenames, '*.properties'):
                  files.append(os.path.join(root, filename))

            for file_path in files:
                f = open(file_path)
                l10nobject = silme.format.properties.PropertiesFormatParser.get_structure(f.read())
                file_name = file_path.split('/')[-1]

                for line in l10nobject:
                    if isinstance(line, silme.core.entity.Entity):
                        if l.code == 'en-US':
                            try: # Update entity
                                e = Entity.objects.get(project=p, key=line.id, source=file_name, string=line.value)
                            except Entity.DoesNotExist: # New entity
                                e = Entity(project=p, key=line.id, source=file_name, string=line.value)
                            e.save()
                        else:
                            try:
                                e = Entity.objects.get(project=p, key=line.id, source=file_name)
                            except Entity.DoesNotExist:
                                log.debug("Line ID " + line.id + " in " + file_path + " is obsolete.")
                                break;
                            try: # Update translation
                                t = Translation.objects.get(entity=e, locale=l)
                                t.string = line.value
                                t.date = datetime.datetime.now()
                            except Translation.DoesNotExist: # New translation
                                t = Translation(entity=e, locale=l,
                                    string=line.value, date=datetime.datetime.now())
                            t.save()

    elif url_repository.find('://svn') > 0:
        """ Subversion """
        software = 'svn'
        path = os.path.join(settings.MEDIA_ROOT, software, p.name)
        client = pysvn.Client()

        try:
            client.checkout(url_repository, path)
        except pysvn.ClientError, e:
            log.debug("Subversion: " + str(e))
            return HttpResponse("error")

        for l in p.locales.all():
            """Save or update repository data to DB."""
            po = polib.pofile(settings.MEDIA_ROOT + '/svn/' + p.name + '/locale/' + l.code + '/LC_MESSAGES/messages.po')
            entities = [e for e in po if not e.obsolete]
            for entity in entities:
                _updateDB(project=p, locale=l, original=entity.msgid,
                    comment=entity.comment, translation=entity.msgstr,
                    author=po.metadata['Last-Translator'])
            log.debug("Repository data for " + l.name + " saved to DB.")

    else:
        """ Not supported """
        return HttpResponse("error")

    return HttpResponse("200")

def update_from_transifex(request, template=None):
    """Update all project locales from Transifex repository."""
    log.debug("Update all project locales from Transifex repository.")

    if not request.is_ajax():
        raise Http404

    try:
        pk = request.GET['pk']
        transifex_project = request.GET['transifex_project']
        transifex_resource = request.GET['transifex_resource']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = request.GET.get('transifex_username', profile.transifex_username)
    password = request.GET.get('transifex_password', base64.decodestring(profile.transifex_password))

    if (len(username) == 0 or len(password) == 0):
        return HttpResponse("authenticate")

    for l in p.locales.all():
        """Make GET request to Transifex API."""
        response = _request('get', transifex_project, transifex_resource,
            l.code, username, password)

        """Save or update Transifex data to DB."""
        if hasattr(response, 'status_code') and response.status_code == 200:
            entities = json.loads(response.content)
            for entity in entities:
                _updateDB(project=p, locale=l, original=entity["key"],
                    comment=entity["comment"], translation=entity["translation"],
                    author=entity["user"])
            log.debug("Transifex data for " + l.name + " saved to DB.")
        else:
            return HttpResponse(response)

    """Save Transifex username and password."""
    if 'remember' in request.GET and request.GET['remember'] == "on":
        profile.transifex_username = request.GET['transifex_username']
        profile.transifex_password = base64.encodestring(request.GET['transifex_password'])
        profile.save()

    return HttpResponse(response.status_code)
