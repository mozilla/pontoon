
import logging

from django import http
from django.shortcuts import render

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
