
import base64
import commonware
import datetime
import json
import logging
import polib
import requests
import traceback
from hashlib import md5

from django import http
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django_browserid import verify as browserid_verify
from django_browserid import get_audience
from pontoon.base.models import Project, Entity, Locale, Translation

from funfactory.log import log_cef
from mobility.decorators import mobile_template


log = commonware.log.getLogger('playdoh')


@mobile_template('{mobile/}home.html')
def home(request, template=None):
    """Main view."""
    log.debug("Main view.")

    data = {
        'accept_language': request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0],
        'locales': Locale.objects.all(),
        'projects': Project.objects.all()
    }

    return render(request, template, data)

@mobile_template('{mobile/}translate.html')
def translate(request, locale, url, template=None):
    """Translate view."""
    log.debug("Translate view.")

    data = {
        'locale_code': locale,
        'project_url': url,
        'locales': Locale.objects.all()
    }

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        data['mt_apikey'] = settings.MICROSOFT_TRANSLATOR_API_KEY

    return render(request, template, data)

def check_url(request, template=None):
    """Check if URL exists."""
    log.debug("Check if URL exists.")

    try:
        url = request.GET['url']
    except MultiValueDictKeyError:
        raise Http404

    log.debug(url)

    validate = URLValidator(verify_exists=True)
    try:
        validate(url)
        status = "valid"
    except ValidationError, e:
        log.debug(e)
        status = "invalid"
    return HttpResponse(status)

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
    url = 'https://www.transifex.com/api/2/project/' + project + '/resource/' + resource + '/translation/' + locale + '/strings/'

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

    try:
        original = request.GET['original']
        project = request.GET['project']
        locale = request.GET['locale']
    except MultiValueDictKeyError:
        raise Http404

    log.debug("Entity: " + original)
    log.debug("Project: " + project)
    log.debug("Locale: " + locale)

    p = Project.objects.filter(name=project)
    e = Entity.objects.filter(project=p, string=original)
    l = Locale.objects.get(code=locale)

    try:
        t = Translation.objects.get(entity=e, locale=l)
        log.debug("Translation: " + t.string)
        return HttpResponse(t.string)
    except Translation.DoesNotExist:
        log.debug("Translation does not exist.")
        return HttpResponse("error")

@login_required(redirect_field_name='', login_url='/404')
def save_translation(request, template=None):
    """Save entity translation to the specified project and locale."""
    log.debug("Save entity translation to the specified project and locale.")

    try:
        original = request.GET['original']
        translation = request.GET['translation']
        project = request.GET['project']
        locale = request.GET['locale']
    except MultiValueDictKeyError:
        raise Http404

    log.debug("Entity: " + original)
    log.debug("Translation: " + translation)
    log.debug("Project: " + project)
    log.debug("Locale: " + locale)

    p = Project.objects.filter(name=project)
    e = Entity.objects.filter(project=p, string=original)
    l = Locale.objects.get(code=locale)

    try:
        """Update existing translation."""
        t = Translation.objects.get(entity=e[0], locale=l)
        t.string = translation
        t.save()

        if translation != '':
            log.debug("Translation updated.")
            return HttpResponse("updated")
        else:
            log.debug("Translation deleted.")
            return HttpResponse("deleted")

    except Translation.DoesNotExist:
        """Save new translation."""
        if translation != '':
            t = Translation(entity=e[0], locale=l, string=translation, 
                author=request.user.email, date=datetime.datetime.now())
            t.save()
            log.debug("Translation saved.")
            return HttpResponse("saved")
        else:
            log.debug("Translation not set.")
            return HttpResponse("not set")

