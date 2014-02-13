
import base64
import configparser
import codecs
import commonware
import datetime
import fnmatch
import json
import os
import polib
import requests
import silme.core, silme.format.properties
import StringIO
import traceback
import urllib
import zipfile
from hashlib import md5

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from django_browserid import verify as browserid_verify
from django_browserid import get_audience
from pontoon.base.models import Locale, Project, Subpage, Entity, Translation, UserProfile
from pontoon.base.utils.permissions import add_can_localize
from session_csrf import anonymous_csrf_exempt


log = commonware.log.getLogger('pontoon')


def home(request, template='home.html'):
    """Home view."""
    log.debug("Home view.")

    data = {
        'accept_language': request.META.get('HTTP_ACCEPT_LANGUAGE', '').split(',')[0],
        'locales': Locale.objects.all(),
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    if request.user.is_authenticated() and not request.user.has_perm('base.can_localize'):
        messages.error(request, "You don't have permission to localize.")

    translate_error = request.session.pop('translate_error', {})
    locale = translate_error.get('locale')
    url = translate_error.get('url')

    if locale is not None:
        data['locale_code'] = locale

    if url is not None:
        data['project_url'] = url

    return render(request, template, data)


def handle_error(request):
    """
    A view to handle errors during loading a website for translation
    by Pontoon. This view is bound with a generic URL which can
    be called from Pontoon's javascript with appropriate GET parameters
    and the page will get redirected to the home page showing proper
    error messages, url and locale.
    """
    messages.error(request, request.GET.get('error', ''))
    request.session['translate_error'] = {
        'locale': request.GET.get('locale'),
        'url': request.GET.get('url')
    }
    return HttpResponseRedirect(reverse('pontoon.home'))


def translate_site(request, locale, url, template='translate.html'):
    """Translate view: site."""
    log.debug("Translate view: site.")

    # Validate URL
    # The default configuration of Apache doesn't allow encoded slashes in URLs
    # https://github.com/mozilla/playdoh/issues/143
    url = urllib.unquote(url)
    log.debug("URL: " + url)
    validate = URLValidator()

    try:
        validate(url)
    except ValidationError, e:
        log.debug(e)
        request.session['translate_error'] = {
            'locale': locale,
            'url': url
        }
        messages.error(request, "Oops, this is not a valid URL.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        messages.error(request, "Oops, locale is not supported.")
        request.session['translate_error'] = {
            'locale': locale,
            'url': url
        }
        return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'locale_code': locale,
        'locales': Locale.objects.all(),
        'project_url': url,
        'project': {},
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    try:
        p = Project.objects.get(url=url)
        try:
            # Select project and a subpage
            s = Subpage.objects.get(url=url)
            page = s.name
        except Subpage.DoesNotExist:
            # Select project, subpage does not exist
            page = None
    except Project.DoesNotExist:
        try:
            # Select subpage and its project
            s = Subpage.objects.get(url=url)
            p = s.project
            page = s.name
        except Subpage.DoesNotExist:
            # Project not stored in the DB
            data['project']['locales'] = Locale.objects.all()
            return render(request, template, data)

    # Check if user authenticated and has sufficient privileges
    if not p.name == 'testpilot':
        if not request.user.is_authenticated():
            messages.error(request, "You need to sign in first.")
            return HttpResponseRedirect(reverse('pontoon.home'))
        if not request.user.has_perm('base.can_localize'):
            messages.error(request, "You don't have permission to localize.")
            return HttpResponseRedirect(reverse('pontoon.home'))

    # Project stored in the DB, add more data
    if page is None:
        return HttpResponseRedirect(reverse('pontoon.translate.project',
        kwargs={'locale': locale, 'project': p.name}))
    else:
        return HttpResponseRedirect(reverse('pontoon.translate.project.page',
        kwargs={'locale': locale, 'project': p.name, 'page': page}))


def _get_entities(project, locale, page=None):
    """Load all project entities and translations."""
    log.debug("Load all project entities and translations.")

    entities = Entity.objects.filter(project=project)
    if page != None and entities[0].source != '':
        entities = entities.filter(source__endswith=page + '.properties')

    entities_array = []
    for e in entities:
        suggestions = None
        translations = Translation.objects.filter(entity=e, locale=locale).order_by('date')

        if len(translations) == 0:
            translation = ""
        else:
            first = translations.reverse()[0]
            translation = first.string
            if len(translations) > 1:
                suggestions = []
                for t in translations.exclude(id=first.id):
                    o = {
                        "author": t.author,
                        "date": t.date.strftime("%b %d, %Y %H:%M"),
                        "translation": t.string
                    }
                    suggestions.append(o)

        obj = {
            "original": e.string,
            "comment": e.comment,
            "key": e.key,
            "pk": e.pk,
            "translation": translation
        }
        if suggestions != None:
            obj["suggestions"] = suggestions

        entities_array.append(obj)
    return entities_array


def translate_project(request, locale, project, page=None, template='translate.html'):
    """Translate view: project."""
    log.debug("Translate view: project.")

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        messages.error(request, "Oops, locale is not supported.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate project
    try:
        p = Project.objects.get(name=project, pk__in=Entity.objects.values('project'))
    except Project.DoesNotExist:
        messages.error(request, "Oops, project could not be found.")
        request.session['translate_error'] = {'locale': locale}
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Check if user authenticated and has sufficient privileges
    if not p.name == 'testpilot':
        if not request.user.is_authenticated():
            messages.error(request, "You need to sign in first.")
            return HttpResponseRedirect(reverse('pontoon.home'))
        if not request.user.has_perm('base.can_localize'):
            messages.error(request, "You don't have permission to localize.")
            return HttpResponseRedirect(reverse('pontoon.home'))

    data = {
        'locale_code': locale,
        'locales': Locale.objects.all(),
        'project_url': p.url,
        'project': p,
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    # Validate project locales
    if len(p.locales.filter(code=locale)) == 0:
        request.session['translate_error'] = {
            'locale': locale,
            'url': data['project_url']
        }
        messages.error(request, "Oops, locale is not supported for this website.")
        return HttpResponseRedirect(reverse('pontoon.home'))

    # Validate subpages
    pages = Subpage.objects.filter(project=p)
    if len(pages) > 0:
        if page is None:
            try:
                # If page exist, but not specified in URL
                page = pages.filter(url__startswith=p.url)[0].name
            except IndexError:
                request.session['translate_error'] = {
                    'locale': locale,
                    'url': p.url
                }
                messages.error(request, "Oops, project URL doesn't match any subpage.")
                return HttpResponseRedirect(reverse('pontoon.home'))
        else:
            try:
                data['project_url'] = pages.get(name=page).url
            except Subpage.DoesNotExist:
                request.session['translate_error'] = {
                    'locale': locale,
                    'url': p.url
                }
                messages.error(request, "Oops, subpage could not be found.")
                return HttpResponseRedirect(reverse('pontoon.home'))
        data['pages'] = pages
        data['current_page'] = page

    # Get entities
    if page is not None:
        page = page.lower().replace(" ", "")
    data['entities'] = json.dumps(_get_entities(p, l, page))

    return render(request, template, data)


def _request(type, project, resource, locale, username, password, payload=False):
    """
    Make request to Transifex server.

    Args:
        type: Request type
        project: Transifex project name
        resource: Transifex resource name
        locale: Locale code
        username: Transifex username
        password: Transifex password
        payload: Data to be sent to the server
    Returns:
        A server response or error message.
    """
    url = os.path.join('https://www.transifex.com/api/2/project/', project, 'resource', resource, 'translation', locale, 'strings')

    try:
        if type == 'get':
            r = requests.get(url + '?details', auth=(username, password), timeout=10)
        elif type == 'put':
            r = requests.put(url, auth=(username, password), timeout=10, 
                data=json.dumps(payload), headers={'content-type': 'application/json'})
        log.debug(r.status_code)
        if r.status_code == 401:
            return "authenticate"
        elif r.status_code != 200:
            return "error"
        return r
    # Network problem (DNS failure, refused connection, etc.)
    except requests.exceptions.ConnectionError, e:
        log.debug('ConnectionError: ' + str(e))
        return "error"
    # Invalid HTTP response
    except requests.exceptions.HTTPError, e:
        log.debug('HTTPError: ' + str(e))
        return "error"
    # A valid URL is required
    except requests.exceptions.URLRequired, e:
        log.debug('URLRequired: ' + str(e))
        return "error"
    # Request times out
    except requests.exceptions.Timeout, e:
        log.debug('Timeout: ' + str(e))
        return "error"
    # Request exceeds the number of maximum redirections
    except requests.exceptions.TooManyRedirects, e:
        log.debug('TooManyRedirects: ' + str(e))
        return "error"
    # Ambiguous exception occurres
    except requests.exceptions.RequestException, e:
        log.debug('RequestException: ' + str(e))
        return "error"
    except Exception:
        log.debug('Generic exception: ' + traceback.format_exc())
        return "error"


def get_translations_from_other_locales(request, template=None):
    """Get entity translations for all but specified locale."""
    log.debug("Get entity translation for all but specified locale.")

    if not request.is_ajax():
        raise Http404

    try:
        entity = request.GET['entity']
        locale = request.GET['locale']
    except MultiValueDictKeyError as e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Locale: " + locale)

    try:
        entity = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(str(e))
        return HttpResponse("error")

    payload = []
    translations = Translation.objects.filter(entity=entity)

    for l in entity.project.locales.all().exclude(code=locale.code):
        translation = translations.filter(locale=l).order_by('date')

        if len(translation) != 0:
            t = translation.reverse()[0]
            payload.append({
                "locale": {
                    "code": t.locale.code,
                    "name": t.locale.name
                },
                "translation": t.string
            })

    if len(payload) == 0:
        log.debug("Translations do not exist.")
        return HttpResponse("error")
    else:
        return HttpResponse(json.dumps(payload, indent=4),
            mimetype='application/json')


@login_required(redirect_field_name='', login_url='/403')
def update_translation(request, template=None):
    """Update entity translation for the specified locale and author."""
    log.debug("Update entity translation for the specified locale and author.")

    if request.method != 'POST':
        raise Http404

    try:
        entity = request.POST['entity']
        translation = request.POST['translation']
        locale = request.POST['locale']
    except MultiValueDictKeyError, e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Translation: " + translation)
    log.debug("Locale: " + locale)

    try:
        e = Entity.objects.get(pk=entity)
    except Entity.DoesNotExist, e:
        log.error(str(e))
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist, e:
        log.error(str(e))
        return HttpResponse("error")

    translations = Translation.objects.filter(entity=e, locale=l).order_by('date')

    # No translation saved yet
    if len(translations) == 0:
        if translation != '':
            t = Translation(entity=e, locale=l, string=translation,
                author=request.user.email, date=datetime.datetime.now())
            t.save()
            log.debug("Translation saved.")
            return HttpResponse("saved")

        else:
            log.debug("Translation not set.")
            return HttpResponse("not set")

    # Translations exist
    else:
        if translation == '':
            translations.delete()
            log.debug("Translation deleted.")
            return HttpResponse("deleted")

        else:
            # Translation by author exist
            try:
                t = translations.get(entity=e, locale=l, author=request.user.email)
                t.string = translation
                t.date = datetime.datetime.now()

            # Translation by author doesn't exist
            except Translation.DoesNotExist:
                t = Translation(entity=e, locale=l, string=translation,
                    author=request.user.email, date=datetime.datetime.now())

            t.save()
            log.debug("Translation updated.")
            return HttpResponse("updated")


@login_required(redirect_field_name='', login_url='/403')
def translation_memory(request):
    """Get translation from translation memory service."""
    log.debug("Get translation from translation memory service.")

    try:
        text = request.GET['text']
        locale = request.GET['locale']
    except MultiValueDictKeyError, e:
        log.error(str(e))
        return HttpResponse("error")

    url = "http://transvision.mozfr.org/"
    payload = {
        "recherche": text,
        "sourcelocale": "en-US",
        "locale": locale,
        "perfect_match": "perfect_match",
        "repo": "aurora",
        "json": True,
    }

    try:
        r = requests.get(url, params=payload)

        if r.text != '[]':
            translation = r.json().itervalues().next().itervalues().next()

            # Use JSON to distinguish from "error" if such translation returned
            return HttpResponse(json.dumps({
                'translation': translation
            }), mimetype='application/json')

        else:
            return HttpResponse("no")

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


@login_required(redirect_field_name='', login_url='/403')
def machine_translation(request):
    """Get translation from machine translation service."""
    log.debug("Get translation from machine translation service.")

    try:
        text = request.GET['text']
        to = request.GET['locale']
    except MultiValueDictKeyError, e:
        log.error(str(e))
        return HttpResponse("error")

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        api_key = settings.MICROSOFT_TRANSLATOR_API_KEY
    else:
        log.error("MICROSOFT_TRANSLATOR_API_KEY not set")
        return HttpResponse("apikey")

    url = "http://api.microsofttranslator.com/V2/Http.svc/Translate"
    payload = {
        "appId": api_key,
        "text": text,
        "from": "en",
        "to": to,
        "contentType": "text/html",
    }

    try:
        r = requests.get(url, params=payload)
        log.debug(r.content)

        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.content)
        translation = root.text

        # Use JSON to distinguish from "error" if such translation returned
        return HttpResponse(json.dumps({
            'translation': translation
        }), mimetype='application/json')

    except Exception as e:
        log.error(e)
        return HttpResponse("error")


def _get_locale_repository_path(project, locale):
    """Get path to locale directory."""
    log.debug("Get path to locale directory.")

    path = os.path.join(
        settings.MEDIA_ROOT, project.repository_type, project.name)

    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for dirname in fnmatch.filter(dirnames, locale):
            return os.path.join(root, dirname)

    # Fallback to project's repository_path
    return path


def _get_locale_paths(path, format):
    """Get paths to locale files."""

    locale_paths = []
    for root, dirnames, filenames in os.walk(path):
        # Ignore hidden files and folders
        filenames = [f for f in filenames if not f[0] == '.']
        dirnames[:] = [d for d in dirnames if not d[0] == '.']

        for filename in fnmatch.filter(filenames, '*.' + format):
            locale_paths.append(os.path.join(root, filename))

    return locale_paths


def _update_files(p, locale, locale_repository_path):
    entities = Entity.objects.filter(project=p)
    locale_paths = _get_locale_paths(locale_repository_path, p.format)

    if p.format == 'po':
        for path in locale_paths:
            po = polib.pofile(path)
            valid_entries = [e for e in po if not e.obsolete]

            for entity in entities:
                entry = po.find(entity.string)
                if entry:
                    translations = Translation.objects.filter(entity=entity, locale=locale).order_by('date')
                    if len(translations) > 0:
                        entry.msgstr = translations.reverse()[0].string

                    if 'fuzzy' in entry.flags:
                        entry.flags.remove('fuzzy')

            po.save()
            log.debug("File updated: " + path)

    elif p.format == 'properties':
        for path in locale_paths:
            format_parser = silme.format.properties.PropertiesFormatParser
            with codecs.open(path, 'r+', 'utf-8') as f:
                l10nobject = format_parser.get_structure(f.read())

                short_path = '/' + path.split('/' + locale.code + '/')[-1]
                entities_with_path = entities.filter(source=short_path)
                for entity in entities_with_path:
                    key = entity.key
                    translations = Translation.objects.filter(entity=entity, locale=locale).order_by('date')
                    if len(translations) == 0:
                        translation = ''
                    else:
                        translation = translations.reverse()[0].string

                    try:
                        l10nobject.modify_entity(key, translation)
                    except KeyError:
                        # Only add new keys if translation available
                        if translation != '':
                            new_entity = silme.core.entity.Entity(key, translation)
                            l10nobject.add_entity(new_entity)

                # Erase file and then write, otherwise content gets appended
                f.seek(0)
                f.truncate()
                content = format_parser.dump_structure(l10nobject)
                f.write(content)
                log.debug("File updated: " + locale_paths[0])

    elif p.format == 'ini':
        config = configparser.ConfigParser()
        with codecs.open(locale_paths[0], 'r+', 'utf-8', errors='replace') as f:
            try:
                config.read_file(f)
                if config.has_section(locale.code):

                    for entity in entities:
                        key = entity.key
                        translations = Translation.objects.filter(entity=entity, locale=locale).order_by('date')
                        if len(translations) == 0:
                            translation = ''
                        else:
                            translation = translations.reverse()[0].string
                        config.set(locale.code, key, translation)

                    # Erase file and then write, otherwise content gets appended
                    f.seek(0)
                    f.truncate()
                    config.write(f)
                    log.debug("File updated: " + locale_paths[0])

                else:
                    log.debug("Locale not available in the source file.")
                    raise Exception("error")

            except Exception, e:
                log.debug("INI configparser: " + str(e))
                raise Exception("error")

    elif p.format == 'lang':
        for path in locale_paths:
            with codecs.open(path, 'r+', 'utf-8', errors='replace') as lines:
                content = []
                translation = None

                for line in lines:
                    if translation:
                        # Keep newlines and white spaces in line if present
                        trans_line = line.replace(line.strip(), translation)
                        content.append(trans_line)
                        translation = None
                        continue

                    content.append(line)
                    line = line.strip()

                    if not line:
                        continue

                    if line[0] == ';':
                        original = line[1:].strip()

                        try:
                            entity = Entity.objects.get(project=p, string=original)
                        except Entity.DoesNotExist, e:
                            log.error(path + ": Entity with string \"" + original + "\" does not exist in " + p.name)
                            continue

                        translations = Translation.objects.filter(entity=entity, locale=locale).order_by('date')
                        if len(translations) == 0:
                            translation = original
                        else:
                            translation = translations.reverse()[0].string

                # Erase file and then write, otherwise content gets appended
                lines.seek(0)
                lines.truncate()
                lines.writelines(content)
                log.debug("File updated: " + path)


def _generate_zip(pk, locale):
    """
    Generate .zip file of all project files for the specified locale.

    Args:
        pk: Primary key of the project
        locale: Locale code
    Returns:
        A string for generated ZIP content.
    """

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist as e:
        log.error(e)

    try:
        locale = Locale.objects.get(code=locale)
    except Locale.DoesNotExist as e:
        log.error(e)

    path = _get_locale_repository_path(p, locale.code)
    _update_files(p, locale, path)

    s = StringIO.StringIO()
    zf = zipfile.ZipFile(s, "w")

    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            zip_path = os.path.relpath(file_path, os.path.join(path, '..'))
            zf.write(file_path, zip_path)

    zf.close()
    return s.getvalue()


@anonymous_csrf_exempt
def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations.")

    if request.method != 'POST':
        raise Http404

    try:
        type = request.POST['type']
        content = request.POST['content']
        locale = request.POST['locale']
    except MultiValueDictKeyError:
        raise Http404

    filename = locale
    response = HttpResponse()
    if type == 'html':
        response['Content-Type'] = 'text/html'
    elif type == 'json':
        response['Content-Type'] = 'application/json'
    elif type == 'zip':
        content = _generate_zip(content, locale)
        response['Content-Type'] = 'application/x-zip-compressed'

    response.content = content
    response['Content-Disposition'] = 'attachment; filename=' + filename +\
            '.' + type
    return response


@login_required(redirect_field_name='', login_url='/403')
def commit_to_svn(request, template=None):
    """Commit translations to SVN."""
    log.debug("Commit translations to SVN.")

    try:
        import pysvn
    except ImportError as e:
        log.error(e)
        return HttpResponse("error")

    if request.method != 'POST':
        log.error("Only POST method supported")
        raise Http404

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError as e:
        log.error(e)
        return HttpResponse("error")

    try:
        locale = Locale.objects.get(code=data['locale'])
    except Locale.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    try:
        p = Project.objects.get(pk=data['pk'])
    except Project.DoesNotExist as e:
        log.error(e)
        return HttpResponse("error")

    project = p.name
    locale_repository_path = _get_locale_repository_path(p, locale.code)

    _update_files(p, locale, locale_repository_path)

    client = pysvn.Client()
    client.exception_style = 1

    """Check if user authenticated to SVN."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    username = data.get('auth', {}).get('username', profile.svn_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.svn_password))

    if len(username) > 0 and len(password) > 0:
        client.set_default_username(username)
        client.set_default_password(password)

    try:
        client.checkin([locale_repository_path],
            'Pontoon: update ' + locale.code + ' localization of ' + project)
        log.info('Commited ' + locale.code + ' localization of ' + project)

    except pysvn.ClientError, e:
        log.debug(str(e))
        if "callback_get_login" in str(e):
            log.error('Subversion CommitError for %s: please authenticate' % locale_repository_path)
            return HttpResponse(json.dumps({
                'type': 'authenticate',
                'message': 'Authentication failed.'
            }), mimetype='application/json')

        log.error('Subversion CommitError for %s: %s' % (locale_repository_path, e))
        return HttpResponse(json.dumps({
            'type': 'error',
            'message': str(e)
        }), mimetype='application/json')

    """Save SVN username and password."""
    if data.get('auth', {}).get('remember', {}) == 1:
        if profile.svn_username != username:
            profile.svn_username = username
        if base64.decodestring(profile.svn_password) != password:
            profile.svn_password = base64.encodestring(password)
        profile.save()
        log.info("SVN username and password saved.")

    return HttpResponse("200")


@login_required(redirect_field_name='', login_url='/403')
def save_to_transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    if request.method != 'POST':
        raise Http404

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError:
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    username = data.get('auth', {}).get('username', profile.transifex_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.transifex_password))
    if len(username) == 0 or len(password) == 0:
        return HttpResponse("authenticate")

    """Make PUT request to Transifex API."""
    payload = []
    for entity in data.get('strings'):
        obj = {
            # Identify translation strings using hashes
            "source_entity_hash": md5(':'.join([entity['original'], '']).encode('utf-8')).hexdigest(),
            "translation": entity['translation']
        }
        payload.append(obj)
    log.debug(json.dumps(payload, indent=4))

    """Make PUT request to Transifex API."""
    try:
        p = Project.objects.get(url=data['url'])
    except Project.DoesNotExist:
        return HttpResponse("error")
    response = _request('put', p.transifex_project, p.transifex_resource, data['locale'], username, password, payload)

    """Save Transifex username and password."""
    if data.get('auth', {}).get('remember', {}) == 1:
        profile.transifex_username = data['auth']['username']
        profile.transifex_password = base64.encodestring(data['auth']['password'])
        profile.save()

    try:
        return HttpResponse(response.status_code)
    except AttributeError:
        return HttpResponse(response)


@anonymous_csrf_exempt
def verify(request, template=None):
    """Verify BrowserID assertion, and return whether a user is registered."""
    log.debug("Verify BrowserID assertion.")

    if request.method != 'POST':
        raise Http404

    assertion = request.POST['assertion']
    if assertion is None:
        return HttpResponseBadRequest()

    verification = browserid_verify(assertion, get_audience(request))
    if not verification:
        return HttpResponseForbidden()

    response = 'error'
    user = authenticate(assertion=assertion, audience=get_audience(request))

    if user is not None:
        login(request, user)

        # Check for permission to localize if not granted on every login
        if not user.has_perm('base.can_localize'):
            user = User.objects.get(username=user)
            add_can_localize(user)

        response = {'browserid': verification,
            'manager': user.has_perm('base.can_manage'),
            'localizer': user.has_perm('base.can_localize')
        }

    return HttpResponse(json.dumps(response), mimetype='application/json')


def get_csrf(request, template=None):
    """Get CSRF token."""
    log.debug("Get CSRF token.")

    if not request.is_ajax():
        raise Http404

    return HttpResponse(request.csrf_token)
