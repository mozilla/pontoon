"""Example views. Feel free to delete this app."""

from django import http

import bleach
import commonware
import jingo
from session_csrf import anonymous_csrf


log = commonware.log.getLogger('playdoh')

def home(request):
    """Main example view."""
    data = {}  # You'd add data here that you're sending to the template.
    log.debug("I'm alive!")
    return jingo.render(request, 'examples/home.html', data)


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

    return jingo.render(request, 'examples/bleach.html', data)
