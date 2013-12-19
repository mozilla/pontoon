
import base64
import codecs
import ConfigParser
import commonware
import datetime
import fnmatch
import json
import os
import shutil
import polib
import silme.core, silme.format.properties
import urllib2

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.contrib import messages
from django.db import transaction
from django.forms.models import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import ugettext_lazy as _
from pontoon.base.models import Locale, Project, Subpage, Entity, Translation, ProjectForm, UserProfile
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
                    messages.warning(request,
                        _("Before localizing projects, you need to import strings from the repository."))
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
                messages.warning(request,
                    _("Before localizing projects, you need to import strings from the repository."))
        except Project.DoesNotExist:
            form = ProjectForm(initial={'name': name})

    data = {
        'form': form,
        'formset': formset,
        'locales_selected': locales_selected,
        'locales_available': Locale.objects.exclude(pk__in=locales_selected),
        'REPOSITORY_TYPE_CHOICES': Project.REPOSITORY_TYPE_CHOICES,
        'subtitle': subtitle,
        'pk': pk
    }

    return render(request, template, data)

@transaction.commit_manually
def delete_project(request, pk, template=None):
    """Admin interface: delete project."""
    try:
        log.debug("Admin interface: delete project.")

        if not (request.user.is_authenticated() and request.user.has_perm(
                'base.can_manage')):
            raise Http404

        project = Project.objects.get(pk=pk)
        project.delete()
        import re
        m = re.search(r'://(?P<software>(?:hg)|(?:svn))', project.repository)
        if m:
            software = m.group('software')
            project_path = os.path.join(
                settings.MEDIA_ROOT, software, project.name)
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
        transaction.commit()
        return HttpResponseRedirect(reverse('pontoon.admin'))
    except Exception as e:
        log.error("Admin interface: delete project error.\n%s"
            % unicode(e), exc_info=True)
        transaction.rollback()
        messages.error(request,
            _("There was an error during deleting this project."))
        return HttpResponseRedirect(reverse('pontoon.admin.project',
            args=[project.name]))

def _save_entity(project, original, comment="", key="", source=""):
    """Admin interface: save new or update existing entity in DB."""

    try: # Update existing entity
        if key is "":
            e = Entity.objects.get(project=project, string=original)
        else:
            e = Entity.objects.get(project=project, key=key, source=source)
            e.string = original
    except Entity.DoesNotExist: # Add new entity
        e = Entity(project=project, string=original, key=key, source=source)

    if len(comment) > 0:
        e.comment = comment
    e.save()

def _save_translation(entity, locale, translation, author=""):
    """Admin interface: save new or update existing translation in DB."""

    translations = Translation.objects.filter(entity=entity, locale=locale).order_by('date')

    if len(translations) == 0: # New translation
        t = Translation(entity=entity, locale=locale, string=translation,
            author=author, date=datetime.datetime.now())
    else: # Update translation
        t = translations.reverse()[0]
        t.string = translation
        t.author = author
        t.date = datetime.datetime.now()
    t.save()

def _get_locale_paths(source_paths, source_directory, locale_code):
    """Get paths to locale files."""

    locale_paths = []
    for sp in source_paths:
        locale_paths.append(sp.replace('/' + source_directory + '/', '/' + locale_code + '/').rstrip("t"))
    return locale_paths

def _get_format_and_source_paths(path):
    """Get file format based on extensions and paths to source files."""
    log.debug("Get file format based on extensions and paths to source files.")

    format = None
    source_paths = []
    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for extension in ('pot', 'po', 'properties', 'ini', 'lang'):
            for filename in fnmatch.filter(filenames, '*.' + extension):
                if format is None:
                    format = 'po' if extension == 'pot' else extension
                source_paths.append(os.path.join(root, filename))

    return format, source_paths

def _get_source_directory(path):
    """Get name and path of the directory with source strings."""
    log.debug("Get name and path of the directory with source strings.")

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for directory in ('templates', 'en-US', 'en-GB', 'en'):
            for dirname in fnmatch.filter(dirnames, directory):
                return dirname, root

        # INI Format
        return '', path

def _is_one_locale_repository(repository_url, repository_path_master):
    """Check if repository contains one or multiple locales."""

    source_directory = repository_url_master = False
    repository_path = repository_path_master
    last = os.path.basename(os.path.normpath(repository_url))

    if last in ('templates', 'en-US', 'en-GB', 'en'):
        source_directory = last
        repository_url_master = repository_url.rsplit(last, 1)[0]
        repository_path = os.path.join(repository_path_master, source_directory)

    return source_directory, repository_url_master, repository_path

