
import base64
import commonware
import datetime
import fnmatch
import json
import os
import polib
import pysvn
import requests
import silme.core, silme.format.properties
import traceback
from hashlib import md5

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django_browserid import verify as browserid_verify
from django_browserid import get_audience
from pontoon.base.models import Locale, Project, Subpage, Entity, Translation, UserProfile
from session_csrf import anonymous_csrf_exempt

from mobility.decorators import mobile_template


log = commonware.log.getLogger('playdoh')


@mobile_template('{mobile/}home.html')
def home(request, error=None, locale=None, url=None, template=None):
    """Home view."""
    log.debug("Home view.")

    data = {
        'accept_language': request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0],
        'locales': Locale.objects.all(),
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    if error is not None:
        data['error'] = error

    if locale is not None:
        data['locale_code'] = locale

    if url is not None:
        data['project_url'] = url

    return render(request, template, data)

@mobile_template('{mobile/}translate.html')
def translate_site(request, locale, template=None):
    """Translate view: site."""
    log.debug("Translate view: site.")

    # Validate URL
    url = request.build_absolute_uri().split('/site/')[1]
    log.debug("URL: " + url)
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError, e:
        log.debug(e)
        return home(request, "Oops, this is not a valid URL.", locale, url)

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        return home(request, "Oops, locale is not supported.", locale, url)

    data = {
        'locale_code': locale,
        'project_url': url,
        'project': {},
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        data['mt_apikey'] = settings.MICROSOFT_TRANSLATOR_API_KEY

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
        entities = entities.filter(source=page + '.properties')

    entities_array = []
    for e in entities:
        try:
            t = Translation.objects.get(entity=e, locale=locale)
            translation = t.string
        except Translation.DoesNotExist:
            translation = ""

        obj = {
            "original": e.string,
            "comment": e.comment,
            "key": e.key,
            "pk": e.pk,
            "translation": translation
        }
        entities_array.append(obj)
    return entities_array

@mobile_template('{mobile/}translate.html')
def translate_project(request, locale, project, page=None, template=None):
    """Translate view: project."""
    log.debug("Translate view: project.")

    # Validate locale
    log.debug("Locale: " + locale)
    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        return home(request, "Oops, locale is not supported.")

    # Validate project
    try:
        p = Project.objects.get(name=project, pk__in=Entity.objects.values('project'))
    except Project.DoesNotExist:
        return home(request, "Oops, project could not be found.", locale)

    data = {
        'locale_code': locale,
        'project_url': p.url,
        'project': p,
        'projects': Project.objects.filter(pk__in=Entity.objects.values('project'))
    }

    # Validate project locales
    if len(p.locales.filter(code=locale)) == 0:
        return home(request, "Oops, locale is not supported for this website.", locale, data['project_url'])

    # Validate subpages
    pages = Subpage.objects.filter(project=p)
    if len(pages) > 0:
        if page is None:
            page = pages.filter(url=p.url)[0].name # If page exist, but not specified
        else:
            try:
                data['project_url'] = pages.get(name=page).url
            except Subpage.DoesNotExist:
                return home(request, "Oops, subpage could not be found.", locale, p.url)
        data['pages'] = pages
        data['current_page'] = page

    # Get entities
    data['entities'] = json.dumps(_get_entities(p, l, page.lower().replace(" ", "")))

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        data['mt_apikey'] = settings.MICROSOFT_TRANSLATOR_API_KEY

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

def get_translation(request, template=None):
    """Get entity translation of a specified project and locale."""
    log.debug("Get entity translation of a specified project and locale.")

    if not request.is_ajax():
        raise Http404

    try:
        original = request.GET['original']
        pk = request.GET['pk']
        locale = request.GET['locale']
    except MultiValueDictKeyError:
        return HttpResponse("error")

    log.debug("Entity: " + original)
    log.debug("Project ID: " + pk)
    log.debug("Locale: " + locale)

    try:
        p = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return HttpResponse("error")

    try:
        e = Entity.objects.get(project=p, string=original)
    except Entity.DoesNotExist:
        return HttpResponse("error")

    try:
        l = Locale.objects.get(code=locale)
    except Locale.DoesNotExist:
        return HttpResponse("error")

    try:
        t = Translation.objects.get(entity=e, locale=l)
        log.debug("Translation: " + t.string)
        return HttpResponse(t.string)
    except Translation.DoesNotExist:
        log.debug("Translation does not exist.")
        return HttpResponse("error")

@login_required(redirect_field_name='', login_url='/404')
def update_translation(request, template=None):
    """Update entity translation for the specified project and locale."""
    log.debug("Update entity translation for the specified project and locale.")

    if not request.is_ajax():
        raise Http404

    try:
        entity = request.GET['entity']
        translation = request.GET['translation']
        project = request.GET['project']
        locale = request.GET['locale']
    except MultiValueDictKeyError, e:
        log.error(str(e))
        return HttpResponse("error")

    log.debug("Entity: " + entity)
    log.debug("Translation: " + translation)
    log.debug("Project ID: " + project)
    log.debug("Locale: " + locale)

    try:
        p = Project.objects.get(pk=project)
    except Project.DoesNotExist, e:
        log.error(str(e))
        return HttpResponse("error")

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

    try:
        """Update existing translation."""
        t = Translation.objects.get(entity=e, locale=l)

        if translation != '':
            log.debug("Translation updated.")
            t.string = translation
            t.save()
            return HttpResponse("updated")
        else:
            log.debug("Translation deleted.")
            t.delete()
            return HttpResponse("deleted")

    except Translation.DoesNotExist:
        """Save new translation."""
        if translation != '':
            t = Translation(entity=e, locale=l, string=translation, 
                author=request.user.email, date=datetime.datetime.now())
            t.save()
            log.debug("Translation saved.")
            return HttpResponse("saved")
        else:
            log.debug("Translation not set.")
            return HttpResponse("not set")

def _generate_properties_content(url, locale):
    """
    Generate .properties file content.

    Args:
        pid: project ID
        locale: locale code
    Returns:
        A string for generated .properties file.
    """

    try:
        s = Subpage.objects.get(url=url)
    except Subpage.DoesNotExist:
        log.debug('Subpage with this URL does not exist')
        return "error"

    subpage = s.name.lower().replace(" ", "")
    p = s.project
    l = Locale.objects.get(code=locale)

    original_path = os.path.join(settings.MEDIA_ROOT, 'hg', p.name, 'en-US')
    path = []
    for root, dirnames, filenames in os.walk(original_path):
      for filename in fnmatch.filter(filenames, subpage + '.properties'):
          path.append(os.path.join(root, filename))

    path = path[0]
    l10nobject = silme.format.properties.PropertiesFormatParser.get_structure(open(path).read().decode('utf-8'))

    for line in l10nobject:
        if isinstance(line, silme.core.entity.Entity):
            e = Entity.objects.get(project=p, key=line.id, source=subpage + '.properties')
            try:
                t = Translation.objects.get(entity=e, locale=l)
                line.set_value(t.string)
            except Translation.DoesNotExist:
                line.id = '#TODO: ' + line.id
                line.set_value(line.value)

    content = silme.format.properties.PropertiesFormatParser.dump_structure(l10nobject)
    properties = unicode(content).encode('utf-8')

    path = path.replace('en-US', l.code, 1)
    try:
        f = open(path, 'w')
    except IOError, e:
        log.debug("File does not exist yet. Creating a new one.")
        os.makedirs(os.path.dirname(path))
        f = open(path, 'w')
    finally:
        f.write(properties)
        f.close()
        log.debug("File saved.")

    return (properties, subpage)

def _generate_po_content(data):
    """
    Generate .po file content from data JSON.

    Args:
        data: A JSON string
    Returns:
        A string for generated PO content.
    """
    json_dict = json.loads(data)
    po = polib.POFile()
    current_time = datetime.datetime.now()
    metadata = json_dict.get('metadata', {})
    translations = json_dict.get('translations', {})

    # Add PO metadata
    po.metadata = {
        'Project-Id-Version': '1.0',
        'POT-Creation-Date': current_time,
        'PO-Revision-Date': current_time,
        'Last-Translator': '%s <%s>' % (json_dict['metadata'].get('username'),
            json_dict['metadata'].get('user_email')),
        'Language-Team': json_dict['metadata'].get('locale_language'),
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit'
    }

    # Add PO header
    po.header = (
            "%(project_title)s language file (%(locale_language)s)\n"
            "This is distributed under the same license as the website.\n"
            "%(username)s <%(user_email)s>, %(year)s\n" % {
                'project_title': metadata.get('project_title'),
                'locale_language': metadata.get('locale_language'),
                'username': metadata.get('username'),
                'user_email': metadata.get('user_email'),
                'year': current_time.year
             }
    )

    # Append PO entries
    for msgid in translations.keys():
        po_entry = polib.POEntry(
                msgid=msgid,
                msgstr=translations[msgid].get('msgstr', ''),
                occurrences = [(translations[msgid].get('occurrence', ''), '')]
        )
        if translations[msgid].get('fuzzy'):
            po_entry.flags.append('fuzzy')
        po.append(po_entry)
    return unicode(po).encode('utf-8')

@login_required(redirect_field_name='', login_url='/404')
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
    elif type == 'po':
        content = _generate_po_content(content)
        response['Content-Type'] = 'text/plain'
    elif type == 'properties':
        content, filename = _generate_properties_content(content, locale)
        response['Content-Type'] = 'text/plain'

    response.content = content
    response['Content-Disposition'] = 'attachment; filename=' + filename +\
            '.' + type
    return response

@login_required(redirect_field_name='', login_url='/404')
def commit_to_svn(request, template=None):
    """Commit translations to SVN."""
    log.debug("Commit translations to SVN.")

    if request.method != 'POST':
        return HttpResponse("error")

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError:
        return HttpResponse("error")

    """Check if user authenticated to SVN."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    username = data.get('auth', {}).get('username', profile.svn_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.svn_password))
    if (len(username) == 0 or len(password) == 0):
        return HttpResponse("authenticate")

    locale = data['locale']
    content = data['content']

    try:
        p = Project.objects.get(url=data['url'])
    except Project.DoesNotExist:
        return HttpResponse("error")
    project = p.name

    client = pysvn.Client()
    client.set_default_username(username)
    client.set_default_password(password)

    f = open(os.path.join(settings.MEDIA_ROOT, 'svn', project, 'locale', locale, 'LC_MESSAGES', 'messages.po'), 'w')
    f.write(_generate_po_content(content))
    f.close()

    """Save SVN username and password."""
    if 'auth' in data and 'remember' in data['auth'] and data['auth']['remember'] == 1:
        profile.svn_username = data['auth']['username']
        profile.svn_password = base64.encodestring(data['auth']['password'])
        profile.save()

    try:
        client.checkin([os.path.join(settings.MEDIA_ROOT, 'svn', project, 'locale', locale)],
            'Pontoon: update ' + locale + ' localization of ' + project + '')
        return HttpResponse("200")
    except pysvn.ClientError, e:
        log.debug(str(e))
        return HttpResponse("error")

@login_required(redirect_field_name='', login_url='/404')
def save_to_transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    if request.method != 'POST':
        return HttpResponse("error")

    try:
        data = json.loads(request.POST['data'])
    except MultiValueDictKeyError:
        return HttpResponse("error")

    """Check if user authenticated to Transifex."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    username = data.get('auth', {}).get('username', profile.transifex_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.transifex_password))
    if (len(username) == 0 or len(password) == 0):
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
    if 'auth' in data and 'remember' in data['auth'] and data['auth']['remember'] == 1:
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

    response_data = {'registered': False, 'browserid': verification}
    user = auth.authenticate(assertion=assertion, audience=get_audience(request))
    if user is not None:
        auth.login(request, user)
        response_data = {'registered': True, 'browserid': verification,
            'manager': user.has_perm('base.can_manage')}

    return HttpResponse(json.dumps(response_data), mimetype='application/json')

def get_csrf(request, template=None):
    """Get CSRF token."""
    log.debug("Get CSRF token.")

    if not request.is_ajax():
        raise Http404

    return HttpResponse(request.csrf_token)
