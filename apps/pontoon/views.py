
import logging
import urllib2
import base64
import json
import traceback

from django import http
from django.http import HttpResponse
from django.shortcuts import render

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

import commonware
from funfactory.log import log_cef
from mobility.decorators import mobile_template
from web import *

from django_browserid import verify as browserid_verify
from django_browserid import get_audience
from django.http import (HttpResponseBadRequest, HttpResponseForbidden)
from django.contrib import auth
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


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
    return render(request, template, data)

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

@login_required(login_url='/')
def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations.")

    type = request.POST['type']
    data = request.POST['data']
    locale = request.POST['locale']

    response = HttpResponse(data)
    if type == 'json':
        response['Content-Type'] = 'application/json'
    elif type == 'html':
        response['Content-Type'] = 'text/html'
    elif type == 'po':
        response['Content-Type'] = 'text/plain'

    response['Content-Disposition'] = 'attachment; filename=' + locale + '.' + type
    return response

@login_required(login_url='/')
def transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex.")

    profile = request.user.profile
    username = request.GET.get('auth[username]', profile.transifex_username)
    password = request.GET.get('auth[password]', profile.transifex_password)

    if not (password or username):
        return HttpResponse("authenticate")

    locale = request.GET['locale']
    project = request.GET['transifex[project]']
    resource = request.GET['transifex[resource]']
    po = request.GET['transifex[po]']

    """ Save PO file to Pontoon server """
    f = open(locale + '.po', 'w')
    f.write(po.encode('utf-8'))
    f.close()

    """ Save PO file to Transifex """
    url = 'https://www.transifex.net/api/2/project/' + project + '/resource/' + resource + '/translation/' + locale + '/'
    data = { "resource" : resource,
             "language" : locale,
             "uploaded_file" : open(locale + '.po', 'rb') }
    req = RequestWithMethod(url=url, data=data, method='PUT')

    base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
    req.add_header("Authorization", "Basic %s" % base64string)
    req.add_header("Accept-Encoding", "gzip,deflate")
    urllib2.install_opener(urllib2.build_opener(MultipartPostHandler))

    try: 
        urllib2.urlopen(req, timeout=10)
    except urllib2.HTTPError, e:
        log.debug('HTTPError: ' + str(e.code))
        if e.code == 401:
            return HttpResponse("authenticate")
        return HttpResponse("error")
    except urllib2.URLError, e:
        log.debug('URLError: ' + str(e.reason))
        return HttpResponse("error")
    except httplib.HTTPException, e:
        log.debug('HTTPException')
        return HttpResponse("error")
    except Exception:
        log.debug('Generic exception: ' + traceback.format_exc())
        return HttpResponse("error")

    """ TODO: Save Transifex credentials """
    if 'auth[remember]' in request.GET:
        log.debug("UN: " + username)
        log.debug("PW: " + password)
        log.debug(request.GET['auth[remember]'])
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
