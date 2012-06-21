
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
from django.http import (HttpResponse, HttpResponseBadRequest, HttpResponseForbidden)
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django_browserid import verify as browserid_verify
from django_browserid import get_audience

from funfactory.log import log_cef
from mobility.decorators import mobile_template


log = commonware.log.getLogger('playdoh')


@mobile_template('{mobile/}home.html')
def home(request, locale=None, url=None, template=None):
    """Main view."""
    log.debug("Main view.")

    data = {
        'locale_code': locale,
        'project_url': url,
        'accept_language': request.META['HTTP_ACCEPT_LANGUAGE'].split(',')[0]
    }

    if hasattr(settings, 'MICROSOFT_TRANSLATOR_API_KEY'):
        data['mt_apikey'] = settings.MICROSOFT_TRANSLATOR_API_KEY

    return render(request, template, data)

@login_required(redirect_field_name='', login_url='/')
def check_url(request, template=None):
    """Check if URL exists."""
    log.debug("Check if URL exists.")
    log.debug(request.GET['url'])

    validate = URLValidator(verify_exists=True)
    try:
        validate(request.GET['url'])
        status = "valid"
    except ValidationError, e:
        log.debug(e)
        status = "invalid"
    return HttpResponse(status)

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

@login_required(redirect_field_name='', login_url='/')
def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations.")
    type = request.GET['type']
    data = request.GET['data']
    locale = request.GET['locale']

    response = HttpResponse()
    if type == 'json':
        response['Content-Type'] = 'application/json'
    elif type == 'html':
        response['Content-Type'] = 'text/html'
    elif type == 'po':
        data = _generate_po_content(data)
        response['Content-Type'] = 'text/plain'

    response.content = data
    response['Content-Disposition'] = 'attachment; filename=' + locale +\
            '.' + type
    return response

@login_required(redirect_field_name='', login_url='/')
def transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    data = json.loads(request.GET['data'])

    """Check if user authenticated to Transifex."""
    profile = request.user.get_profile()
    log.debug("PROFILE");
    log.debug(profile.transifex_username);
    log.debug(profile.transifex_password);
    log.debug("PROFILE");
    username = data.get('auth', {}).get('username', profile.transifex_username)
    password = data.get('auth', {}).get('password', base64.decodestring(profile.transifex_password))
    if not (password or username):
        return HttpResponse("authenticate")

    """Make PUT request to Transifex API."""
    project = data['project']
    resource = data['resource']
    locale = data['locale']
    url = 'https://www.transifex.net/api/2/project/' + project + '/resource/' + resource + '/translation/' + locale + '/strings/'
    headers = {'content-type': 'application/json'}

    payload = []
    for entity in data.get('strings'):
        obj = {
            # Identify translation strings using hashes
            "source_entity_hash": md5(':'.join([entity['original'], '']).encode('utf-8')).hexdigest(),
            "translation": entity['translation']
        }
        payload.append(obj)

    try:
        r = requests.put(url, auth=(username, password), data=json.dumps(payload), headers=headers, timeout=10)
        log.debug(r.text)
        if r.status_code == 401:
            return HttpResponse("authenticate")
    except requests.exceptions.ConnectionError, e: # Network problem (DNS failure, refused connection, etc.)
        log.debug('ConnectionError: ' + str(e))
        return HttpResponse("error")
    except requests.exceptions.HTTPError, e: # Invalid HTTP response
        log.debug('HTTPError: ' + str(e))
        return HttpResponse("error")
    except requests.exceptions.URLRequired, e: # A valid URL is required
        log.debug('URLRequired: ' + str(e))
        return HttpResponse("error")
    except requests.exceptions.Timeout, e: # Request times out
        log.debug('Timeout: ' + str(e))
        return HttpResponse("error")
    except requests.exceptions.TooManyRedirects, e: # Request exceeds the number of maximum redirections
        log.debug('TooManyRedirects: ' + str(e))
        return HttpResponse("error")
    except requests.exceptions.RequestException, e: # Ambiguous exception occurres
        log.debug('RequestException: ' + str(e))
        return HttpResponse("error")
    except Exception:
        log.debug('Generic exception: ' + traceback.format_exc())
        return HttpResponse("error")

    """Save Transifex username and password."""
    if 'auth' in data and 'remember' in data['auth'] and data['auth']['remember'] == '1':
        profile.transifex_username = data['auth']['username']
        profile.transifex_password = base64.encodestring(data['auth']['password'])
        profile.save()
    return HttpResponse("done")

@require_POST
def verify(request, template=None):
    """Verify BrowserID assertion, and return whether a user is registered."""
    log.debug("Verify BrowserID assertion.")

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
