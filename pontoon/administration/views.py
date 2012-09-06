
import base64
import commonware
import datetime
import json
import polib
import pysvn

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from pontoon.base.models import Locale, Project, Subpage, Entity, Translation, ProjectForm
from pontoon.base.views import _request

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
        'form': ProjectForm()
    }

    return render(request, template, data)

@mobile_template('{mobile/}admin_project.html')
def admin_project(request, name=None, template=None):
    """Admin interface: project."""
    log.debug("Admin interface: project.")

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

def update_from_svn(request, template=None):
    """Update all project locales from SVN repository."""
    log.debug("Update all project locales from SVN repository.")

    try:
        pk = request.GET['pk']
        svn = request.GET['svn']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    client = pysvn.Client()

    try:
        client.checkout(svn, settings.MEDIA_ROOT + '/svn/' + p.name)
    except pysvn.ClientError, e:
        log.debug(str(e))
        return HttpResponse("error")

    for l in p.locales.all():
        """Save or update SVN data to DB."""
        po = polib.pofile(settings.MEDIA_ROOT + '/svn/' + p.name + '/locale/' + l.code + '/LC_MESSAGES/messages.po')
        entities = [e for e in po if not e.obsolete]

        for entity in entities:
            try: # Update entity
                e = Entity.objects.get(project=p, string=entity.msgid)
            except Entity.DoesNotExist: # New entity
                e = Entity(project=p, string=entity.msgid)

            comment = entity.comment
            if len(comment) > 0:
                e.comment = comment
            e.save()

            translation = entity.msgstr
            if len(translation) > 0:
                try: # Update translation
                    t = Translation.objects.get(entity=e, locale=l)
                    t.string = translation
                    t.author = po.metadata['Last-Translator']
                    t.date = datetime.datetime.now()
                except Translation.DoesNotExist: # New translation
                    t = Translation(entity=e, locale=l, string=translation,
                        author=po.metadata['Last-Translator'], date=datetime.datetime.now())
                t.save()

        log.debug("SVN data for " + l.name + " saved to DB.")
    return HttpResponse("200")

def update_from_transifex(request, template=None):
    """Update all project locales from Transifex repository."""
    log.debug("Update all project locales from Transifex repository.")

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
    profile = request.user.get_profile()
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
                try: # Update entity
                    e = Entity.objects.get(project=p, string=entity["key"])
                except Entity.DoesNotExist: # New entity
                    e = Entity(project=p, string=entity["key"])

                comment = entity["comment"]
                if len(comment) > 0:
                    e.comment = comment
                e.save()

                translation = entity["translation"]
                if len(translation) > 0:
                    try: # Update translation
                        t = Translation.objects.get(entity=e, locale=l)
                        t.string = translation
                        t.author = entity["user"]
                        t.date = datetime.datetime.now()
                    except Translation.DoesNotExist: # New translation
                        t = Translation(entity=e, locale=l, string=translation,
                            author=entity["user"], date=datetime.datetime.now())
                    t.save()

            log.debug("Transifex data for " + l.name + " saved to DB.")
        else:
            return HttpResponse(response)

    """Save Transifex username and password."""
    if 'remember' in request.GET and request.GET['remember'] == "on":
        profile.transifex_username = request.GET['transifex_username']
        profile.transifex_password = base64.encodestring(request.GET['transifex_password'])
        profile.save()

    return HttpResponse(response.status_code)
