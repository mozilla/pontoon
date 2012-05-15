
import logging
import urllib2
import base64

from django import http
from django.http import HttpResponse
from django.shortcuts import render

import commonware
from funfactory.log import log_cef
from mobility.decorators import mobile_template
from web import *


log = commonware.log.getLogger('playdoh')


@mobile_template('{mobile/}home.html')
def home(request, template=None):
    """Main example view."""
    data = {}  # You'd add data here that you're sending to the template.
    log.debug("I'm alive!")
    return render(request, template, data)

def download(request, template=None):
    """Download translations in appropriate form."""
    log.debug("Download translations")

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

def transifex(request, template=None):
    """Save translations to Transifex."""
    log.debug("Save to Transifex")

    locale = request.GET['locale']
    username = request.GET['transifex[username]']
    password = request.GET['transifex[password]']
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
    urllib2.urlopen(req, timeout=10)

    return HttpResponse()