def _update_hg(url, path):
    """Clone or update HG repository."""
    log.debug("Clone or update HG repository.")

    # Folders need to be manually created
    if not os.path.exists(path):
        os.makedirs(path)

    # Doesn't work with unicode type
    url = str(url)
    path = str(path)

    # First try updaiting the repo
    from mercurial import commands, hg, ui, error
    try:
        repo = hg.repository(ui.ui(), path)
        commands.pull(ui.ui(), repo, source=url)
        commands.update(ui.ui(), repo)
        log.debug("Mercurial: repository at " + url + " updated.")

    # If it doesn't exist, clone it
    except error.RepoError, e:
        log.debug("Mercurial: " + str(e))
        try:
            commands.clone(ui.ui(), url, path)
            log.debug("Mercurial: repository at " + url + " cloned.")
        except Exception, e:
            log.debug("Mercurial: " + str(e))

def _update_svn(url, path):
    """Checkout or update SVN repository."""
    log.debug("Checkout or update SVN repository.")

    import pysvn
    client = pysvn.Client()
    try:
        client.checkout(url, path)
    except pysvn.ClientError, e:
        log.debug("Subversion: " + str(e))

def _update_vcs(type, url, path):
    """Checkout or update repository with a given url to the path."""

    if type == 'hg':
        _update_hg(url, path)
    elif type == 'svn':
        _update_svn(url, path)

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

def parse_lang(path, skip_untranslated=True, extract_comments=False):
    """Parse a dotlang file and return a dict of translations."""
    trans = {}

    if not os.path.exists(path):
        return trans

    with codecs.open(path, 'r', 'utf-8', errors='replace') as lines:
        source = None
        comment = ''

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0] == '#':
                comment = line.lstrip('#').strip()
                continue

            if line[0] == ';':
                source = line[1:]

            elif source:
                for tag in ('{ok}', '{l10n-extra}'):
                    if line.lower().endswith(tag):
                        line = line[:-len(tag)]
                line = line.strip()
                if skip_untranslated and source == line:
                    continue
                if extract_comments:
                    trans[source] = [comment, line]
                    comment = ''
                else:
                    trans[source] = line

    return trans

def _extract_lang(project, locale, paths):
    """Extract .lang files from paths and save or update in DB."""

    for path in paths:
        lang = parse_lang(path, skip_untranslated=False, extract_comments=True)

        for key, value in lang.items():
            _save_entity(project, key, value[0])
            if key is value[1]:
                e = Entity.objects.get(project=project, string=key)
                _save_translation(entity=e, locale=locale, translation=value[1])

        log.debug("[" + locale.code + "]: saved to DB.")

def _extract_ini(project, path):
    """Extract .ini file from path and save or update in DB."""

    config = ConfigParser.ConfigParser()
    try:
        with open(path) as f:
            try:
                config.readfp(f)
            except Exception, e:
                log.debug("INI ConfigParser: " + str(e))
                raise Exception("error")
    except IOError, e:
        log.debug("IOError: " + str(e))
        raise Exception("error")

    sections = config.sections()

    source_locale = None
    for s in ('templates', 'en-US', 'en-GB', 'en'):
        if s in sections:
            source_locale = s
            break
    if source_locale is None:
        raise Exception("error")

    sections.insert(0, sections.pop(sections.index(source_locale)))

    for section in sections:
        for item in config.items(section):
            if section == source_locale:
                _save_entity(project=project, original=item[1], key=item[0], source=path)
            else:
                try:
                    l = Locale.objects.get(code=section)
                except Locale.DoesNotExist:
                    log.debug("Locale not supported: " + section)
                    break
                try:
                    e = Entity.objects.get(project=project, key=item[0], source=path)
                    _save_translation(entity=e, locale=l, translation=item[1])
                except Entity.DoesNotExist:
                    log.debug("[" + section + "]: line ID " + item[0] + " is obsolete.")
                    continue
        log.debug("[" + section + "]: saved to DB.")

def _extract_properties(project, locale, paths, source_directory):
    """Extract .properties files from paths and save or update in DB."""

    for path in paths:
        try:
            f = open(path)
            l10nobject = silme.format.properties.PropertiesFormatParser.get_structure(f.read())
            short_path = path.split(locale.code)[-1]

            for line in l10nobject:
                if isinstance(line, silme.core.entity.Entity):
                    if locale.code == source_directory:
                        _save_entity(project=project, original=line.value, key=line.id, source=short_path)
                    else:
                        try:
                            e = Entity.objects.get(project=project, key=line.id, source=short_path)
                            _save_translation(entity=e, locale=locale, translation=line.value)
                        except Entity.DoesNotExist:
                            # [Too verbose] log.debug("[" + l.code + "]: " + "line ID " + line.id + " in " + short_path + " is obsolete.")
                            continue
            log.debug("[" + locale.code + "]: " + path + " saved to DB.")
            f.close()
        except IOError:
            log.debug("[" + locale.code + "]: " + path + " doesn't exist. Skipping.")