def load_entities(request, template=None):
    """Load all project entities and translations."""
    log.debug("Load all project entities and translations.")

    try:
        project = request.GET['project']
        resource = request.GET['resource']
        locale = request.GET['locale']
        project_url = request.GET['url']
        callback = str(request.GET.get('callback', '')) # JSONP
    except MultiValueDictKeyError:
        raise Http404

    log.debug("Project: " + project)
    log.debug("Locale: " + locale)

    """Query DB by project name and locale or load data from Transifex."""
    l = Locale.objects.get(code=locale)
    p = Project.objects.filter(name=project)
    if len(p) > 0 and len(p[0].locales.filter(code=locale)) > 0:
        log.debug("Load data from DB.")
        entities = Entity.objects.filter(project=p)

        data = []
        for e in entities:
            try:
                t = Translation.objects.get(entity=e, locale=l)
                translation = t.string
            except Translation.DoesNotExist:
                translation = ""

            obj = {
                "key": e.string,
                "comment": e.comment,
                "translation": translation
            }
            data.append(obj)

        log.debug(json.dumps(data, indent=4))
        return HttpResponse(callback + '(' + json.dumps(data, indent=4) + ');')

    else:
        log.debug("Load data from Transifex.")
        """Check if user authenticated to Transifex."""
        if project == 'testpilot':
            username = 'pontoon'
            password = 'mozilla'
        else:
            profile = request.user.get_profile()
            username = profile.transifex_username
            password = base64.decodestring(profile.transifex_password)
        if not (password or username):
            return HttpResponse(callback + '(authenticate);')

        """Make GET request to Transifex API."""
        response = _request('get', project, resource, locale, username, password)

        """Save Transifex data to DB."""
        if response.status_code == 200:
            log.debug(response.content)
            entities = json.loads(response.content)
            p = Project.objects.filter(name=project)
            if len(p) > 0:
                """Add locale and translations to the project."""
                p[0].locales.add(l)

                for entity in entities:
                    e = Entity.objects.filter(project=p[0], string=entity["key"])
                    translation = entity["translation"]
                    if len(translation) > 0:
                        t = Translation(entity=e[0], locale=l, string=translation, 
                            author=entity["user"], date=datetime.datetime.now())
                        t.save()
            else:
                """Create a new project."""
                p = Project(name=project, url=project_url)
                p.save()
                p.locales.add(l)

                for entity in entities:
                    e = Entity(project=p, string=entity["key"])
                    comment = entity["comment"]
                    if len(comment) > 0:
                        e.comment = comment
                    e.save()
                    translation = entity["translation"]
                    if len(translation) > 0:
                        t = Translation(entity=e, locale=l, string=translation, 
                            author=entity["user"], date=datetime.datetime.now())
                        t.save()

            log.debug("Transifex data saved to DB.")
        return HttpResponse(callback + '(' + response.content + ');')

def _generate_po_content(data):
    """
    Generate PO content from data JSON.

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

    response = HttpResponse()
    if type == 'json':
        response['Content-Type'] = 'application/json'
    elif type == 'html':
        response['Content-Type'] = 'text/html'
    elif type == 'po':
        content = _generate_po_content(content)
        response['Content-Type'] = 'text/plain'

    response.content = content
    response['Content-Disposition'] = 'attachment; filename=' + locale +\
            '.' + type
    return response

@login_required(redirect_field_name='', login_url='/404')
def transifex_save(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    try:
        data = json.loads(request.GET['data'])
    except MultiValueDictKeyError:
        raise Http404

    """Check if user authenticated to Transifex."""
    profile = request.user.get_profile()
    username = data.get('auth', {}).get('username', profile.transifex_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.transifex_password))
    if not (password or username):
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
    response = _request('put', data['project'], data['resource'], data['locale'], username, password, payload)

    """Save Transifex username and password."""
    if 'auth' in data and 'remember' in data['auth'] and data['auth']['remember'] == 1:
        profile.transifex_username = data['auth']['username']
        profile.transifex_password = base64.encodestring(data['auth']['password'])
        profile.save()

    try:
        return HttpResponse(response.status_code)
    except AttributeError:
        return HttpResponse(response)

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
        response_data = {'registered': True, 'browserid': verification}

    return HttpResponse(json.dumps(response_data), mimetype='application/json')
