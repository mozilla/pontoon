"""Example views. Feel free to delete this app."""

from django import http
from django.shortcuts import render

import bleach
import commonware
from mobility.decorators import mobile_template
from session_csrf import anonymous_csrf


log = commonware.log.getLogger('playdoh')


@mobile_template('examples/{mobile/}home.html')
def home(request, template=None):
    """Main example view."""
    data = {}  # You'd add data here that you're sending to the template.
    log.debug("I'm alive!")
    return render(request, template, data)


@anonymous_csrf
def bleach_test(request):
    """A view outlining bleach's HTML sanitization."""
    allowed_tags = ('strong', 'em')

    data = {}

    if request.method == 'POST':
        bleachme = request.POST.get('bleachme', None)
        data['bleachme'] = bleachme
        if bleachme:
            data['bleached'] = bleach.clean(bleachme, tags=allowed_tags)

    return render(request, 'examples/bleach.html', data)
