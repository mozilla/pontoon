
import logging

from django import http
from django.http import HttpResponse
from django.shortcuts import render

import subprocess

import commonware
from funfactory.log import log_cef
from mobility.decorators import mobile_template


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
    data = {}  # You'd add data here that you're sending to the template.
    log.debug("Save to Transifex")

    locale = request.GET['locale'];
    username = request.GET['transifex[username]'];
    password = request.GET['transifex[password]'];
    project = request.GET['transifex[project]'];
    resource = request.GET['transifex[resource]'];
    data = request.GET['transifex[po]'];

    """ Save PO file to Pontoon server """
    f = open(locale + '.po', 'w')
    f.write(data.encode('utf-8'))
    f.close()

    """ Save PO file to Transifex """
    subprocess.call("curl -i -L --user " + username + ":" + password + " -F file=@" + locale + ".po -X PUT https://www.transifex.net/api/2/project/" + project + "/resource/" + resource + "/translation/" + locale + "/", shell=True);
    
    return HttpResponse()