def _extract_po(project, locale, paths):
    """Extract .po (gettext) files from paths and save or update in DB."""

    for path in paths:
        po = polib.pofile(path)
        entities = [e for e in po if not e.obsolete]

        for entity in entities:
            _save_entity(project, entity.msgid, entity.comment)
            if len(entity.msgstr) > 0:
                e = Entity.objects.get(project=project, string=entity.msgid)
                _save_translation(entity=e, locale=locale, translation=entity.msgstr, author=po.metadata['Last-Translator'])
        log.debug("[" + locale.code + "]: saved to DB.")

def update_from_repository(request, template=None):
    """Update all project locales from repository."""
    log.debug("Update all project locales from repository.")

    if not (request.user.is_authenticated() and request.user.has_perm('base.can_manage')) or request.method != 'POST':
        raise Http404

    try:
        pk = request.POST['pk']
        repository_type = request.POST['repository_type']
        repository_url = request.POST['repository']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    repository_path_master = os.path.join(settings.MEDIA_ROOT, repository_type, p.name)

    if repository_type == 'file':
        file_name = repository_url.rstrip('/').rsplit('/', 1)[1]

        temp, file_extension = os.path.splitext(file_name)
        format = file_extension[1:].lower()
        p.format = format;
        p.save()

        # Store file to server
        u = urllib2.urlopen(repository_url)
        file_path = os.path.join(repository_path_master, file_name)
        if not os.path.exists(repository_path_master):
            os.makedirs(repository_path_master)
        try:
            with open(file_path, 'w') as f:
                f.write(u.read())
        except IOError, e:
            log.debug("IOError: " + str(e))
            return HttpResponse("error")

        if format in ('po', 'pot'):
            locales = p.locales.all()
            for l in locales:
                _extract_po(p, l, [file_path])

        elif format == 'properties':
            # .properties format only stores translations, so the input file has to contain source (en-US) strings
            source_directory = 'en-US'
            locales = [Locale.objects.get(code=source_directory)]
            locales.extend(p.locales.all())
            for l in locales:
                _extract_properties(p, l, [file_path], source_directory)

        elif format == 'ini':
            try:
                _extract_ini(p, file_path)
            except Exception, e:
                os.remove(file_path)
                return HttpResponse("error")

        elif format == 'lang':
            locales = p.locales.all()
            for l in locales:
                _extract_lang(p, l, [file_path])

    elif repository_type in ('hg', 'svn'):
        """ Mercurial """
        # Update repository URL and path if one-locale repository
        source_directory, repository_url_master, repository_path = _is_one_locale_repository(repository_url, repository_path_master)

        _update_vcs(repository_type, repository_url, repository_path)

        # Get file format and paths to source files
        if source_directory is False:
            source_directory, source_directory_path = _get_source_directory(repository_path)
            format, source_paths = _get_format_and_source_paths(os.path.join(source_directory_path, source_directory))
        else:
            format, source_paths = _get_format_and_source_paths(repository_path)

            # Get remaining repositories if one-locale repository specified
            for l in p.locales.all():
                _update_hg(os.path.join(repository_url_master, l.code),
                    os.path.join(repository_path_master, l.code))

        p.format = format
        p.save()

        if format == 'po':
            locales = p.locales.all()
            for l in locales:
                _extract_po(p, l, _get_locale_paths(source_paths, source_directory, l.code))

        elif format == 'properties':
            locales = [Locale.objects.get(code=source_directory)]
            locales.extend(p.locales.all())
            for l in locales:
                _extract_properties(p, l, _get_locale_paths(source_paths, source_directory, l.code), source_directory)

        elif format == 'ini':
            try:
                _extract_ini(p, source_paths[0])
            except Exception, e:
                return HttpResponse("error")

    else:
        """ Not supported """
        return HttpResponse("error")

    return HttpResponse("200")

def update_from_transifex(request, template=None):
    """Update all project locales from Transifex repository."""
    log.debug("Update all project locales from Transifex repository.")

    if not (request.user.is_authenticated() and request.user.has_perm('base.can_manage')):
        raise Http404

    if request.method != 'POST':
        raise Http404

    try:
        pk = request.POST['pk']
        transifex_project = request.POST['transifex_project']
        transifex_resource = request.POST['transifex_resource']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = request.POST.get('transifex_username', profile.transifex_username)
    password = request.POST.get('transifex_password', base64.decodestring(profile.transifex_password))

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
                _save_entity(p, entity["key"], entity["comment"])
                if len(entity["translation"]) > 0:
                    e = Entity.objects.get(project=p, string=entity["key"])
                    _save_translation(entity=e, locale=l, translation=entity["translation"], author=entity["user"])
            log.debug("Transifex data for " + l.name + " saved to DB.")
        else:
            return HttpResponse(response)

    """Save Transifex username and password."""
    if 'remember' in request.POST and request.POST['remember'] == "on":
        profile.transifex_username = request.POST['transifex_username']
        profile.transifex_password = base64.encodestring(request.POST['transifex_password'])
        profile.save()

    return HttpResponse(response.status_code)
